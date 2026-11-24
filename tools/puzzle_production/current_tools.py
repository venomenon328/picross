"""Current image/raster preparation; only useful result files survive the call."""
import argparse
import json
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
from time import monotonic
from . import catalog_io as io, current_authoring as current, current_content as content
from .authoring_package import require
from .raster_parameters import require_color_count, used_foreground
from .contract import Budget, Aborted
from .background_contract import BackgroundError


def independent_verification(logic, proof, seconds, lines, pair_work, pair_records, shared):
    args = [sys.executable, '-m', 'tools.puzzle_production', 'verify',
            '--input', str(logic), '--proof', str(proof)]
    if shared is not None:
        seconds = max(0, shared.deadline - monotonic())
        lines = shared.max_lines - shared.lines
        pair_work = shared.max_pair_work - shared.pair_work
        pair_records = shared.max_pair_records  # Peak live storage, released between processes.
        args.extend(['--deadline', str(shared.deadline)])
    args.extend(['--seconds', str(seconds), '--max-lines', str(lines),
                 '--max-pair-work', str(pair_work), '--max-pair-records', str(pair_records)])
    process = subprocess.run(args, cwd=Path(__file__).resolve().parents[2],
                             capture_output=True, timeout=seconds + 30)
    require(process.returncode in (0, 4), 'Independent current proof process failed')
    require(len(process.stdout) <= 1024 * 1024, 'Oversized proof process result')
    checked = json.loads(process.stdout)
    current.encoded(checked)
    if shared is not None and process.returncode == 4 and checked.get('status') == 'aborted':
        raise Aborted('verifier_' + (checked.get('message') or checked.get('reason') or 'aborted'))
    require(checked.get('proof_verified') is True, 'Independent current proof not checked')
    if shared is not None:
        shared.lines += checked['line_evaluations']
        shared.pair_work += checked.get('pair_work', 0)
        shared.pair_peak_records = max(shared.pair_peak_records, checked.get('pair_peak_records', 0))
        shared.check()
    return checked


@io.bounded
def raster(definition, output, *, mode, profile='line', method='picross-difficulty-0.4',
           solve_seconds=120, solve_lines=100000, verify_seconds=120, verify_lines=100000,
           max_pair_work=20000000, max_pair_records=250000, final_budget=None):
    """Certify a current definition without import, repair or producer history."""
    from . import catalog_rating, catalog_analysis, current_rating, solver
    from .editor_raster import check_end
    raw=definition if isinstance(definition, bytes) else current.encoded(definition)
    definition,puzzle,_,_=catalog_rating.definition(raw)
    used = used_foreground(definition['solution'])
    require_color_count(mode, len(used))
    require(used == {p['id'] for p in definition['palette']}, 'Palette must contain exactly used colors')
    require(profile in ('line','paired'), 'Invalid current proof profile')
    output=io.external(output);require(not output.exists(),'Current result output already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.current-raster-',dir=output.parent) as temporary:
        work=Path(temporary);stage=work/'result';stage.mkdir()
        (stage/'definition.json').write_bytes(raw)
        budget = final_budget or Budget(solve_seconds, solve_lines, max_pair_work=max_pair_work,
                                        max_pair_records=max_pair_records)
        baseline = solver.solve(puzzle, budget)
        use_pair = profile == 'paired' and baseline['status'] == 'stalled'
        proof = solver.solve(puzzle, budget, profile='paired-lines-color') if use_pair else baseline
        if final_budget is not None and proof['status'] == 'aborted':
            raise Aborted('solver_' + proof['reason'])
        (stage/'proof.json').write_bytes(current.encoded(proof))
        # A fresh process consumes only logic/proof, never the known solution or image.
        (work/'logic.json').write_bytes(current.encoded(puzzle.to_wire()))
        if use_pair:
            (work/'baseline.json').write_bytes(current.encoded(baseline))
            if final_budget is not None:
                independent_verification(work/'logic.json', work/'baseline.json', verify_seconds, verify_lines,
                                         max_pair_work, max_pair_records, final_budget)
        checked = independent_verification(work/'logic.json', stage/'proof.json', verify_seconds, verify_lines,
                                           max_pair_work, max_pair_records, final_budget)
        current.qualification.remember(('verified-proof', puzzle.logic_hash, io.checksum((stage/'proof.json').read_bytes())), checked)
        rating_ref=None
        if checked.get('certified'):
            check_end(definition,proof)
            if final_budget is not None:
                final_budget.check()
            arguments={}
            if use_pair:
                arguments={'proof':stage/'proof.json','baseline':work/'baseline.json'}
            rating=catalog_analysis.analyze_single(stage/'definition.json',work/'analysis',production_mode=mode,method=method,**arguments)
            (stage/'difficulty.json').write_bytes(current.encoded(current_rating.from_checked(rating)))
            rating_ref=content.ref('difficulty.json',(stage/'difficulty.json').read_bytes())
        (stage/'preview.png').write_bytes(current.raster_preview(definition, mode=mode))
        refs={k:content.ref(name,(stage/name).read_bytes()) for k,name in
              (('definition','definition.json'),('proof','proof.json'),('preview','preview.png'))}
        refs['difficulty']=rating_ref
        from .catalog_publication import rename
        rename(stage,output,replace=False)
    return {'status':checked['status'],'certified':bool(checked.get('certified')),'files':refs}


@io.bounded
def image(source, design_path, output, *, puzzle_id, name, revision=1, profile='line', method='picross-difficulty-0.4',
          existing_candidate=None):
    """Use existing pixel algorithms without their old archival bundle writer."""
    from . import images, authoring_inspection
    source=io.external(source);design_path=io.external(design_path);output=io.external(output)
    raw=io.read(source.parent,source.name,32*current.LIMIT)
    design_raw=io.read(design_path.parent,design_path.name,2*current.LIMIT)
    design=images.validate_design(io.json_bytes(design_raw,2*current.LIMIT));images.versions()
    require(design['width']<=50 and design['height']<=50,'Regular raster size exceeded')
    normal,_,_=images.normalize_bytes(raw,max_bytes=images.MAX_BYTES,max_axis=images.MAX_AXIS,max_pixels=images.MAX_PIXELS)
    require(not output.exists(),'Current image output already exists')
    candidates = []
    for variant in design['variants']:
        matrix = images.rasterize(normal, design, variant)
        used = used_foreground(matrix, 'empty')
        require_color_count(design['mode'], len(used))
        candidates.append((variant['id'], matrix, used))
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.current-image-',dir=output.parent) as temporary:
        stage=Path(temporary)/'results';stage.mkdir();results=[]
        for identifier, matrix, used in candidates:
            actual=deepcopy(design);actual['palette']=[p for p in actual['palette'] if p['id'] in used]
            logic=images.logic_from_matrix(matrix,actual)
            definition,_=authoring_inspection.definition({'puzzle_id':puzzle_id},actual,matrix,logic,name,revision,puzzle_id+'.png')
            duplicate = existing_candidate(definition) if existing_candidate is not None else None
            if duplicate is not None:
                results.append({'id': identifier, 'duplicate': duplicate})
                continue
            result=raster(definition,stage/identifier,mode=design['mode'],profile=profile,method=method)
            results.append({'id':identifier,**result})
        require(io.read(source.parent,source.name,32*current.LIMIT)==raw and
                io.read(design_path.parent,design_path.name,2*current.LIMIT)==design_raw,'Current image input changed')
        from .catalog_publication import rename
        rename(stage,output,replace=False)
    return {'status':'produced','candidates':results}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    bg=sub.add_parser('background');bg.add_argument('--input',required=True,type=Path);bg.add_argument('--output',required=True,type=Path)
    bg.add_argument('--profile-id',default='picross-background-png2304x768-v1')
    for command in ('raster','image'):
        p=sub.add_parser(command);p.add_argument('--input',required=True,type=Path);p.add_argument('--output-dir',required=True,type=Path)
        p.add_argument('--profile',choices=('line','paired'),default='line');p.add_argument('--method',default='picross-difficulty-0.4')
        if command=='raster':p.add_argument('--mode',choices=('mono','color'),required=True)
        else:
            p.add_argument('--design',required=True,type=Path);p.add_argument('--puzzle-id',required=True);p.add_argument('--name',required=True)
            p.add_argument('--runtime-revision',type=int,default=1)
    args=parser.parse_args(argv)
    try:
        if args.command=='background': result=current.prepare_background(args.input,args.output,profile_id=args.profile_id)
        elif args.command=='raster':
            raw=io.read(args.input.absolute().parent,args.input.name,2*current.LIMIT)
            result=raster(io.json_bytes(raw,2*current.LIMIT),args.output_dir,mode=args.mode,profile=args.profile,method=args.method)
        else: result=image(args.input,args.design,args.output_dir,puzzle_id=args.puzzle_id,name=args.name,
                          revision=args.runtime_revision,profile=args.profile,method=args.method)
        print(current.encoded(result).decode(),end='');return 0
    except (Aborted,KeyboardInterrupt) as exc:
        print(current.encoded({'status':'aborted','message':str(exc)}).decode(),end='');return 4
    except (ValueError,OSError,RuntimeError,BackgroundError,subprocess.TimeoutExpired) as exc:
        print(current.encoded({'status':'invalid_input','message':str(exc)}).decode(),end='');return 2


if __name__=='__main__':raise SystemExit(main())
