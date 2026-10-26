"""CI2-D: bounded native history and independent contract-level replay.

No product history implementation is imported. Every semantic command, including
selection, tool/color changes and quit, is in the fixed two-process plan.
"""
from copy import deepcopy
from collections import Counter
import hashlib
import json
from pathlib import Path

WIDTH = HEIGHT = 50
FOREIGN = {'t09.json': b'foreign damaged primary\n', 't09.bak': b'foreign damaged backup\n',
           'unregistered.json': b'foreign unregistered slot\n'}
NEGATIVES = ['changed cell rejected', 'incomplete trace rejected']


def build_plan():
    writer = [dict(kind='select', index=3), dict(kind='color', value=2),
              dict(kind='cell', start=[2, 2], end=[5, 2], button='left'),
              dict(kind='cell', start=[6, 2], end=[9, 2], button='right'),
              dict(kind='tool', value='erase'),
              dict(kind='cell', start=[2, 2], end=[3, 2], button='left'),
              dict(kind='tool', value='fill'), dict(kind='undo'), dict(kind='redo'), dict(kind='undo'),
              dict(kind='cell', start=[10, 3], end=[12, 3], button='left'),
              dict(kind='zoom', direction=-1), dict(kind='undo'), dict(kind='quit')]
    reader = [dict(kind='select', index=3), dict(kind='redo'), dict(kind='quit')]
    return [dict(number=i+1, process=process, **action) for i, (process, action) in
            enumerate([('writer', a) for a in writer]+[('reader', a) for a in reader])]


def write_plan(path):
    plan = build_plan()
    path.write_text(json.dumps(plan)+'\n', encoding='utf-8')
    return plan


class Oracle:
    def __init__(self):
        self.cells = [-1]*(WIDTH*HEIGHT)
        self.history = []
        self.cursor = 0
        self.undo_used = False
        self.color, self.tool, self.transactions = 1, 'fill', 0

    def state(self):
        return deepcopy(dict(cells=self.cells, history=self.history, cursor=self.cursor, undo_used=self.undo_used))

    def step(self, action):
        kind = action['kind']
        changes = []
        if kind == 'color':
            self.color, self.tool = action['value'], 'fill'
        elif kind == 'tool':
            self.tool = action['value']
        elif kind == 'undo':
            if not self.cursor:
                raise AssertionError('empty Undo')
            self.cursor -= 1
            changes = [dict(index=c['index'], before=c['after'], after=c['before'])
                       for c in self.history[self.cursor]]
            self.undo_used = True
        elif kind == 'redo':
            if self.cursor >= len(self.history):
                raise AssertionError('empty Redo')
            changes = self.history[self.cursor]
            self.cursor += 1
        elif kind == 'cell':
            sx, sy = action['start']
            ex, ey = action['end']
            assert sy == ey  # The bounded plan uses horizontal strokes only.
            target = -1 if self.tool == 'erase' else 0 if action['button'] == 'right' else self.color
            for x in range(sx, ex+1):
                index = sy*WIDTH+x
                before = self.cells[index]
                if before != target:
                    changes.append(dict(index=index, before=before, after=target))
            assert changes, 'ineffective edit'
            self.history = self.history[:self.cursor]+[deepcopy(changes)]
            self.cursor += 1
            self.transactions += 1
        for change in changes:
            assert self.cells[change['index']] == change['before']
            self.cells[change['index']] = change['after']
        return changes


def read_trace(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def validate_trace(plan, trace_path):
    if plan != build_plan():
        raise AssertionError('history requires the complete fixed two-process plan')
    actual = read_trace(trace_path)
    if len(actual) != len(plan):
        raise AssertionError('incomplete trace')
    pids = [{r['pid'] for r in actual if r['action']['process'] == stage} for stage in ('writer','reader')]
    assert all(len(ids) == 1 for ids in pids) and pids[0] != pids[1], 'two distinct native processes'
    oracle, previous = Oracle(), None
    states = {}
    for action, observed in zip(plan, actual, strict=True):
        changes = oracle.step(action)
        expected = dict(action=action, changes=changes, **oracle.state())
        for key, value in expected.items():
            if observed.get(key) != value:
                raise AssertionError(f"action {action['number']}: {key} differs from independent oracle")
        assert 4 < observed['actual_cell'] <= observed['fit_ceiling']+.001, 'bounded native geometry'
        view = observed['view']
        assert view['active_color'] == oracle.color and view['tool'] == oracle.tool, 'tool/color state'
        assert view['center'] == [25, 25] and 4 < view['zoom'] <= 72, 'bounded full view'
        assert len(view['row_clue_reads']) == HEIGHT and len(view['column_clue_reads']) == WIDTH
        if previous:
            prior = previous['view']
            if action['kind'] == 'zoom':
                steps = (12,14,16,18,20,22,24,26,28,30,32,34,36,40,44,48,54,60,66,72)
                lower = [n for n in steps if n < previous['actual_cell']]
                assert lower and view['zoom'] == max(lower) and not view['overview'], 'effective navigation'
            else:
                allowed = {'active_color','tool'} if action['kind'] in ('tool','color') else set()
                assert {k:v for k,v in view.items() if k not in allowed} == {k:v for k,v in prior.items() if k not in allowed}, 'saved view/restart changed'
        if action['kind'] == 'quit':
            states[action['process']] = dict(**oracle.state(), view=view)
        previous = observed
    assert 0 < oracle.transactions <= 6 and len(plan) <= 20
    assert states['writer']['cursor'] < len(states['writer']['history']), 'open redo at quit'
    assert states['reader']['cursor'] == len(states['reader']['history']), 'real restart redo'
    return states


def negative_controls(plan, trace_path):
    """Tamper only evidence bytes; never launch another game process."""
    import tempfile
    rows = read_trace(trace_path)
    with tempfile.TemporaryDirectory(prefix='ci2-d-negative-') as temporary:
        path = Path(temporary)/'trace.jsonl'
        changed = deepcopy(rows)
        changed[2]['cells'][102] = 0
        for bad, expected in ((changed, 'action 3'), (rows[:-1], 'incomplete trace')):
            path.write_text(''.join(json.dumps(r)+'\n' for r in bad), encoding='utf-8')
            try:
                validate_trace(plan, path)
            except AssertionError as error:
                if expected not in str(error):
                    raise
            else:
                raise AssertionError('negative control unexpectedly accepted')
    return NEGATIVES


def verify_evidence(directory):
    plan = json.loads((directory/'plan.json').read_text(encoding='utf-8'))
    states = validate_trace(plan, directory/'trace.jsonl')
    for stage, expected in states.items():
        saved = json.loads((directory/(stage+'-save.json')).read_text(encoding='utf-8'))
        for key, value in expected.items():
            assert saved[key] == value, 'actual saved '+stage+' '+key
    foreign = json.loads((directory/'foreign-slots.json').read_text(encoding='utf-8'))
    hashes = {name: hashlib.sha256(value).hexdigest() for name,value in FOREIGN.items()}
    assert foreign == {stage:hashes for stage in ('before','writer','reader')}, 'foreign slot bytes changed'
    return dict(schema=2, actions=len(plan), processes=2, effective_transactions=4,
                categories=dict(Counter(a['kind'] for a in plan)),
                writer_cursor=states['writer']['cursor'], history_size=len(states['writer']['history']),
                reader_cursor=states['reader']['cursor'], negative_controls=negative_controls(plan,directory/'trace.jsonl'),
                full_state_and_saved_view=True, foreign_slots_unchanged=len(hashes))
