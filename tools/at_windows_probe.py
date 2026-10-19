"""AT-N02: two genuine Windows exports, unchanged definitions and one isolated save profile."""
import argparse
import json
from pathlib import Path
import platform
import shutil
import subprocess

import p1_preflight as tc
from p1_product import run_phase, require_clean_output
from p1_evidence import source_identity
from product_fixtures import copy_regression_game
from web_tests.fixtures import adapt
from at_fixtures import install


def run(cache, output, development=False):
    root=Path(__file__).resolve().parents[1]
    if platform.system()!='Windows': raise ValueError('Actual Windows execution required')
    if not development and subprocess.check_output(['git','status','--porcelain'],cwd=root).strip():
        raise ValueError('Clean checkout required for final Windows evidence')
    if output.exists() and any(output.iterdir()): raise ValueError('Preserve previous original evidence; output must be empty')
    output.mkdir(parents=True,exist_ok=True);logs=output/'logs';logs.mkdir()
    editor=tc.EDITORS['Windows'];tc.verify_sha256(cache/editor.name,editor.sha256);tc.verify_sha256(cache/tc.TEMPLATES.name,tc.TEMPLATES.sha256)
    work=output/'workspace';work.mkdir();engine=tc.extract_editor(cache/editor.name,work/'engine','Windows')
    tc.extract_windows_templates(cache/tc.TEMPLATES.name,tc.template_directory(work,'Windows'))
    project=work/'game';copy_regression_game(root,project);adapt(project)
    shutil.copyfile(root/'game/tests/at_pack.gd',project/'ui/at_pack.gd')
    scene=project/'main.tscn'
    scene.write_text(scene.read_text(encoding='utf-8').replace('res://ui/main.gd','res://ui/at_pack.gd'),encoding='utf-8',newline='\n')
    preset=project/'export_presets.cfg';preset.write_text(preset.read_text(encoding='utf-8').replace('data/*.json,','data/fixtures/*.json,data/*.json,'),encoding='utf-8',newline='\n')
    export_environment=tc.isolated_environment(work,'Windows')
    # Both exported EXEs use exactly this same isolated native profile.
    environment=tc.isolated_environment(output/'shared-profile','Windows')
    environment['AT_PACK_OUTPUT']=str(output)
    phases=[];exports=[]
    def phase(name,command,env,marker=None):
        result=run_phase(name,command,env,300,logs);require_clean_output(result,marker)
        phases.append({k:v for k,v in result.items() if k!='output'})
    for revision in (1,2):
        fixture=install(project,revision);target=output/f'export-{revision}';target.mkdir()
        phase(f'import-{revision}',[str(engine),'--headless','--path',str(project),'--import'],export_environment)
        phase(f'export-{revision}',[str(engine),'--headless','--path',str(project),'--export-debug','P1 Windows x86_64',str(target/'picross-at.exe')],export_environment)
        exports.append(dict(fixture=fixture,files={p.name:dict(bytes=p.stat().st_size,sha256=tc.sha256_file(p)) for p in sorted(target.iterdir()) if p.is_file()}))
        for mode in (('before',) if revision==1 else ('after','restart')):
            environment['AT_PACK_MODE']=mode
            phase('process-'+mode,[str(target/'picross-at.console.exe'),'--rendering-driver','opengl3','--audio-driver','Dummy',
                '--','--p1-capture'],environment,'AT_WINDOWS_PROCESS_OK')
    reports=[json.loads((output/(mode+'.json')).read_text(encoding='utf-8')) for mode in ('before','after','restart')]
    first=reports[0]
    for report in reports:
        if report['failures'] or report['checks']<=0 or report['display']!='Windows': raise ValueError('Windows process assertions failed')
        for field in ('slots','slot_hashes','definitions','registry_sha256','profile'):
            if report[field]!=first[field]: raise ValueError('Image-only process switch changed '+field)
    if len({r['pid'] for r in reports})!=3: raise ValueError('Three real processes required')
    if exports[0]['fixture']['definitions']!=exports[1]['fixture']['definitions'] or exports[0]['fixture']['registry_sha256']!=exports[1]['fixture']['registry_sha256']:
        raise ValueError('Export definition/runtime identity changed')
    if exports[0]['files']['picross-at.pck']['sha256']==exports[1]['files']['picross-at.pck']['sha256']: raise ValueError('Second PCK was not rebuilt')
    binding=dict(format='picross-at-windows-v1',status='passed',**source_identity(root),platform=platform.platform(),exports=exports,processes=reports,phases=phases,
                 probe_sha256=tc.sha256_file(root/'game/tests/at_pack.gd'),engine_sha256=tc.sha256_file(engine),
                 originals={p.name:tc.sha256_file(p) for p in sorted(output.glob('*.png'))},independent_review='OPEN AT-A-R01')
    (output/'windows-binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('AT_WINDOWS_OK',binding['source_commit'])
    return binding


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir',required=True,type=Path);parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--development',action='store_true')
    args=parser.parse_args();run(args.cache_dir.resolve(),args.output_dir.resolve(),args.development)
