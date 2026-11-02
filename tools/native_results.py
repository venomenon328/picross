"""Fail-closed native evidence gate. Standard library only; verify delivered bytes."""
import hashlib
import gzip
import math
import struct
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

from native_contract import GROUPS, SCOPES, WORKER_CHECKS, CATALOG_MODES, artifacts, checks, coverage
from book_contract import SOURCES as BOOK_SOURCES, INTEGRATION_ASSERTIONS, HELP_ORIGINALS
INFO_ROUTES = [('work','settings'),('settings','work'),('work','help'),('help','work'),
          ('catalog','settings'),('settings','help'),('help','settings'),('settings','catalog'),
          ('catalog','help'),('help','catalog')]
INFO_CONFIGURATIONS = [(1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25),(1920,1200,1.0)]
INFO_HANDOFFS = {f'info-handoff-direct-{s}.png' for s in ('settings','help','work','catalog')}


def information_pose(endpoint):
    height = 13.4 if endpoint == 'catalog' else 6.075
    return [0 if endpoint == 'catalog' else -5 if endpoint == 'settings' else 5,
            0 if endpoint == 'catalog' else 6.48-height/2,height]


def information_close(a, b):
    return len(a) == len(b) and all(isinstance(x,(int,float)) and math.isfinite(x) and abs(x-y) < .0001 for x,y in zip(a,b))


def validate_n06(native, directory):
    data = native['n06']
    rows = data['depth_cases']
    labels = ['rest','landed','wide-gap','flat-sheet']
    if len(rows) != 4 or [r['case'] for r in rows] != labels:
        raise ValueError('N06 incomplete depth cases')
    for row in rows:
        accepted = row['case'] in ('rest','landed')
        if (row['accepted'] is not accepted or row['raised_shoulders'] is not (row['case'] != 'flat-sheet')
                or row['low_valley_flat_outer'] is not (row['case'] != 'wide-gap')
                or not 0 <= row['gap_pixels'] <= 40
                or (row['gap_pixels'] <= 3) is not (row['case'] != 'wide-gap')
                or row['file'] != 'fold-depth-'+row['case']+'.png'):
            raise ValueError('N06 failed depth/counterexample')
        header = (directory/row['file']).read_bytes()[:24]
        if header[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' or struct.unpack('>II',header[16:24]) != (640,128):
            raise ValueError('N06 missing original depth strip')
    counts = data['binding']
    if (data.get('focus_reparent') is not True
            or not .30 < data['joint_depth'] < .40 or not .005 < data['minimum_cover_clearance'] < .02
            or not 0 < counts['vertices'] <= 8511 or not 0 < counts['triangles'] <= 16262
            or not 0 < counts['surfaces'] <= 6):
        raise ValueError('N06 invalid binding depth/clearance/budget')


def validate_n05(native, directory):
    data = native['n05']
    routes = data['routes']
    if [(r['source'],r['target']) for r in routes] != INFO_ROUTES:
        raise ValueError('N05 missing, reordered or wrong information route')
    for r in routes:
        source, target = r['source'], r['target']
        pan = source in ('settings','help') and target in ('settings','help')
        entering = source in ('catalog','work')
        direction = 0 if pan else 1 if entering else -1
        seconds = .65 if pan else .85
        if (r['kind'] != ('pan' if pan else 'enter' if entering else 'return')
                or r['direction'] != direction or r['seconds'] != seconds or r['wall_seconds'] < seconds
                or r['leaves'] != (0 if pan else 1) or not information_close(r['start'],information_pose(source)) or not information_close(r['end'],information_pose(target))
                or r['state_unchanged'] is not True or r['return_context_unchanged'] is not True
                or r['view_before'] != r['view_after']
                or r['id'] != 'T-06' or r['origin']['id'] != r['id'] or not r['samples']):
            raise ValueError('N05 wrong leaf, camera, duration, ID or work state')
        previous = -1
        for elapsed, camera, turn in r['samples']:
            t = elapsed/seconds
            s = t*t*(3-2*t)
            expected = [a+(b-a)*s for a,b in zip(information_pose(source),information_pose(target))]
            if not 0 <= elapsed <= seconds or elapsed < previous or not information_close(camera,expected) or abs(turn-(1 if pan else s)) > .0001:
                raise ValueError('N05 camera/leaf trace deviates from bound choreography')
            previous = elapsed
        origin = 'work' if (source,target) in INFO_ROUTES[:4] else 'catalog'
        if r['origin']['kind'] != origin:
            raise ValueError('N05 visit origin overwritten by current information page')
        if origin == 'catalog':
            c = r['origin']['catalog']
            if (c['scroll'],c['right_scroll'],c['selection'],c['criterion'],c['direction'],c['page']) != (91,173,'T-08','size','desc',0):
                raise ValueError('N05 lost/mirrored catalog origin')
            if target == 'catalog' and r['catalog_after'] != c:
                raise ValueError('N05 catalog return differs from immutable origin')
    layouts = data['layouts']
    if (len(layouts) != 8 or {(r['section'],r['width'],r['height'],r['scale']) for r in layouts}
            != {(s,w,h,u) for s in ('settings','help') for w,h,u in INFO_CONFIGURATIONS}):
        raise ValueError('N05 missing native layout')
    for r in layouts:
        w,h = r['width'],r['height']
        factor = h/max(6.075,10.8*h/w)
        x,y,rw,rh = r['hull']
        left = w/2-5*factor+(.75*factor if r['section'] == 'help' else 0)
        right = w/2+5*factor-(.75*factor if r['section'] == 'settings' else 0)
        top, bottom = .28*factor, (12.4+.28)*factor
        margin = min(x-left,right-x-rw,y-top,bottom-y-rh)
        cx,cy,cw,ch = r['clip']
        with (directory/r['file']).open('rb') as stream: header = stream.read(24)
        if (len(header) != 24 or header[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
                or struct.unpack('>II',header[16:24]) != (w,h)
                or min(rw,rh,cw,ch) <= 0 or margin < 8 or abs(margin-r['margin']) > .002
                or min(cx-left,right-cx-cw,cy-top,h-cy-ch) < 8
                or r['scroll'] != r['limit'] or r['limit'] < 0):
            raise ValueError('N05 native ink/clip leaves independently projected safe paper or help end')
    expected = {(k,p,r) for k in ('enter','pan','return') for p in ('prepare','motion') for r in ('resize','ui-scale','focus','leave')}
    if len(data['logic']) != 24 or {(r['kind'],r['phase'],r['reason']) for r in data['logic']} != expected:
        raise ValueError('N05 incomplete interruption decision table')
    for r in data['logic']+data['interruptions']:
        expected_endpoint = 'work' if r['kind'] == 'return' or (r['kind'] == 'enter' and r['reason'] == 'leave') else 'settings' if r['kind'] == 'pan' and r['reason'] == 'leave' else 'help'
        if r['endpoint'] != expected_endpoint:
            raise ValueError('N05 wrong interruption endpoint')
    interruptions = data['interruptions']
    if (len(interruptions) != 6 or {(r['kind'],r['phase']) for r in interruptions} != {(k,p) for k in ('enter','pan','return') for p in ('prepare','motion')}
            or any(r['held_blocked'] is not True or r['released'] is not True or r['textures'] != 0 for r in interruptions)):
        raise ValueError('N05 incomplete native interruption/input/resource proof')
    if data['settings'] != dict(mode='V',mark=False,animations=False,ui=1.0):
        raise ValueError('N05 deliberate settings not exercised')
    required = {'N05 old tab removed including signal and focus','N05 work navigation order catalog settings help',
                'N05 begun work has undo and redo history','N05 explicit clue reset remains effective',
                'N05 catalog help settings returns original context without saves',
                'N05 catalog placeholder never creates save obligation','N05 actual UI toggle 1.25','N05 actual UI toggle 1.0',
                'N05 actual controls change settings','N05 explicit settings survive work return',
                'N05 failed mandatory flush blocks preparation','N05 stable completion origin','N05 completion return never replays success'}
    if not required <= {r['label'] for r in native['assertions'] if r['passed'] is True}:
        raise ValueError('N05 missing control/state assertions')



def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: '+key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def safe(root, name):
    p = PurePosixPath(name)
    if (not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name
            or p.as_posix() != name or (root/name).is_symlink()
            or not (root/name).resolve().is_relative_to(root.resolve())):
        raise ValueError('Unsafe native evidence path')
    return root/name


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_files(root, exclude=(), only=None):
    return [dict(file=p.relative_to(root).as_posix(), bytes=p.stat().st_size, sha256=digest(p))
            for p in sorted(root.rglob('*')) if p.is_file() and p.relative_to(root).as_posix() not in exclude
            and (only is None or p.relative_to(root).as_posix() in only)]


def verify_file(root, row):
    path = safe(root, row['file'])
    if (not path.is_file() or type(row['bytes']) is not int or row['bytes'] <= 0
            or path.stat().st_size != row['bytes'] or digest(path) != row['sha256']):
        raise ValueError('Missing/empty/changed native evidence: '+row['file'])


def check_phases(report, expected, directory):
    rows = report['checks']
    if sorted(r['name'] for r in rows) != sorted(expected):
        raise ValueError('Missing/duplicate/unexpected native checks')
    for row in rows:
        if (row['status'] != 'success' or row.get('timed_out') or
                not isinstance(row.get('seconds'), (float, int)) or row['seconds'] < 0):
            raise ValueError('Unsuccessful/incomplete native phase')
        negative = row['name'] in ('expected-failure', 'rp6-t04-foreign-slot-control')
        expected_exit = 23 if row['name'] == 'expected-failure' else 4 if negative else 0
        if row.get('exit_code') != expected_exit or bool(row.get('expected_failure')) != negative:
            raise ValueError('Incorrect native process outcome')
        python_checks = {'current-resource-hashes', 'verified-toolchain-assets', 'current-atlas-resources', 'kat2-adapter-export',
                         'kat2-adapter-register', 'kat2-imported-base-copies', 'kat2-image-processing', 'ea-image-processing', 'za1-test-only-registration',
                         'current-vs2-complete', 'retained-hc92-font-samples', 'current-drawing-pixel-oracles', 'regular-book-integration'}
        if ('log' in row) != (row['name'] not in python_checks):
            raise ValueError('Missing/unexpected native process log')
        if 'log' in row:
            log = row['log']
            verify_file(directory/'logs', dict(file=log['file'], bytes=log['retained_bytes'], sha256=log['sha256']))
            if log['abbreviated'] or log['original_bytes'] != log['retained_bytes']:
                raise ValueError('Truncated native phase log')
            if row.get('required_marker') and row['required_marker'] not in (directory/'logs'/log['file']).read_text(encoding='utf-8'):
                raise ValueError('Missing native success marker')


def validate_book_study(report, directory, identity, host):
    """Require shared presentation originals and the real B-B product lifecycle."""
    study = read(directory/'report.json')
    native = read(directory/'native.json')
    assertions = native.get('assertions', [])
    required_assertions = {'three independently moving leaves', 'actual catalog pointer selects correct ID',
                           'motion and blocked pointer input preserve cells/history/redo', 'presentation creates no save action',
                           'correct ID from page half 0', 'correct ID from page half 12',
                           'empty filter is immediate and reachable', 'sort is global and immediate',
                           'empty filter retains settings and quit',
                           'normal registry and definition validators accept all 27 instances',
                           'foreign fixture binding rejected definition_id', 'duplicate fixture binding rejected reveal',
                           'copied ID on second spread has its earned reveal', 'earned copied reveal returns to second spread',
                           'explicit catalog tab starts return', 'return starts with actual edited content',
                           'return retains exact catalog context', 'return does not mutate history or add saves',
                           'return catalog shows current edited progress', 'return cancellation never commits held gesture',
                           'idle Escape is not catalog navigation', 'stable ending accepts animated return',
                           'same logical page retains exact paper after return', 'different logical pages have different organic paper',
                           'control states retain non-color ink distinctions', 'popup remains opaque in study',
                           'fresh actual pointer gesture works after interruption',
                           'solved puzzle opens directly without replay', 'ending reset opens same empty page without book animation'}
    for target in (0, 1):
        required_assertions.update(f'{label} {target}' for label in ('pointer starts catalog turn', 'filter and sort discarded during turn',
                                  'short catalog motion settles target', 'partial last spread', 'global ordering precedes pagination', 'edge action has no animation'))
    expected_interruptions = {(kind, phase, reason) for kind in ('page', 'open', 'return') for phase in ('prepare', 'motion')
                              for reason in ('resize', 'ui-scale', 'focus', 'leave')}
    for kind, phase, reason in expected_interruptions:
        required_assertions.update(f'{label} {kind}/{phase}/{reason}' for label in
                                   ('matrix stable target', 'matrix no history or save', 'matrix releases resources'))
    required_assertions.update({'native tooltip delay is not bypassed',
                                'negative empty tooltip reproduced by native hover',
                                'negative detached hover stroke rejected'})
    f01_gestures = ('left','right','outside','clue','chord','escape','lost-release','resize')
    required_assertions.update('F01 '+label for label in (
        'regular BookButton default', 'deferred popup teardown', 'popup released after dispatch',
        'lost release cancels without commit', 'outside releases never click another control',
        'exact undo redo', 'negative synchronous popup hide rejected'))
    for kind in f01_gestures:
        required_assertions.update('F01 '+label+' '+kind for label in ('starts','gesture','crosshair returns'))
    configurations = {(1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25),(1920,1200,1.0)}
    if (report.get('book_study') != study or study['package'] != 'B-B-T01'
            or study['host'] != host or any(study.get(k) != v for k,v in identity.items())
            or native['checks'] != len(assertions) or native['failures'] != []
            or not all(a.get('passed') is True for a in assertions)
            or not required_assertions <= {a.get('label') for a in assertions}
            or {(r['kind'], r['phase'], r['reason']) for r in native['interruptions']} != expected_interruptions
            or len(native['interruptions']) != 24 or len(native['catalog_layouts']) != 3
            or {(r['view'],r['width'],r['height'],r['scale']) for r in native['ink_margins']} != {(v,w,h,s) for v in ('catalog','work') for w,h,s in configurations}
            or any(sum((r['view'],r['width'],r['height'],r['scale']) == (v,w,h,s) for r in native['ink_margins']) != n for v,n in (('catalog',13),('work',4)) for w,h,s in configurations)
            or any(r['margin'] < 8 or min(r['hull'][2:]) <= 0 for r in native['ink_margins'])
            or len(native['returns']) != 1 or native['returns'][0]['seconds'] != 1.8 or native['returns'][0]['page'] != 1
            or any(len(r['cards']) != 24 for r in native['catalog_layouts'])
            or [(r['target'],r['direction'],r['seconds']) for r in native['page_motions']] != [(1,1,.85),(0,-1,.85)]
            or len(native['layouts']) != 3 or len(native['handoffs']) != 9
            or native['motion_wall_seconds_quiet'] < 3.0 or not native['motion_frame_ms_quiet']
            or native['resources']['ui_capture_targets'] != 0 or native['resources']['catalog_rgba_textures'] != 0
            or native['resources']['visible_leaves'] != 0 or native['resources']['moving_leaves'] != 3
            or native['resources']['information_snapshots'] != 0 or native['resources']['information_visit'] is not False
            or study['organic_paper']['sha256'] != '1af9f61957619d7cea98b69021688b0b78997d84baf93698c9f02dcbb866362f'
            or study['organic_paper']['size'] != [1254,1254] or study['organic_paper']['imported_texture']['bytes'] <= 0
            or study['leather']['sha256'] != '58372a4329973e3ad308fde17ab5bc77148d7f724e55671e540bb5344f8e0f41'
            or study['leather']['size'] != [1254,1254] or study['leather']['imported_texture']['bytes'] <= 0
            or study['table']['sha256'] != '5b02fe08710efb47df7b23307f460035aebaa3fa411e846b4a06558cc79678da'
            or study['table']['size'] != [1536,1024] or study['table']['imported_texture']['bytes'] <= 0
            or study['material_source']['sha256'] != '957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a'):
        raise ValueError('Incomplete/wrong isolated book study assertions or binding')
    tooltip_cases = native['tooltip_cases']
    f01 = native.get('f01', [])
    f01_cases = {'default-idle','negative-consumed-release','release-recovered',*f01_gestures}
    if (len(f01) != len(f01_cases)+1 or {r['case'] for r in f01} != f01_cases | {'negative-synchronous-hide'}
            or any(r.get('passed') is not True for r in f01)
            or any(r.get('visible') is not (r['case'] != 'negative-consumed-release')
                   for r in f01 if r['case'] in f01_cases)):
        raise ValueError('F01 native tooltip/release regression or counterexample missing/failed')
    captions = {'direction','reset','mode','click-before','caption-after-click','fill','help','wrapped-edge'}
    empty = {'footer-0','footer-1','footer-2','whitespace'}
    for width, height, scale in ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25)):
        cases = captions | empty | ({'mode-empty','mode-whitespace'} if width == 1920 else set())
        rows = [r for r in tooltip_cases if r.get('width') == width and r['case'] in cases]
        if len(rows) != len(cases) or {r['case'] for r in rows} != cases:
            raise ValueError('Missing/duplicate delayed tooltip scenario')
        for row in rows:
            if row['height'] != height or row['scale'] != scale or row['wait_seconds'] < .65 or row.get('hovered') is not True or row['visible'] != (row['case'] in captions):
                raise ValueError('Bypassed delay/incorrect tooltip visibility')
            if row['visible']:
                x,y,w,h = row['popup']
                if (not row['caption'].strip() or row['caption'] != row['text']
                        or min(x,y) < 0 or min(w,h) <= 0 or x+w > width or y+h > height
                        or min(row['label']) <= 0 or row['label'][0] > w or row['label'][1] > h):
                    raise ValueError('Empty/stale/clipped tooltip content')
            elif row['caption']:
                raise ValueError('Unexpected redundant footer tooltip')
    dismissals = {f'dismiss-{kind}-{w}' for w in (1280,1920,2560) for kind in ('switch','leave','click')}
    dismissals |= {'dismiss-'+kind for kind in ('resize','ui-scale','focus','motion-start','motion-end-no-revival')}
    rows = [r for r in tooltip_cases if r['case'].startswith('dismiss-')]
    negatives = [r for r in tooltip_cases if r['case'] == 'negative-controls']
    if ({r['case'] for r in rows} != dismissals or len(rows) != len(dismissals) or any(r['visible'] for r in rows)
            or len(negatives) != 1 or negatives[0]['empty_popup'] is not True
            or negatives[0]['current_detached_pixels'] != 0 or negatives[0]['legacy_detached_pixels'] < 8):
        raise ValueError('Tooltip lifetime or native counterexample failed')
    details = study['edge_details']
    expected_edges = {f'edge-{kind}-{suffix}.png' for suffix in ('1280','1920','2560','1920x1200')
                      for kind in ('bottom-left','bottom-right','bottom-fold','top-fold','outer-left','outer-right')}
    if ({r['file'] for r in details} != expected_edges or len(details) != 24
            or any(r['scale'] != 1 or len(r['rect']) != 4 or r['rect'][2] <= r['rect'][0] or r['rect'][3] <= r['rect'][1] for r in details)):
        raise ValueError('Incomplete/unscaled native edge detail evidence')
    movie = read(directory/'movie.json')
    if (movie['fps'] != 30 or movie['failures'] != [] or movie['final_state'] != 'CATALOG' or movie['final_id'] != 'T-06' or movie['edited_cursor'] != 2
            or [(e['kind'], e['direction'], e['seconds']) for e in movie['events'] if e['kind'] != 'information'] != [('page',1,.85),('page',-1,.85),('open',1,3.0),('return',-1,1.8)]
            or any(e['last_frame'] <= e['first_frame'] for e in movie['events'])):
        raise ValueError('Incomplete/incorrect book motion evidence')
    info_movie = [e for e in movie['events'] if e['kind'] == 'information']
    if ([(e['source'],e['target']) for e in info_movie] != [('work','settings'),('settings','help'),('help','work'),('work','help'),('help','settings'),('settings','work'),('catalog','settings'),('settings','catalog'),('catalog','help'),('help','catalog')]
            or any((e['direction'],e['seconds']) != ((0,.65) if e['source'] in ('settings','help') and e['target'] in ('settings','help') else (1,.85) if e['target'] in ('settings','help') else (-1,.85)) for e in info_movie)):
        raise ValueError('Missing/incorrect information film choreography')
    expected = ['book-version', 'book-import', 'book-integration', 'book-native', 'book-movie']
    integration = read(directory/'integration/integration.json')
    source_root = Path(__file__).resolve().parents[1]
    if (integration.get('passed') is not True or not integration.get('assertions')
            or any(row.get('passed') is not True for row in integration['assertions'])
            or not INTEGRATION_ASSERTIONS <= {row.get('label') for row in integration['assertions']}
            or any(study.get('sources', {}).get(name) != hashlib.sha256((source_root/name).read_bytes()).hexdigest() for name in BOOK_SOURCES)
            or study.get('scope') != 'shared-presentation-and-product-lifecycle'
            or [p['name'] for p in study['phases']] != expected
            or any(p['exit_code'] != 0 or p['timed_out'] or p['seconds'] < 0 for p in study['phases'])):
        raise ValueError('Incomplete/failed shared book or product lifecycle phases')
    names = set(study['files'])
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()} - {'report.json'}
    required = {'opening.avi', 'movie.json', 'movie-final.png', 'native.json', 'catalog.png', 'opening-middle.png', 'opening-back.png',
                'return-middle.png', 'return-edited-work.png', 'paper-page-one.png', 'paper-page-two.png', 'paper-page-two-return.png',
                'return-handoff-texture.png','return-handoff-direct.png','control-states.png',
                'page-forward.png', 'page-backward.png', 'material-original-detail.png', 'material-study-detail.png',
                'integration/integration.json'}
    required.update(HELP_ORIGINALS)
    required.update('logs/'+name+'.log' for name in expected)
    required.update(f'{kind}-{width}.png' for kind in ('baseline', 'handoff-texture', 'work', 'catalog') for width in (1280,1920,2560))
    required.update(expected_edges)
    required.update(f'tooltip-{kind}-{w}.png' for w in (1280,1920,2560) for kind in captions | empty if kind != 'click-before')
    required.update({'tooltip-negative-empty.png','hover-negative.png','hover-current.png','tooltip-after-motion-1920.png'})
    required.update({'tooltip-mode-empty-1920.png','tooltip-mode-whitespace-1920.png'})
    required.update({'catalog-1920x1200.png','work-1920x1200.png','return-handoff-texture-1920x1200.png','return-handoff-direct-1920x1200.png'})
    required.update(INFO_HANDOFFS | {n.replace('direct','texture') for n in INFO_HANDOFFS})
    required.update({'info-pan-help-middle.png','info-pan-settings-middle.png'})
    required.update(r['file'] for r in native['n05']['layouts'])
    if names != actual or not required <= names:
        raise ValueError('Missing/unexpected book study evidence inventory')
    for name, metadata in study['files'].items():
        verify_file(directory, dict(file=name, **metadata))
    pixels = study['handoff_pixels']
    if (set(pixels['samples']) != {f'work-{w}.png' for w in (1280,1920,2560)} | {'return-handoff-direct.png','return-handoff-direct-1920x1200.png'} | INFO_HANDOFFS
            or any(s['max_channel_delta'] > 4 or max(s['mean_channel_delta']) > .1 for s in pixels['samples'].values())
            or pixels['negative_controls'] != 'one-pixel displacement and alpha mutation rejected'):
        raise ValueError('Failed/incomplete book study handoff pixels or counterexamples')
    validate_book_n04(native, directory, details, configurations)
    validate_n05(native, directory)
    validate_n06(native, directory)


def validate_book_n04(native, directory, details, configurations):
    """Independent N14-N17 scenario, projection, viewport and scroll guards."""
    import struct
    def frame_size(path):
        with path.open('rb') as stream: header = stream.read(24)
        if len(header) != 24 or header[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
            raise ValueError('Invalid native PNG header')
        return struct.unpack('>II',header[16:24])
    rows = native['n04']
    expected_counts = [(0,0,0,0),(1,0,1,0),(12,0,12,0),(13,0,12,1),(24,0,12,12),(27,0,12,12),(27,1,3,0)]
    ids = ['T-01','T-06','T-08'] + [f'T-{i:02d}' for i in range(13,37)]
    if ([(r['count'],r['page'],r['left'],r['right']) for r in rows['counts']] != expected_counts
            or any(r['ids'] != ids[r['page']*24:min(r['count'],(r['page']+1)*24)] for r in rows['counts'])):
        raise ValueError('Wrong left-first membership or global ID order')
    scroll = rows['scroll']
    expected = {'wheel-left','wheel-right','bar-left','bar-right','ensure-right','right-edge',
                'return-left','return-right','no-op','empty-right','reset-filter','reset-sort','reset-reverse','resize-clamp'}
    if {r['case'] for r in scroll} != expected or len(scroll) != len(expected):
        raise ValueError('Missing independent scroll scenario')
    for row in scroll:
        case, after = row['case'], row['after']
        if case.startswith('reset-'):
            ok = after == [0,0]
        elif case == 'resize-clamp':
            ok = after[0] == row['before'][0] == 91 and after[1] == row['right_limit'] and 0 < after[1] < row['before'][1]
        elif case in {'wheel-left','bar-left','wheel-right','bar-right','ensure-right'}:
            side = 0 if case.endswith('-left') else 1
            ok = after[side] > row['before'][side] and after[1-side] == row['before'][1-side]
        else:
            ok = after == row['before']
            if case in {'return-left','return-right','no-op'}: ok = ok and min(after) > 0 and after[0] != after[1]
            if case == 'empty-right': ok = ok and after == [80,0]
        if not ok: raise ValueError('Mirrored/lost scroll context: '+case)
    for row in native['interruptions']:
        if row['source_offsets'] != [40,120]: raise ValueError('Unbound two-offset interruption source')
        if not (row['kind'] == 'open' and row['reason'] != 'leave'):
            expected = [0,0] if row['kind'] == 'page' and row['reason'] != 'leave' else [40,120]
            if row['final_offsets'] != expected: raise ValueError('Wrong abort/settle scroll pair')
    boundaries = rows['boundaries']
    if ({(r['width'],r['height'],r['scale']) for r in boundaries} != {(1920,1200,1.25),(1920,1192,1.0),(1920,1208,1.0),(1920,1088,1.0)}
            or len(boundaries) != 4 or any(r['margin'] < 8 or r['offsets'] != [91,173] for r in boundaries)):
        raise ValueError('Missing/unsafe aspect or UI boundary')
    if len(rows['clips']) != 2 or {r['side'] for r in rows['clips']} != {-1,1}:
        raise ValueError('Missing half-page clipping geometry')
    factor = 1920/22
    for row in rows['clips']:
        x,y,w,h = row['rect']
        left = 960 + (-10 if row['side'] == -1 else .75)*factor
        right = 960 + (-.75 if row['side'] == -1 else 10)*factor
        top = (1200-12.4*factor)/2
        if min(x-left,right-x-w,y-top,1200-top-y-h) < 8:
            raise ValueError('Card clipping leaves quiet flat paper')
    for row in native['ink_margins']:
        w,h = row['width'],row['height']
        work = row['view'] == 'work'
        world_h = max(6.075,10.8*h/w) if work else max(13.4,22*h/w)
        factor = h/world_h
        x,y,rw,rh = row['hull']
        side = 1 if work or x+rw/2 > w/2 else -1
        paper = [w/2+(0 if side == 1 else -10)*factor-(5*factor if work else 0),
                 .28*factor if work else (h-12.4*factor)/2,10*factor,12.4*factor]
        safe = [paper[0]+(.75*factor if side == 1 else 0),paper[1],paper[2]-.75*factor,paper[3]]
        margin = min(x-safe[0],safe[0]+safe[2]-x-rw,y-safe[1],safe[1]+safe[3]-y-rh)
        if (any(abs(a-b) > .002 for a,b in zip(paper,row['paper'],strict=True))
                or any(abs(a-b) > .002 for a,b in zip(safe,row['flat_safe'],strict=True))
                or margin < 8 or abs(margin-row['margin']) > .002):
            raise ValueError('Ink outside independently projected quiet paper')
    for w,h,_ in configurations:
        suffix = '1920x1200' if (w,h) == (1920,1200) else str(w)
        for kind in ('catalog','work'):
            if frame_size(directory/f'{kind}-{suffix}.png') != (w,h):
                raise ValueError('Wrong actual native framebuffer size')
    for row in details:
        x0,y0,x1,y1 = row['rect']
        if (frame_size(directory/row['source']) != (row['width'],row['height'])
                or frame_size(directory/row['file']) != (x1-x0,y1-y0)
                or min(x0,y0) < 0 or x1 > row['width'] or y1 > row['height']):
            raise ValueError('Wrong original framebuffer/crop dimensions')


def validate_catalog_images(costs, summary, required, direct_images):
    """Separate Python crops from unchanged images already emitted by KE natively."""
    expected_crops = [dict(file=Path(capture['file']).stem+'-'+name+'.png',
                           source=capture['file'], region=rectangle)
                      for report in summary['reports'] for capture in report['captures']
                      for name,rectangle in capture['regions'].items()]
    if (costs['status'] != 'success' or summary['image_costs'] != costs
            or costs['input_frames'] != sum(len(r['captures']) for r in summary['reports'])
            or costs['crops'] != len(expected_crops) or costs['entries'] != summary['crops']
            or [{k:r[k] for k in ('file','source','region')} for r in costs['entries']] != expected_crops
            or {'kat2/'+r['file'] for r in costs['entries']} | set(direct_images)
               != {p for p in required if p.endswith('.png')}):
        raise ValueError('Incomplete native image costs/crops')


def validate_payload(result, root, player_root=None):
    groups = result['groups']
    if (result.get('format') != 'picross-native-result-v1' or result['status'] != 'success'
            or groups != [g for g in GROUPS if g in groups] or not groups
            or result['expected'] != coverage(groups)):
        raise ValueError('Invalid native selection/result')
    rows = result['results']
    if [r['group'] for r in rows] != groups or any(r['status'] != 'success' or r['exit_code'] != 0 for r in rows):
        raise ValueError('Missing/duplicate/failed native groups')
    inventory = result['files']
    names = [r['file'] for r in inventory]
    actual = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() != 'native-result.json')
    if sorted(names) != actual or len(names) != len(set(names)):
        raise ValueError('Incomplete/duplicate/unexpected native delivered inventory')
    for row in inventory:
        verify_file(root, row)
    isolation_roots = set()
    for group in groups:
        directory = root/group
        report = read(directory/'product-report.json')
        if report['status'] != 'success' or report['native_group'] != group or report['host'] != result['host']:
            raise ValueError('Wrong native group report')
        isolation = report['isolation']
        workspace = isolation['workspace'].replace('\\', '/')
        if not workspace or workspace in isolation_roots:
            raise ValueError('Shared native group workspace/profile')
        isolation_roots.add(workspace)
        profiles = isolation['profiles']
        expected_profiles = {'APPDATA','LOCALAPPDATA'} if result['host'] == 'Windows' else {'XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME'}
        if set(profiles) != expected_profiles or any(not str(v).replace('\\','/').startswith(workspace+'/')
                                                   for v in [isolation['project'],*profiles.values()]):
            raise ValueError('Native project/profile escapes its isolated workspace')
        for key, value in result['identity'].items():
            if report.get(key) != value:
                raise ValueError('Native original report binding mismatch: '+key)
        enabled = set(SCOPES[group])
        if set(report['scope']) != {s for v in SCOPES.values() for s in v}:
            raise ValueError('Incomplete native scope declaration')
        for name, scope in report['scope'].items():
            if scope['enabled'] != (name in enabled) or scope['status'] != ('success' if name in enabled else 'not_applicable'):
                raise ValueError('Unselected/skipped scope misreported')
        check_phases(report, checks(group, result['host']), directory)
        if group == 'export':
            validate_book_study(report, directory/'book-study', result['identity'], result['host'])
        if group == 'graphics':
            worker = read(directory/'vs2-worker/technical/product-report.json')
            if worker['status'] != 'success' or any(worker.get(k) != v for k,v in result['identity'].items()):
                raise ValueError('Incomplete/wrong graphics worker')
            check_phases(worker, WORKER_CHECKS, directory/'vs2-worker/technical')
        required = set(artifacts(group))
        if group == 'completion':
            native = read(directory/'selected/ea/native.json')
            sequence = native['sequence']
            if len(sequence) < 10:
                raise ValueError('Incomplete actual EA motion sequence')
            indices = {min(range(len(sequence)), key=lambda i:abs(sequence[i]['seconds']-t)) for t in (0,.5,1.1,1.65,2.15)}
            required.update('ea/'+sequence[i]['file'] for i in indices)
        selected = report['selected_evidence']['files']
        if sorted(r['file'] for r in selected) != sorted(required) or report['selected_evidence']['omitted']:
            raise ValueError('Missing/duplicate/unexpected mandatory files for '+group)
        for row in selected:
            verify_file(directory/'selected', row)
        contracts = read(Path(__file__).with_name('native_artifacts.json'))['report_contracts']
        for name in required & contracts.keys():
            path = directory/'selected'/name
            data = json.loads(gzip.decompress(path.read_bytes()), object_pairs_hook=unique) if name.endswith('.gz') else read(path)
            for field, rule in contracts[name].items():
                if field not in data:
                    raise ValueError('Missing original native assertion field: '+name+'/'+field)
                value = data[field]
                accepted = (value == rule['equals'] if isinstance(rule,dict) else
                            type(value) is int and value > 0 if rule == 'positive-int' else
                            type(value) is int and value == 0 if rule == 'zero-int' else
                            value == [] if rule == 'empty-list' else value is False)
                if not accepted:
                    raise ValueError('Failed original native assertions: '+name+'/'+field)
        if group == 'history':
            summary = read(directory/'selected/integration/summary.json')
            from p14_integration import verify_evidence
            try:
                actual = verify_evidence(directory/'selected/integration')
                if report.get('integration') != summary or summary != actual:
                    raise AssertionError('summary disagrees with complete native evidence')
            except (AssertionError, KeyError, TypeError) as error:
                raise ValueError('Incomplete/inconsistent bounded native history evidence: '+str(error)) from error
        if group == 'catalog':
            reuse = read(directory/'selected/kat2/import-copies.json')
            copies = reuse['copies']
            if (reuse.get('base_unchanged') is not True or len(copies) != len(CATALOG_MODES)
                    or not re.fullmatch('[0-9a-f]{64}', reuse['base_sha256'])
                    or len({r['project'] for r in copies}) != len(CATALOG_MODES)
                    or any(r['base_sha256'] != reuse['base_sha256'] or r['files'] != reuse['base_files']
                           or r['bytes'] != reuse['base_bytes'] or r['seconds'] < 0
                           or not r['project'].replace('\\','/').startswith(workspace+'/kat2-') for r in copies)):
                raise ValueError('Incomplete/changed/shared catalog imported base copies')
            costs = read(directory/'selected/kat2/image-costs.json')
            summary = read(directory/'selected/kat2/summary.json')
            validate_catalog_images(costs, summary, required,
                                    read(Path(__file__).with_name('native_artifacts.json'))['catalog_direct_images'])
            if costs['comparison'] and any(r.get('identical') is not True for r in costs['entries']):
                raise ValueError('Native PNG comparison failed')
            for entry in costs['entries']:
                if (not re.fullmatch('[0-9a-f]{64}', entry['source_sha256']) or
                        len(entry['source_size']) != 2 or len(entry['region']) != 4):
                    raise ValueError('Missing native input frame/region binding')
                if costs['comparison'] and (entry['reference'] != entry['actual'] or
                        entry['actual']['size'] != [entry['region'][2]-entry['region'][0],entry['region'][3]-entry['region'][1]]):
                    raise ValueError('Native comparison dimensions/RGBA disagree')
            if summary['reports'] != [read(directory/'selected/kat2'/(mode+'.json')) for mode in
                                      CATALOG_MODES]:
                raise ValueError('Catalog original reports disagree with summary')
            if report['kat2'] != summary:
                raise ValueError('Catalog group/summary mismatch')
            from at_evidence import native
            native(directory/'selected/kat2', read(directory/'selected/kat2/at.json'), ('small','hover'))
        if group == 'completion':
            costs = read(directory/'selected/ea/image-costs.json')
            if report['ea']['image_costs'] != costs or costs['input_frames'] != len(sequence):
                raise ValueError('EA image timing/sequence mismatch')
            if report['ea']['reports'] != [read(directory/'selected/ea'/(mode+'.json')) for mode in ('native','restart')]:
                raise ValueError('EA group/original mismatch')
            from at_evidence import native
            native(directory/'selected/ea', read(directory/'selected/ea/native.json'), ('final','reopen','blend'))
    if 'export' in groups:
        if player_root is None:
            raise ValueError('Selected export requires delivered player bytes')
        verify_file(player_root, result['player'])
        with zipfile.ZipFile(player_root/result['player']['file']) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate player member')
            export = read(root/'export/product-report.json')
            if set(export['export_files']) != {'picross-p1.exe','picross-p1.console.exe','picross-p1.pck'}:
                raise ValueError('Incomplete export file contract')
            for name, expected in export['export_files'].items():
                if not archive.read(name) or hashlib.sha256(archive.read(name)).hexdigest() != expected:
                    raise ValueError('Wrong delivered Windows export')
            if json.loads(archive.read('product-report.json'), object_pairs_hook=unique) != export:
                raise ValueError('Player source/report differs from actual export report')
        audit = read(root/'export/player-audit.json')
        if (audit['sha256'] != result['player']['sha256'] or audit['bytes'] != result['player']['bytes']
                or audit['files'] != names
                or export['content_pack']['pack_sha256'] != export['export_files']['picross-p1.pck']
                or export['content_pack']['executable_sha256'] != export['export_files']['picross-p1.exe']):
            raise ValueError('Player packaging audit mismatch')
    elif 'player' in result:
        raise ValueError('Unselected export reported')
    return dict(groups=groups, files=len(inventory), bytes=sum(r['bytes'] for r in inventory))


def validate_all(plan, root, player_root, outputs, gate_attempt):
    result = read(root/'native-result.json')
    identity = result['identity']
    for key, field in (('source_commit','source_head'), ('base_commit','base_commit'),
                       ('tested_checkout_commit','tested_checkout'), ('github_run_id','run_id'), ('github_event_name','event')):
        if not plan.get(field) or identity.get(key) != plan[field]:
            raise ValueError('Native source/run binding mismatch: '+key)
    attempt = outputs.get('product_attempt')
    attempts = [plan['run_attempt'], attempt, gate_attempt]
    if (any(not isinstance(v,str) or not re.fullmatch(r'[1-9][0-9]*',v) for v in attempts)
            or not int(attempts[0]) <= int(attempts[1]) <= int(attempts[2])
            or identity['github_run_attempt'] != attempt or result['selection_attempt'] != plan['run_attempt']):
        raise ValueError('Native producer/selection/gate attempt mismatch')
    if identity['source_tree_dirty'] is not False or result['groups'] != plan['native_groups'] or result['expected'] != plan['native_expected']:
        raise ValueError('Native actual selection/source mismatch')
    return dict(validate_payload(result, root, player_root), attempt=attempt)
