"""Independent reader for the selected ZS2 core cases, never the pixel worker."""
from collections import Counter
import hashlib
import json
import math
import re

# Explicit risk-based sample. IDs alone cannot attest these observed traces.
STROKES = ((1, 1, 0, 1), (1, -1, 0, 2), (4, 0, 1, 1), (4, 0, -1, 2),
           (16, 1, 0, 1), (16, 0, 1, 2), (17, -1, 0, 1), (17, 0, -1, 2),
           (50, 0, 1, 1), (50, 1, 0, 2))
FONT_CASES = tuple(f'font-{sheet}-ui{ui}' for sheet in ('T-01', 'T-06') for ui in (100, 125))
STROKE_IDS = tuple('stroke-%d-%d-%d-%d' % case for case in STROKES)
CASE_IDS = ('setup',) + FONT_CASES + ('gesture-probe',) + STROKE_IDS + (
    'protection-and-g1', 'lifecycle', 'chords', 'checkbox-save',
    'toggle-T-01', 'toggle-T-06', 'restart', 'g1-and-time-boundaries')


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate ZS2 JSON key')
        result[key] = value
    return result


def cells_hash(cells):
    return hashlib.sha256(json.dumps(cells, separators=(',', ':')).encode()).hexdigest()


def validate_stroke(data, sample):
    length, dx, dy, button = sample
    x, y = (0 if dx > 0 else length-1, 2) if dx else (2, 0 if dy > 0 else length-1)
    indices = [(y+dy*i)*50+x+dx*i for i in range(length)]
    target = 1 if button == 1 else 0
    cells = [-1]*2500
    for index in indices:
        cells[index] = target
    # History is canonical cell order; animation starts follow gesture order.
    history = [[dict(index=i, before=-1, after=target) for i in sorted(indices)]]
    expected = dict(definition='T-06', model=cells_hash(cells), mini=cells_hash(cells),
                    saved_cells=cells_hash(cells), history=history, cursor=1,
                    saved_history=history, saved_cursor=1, completed=False, saved_completed=False)
    effects = [[index, 1000000+(i*12000 if length <= 16 else math.floor(180000*i/(length-1)+0.5)),
                target, 0.21] for i, index in enumerate(indices)]
    after = data.get('after', {})
    if (set(data) != set(expected) | {'save_sha256', 'save_bytes', 'effects', 'processing', 'after'}
            or set(after) != set(data)-{'after'}
            or any(data.get(k) != v or after.get(k) != v for k, v in expected.items())
            or data.get('effects') != effects or data.get('processing') is not True
            or after.get('effects') != [] or after.get('processing') is not False
            or type(data.get('save_bytes')) is not int or data['save_bytes'] <= 0
            or not isinstance(data.get('save_sha256'), str)
            or not re.fullmatch('[0-9a-f]{64}', data['save_sha256'])
            or any(after.get(k) != data[k] for k in ('save_sha256', 'save_bytes'))):
        raise ValueError('Wrong ZS2 native stroke/model/mini/history/save trace')
    for observed in (data, after):
        if (observed['completed'] is not False or observed['saved_completed'] is not False
                or any(type(observed[k]) not in (int, float) for k in ('cursor', 'saved_cursor'))
                or any(type(v) not in (int, float) for history_key in ('history', 'saved_history')
                       for change in observed[history_key][0] for v in change.values())
                or any(type(v) not in (int, float) for effect in observed['effects'] for v in effect)):
            raise ValueError('Invalid ZS2 trace value types')


def validate_log(output):
    rows = [json.loads(line.removeprefix('ZS2_CASE '), object_pairs_hook=unique)
            for line in output.splitlines() if line.startswith('ZS2_CASE ')]
    if (any(not isinstance(row, dict) for row in rows)
            or [row.get('id') for row in rows] != list(CASE_IDS)):
        raise ValueError('Missing/duplicate/relabeled ZS2 selected case')
    total = 0
    for row in rows:
        assertions = row.get('assertions', [])
        if (set(row) != {'id', 'checks', 'failures', 'seconds', 'assertions', 'data'}
                or not isinstance(assertions, list) or not assertions
                or any(not isinstance(a, dict) or set(a) != {'label', 'passed'}
                       or not isinstance(a['label'], str) or not a['label']
                       or a['passed'] is not True for a in assertions)
                or type(row['checks']) is not int or row['checks'] != len(assertions)
                or type(row['failures']) is not int or row['failures'] != 0
                or type(row['seconds']) not in (int, float)
                or not math.isfinite(row['seconds']) or row['seconds'] < 0
                or not isinstance(row['data'], dict)):
            raise ValueError('Missing/failed ZS2 native assertions or cost')
        labels = Counter(a['label'] for a in assertions)
        case, data = row['id'], row['data']
        required = REQUIRED.get(case, ())
        if case in STROKE_IDS:
            sample = STROKES[STROKE_IDS.index(case)]
            validate_stroke(data, sample)
            required = WAVE_LABELS
            for label in WAVE_CELL_LABELS:
                if labels[label] != sample[0]:
                    raise ValueError('Missing ZS2 per-cell checks')
        elif case in FONT_CASES:
            _, sheet, number, ui = case.split('-')
            pitch = data.get('pitch')
            if (set(data) != {'definition', 'ui', 'font', 'system_fallback', 'pitch', 'slots'}
                    or data['definition'] != sheet+'-'+number or data['ui'] != int(ui[2:])/100
                    or data['font'] != 'Delight Coffee' or data['system_fallback'] is not False
                    or not isinstance(pitch, list) or len(pitch) != 2
                    or any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in pitch)
                    or data['slots'] != pitch or labels['explicit Plex punctuation'] != 2):
                raise ValueError('Wrong ZS2 selected font/slot/UI trace')
            required = ('selected row pitch', 'selected column pitch', 'selected offline font')
        elif case.startswith('toggle-'):
            if data != dict(definition=case.removeprefix('toggle-'), animations=False, checked=False):
                raise ValueError('Wrong ZS2 selected session trace')
            required = ('session choice survives sheet/page/reset',)
        elif data:
            raise ValueError('Unexpected ZS2 case data')
        if not set(required) <= labels.keys():
            raise ValueError('Missing ZS2 protected/selected assertions: '+case)
        total += row['checks']
    summaries = re.findall(r'^ZS2_TESTS checks=(\d+) failures=(\d+)$', output, re.M)
    if (summaries != [(str(total), '0')] or output.splitlines().count('ZS2_TESTS_OK') != 1
            or 'ERROR:' in output or 'ZS1 FAIL:' in output):
        raise ValueError('ZS2 original total/failure/marker mismatch')
    return dict(cases=len(rows), checks=total, failures=0)


WAVE_CELL_LABELS = ('effective cell has effect', 'start follows gesture direction and effective ordinal',
                    '210ms target only', 'model and miniature already committed')
WAVE_LABELS = ('only effective cells animate', 'all cells saved before visual starts',
               'save-byte oracle reads a real slot', 'one atomic history entry contains every effective cell',
               'maximum 180ms spread', 'last cell still active at 209ms',
               'last ends by 390ms and ticker stops',
               'elapsed effects never write model/history/mini/save/completion') + WAVE_CELL_LABELS

# Existing protected assertions remain real native work; no frozen grand total.
REQUIRED = {'setup': ('regular scene and isolated test save root',
           'all registered regular sheets available',
           'new session starts enabled',
           'no study controls in regular app'),
 'gesture-probe': ('native route long static preview',
                   'preview no effect/history',
                   'one atomic commit, 20 directed effects',
                   'directed bounded timestamp',
                   'second gesture before first finishes',
                   'conversion preview replaces old fill',
                   'retraction never resurrects effect',
                   'immediate conversion commit',
                   'only youngest target',
                   'undo immediate, no effect',
                   'redo exact, no effect',
                   'erase preview unknown with contour',
                   'erase effect only neutral target',
                   'disable clears and stops ticking',
                   'enable no replay/history',
                   'toggle does not save',
                   'protected cells absent from preview',
                   'protected cells do not animate',
                   'noop does not animate',
                   'escape without action/effect',
                   'focus loss clears preview',
                   'lifecycle starts effect',
                   'lifecycle clears zoom',
                   'lifecycle clears resize',
                   'lifecycle clears information',
                   'lifecycle clears album',
                   'lifecycle clears reset',
                   'lifecycle clears switch',
                   'finish has no animation delay',
                   'completion saved immediately'),
 'protection-and-g1': ('longer wave still active after the old 260ms bound',
                       'fresh input commits inside extended animation window',
                       'extended-window input is saved immediately',
                       'preview supersedes pending fills',
                       'retracted waiting fill never returns',
                       'new commit wins without input lock',
                       'removal has no staggering or old mark',
                       'whole removal ends at 120ms'),
 'lifecycle': ('redo never schedules effects',
               'lifecycle has genuinely waiting effects: undo',
               'lifecycle has genuinely waiting effects: escape',
               'lifecycle has genuinely waiting effects: focus',
               'lifecycle has genuinely waiting effects: zoom',
               'lifecycle has genuinely waiting effects: pan',
               'lifecycle has genuinely waiting effects: resize',
               'lifecycle has genuinely waiting effects: information',
               'lifecycle has genuinely waiting effects: album',
               'lifecycle has genuinely waiting effects: reset',
               'lifecycle has genuinely waiting effects: restore',
               'lifecycle has genuinely waiting effects: switch',
               'lifecycle has genuinely waiting effects: off',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: undo',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: escape',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: focus',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: zoom',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: pan',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: resize',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: information',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: album',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: reset',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: restore',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: switch',
               'VS2 no-op navigation preserves live effect; real lifecycle clears: off',
               'no deferred resurrection after undo',
               'no deferred resurrection after escape',
               'no deferred resurrection after focus',
               'no deferred resurrection after zoom',
               'no deferred resurrection after pan',
               'no deferred resurrection after resize',
               'no deferred resurrection after information',
               'no deferred resurrection after album',
               'no deferred resurrection after reset',
               'no deferred resurrection after restore',
               'no deferred resurrection after switch',
               'no deferred resurrection after off'),
 'chords': ('opposite Down cancels globally',
            'both buttons must be released',
            're-Down and movement while either held stay blocked',
            'aborted chord leaves old action/save/mini intact and never commits',
            'release barrier recovers',
            'fresh Down after both Up works',
            'focus loss permits idle recovery',
            'fresh focus-return gesture works',
            'focus return with original still held cannot start opposite gesture',
            'release after focus-held chord recovers',
            'wrong Up alone does not cancel',
            'original Up still commits',
            'VS2 grid MMB never enters navigation',
            'VS2 obsolete hand has neither pan nor cell route'),
 'checkbox-save': ('checkbox ends active effects',
                   'checkbox preserves view/history',
                   'checkbox preserves save bytes'),
 'restart': ('reenabling never replays', 'new app ignores previous session choice'),
 'g1-and-time-boundaries': ('G1 reorients static target',
                            'retracted horizontal effect stays superseded',
                            'cancel leaves confirmed action only',
                            'remove remains purely visual at 119ms',
                            'remove ends at 120ms',
                            'set still active at 209ms',
                            'set ends at 210ms and ticker stops')}
