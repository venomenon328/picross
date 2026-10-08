"""VS-1 native measurement, separate Windows export and compact audited delivery."""
from __future__ import annotations

import html
import json
import zipfile
from pathlib import Path

import p1_preflight as toolchain


def verify(renders: Path) -> dict:
    report=json.loads((renders/'vs1-matrix.json').read_text(encoding='utf-8'))
    expected={(f'VS{i:02}',w,u,m) for i in range(1,11) for w in (1280,1920) for u in (1.0,1.25) for m in ('R','G','V')}
    rows=report['records']
    main=[r for r in rows if r['client'][0] in (1280,1920)]
    actual={(r['id'],r['client'][0],r['ui_scale'],r['mode']) for r in main}
    if report['failures'] or actual!=expected or len(main)!=120 or len(rows)!=150:
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
    return report


def capture(root, project, workspace, output, engine, render_command, environment, phase):
    from tools.puzzle_production.vs1 import verify_cases
    corpus=verify_cases()
    phase('vs1-tests',[engine,'--headless','--path',str(project),'--script','res://tests/vs1_tests.gd'],'VS1_TESTS_OK')
    # Deliberately no VS1_TEST_ROOT: exercise the same default stable root as EXE.
    for stage in ('write','read'):
        environment['VS1_STAGE']=stage
        phase('vs1-roundtrip-'+stage,[engine,'--headless','--path',str(project),'--script','res://tests/vs1_roundtrip.gd'],f'VS1_ROUNDTRIP_{stage.upper()}_OK')
    environment.pop('VS1_STAGE',None)
    renders=output/'vs1-renders'; renders.mkdir()
    old=environment.get('P1_CAPTURE_DIR')
    environment['P1_CAPTURE_DIR']=str(renders)
    try:
        phase('vs1-native-capture',render_command+[engine,'--path',str(project),'--rendering-driver','opengl3','--script','res://tests/vs1_capture.gd','--','--p1-capture'],'VS1_CAPTURE_OK')
    finally:
        if old is None: environment.pop('P1_CAPTURE_DIR',None)
        else: environment['P1_CAPTURE_DIR']=old
    evidence=verify(renders)
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
    manifest.update(schema=1,study='VS-1 revision 1',drawing_basis='985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f',export_files=files,
                    plan_sha256=toolchain.sha256_file(root/'examples/vs1/plan.json'),corpus_manifest_sha256=toolchain.sha256_file(root/'examples/vs1/manifest.json'),
                    matrix_sha256=toolchain.sha256_file(output/'vs1-renders/vs1-matrix.json'),
                    VS_M01='OPEN owner trial',VS_D01='OPEN owner decision',independent_review='OPEN',
                    windows_download_probe='Separate implementer evidence in PR; CI Linux export is not a native Windows launch')
    report=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'
    (output/'vs1-report.json').write_text(report,encoding='utf-8')
    player=output/'picross-vs1-windows-x86_64.zip'
    with zipfile.ZipFile(player,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in files: bundle.write(build/name,name)
        bundle.writestr('vs1-report.json',report)
        bundle.write(root/'docs/VS1_OWNER_TRIAL.md','README.txt')
        bundle.write(root/'examples/vs1/owner-protocol.json','owner-protocol.json')
        for path in (root/'prototypes/p1/art/book').glob('*-OFL.txt'): bundle.write(path,'licenses/'+path.name)
        bundle.write(root/'prototypes/p1/study/fonts/NOTICES.md','licenses/study-fonts-NOTICES.md')
    audit(player,files)
    review=output/'picross-vs1-review.zip'
    with zipfile.ZipFile(review,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
        for item in evidence['pictures']+evidence['diagnostics']: bundle.write(output/'vs1-renders'/item['file'],item['file'])
        bundle.write(output/'vs1-renders/vs1-matrix.json','vs1-matrix.json')
        bundle.writestr('vs1-report.json',report)
        for name in ('VS1_STUDY.md','VS1_VERIFICATION.md'): bundle.write(root/'docs'/name,name)
        for name in ('manifest.json','plan.json','production.json','owner-protocol.json'): bundle.write(root/'examples/vs1'/name,name)
        for path in (output/'logs').glob('vs1-*.log'): bundle.write(path,'logs/'+path.name)
        bundle.writestr('index.html',gallery(evidence))
    for p in (player,review): print(f'VS1 ARTIFACT {p} sha256:{toolchain.sha256_file(p)}',flush=True)


def audit(archive, files):
    import hashlib
    with zipfile.ZipFile(archive) as bundle:
        if len(bundle.namelist())!=len(set(bundle.namelist())): raise toolchain.PreflightError('VS1 duplicate archive entry')
        for name,digest in files.items():
            if hashlib.sha256(bundle.read(name)).hexdigest()!=digest: raise toolchain.PreflightError('VS1 ZIP executable differs')
        if any(n.endswith(('.pck','.gd','.tscn','.png')) or '..' in n for n in bundle.namelist()): raise toolchain.PreflightError('VS1 player contains review/source files')


def gallery(evidence):
    rows=''.join(f"<tr><td>{r['id']}</td><td>{r['client']} / {r['ui_scale']}</td><td>{r['mode']}</td><td>{r['cell_pitch']:.2f}</td><td>{r['font_px']}</td><td>{r['hidden_tokens']} / {r['clipped_glyphs']} / {r['glyph_collisions']}</td><td>{html.escape(r['status'])}</td></tr>" for r in evidence['records'])
    pictures=''.join(f"<figure><figcaption>{html.escape(p['file'])}</figcaption><a href='{p['file']}'><img loading='lazy' src='{p['file']}'></a></figure>" for p in evidence['pictures']+evidence['diagnostics'])
    return "<!doctype html><html lang='de'><meta charset='utf-8'><title>VS-1 Nachweise</title><style>body{font:16px system-ui;margin:24px;background:#faf6ec;color:#343f42}td,th{border:1px solid #ccc;padding:5px}img{max-width:100%}figure{margin:32px 0}</style><h1>VS-1 · technische Vergleichsprobe</h1><p>Native logische SubViewports, keine physische Display-/Komfortabnahme. PNG für 1:1-Prüfung öffnen. VS-M01 und VS-D01 offen. Diagnosebilder sind nicht zertifizierte Rätsel.</p><table><tr><th>Fall</th><th>Client / UI</th><th>Modus</th><th>Zellabstand</th><th>Schrift px</th><th>versteckt / abgeschnitten / Kollisionen</th><th>Status</th></tr>"+rows+'</table>'+pictures+'</html>'
