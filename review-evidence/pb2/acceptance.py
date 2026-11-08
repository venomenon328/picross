"""One-time P-B2 acceptance; remove after compact PR evidence is published."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(os.environ['PICROSS_SOURCE_ROOT']).resolve()
sys.path[:0] = [str(ROOT), str(ROOT / 'tests/puzzle_production')]
from tools.puzzle_production import palette_quality as pq, palette_gate as pg
from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import digest, load_json, write_json, InvalidInput
from tools.puzzle_production.images import file_hash
from tools.puzzle_production.target_adapter import inspect, export, verify_export, hashes
from tools.puzzle_production.za1_fixtures import seal, approve, isolated_checkout, rated_registration, rated_update

results = []
def emit(name, **data):
    item = {'scenario': name, **data}
    results.append(item)
    print(json.dumps(item, ensure_ascii=False), flush=True)

def history(path):
    return subprocess.check_output(['git', 'show', '1d5b7e90db4c8843d7737f83411f896ceeee6231:review-evidence/pa-v01/' + path], cwd=ROOT)

def references():
    original = json.loads(history('recalculated.json'))
    plan = json.loads(history('plan.json'))
    q_count = pairs = 0
    for reference, case in zip(original['cases'], plan['cases']):
        raw = history(case['file'])
        assert hashlib.sha256(raw).hexdigest() == case['sha256']
        value = json.loads(raw)
        palette = [{'id': f'c{p["id"]:02d}', 'rgb': p['color']} for p in value['palette']]
        matrix = [[f'c{v:02d}' if v else 'empty' for v in row] for row in value['solution']]
        identity = {'id': value['id'], 'revision': value['revision'], 'source_id': 'pa-v01',
                    'normalized_sha256': hashlib.sha256(raw).hexdigest()}
        report = pq.assess(matrix, palette, identity)
        pq.verify_assessment(report, matrix, palette, identity)
        for color in report['used']:
            assert color['q'] == reference['coordinates'][color['id']]
            q_count += 1
        for pair, expected in zip(report['pairs'], reference['pairs']):
            assert pair['ids'] == [expected['a'], expected['b']] and pair['S'] == expected['d2']
            assert pair['status'] == {'positive_warning': 'borderline'}.get(expected['status'], expected['status'])
            pairs += 1
        assert len(report['pairs']) == len(reference['pairs'])
        # Every supported invalidation cause, including usage and candidate revision.
        for change in ('matrix', 'palette', 'id', 'usage', 'revision', 'norm', 'report'):
            import copy
            m, p, i, r = map(copy.deepcopy, (matrix, palette, identity, report))
            if change == 'matrix': m.reverse()
            elif change == 'palette': p[0]['rgb'] = '#000000'
            elif change == 'id':
                old = p[0]['id']; p[0]['id'] = 'new-id'
                m = [['new-id' if x == old else x for x in row] for row in m]
            elif change == 'usage': m[0][0] = 'empty'
            elif change == 'revision': i['revision'] += 1
            elif change == 'norm': r['norm']['document_revision'] = 6
            else: r['pairs'][0]['S'] += 1
            try: pq.verify_assessment(r, m, p, i)
            except InvalidInput: pass
            else: raise AssertionError((reference['id'], change))
        emit(reference['id'], status=report['status'], pairs=report['pair_count'],
             negative=len(report['negative_pairs']), warning=len(report['warning_pairs']),
             original_file=case['file'], original_commit='1d5b7e90db4c8843d7737f83411f896ceeee6231')
    assert (q_count, pairs) == (27, 47)
    emit('references-total', coordinates=q_count, pairs=pairs, stale_mutations=56,
         visual_scope='Existing P-A original association only; no new visual acceptance or renderer change')

def get_inspection(p, approval=None, auth=None, exception=None):
    with open_package(p, allow_manual_review=auth is not None) as package:
        return inspect(package, approval, manual_authorization=auth, palette_exception=exception)

def upgrade(p, old, design):
    h = load_json(p / 'handoff.json')
    shutil.copyfile(ROOT / 'docs/ai-workflows/PUZZLE_AUTHORING.md', p / 'rulebook.md')
    h['rulebook'] = {'version':'0.6.0','file':'rulebook.md','sha256':file_hash(p / 'rulebook.md')}
    if design['mode'] == 'color':
        review = {'format':pg.VISUAL,'puzzle_id':h['puzzle_id'],'revision':h['revision'],
                  'matrix_hash':old['selection']['matrix_hash'],'logic_hash':old['selection']['logic_hash'],
                  'palette_sha256':digest([{'id':v['id'],'rgb':v['rgb'].lower()} for v in sorted(design['palette'],key=lambda p:p['id'])]),
                  'criteria': {k:{'result':'erfüllt','accepted':False,'actor':'TEST ONLY',
                    'timestamp_utc':'2026-11-08T00:00:00Z','statement':'Synthetic record, no actual sight approval',
                    'reason':'P-B2 one-time boundary exercise',
                    'evidence':[{'file':'evidence.txt','sha256':file_hash(p / 'evidence.txt')}]}
                    for k in pg.CRITERIA}}
        write_json(p / 'palette-review.json', review)
        h['palette_review'] = {'file':'palette-review.json','sha256':file_hash(p / 'palette-review.json')}
    seal(p,h)

def exception_if_needed(p, approval, auth, root):
    report = get_inspection(p,approval,auth)[0]
    g = report['palette_gate']
    if g['assessment']['status'] != 'negative': return None
    record = {'format':pg.EXCEPTION,'binding':g['binding'],'negative_pairs':g['assessment']['negative_pairs'],
              'actor':'TEST ONLY','timestamp_utc':'2026-11-08T00:00:00Z',
              'statement':'Synthetic boundary exception only, never an owner production statement',
              'reason':'One-time coexistence check','approval_sha256':file_hash(approval),'test_only':True}
    path = root / 'palette-exception.json'
    write_json(path,record)
    return path

def do_export(p, root, approval, auth=None, exception=None, name='export', revision=1):
    out = root / name
    export(p,out,name='TEST ONLY',revision=revision,stem='pb2_once',save_slot='pb2_once',approval_path=approval,
           manual_authorization=auth,palette_exception=exception,category_id='voegel',
           categories_path=ROOT/'tests/puzzle_production/fixtures/catalog/categories.json')
    m,r = verify_export(out)
    assert m['format'] == pg.EXPORT and r['technical'] and r['catalog_ready']
    return out, m, r

def manual_paths():
    from unittest.mock import patch
    from tools.puzzle_production import images
    from test_manual_adapter import ManualAdapterTests
    from test_edited_import_adapter import EditedImportAdapterTests
    from test_color_derivation_adapter import ColorDerivationTests
    from test_approved_color_adapter import ApprovedColorTests
    from test_stalled_color_adapter import StalledColorTests
    from test_accepted_raster_adapter import AcceptedRasterTests
    for cls in (ManualAdapterTests,EditedImportAdapterTests,ColorDerivationTests,ApprovedColorTests,StalledColorTests,AcceptedRasterTests):
        fixture = cls()
        try:
            original_import = images.import_image
            def near_import(source, design_path, output, *args, **kwargs):
                from PIL import Image
                design = load_json(design_path)
                if cls is ApprovedColorTests:
                    rgb_values = ['#447799', '#487b9d']
                    mapping = {tuple(bytes.fromhex(e['rgb'][1:])):tuple(bytes.fromhex(rgb[1:]))
                               for e,rgb in zip(design['palette'],rgb_values)}
                    with Image.open(source) as im:
                        im.load(); changed = im.copy()
                    for y in range(changed.height):
                        for x in range(changed.width):
                            value = changed.getpixel((x,y)); changed.putpixel((x,y),mapping.get(value,value))
                    changed.save(source)
                    for e,rgb in zip(design['palette'],rgb_values): e['rgb']=rgb
                    write_json(design_path,design)
                return original_import(source,design_path,output,*args,**kwargs)
            with patch('tools.puzzle_production.za1_fixtures.import_image',side_effect=near_import):
                fixture.setUp()
            if cls is StalledColorTests: fixture.prepare(paired=True)
            p = fixture.p if hasattr(fixture,'p') else fixture.package
            old,design,*_ = get_inspection(p,fixture.approval,fixture.auth)
            upgrade(p,old,design)
            fixture.authorize()
            before = hashes(p)
            exception = exception_if_needed(p,fixture.approval,fixture.auth,fixture.root)
            out,m,r = do_export(p,fixture.root,fixture.approval,fixture.auth,exception)
            assert before == hashes(p) and 'manual_authorization' in m
            emit(cls.__name__, passed=True, format=m['format'], manual=load_json(fixture.auth)['format'],
                 paired='deduction' in m, measurement=r['palette_gate']['assessment']['status'], exception=exception is not None)
        finally: fixture.doCleanups()

def paired_paths():
    from test_paired_production import package
    for color,repaired in ((False,False),(True,False),(False,True),(True,True)):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); p=root/'package'
            package(p,color,repaired)
            old,design,*_ = get_inspection(p)
            upgrade(p,old,design)
            approval=root/'approval.json'; approve(p,approval)
            exception=exception_if_needed(p,approval,None,root)
            out,m,r=do_export(p,root,approval,exception=exception)
            assert 'deduction' in m
            emit('paired', color=color, repaired=repaired, passed=True, profile=m['deduction']['profile']['id'])

def registration():
    from test_palette_gate import PaletteGateTests
    from tools.puzzle_production.content_registry import recover, check_checkout
    f=PaletteGateTests()
    try:
        f.setUp()
        p=f.package(colors=['#447799','#487b9d'])
        f.review(p); approval=f.approve(p); exception=f.exception(p,approval)
        out=f.export(p,approval,exception)
        root=f.root
        checkout=isolated_checkout(root/'checkout')
        before=hashes(checkout)
        original=load_json(out/'manifest.json')
        changed=dict(original); changed['palette_gate']=dict(original['palette_gate']); changed['palette_gate']['allowed']=True
        changed['palette_gate']['assessment']=dict(changed['palette_gate']['assessment']); changed['palette_gate']['assessment']['status']='positive'
        write_json(out/'manifest.json',changed)
        for apply in (False,True):
            try: rated_registration(out,checkout,apply=apply)
            except InvalidInput: pass
            else: raise AssertionError('forged v5 accepted')
            assert before == hashes(checkout)
        write_json(out/'manifest.json',original)
        assert rated_registration(out,checkout)['status']=='planned'
        assert before==hashes(checkout)
        try: rated_registration(out,checkout,apply=True,fail_step='crash-index')
        except InterruptedError: pass
        else: raise AssertionError('No crash injected')
        assert recover(checkout)['status']=='rolled-back'
        assert check_checkout(checkout,replay=True)['entries']==[]
        assert rated_registration(out,checkout,apply=True)['status']=='registered'
        assert rated_registration(out,checkout,apply=True)['status']=='no-op'
        check_checkout(checkout,replay=True)
        # Real update reader: same palette still negative, new revision requires new bindings.
        m=load_json(out/'manifest.json'); old_hash=m['files'][m['definition']]
        h=load_json(p/'handoff.json'); h['revision']='r02'
        review=load_json(p/'palette-review.json'); review['revision']='r02'; write_json(p/'palette-review.json',review)
        h['palette_review']['sha256']=file_hash(p/'palette-review.json'); seal(p,h)
        approve(p,approval); exception=f.exception(p,approval)
        new=f.export(p,approval,exception,output='update-export',revision=2)
        assert rated_update(new,checkout,old_hash)['status']=='planned-update'
        assert rated_update(new,checkout,old_hash,apply=True)['status']=='updated'
        check_checkout(checkout,replay=True)
        emit('v5-integration',forged_plan_register_blocked=True,read_only_plan=True,
             crash_recovery=True,registration=True,no_op=True,raster_update=True,guards='unchanged')
    finally: f.doCleanups()

start=time.monotonic()
emit('source',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
     status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip(),
     python=sys.version,platform=sys.platform)
selected = sys.argv[1:] or ['references','manual','paired','registration']
for name, function in [('references',references),('manual',manual_paths),('paired',paired_paths),('registration',registration)]:
    if name in selected: function()
emit('complete',seconds=round(time.monotonic()-start,3),all_passed=True)
write_json(Path(__file__).with_name('acceptance-result.json'),results)
