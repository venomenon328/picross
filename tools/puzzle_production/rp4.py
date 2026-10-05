"""Bounded RP-4 corpus production/replay. No model calls, search or repair."""
from __future__ import annotations

import argparse
from collections import Counter
import html
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import Image, ImageDraw, ImageOps

from .contract import Budget, InvalidInput, load_json, write_json
from .images import file_hash, import_image, inspect_candidate, normalize, validate_design

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / 'examples/rp4'
CLASSES = {'illustration', 'ai_template', 'photo_clear', 'photo_difficult'}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidInput(message)


def local(root: Path, name: str) -> Path:
    require(isinstance(name, str) and '\\' not in name, 'Invalid local path')
    p = root / name
    require(not Path(name).is_absolute() and '..' not in Path(name).parts and
            not p.is_symlink() and p.resolve().is_relative_to(root.resolve()), 'Unsafe local path')
    require(p.is_file(), f'Missing file: {name}')
    return p


def plan_sources(root: Path) -> tuple[dict, dict]:
    plan = load_json(root / 'plan.json')
    require(plan['format'] == 'picross-rp4-plan-v1' and plan['selection_before_solver'] is True,
            'Unsupported/unfixed corpus')
    sources = plan['sources']
    require(len(sources) == 12 and len({s['id'] for s in sources}) == 12, 'Need twelve unique sources')
    require(Counter(s['class'] for s in sources) == Counter({k: 3 for k in CLASSES}), 'Wrong source classes')
    require({s['mode'] for s in sources} == {'mono', 'color'}, 'Missing color/mono coverage')
    require(any(s['width'] != s['height'] for s in sources), 'Missing rectangular case')
    large = {s['id'] for s in sources if s['large'] is True}
    require(len(large) >= 4 and large == set(plan['policy']['large_sources']), 'Missing distinct large sources')
    policy = plan['policy']
    require(policy['variants_per_arm'] == 2 and policy['ai_rounds_per_asset'] == 1 and
            policy['raster_edits'] == 0, 'Changed comparison budget')
    Budget(policy['solver_seconds'], policy['max_lines'])
    Budget(policy['verifier_seconds'], policy['max_lines'])
    files = {'plan.json': file_hash(root / 'plan.json')}
    for s in sources:
        p = local(root, s['file'])
        require(file_hash(p) == s['sha256'], 'Source changed after selection')
        normal, _, _ = normalize(p)
        require(list(normal.size) == s['dimensions'], 'Wrong source dimensions')
        require(bool(s['rights']) and bool(s['origin']) and bool(s['briefing']), 'Missing provenance/briefing')
        files[s['file']] = s['sha256']
        if s['ai_prompt']:
            files[s['ai_prompt']] = file_hash(local(root, s['ai_prompt']))
        if s['class'].startswith('photo'):
            for name in (s['stylization_prompt'], s['style_reference'], f"stylized/{s['id']}.png"):
                files[name] = file_hash(local(root, name))
            reference, _, _ = normalize(root / s['style_reference'])
            expected = normal.crop(s['crop'])
            require(reference.size == expected.size and reference.tobytes() == expected.tobytes(),
                    'Style reference differs from planned crop')
    return plan, files


def expected_trials(root: Path, plan: dict) -> list[dict]:
    trials = []
    for s in plan['sources']:
        arms = ['direct', 'stylized'] if s['class'].startswith('photo') else ['direct']
        sizes = [(s['width'], s['height'])] + ([(100, 100)] if s['large'] else [])
        for w, h in sizes:
            for arm in arms:
                name = f"{s['id']}-{arm}-{w}x{h}"
                source = s['file'] if arm == 'direct' else f"stylized/{s['id']}.png"
                normal, _, _ = normalize(local(root, source))
                crop = s['crop'] if arm == 'direct' else [0, 0, *normal.size]
                if (w, h) == (100, 100):
                    require(crop[2]-crop[0] >= 100 and crop[3]-crop[1] >= 100,
                            'Large attempt requires source-resolution input, not small raster')
                variants = [{'id': 'area-128', 'method': 'area', 'threshold': 128}]
                variants += ([{'id': 'area-176', 'method': 'area', 'threshold': 176}] if s['mode'] == 'mono'
                             else [{'id': 'contour-40', 'method': 'contour', 'threshold': 40}])
                design = validate_design({
                    'format': 'picross-image-design-v1', 'source_id': s['id'],
                    'origin': s['origin'] + ('; one built-in image stylization, original in plan.json' if arm == 'stylized' else ''),
                    'rights': s['rights'], 'briefing': s['briefing'], 'working_mode': 'faithful',
                    'width': w, 'height': h, 'crop': crop, 'fit': 'contain',
                    'background': '#ffffff', 'alpha_below': 128, 'mode': s['mode'],
                    'palette': s['palette'], 'variants': variants})
                trials.append({'id': name, 'source_id': s['id'], 'arm': arm,
                               'input': source, 'design_file': f'designs/{name}.json', 'design': design})
    return trials


def freeze(root: Path) -> dict:
    require(not (root / 'inputs.json').exists(), 'Input lock already exists')
    plan, files = plan_sources(root)
    trials = expected_trials(root, plan)
    (root / 'designs').mkdir(exist_ok=True)
    for t in trials:
        write_json(root / t['design_file'], t['design'])
        files[t['design_file']] = file_hash(root / t['design_file'])
    for name in ('generation.json', 'effort.json', 'create_illustrations.py', 'SELECTION.md'):
        files[name] = file_hash(local(root, name))
    lock = {'format': 'picross-rp4-inputs-v1', 'selection_commit':
            '37c97a6215a550a6e74fd2536a30c8ff13d9baba', 'files': files, 'trials': trials}
    write_json(root / 'inputs.json', lock)
    return lock


def validate_inputs(root: Path) -> tuple[dict, dict]:
    plan, files = plan_sources(root)
    lock = load_json(root / 'inputs.json')
    require(lock['format'] == 'picross-rp4-inputs-v1', 'Wrong input lock')
    trials = expected_trials(root, plan)
    require(lock['trials'] == trials, 'Missing/changed/duplicate paired trial or design')
    for t in trials:
        p = local(root, t['design_file'])
        require(load_json(p) == t['design'], 'Stored design differs from paired plan')
        files[t['design_file']] = file_hash(p)
    for name in ('generation.json', 'effort.json', 'create_illustrations.py', 'SELECTION.md'):
        files[name] = file_hash(local(root, name))
    require(lock['files'] == files, 'Changed or incomplete input bindings')
    generation = load_json(root / 'generation.json')
    expected = {s['file']: s['ai_prompt'] for s in plan['sources'] if s['class'] == 'ai_template'}
    expected.update({f"stylized/{s['id']}.png": s['stylization_prompt'] for s in plan['sources'] if s['class'].startswith('photo')})
    require(len(generation['calls']) == 9 and {c['output']: c['prompt'] for c in generation['calls']} == expected,
            'Missing/duplicate native image call record')
    for c in generation['calls']:
        require(c['rounds'] == 1 and c['mechanism'] == 'built-in image_gen in ChatGPT/Codex' and
                c['output_sha256'] == files[c['output']] and c['prompt_sha256'] == files[c['prompt']],
                'Incorrect generation record')
    return plan, lock


def produce(root: Path, output: Path) -> dict:
    plan, lock = validate_inputs(root)
    require(not output.exists(), 'Use a fresh output directory; never replace baseline')
    output.mkdir(parents=True)
    report = {'format': 'picross-rp4-production-v1', 'inputs_sha256': file_hash(root / 'inputs.json'),
              'producer_checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'producer_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
              'trials': []}
    policy = plan['policy']
    require(policy['solver_seconds'] == policy['verifier_seconds'], 'RP-3 import uses symmetric operation budgets')
    for t in lock['trials']:
        start = time.perf_counter()
        record = {'id': t['id'], 'status': 'started'}
        try:
            result = import_image(root / t['input'], root / t['design_file'], output / t['id'],
                                  seconds=policy['solver_seconds'], max_lines=policy['max_lines'])
            record.update(status=result['status'], candidates=result['candidates'],
                          manifest_sha256=file_hash(output / t['id'] / 'manifest.json'))
        except (OSError, ValueError, RuntimeError) as exc:
            record.update(status='import_error', error=type(exc).__name__, message=str(exc))
        record['import_wall_seconds'] = time.perf_counter() - start
        report['trials'].append(record)
        write_json(output / 'production.json', report)
        print(t['id'], record['status'], flush=True)
    return report


def inspect_trial(root: Path, bundle: Path, trial: dict, record: dict, policy: dict) -> list[dict]:
    require(record['status'] == 'produced', 'Incomplete import: inspect its recorded error')
    manifest = load_json(bundle / 'manifest.json')
    require(record['manifest_sha256'] == file_hash(bundle / 'manifest.json'), 'Baseline manifest changed')
    require(manifest['design'] == trial['design'], 'Bundle has wrong paired parameters')
    require(file_hash(bundle / manifest['original']) == file_hash(local(root, trial['input'])), 'Wrong source for trial')
    require(manifest['limits']['seconds_per_solver_or_verifier'] == policy['solver_seconds'] and
            manifest['limits']['max_lines'] == policy['max_lines'], 'Unequal original budgets')
    require(record['candidates'] == manifest['candidates'], 'Original report differs from bundle')
    variants = trial['design']['variants']
    require([c['variant'] for c in manifest['candidates']] == [v['id'] for v in variants], 'Dropped/reordered candidate')
    rows = []
    for v, entry in zip(variants, manifest['candidates']):
        c, proof, fresh = inspect_candidate(bundle, v['id'], Budget(policy['verifier_seconds'], policy['max_lines']))
        original = load_json(bundle / f"{v['id']}-result.json")
        require(entry['id'] == c['id'] and entry['technical'] == original, 'Candidate/status binding mismatch')
        require(type(original['certified']) is bool and type(original['proof_verified']) is bool, 'Invalid result flags')
        if original['proof_verified']:
            require(all(original[k] == fresh[k] for k in ('status', 'certified', 'proof_verified', 'logic_hash', 'profile_hash')),
                    'Claimed original verification differs from proof replay')
        else:
            require(original['status'] == 'aborted' and original['certified'] is False and
                    bool(original.get('reason')), 'Unverified original must be explicit aborted result')
        rows.append({'trial': trial['id'], 'variant': v['id'], 'candidate_id': c['id'],
                     'logic_hash': c['logic_hash'], 'original': original, 'fresh': fresh,
                     'logically_accepted': original['certified'] and fresh['certified'],
                     'filled_cells': sum(value != 'empty' for row in c['matrix'] for value in row),
                     'proof_steps': len(proof['steps']),
                     'unresolved_cells': sum(len(d) != 1 for row in proof['final_domains'] for d in row)})
    return rows


def verify_corpus(root: Path, baseline: Path, output: Path) -> dict:
    require(not output.exists(), 'Use a fresh verification output')
    start = time.perf_counter()
    plan, lock = validate_inputs(root)
    original = load_json(baseline / 'production.json')
    require(original['inputs_sha256'] == file_hash(root / 'inputs.json'), 'Baseline input lock changed')
    require([r['id'] for r in original['trials']] == [t['id'] for t in lock['trials']], 'Incomplete/duplicate trial results')
    require({p.name for p in baseline.iterdir()} == {'production.json', *[t['id'] for t in lock['trials']]},
            'Unexpected/missing baseline trial directory')
    rows = []
    for t, r in zip(lock['trials'], original['trials']):
        require(time.perf_counter()-start < plan['policy']['replay_total_seconds'], 'Corpus replay time budget exceeded')
        rows.extend(inspect_trial(root, baseline / t['id'], t, r, plan['policy']))
    editorial = check_reviews(root, lock, rows)
    checkout = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    result = {'format': 'picross-rp4-verification-v1', 'accepted': True,
              'source_commit': os.environ.get('RP1_SOURCE_HEAD', checkout), 'tested_checkout_commit': checkout,
              'base_commit': os.environ.get('RP1_BASE_COMMIT', plan['base_commit']),
              'source_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
              'github_run_id': os.environ.get('GITHUB_RUN_ID'),
              'inputs_sha256': file_hash(root / 'inputs.json'),
              'production_sha256': file_hash(baseline / 'production.json'),
              'source_count': 12, 'photo_pairs': 6, 'large_source_count': sum(s['large'] for s in plan['sources']),
              'trials': len(original['trials']), 'candidates': len(rows),
              'logically_accepted': sum(r['logically_accepted'] for r in rows),
              'original_status_counts': dict(Counter(r['original']['status'] for r in rows)),
              'editorial': editorial,
              'elapsed_seconds': time.perf_counter()-start, 'results': rows}
    require(result['elapsed_seconds'] <= plan['policy']['replay_total_seconds'], 'Corpus replay time budget exceeded')
    output.mkdir(parents=True)
    write_json(output / 'verification.json', result)
    return result


def check_reviews(root: Path, lock: dict, rows: list[dict]) -> dict:
    """Bind recorded judgments to actual rasters; this cannot automate seeing them."""
    reviews = load_json(root / 'reviews.json')
    require(set(reviews) == {t['id'] for t in lock['trials']}, 'Incomplete visual review coverage')
    usable = 0
    for t in lock['trials']:
        review = reviews[t['id']]
        require(bool(review['notes']) and bool(review['reviewer']) and bool(review['review_kind']), 'Missing review attribution')
        require(file_hash(local(root, review['view'])) == review['view_sha256'], 'Changed comparison view')
        require(set(review['variants']) == {v['id'] for v in t['design']['variants']}, 'Incomplete variant judgments')
        for v in t['design']['variants']:
            judgement = review['variants'][v['id']]
            row = next(r for r in rows if r['trial'] == t['id'] and r['variant'] == v['id'])
            require(judgement['verdict'] in ('recognizable', 'reveal_supported', 'needs_revision', 'rejected'), 'Unknown motif verdict')
            require(t['design']['mode'] == 'mono' or judgement['verdict'] != 'reveal_supported', 'Color needs recognizable raster')
            require(judgement['candidate_id'] == row['candidate_id'] and judgement['raster_sha256'] ==
                    file_hash(local(root, f"baseline/{t['id']}/{v['id']}-raster.png")), 'Review applies to another raster')
            acceptable = judgement['verdict'] in ('recognizable', 'reveal_supported')
            require(type(judgement['motif_usable_for_comparison']) is bool and
                    judgement['motif_usable_for_comparison'] == acceptable, 'Inconsistent motif flags')
            row['motif_verdict'] = judgement['verdict']
            row['usable_for_comparison'] = acceptable and row['logically_accepted']
            usable += row['usable_for_comparison']
    effort = load_json(root / 'effort.json')
    require({r['stage'] for r in effort['human']} == {'preparation', 'ai_rounds', 'raster_editing', 'visual_inspection'} and
            len(effort['human']) == 4 and all(r['minutes'] is None and r['status'] == 'not_observed' for r in effort['human']),
            'Human effort must remain explicitly unobserved for this agent-only run')
    require(effort['productivity_per_human_hour'] is None, 'No productivity ratio without human time')
    return {'reviews_sha256': file_hash(root / 'reviews.json'), 'usable_candidates': usable,
            'human_productivity_per_hour': None, 'human_effort_status': 'not_observed',
            'independent_review': 'open', 'owner_playtest': 'RP-6; not performed'}


def make_views(root: Path) -> None:
    """Exact nearest-neighbor contact sheets, without modifying any candidate."""
    plan, lock = validate_inputs(root)
    results = load_json(root / 'baseline/production.json')
    (root / 'views').mkdir(exist_ok=True)
    for s in plan['sources']:
        trials = [t for t in lock['trials'] if t['source_id'] == s['id']]
        canvas = Image.new('RGB', (1050, len(trials)*350), '#efefef')
        draw = ImageDraw.Draw(canvas)
        for i, t in enumerate(trials):
            record = next(x for x in results['trials'] if x['id'] == t['id'])
            draw.text((5, i*350+5), t['id'], fill='black')
            source, _, _ = normalize(root / t['input'])
            source = source.crop(t['design']['crop'])
            source = ImageOps.contain(source.convert('RGB'), (330, 310))
            canvas.paste(source, (5, i*350+30))
            for j, c in enumerate(record['candidates']):
                draw.text((350+j*350, i*350+5), c['variant']+' '+c['technical']['status'], fill='black')
                with Image.open(root / 'baseline' / t['id'] / (c['variant']+'-raster.png')) as cells:
                    cells = ImageOps.contain(cells, (330, 310), Image.Resampling.NEAREST)
                    canvas.paste(cells, (350+j*350, i*350+30))
        canvas.save(root / 'views' / f'{s["id"]}.png')


def make_index(root: Path) -> None:
    plan, lock = validate_inputs(root)
    reviews = load_json(root / 'reviews.json')
    production = load_json(root / 'baseline/production.json')
    require(set(reviews) == {t['id'] for t in lock['trials']}, 'Missing visual trial review')
    esc = html.escape
    parts = ['<!doctype html><html lang="de"><meta charset="utf-8"><title>RP-4 Baseline</title>',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             '<style>body{font:16px system-ui;background:#faf6ed;color:#243b3b;margin:24px}section{border-top:2px solid #999;margin:30px 0}.row{display:flex;gap:20px;flex-wrap:wrap}figure{margin:8px}img{width:300px;height:300px;object-fit:contain}.cells{image-rendering:pixelated}p{max-width:1000px}a{color:#145b78}</style>',
             '<h1>RP-4 · Unveränderte Vergleichsbaseline</h1><p>Produktionsansicht mit Motivspoiler. Logik, Motivurteil und spätere Pilotfreigabe bleiben getrennt. Menschlicher Aufwand unbekannt; keine Produktivitätsquote.</p>']
    for s in plan['sources']:
        parts.append(f'<section><h2>{esc(s["id"])} · {esc(s["title"])}</h2><p>{esc(s["briefing"])}</p>')
        for t in [t for t in lock['trials'] if t['source_id'] == s['id']]:
            r = next(r for r in production['trials'] if r['id'] == t['id'])
            review = reviews[t['id']]
            parts.append(f'<h3><a href="baseline/{t["id"]}/index.html">{t["id"]} · vollständiges RP-3-Bundle</a></h3><div class="row">')
            source_view = s['style_reference'] if t['arm'] == 'direct' and s['class'].startswith('photo') else t['input']
            for label, path, css in [('Eingabe / geplanter Ausschnitt', source_view, '')] + [
                    (f'{c["variant"]} · {c["technical"]["status"]}', f'baseline/{t["id"]}/{c["variant"]}-raster.png', 'cells') for c in r['candidates']]:
                parts.append(f'<figure><figcaption>{esc(label)}</figcaption><a href="{path}"><img class="{css}" src="{path}" alt="{esc(label)}"></a></figure>')
            parts.append('</div><p>' + esc(review['notes']) + '</p>')
        parts.append('</section>')
    (root / 'index.html').write_text('\n'.join(parts) + '\n</html>\n', encoding='utf-8')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('freeze', 'produce', 'verify', 'views', 'index'))
    p.add_argument('--corpus', type=Path, default=CORPUS)
    p.add_argument('--baseline', type=Path)
    p.add_argument('--output-dir', type=Path)
    a = p.parse_args()
    try:
        if a.command == 'freeze':
            result = freeze(a.corpus)
        elif a.command == 'views':
            make_views(a.corpus)
            result = {'views': str(a.corpus / 'views')}
        elif a.command == 'index':
            make_index(a.corpus)
            result = {'index': str(a.corpus / 'index.html')}
        else:
            require(a.output_dir is not None, '--output-dir required')
            result = (produce(a.corpus, a.output_dir) if a.command == 'produce' else
                      verify_corpus(a.corpus, a.baseline or a.corpus / 'baseline', a.output_dir))
        print(json.dumps({k: v for k, v in result.items() if k not in ('trials', 'results', 'files')}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(json.dumps({'accepted': False, 'error': type(exc).__name__, 'message': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
