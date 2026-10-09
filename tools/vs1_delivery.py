"""VS-1 native measurement, separate Windows export and compact audited delivery."""
from __future__ import annotations

import html
import json
import platform
import io
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import p1_preflight as toolchain

GF1_BASE = 'c19b3547eef81fbb7c3c5389834f7cc896c86069'


def gf1_before_project(root: Path, workspace: Path) -> Path:
    payload = subprocess.check_output(['git', 'archive', GF1_BASE, 'prototypes/p1'], cwd=root)
    destination = workspace / 'gf1-before'
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to('prototypes/p1')
            if '..' in relative.parts:
                raise toolchain.PreflightError('Unsafe GF1 comparison path')
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.extractfile(member).read())
    # Fonts provisioned from the same pinned resource manifest.
    for name in ('Fraunces.ttf', 'PlexSans.ttf'):
        shutil.copyfile(root / 'prototypes/p1/art/book' / name, destination / 'art/book' / name)
    shutil.copyfile(root / 'prototypes/p1/tests/vs1_gf1_capture.gd', destination / 'tests/vs1_gf1_capture.gd')
    return destination


def verify_gf1_pairs(renders: Path) -> dict:
    reports = {side: json.loads((renders/f'gf1-{side}.json').read_text(encoding='utf-8')) for side in ('before','after')}
    plan = json.loads((Path(__file__).resolve().parents[1]/'examples/vs1/gf1-plan.json').read_text(encoding='utf-8'))
    expected = [(c['id'],c['client'],c['ui_scale'],c['mode']) for c in plan['comparisons']]
    if any(r['failures'] or r['variant'] != side or len(r['records']) != 4 or len(r['pictures']) != 4 or
           [(c['id'],c['client'],c['ui_scale'],c['mode']) for c in r['records']] != expected
           for side,r in reports.items()):
        raise toolchain.PreflightError('Incomplete GF1 comparisons')
    pairs = []
    for old, new in zip(reports['before']['records'], reports['after']['records']):
        for key in ('id','client','ui_scale','mode','cell_pitch','zoom_ceiling','raw_fit_ceiling','font_px','own_cells_sha256','history_sha256'):
            if old[key] != new[key]:
                raise toolchain.PreflightError(f'GF1 comparison differs: {key}')
        if old['reserve_slots'] != new['minimum_reserve_slots'] or old['column_clues'][1:] != new['column_clues'][1:] or old['grid'][1:] != new['grid'][1:]:
            raise toolchain.PreflightError('GF1 changes minimum/top/grid scale')
        used = (new['reserve_slots'][0]-new['minimum_reserve_slots'][0])*26*new['ui_scale']
        if used < 0 or abs(used-new['horizontal_used_px']) > 0.00001 or abs(new['grid'][0]-old['grid'][0]-used) > 0.00001 or new['horizontal_used_px'] > new['horizontal_budget_px'] + 0.00001 or not new['grid_fit']:
            raise toolchain.PreflightError('GF1 exceeds horizontal budget/frame')
        if new['id'] == 'VS08' and (new['reserve_slots'][0] != 13 or new['axis_counts']['row']['hidden_numbers'] or new['cell_pitch'] != (18.77 if new['ui_scale']==1 else 17.06)):
            raise toolchain.PreflightError('GF-A01 failed')
        pairs.append({'before':old,'after':new})
    for side,report in reports.items():
        for comparison,picture in zip(plan['comparisons'],report['pictures']):
            if picture['file'] != f"gf1-{side}-{comparison['id']}-u{round(comparison['ui_scale']*100)}.png":
                raise toolchain.PreflightError('GF1 image/case binding differs')
            toolchain.verify_sha256(renders/picture['file'],picture['sha256'])
    return {'baseline_commit':GF1_BASE,'pairs':pairs,'pictures':reports['before']['pictures']+reports['after']['pictures']}


def capture_command(render_command):
    if render_command.count('res://tests/capture.gd') != 1:
        raise toolchain.PreflightError('VS1 unknown native harness command')
    return ['res://tests/vs1_capture.gd' if part=='res://tests/capture.gd' else part for part in render_command]


def verify(renders: Path) -> dict:
    report=json.loads((renders/'vs1-matrix.json').read_text(encoding='utf-8'))
    expected={(f'VS{i:02}',w,u,m) for i in range(1,11) for w in (1280,1920) for u in (1.0,1.25) for m in ('G','V')}
    rows=report['records']
    main=[r for r in rows if r['client'][0] in (1280,1920)]
    actual={(r['id'],r['client'][0],r['ui_scale'],r['mode']) for r in main}
    if report['failures'] or actual!=expected or len(main)!=80 or len(rows)!=100:
        raise toolchain.PreflightError('VS1 incomplete/failed native matrix')
    for row in rows:
        if not row['spoiler_free']:
            raise toolchain.PreflightError('VS1 reveal exposed before completion')
        if row['mode']=='R': continue
        if row['layout_valid'] and not row['grid_fit']:
            raise toolchain.PreflightError('VS1 full grid assertion failed')
        if row['mode']=='V' and row['hidden_tokens']:
            raise toolchain.PreflightError('VS1 V silently hides hints')
        if row['controls_clipped'] or row['control_overlaps'] or row['control_collisions']:
            raise toolchain.PreflightError('VS1 controls overlap board or leave client')
        if row['status']=='geometric_fit_owner_open' and (row['cell_pitch']<16 or row['glyph_collisions'] or row['clipped_glyphs']):
            raise toolchain.PreflightError('VS1 failed case reported as positive')
        if [p['requested'] for p in row['checkpoints']] != [16,18,20]:
            raise toolchain.PreflightError('VS1 missing compact checkpoints')
    for picture in report['pictures']+report['diagnostics']:
        if Path(picture['file']).name!=picture['file'] or toolchain.sha256_file(renders/picture['file'])!=picture['sha256']:
            raise toolchain.PreflightError('VS1 image binding differs')
    if {d['id'] for d in report['diagnostics']}!={'VS-D11','VS-D12'} or any(d['certified'] for d in report['diagnostics']):
        raise toolchain.PreflightError('VS1 diagnosis certification error')
    e1=report['VS_E1_R2']
    if len(e1)!=34 or {r['id'] for r in e1}!={*(f'VS-E{i}' for i in range(13,19)),'VS04','VS06','VS08','VS10'} or any(r['minimum_surplus']<0 or r['states']<=0 or r['certified'] for r in e1):
        raise toolchain.PreflightError('VS1 E1 incomplete actual continuous-token evidence')
    return report


def capture(root, project, workspace, output, engine, render_command, environment, phase):
    from tools.puzzle_production.vs1 import verify_cases
    corpus=verify_cases()
    phase('vs1-tests',[engine,'--headless','--path',str(project),'--script','res://tests/vs1_tests.gd'],'VS1_TESTS_OK')
    phase('vs1-e1-tests',[engine,'--headless','--path',str(project),'--script','res://tests/vs1_e1_tests.gd'],'VS1_E1_TESTS_OK')
    phase('vs1-gf1-tests',[engine,'--headless','--path',str(project),'--script','res://tests/vs1_gf1_tests.gd'],'VS1_GF1_TESTS_OK')
    # Deliberately no VS1_TEST_ROOT: exercise the same default stable root as EXE.
    for stage in ('write','read','legacy-write','legacy-read','v-write','v-read'):
        environment['VS1_STAGE']=stage
        phase('vs1-roundtrip-'+stage,[engine,'--headless','--path',str(project),'--script','res://tests/vs1_roundtrip.gd'],f'VS1_ROUNDTRIP_{stage.upper().replace("-","_")}_OK')
    environment.pop('VS1_STAGE',None)
    environment['VS1_PROBE_OUTPUT'] = str(output)
    environment['VS1_GF1_PREFIX'] = 'source'
    for stage in ('write','read'):
        environment['VS1_GF1_STAGE'] = stage
        phase('vs1-gf1-roundtrip-'+stage,[engine,'--headless','--path',str(project),'--script','res://tests/vs1_gf1_roundtrip.gd'],f'VS1_GF1_ROUNDTRIP_{stage.upper()}_OK')
    for name in ('VS1_PROBE_OUTPUT','VS1_GF1_PREFIX','VS1_GF1_STAGE'):
        environment.pop(name,None)
    renders=output/'vs1-renders'; renders.mkdir()
    old=environment.get('P1_CAPTURE_DIR')
    environment['P1_CAPTURE_DIR']=str(renders)
    try:
        phase('vs1-native-capture',capture_command(render_command),'VS1_CAPTURE_OK')
        if platform.system()=='Windows':
            phase('vs1-native-window',[engine,'--path',str(project),'--rendering-driver','opengl3','--audio-driver','Dummy','--script','res://tests/vs1_window.gd'],'VS1_WINDOW_OK')
    finally:
        if old is None: environment.pop('P1_CAPTURE_DIR',None)
        else: environment['P1_CAPTURE_DIR']=old
    evidence=verify(renders)
    before = gf1_before_project(root, workspace)
    phase('vs1-gf1-before-import',[engine,'--headless','--path',str(before),'--import'])
    environment['P1_CAPTURE_DIR'] = str(renders)
    environment['VS1_GF1_PLAN'] = str(root/'examples/vs1/gf1-plan.json')
    for variant, source in (('before',before),('after',project)):
        environment['VS1_GF1_VARIANT'] = variant
        command = [str(source) if part == str(project) else 'res://tests/vs1_gf1_capture.gd' if part == 'res://tests/capture.gd' else part for part in render_command]
        phase('vs1-gf1-'+variant+'-capture',command,'VS1_GF1_CAPTURE_OK')
    environment.pop('VS1_GF1_VARIANT')
    environment.pop('VS1_GF1_PLAN')
    if old is None: environment.pop('P1_CAPTURE_DIR',None)
    else: environment['P1_CAPTURE_DIR']=old
    evidence['GF1'] = verify_gf1_pairs(renders)
    evidence['corpus_replay']=corpus
    return evidence


def export(project, workspace, output, base, phase, host):
    settings=project/'project.godot'; presets=project/'export_presets.cfg'
    original=settings.read_text(encoding='utf-8'); preset=presets.read_text(encoding='utf-8')
    # Preserve app identity. Isolation is explicit before any save read in create_store.
    changed=original.replace('run/main_scene="res://main.tscn"','run/main_scene="res://full_view_study/main.tscn"')
    if changed==original: raise toolchain.PreflightError('VS1 entry not set')
    build=workspace/'vs1-windows'; build.mkdir()
    try:
        settings.write_text(changed,encoding='utf-8')
        filtered=preset.replace('exclude_filter="tests/*,data/*proof*,study/*,full_view_study/*"', 'exclude_filter="tests/*,data/*,art/f*.png,art/f*.svg"')
        filtered=filtered.replace('include_filter="','include_filter="full_view_study/*.json,full_view_study/cases/*/*.json,')
        if filtered==preset: raise toolchain.PreflightError('VS1 export filters not set')
        presets.write_text(filtered,encoding='utf-8')
        phase('vs1-export-import',base+['--import'])
        phase('vs1-separate-start',base+['--','--vs1-smoke'],'VS1_START_OK')
        phase('vs1-windows-export',base+['--export-debug','P1 Windows x86_64',str(build/'picross-vs1.exe')])
        if host=='Windows':
            phase('vs1-exported-start',[str(build/'picross-vs1.console.exe'),'--headless','--','--vs1-smoke'],'VS1_START_OK')
            phase('vs1-exported-gui-start',[str(build/'picross-vs1.console.exe'),'--rendering-driver','opengl3','--','--vs1-smoke'],'VS1_START_OK')
    finally:
        settings.write_text(original,encoding='utf-8'); presets.write_text(preset,encoding='utf-8')
    files={p.name:toolchain.sha256_file(p) for p in build.iterdir() if p.is_file()}
    if set(files)!={'picross-vs1.exe','picross-vs1.console.exe'}: raise toolchain.PreflightError('VS1 unexpected export')
    return build,files


def package(root, output, build, files, product, evidence):
    manifest={k:product[k] for k in ('source_commit','source_tree_dirty','tested_checkout_commit','base_commit','github_run_id','host','engine_version','assets')}
    manifest.update(developer_reference_commit=evidence.get('developer_reference_commit'), schema=1,study='VS-1 revision 1 / VS-GF1',modes=['G','V'],drawing_basis=product['source_commit'],
                    historical_selection_commit='985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f',
                    drawing_sources={name:toolchain.sha256_file(root/'prototypes/p1'/name) for name in
                                     ('ui/board.gd','ui/drawing_board.gd','ui/pencil_marks.gd','study/board.gd','full_view_study/board.gd')},export_files=files,
                    plan_sha256=toolchain.sha256_file(root/'examples/vs1/plan.json'),corpus_manifest_sha256=toolchain.sha256_file(root/'examples/vs1/manifest.json'),
                    matrix_sha256=toolchain.sha256_file(output/'vs1-renders/vs1-matrix.json'),
                    gf1_baseline_commit=GF1_BASE,gf1_plan_sha256=toolchain.sha256_file(root/'examples/vs1/gf1-plan.json'),
                    VS_M01='Incomplete personal protocol; prior integration approved',VS_D01='CONFIRMED / docs/VS1_DECISION.md',GF_M01='PASSED historical #59 / PR #60 comment-6076039228; new ZS2 acceptance remains open',independent_review='OPEN',
                    decision_sha256=toolchain.sha256_file(root/'docs/VS1_DECISION.md'),
                    windows_download_probe='Separate implementer evidence in PR; CI Linux export is not a native Windows launch')
    report=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'
    (output/'vs1-report.json').write_text(report,encoding='utf-8')
    if build is not None: # Explicit legacy developer export only; never standard CI.
        player=output/'picross-vs1-windows-x86_64.zip'
        with zipfile.ZipFile(player,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
            for name in files: bundle.write(build/name,name)
            bundle.writestr('vs1-report.json',report)
            bundle.write(root/'docs/VS1_OWNER_TRIAL.md','README.txt')
            bundle.write(root/'examples/vs1/gf1-owner-protocol.json','owner-protocol.json')
            for path in (root/'prototypes/p1/art/book').glob('*-OFL.txt'): bundle.write(path,'licenses/'+path.name)
            bundle.write(root/'prototypes/p1/study/fonts/NOTICES.md','licenses/study-fonts-NOTICES.md')
        audit(player,files)
    review=output/'picross-vs1-review.zip'
    with zipfile.ZipFile(review,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
        for item in evidence['pictures']+evidence['diagnostics']+evidence['GF1']['pictures']: bundle.write(output/'vs1-renders'/item['file'],item['file'])
        for variant in ('before','after'): bundle.write(output/'vs1-renders'/f'gf1-{variant}.json',f'gf1-{variant}.json')
        bundle.write(output/'vs1-renders/vs1-matrix.json','vs1-matrix.json')
        bundle.writestr('vs1-report.json',report)
        for name in ('VS1_STUDY.md','VS1_VERIFICATION.md','VS1_DECISION.md'): bundle.write(root/'docs'/name,name)
        for name in ('manifest.json','plan.json','plan-vb1.json','production.json','owner-protocol.json'): bundle.write(root/'examples/vs1'/name,name)
        bundle.write(root/'examples/vs1/historical-reference.json','historical-reference.json')
        for name in ('gf1-plan.json','gf1-owner-protocol.json'): bundle.write(root/'examples/vs1'/name,name)
        for path in output.glob('source-gf1-*.json'): bundle.write(path,path.name)
        for path in (output/'logs').glob('vs1-*.log'): bundle.write(path,'logs/'+path.name)
        bundle.writestr('index.html',gallery(evidence))
    for p in ((player,review) if build is not None else (review,)): print(f'VS1 ARTIFACT {p} sha256:{toolchain.sha256_file(p)}',flush=True)


def audit(archive, files):
    import hashlib
    with zipfile.ZipFile(archive) as bundle:
        if len(bundle.namelist())!=len(set(bundle.namelist())): raise toolchain.PreflightError('VS1 duplicate archive entry')
        for name,digest in files.items():
            if hashlib.sha256(bundle.read(name)).hexdigest()!=digest: raise toolchain.PreflightError('VS1 ZIP executable differs')
        if any(n.endswith(('.pck','.gd','.tscn','.png')) or '..' in n for n in bundle.namelist()): raise toolchain.PreflightError('VS1 player contains review/source files')


def gallery(evidence):
    rows=''.join(f"<tr><td>{r['id']}</td><td>{r['client']} / {r['ui_scale']}</td><td>{r['mode']}</td><td>{r['cell_pitch']:.2f}</td><td>{r['font_px']}</td><td>{r['hidden_tokens']} / {r['clipped_glyphs']} / {r['glyph_collisions']}</td><td>{html.escape(r['status'])}</td></tr>" for r in evidence['records'])
    pictures=''.join(f"<figure><figcaption>{html.escape(p['file'])}</figcaption><a href='{p['file']}'><img loading='lazy' src='{p['file']}'></a></figure>" for p in evidence['GF1']['pictures']+evidence['pictures']+evidence['diagnostics'])
    return "<!doctype html><html lang='de'><meta charset='utf-8'><title>VS-GF1 Nachweise</title><style>body{font:16px system-ui;margin:24px;background:#faf6ec;color:#343f42}td,th{border:1px solid #ccc;padding:5px}img{max-width:100%}figure{margin:32px 0}</style><h1>VS-GF1 · technische Vergleichsprobe</h1><p>Native logische SubViewports, keine physische Display-/Komfortabnahme. PNG für 1:1-Prüfung öffnen. VS-D01 bestätigt; GF-M01 und unabhängiges Review offen, früherer persönlicher VS-M01-Bericht unvollständig. Diagnosebilder sind nicht zertifizierte Rätsel.</p><table><tr><th>Fall</th><th>Client / UI</th><th>Modus</th><th>Zellabstand</th><th>Schrift px</th><th>versteckt / abgeschnitten / Kollisionen</th><th>Status</th></tr>"+rows+'</table>'+pictures+'</html>'
