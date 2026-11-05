"""Cheap adversarial reader inputs; these do not replace the native ZS2 run."""
from copy import deepcopy
import json
import unittest

from zs2_evidence import (CASE_IDS, FONT_CASES, STROKES, STROKE_IDS, REQUIRED,
                          WAVE_LABELS, WAVE_CELL_LABELS, cells_hash, validate_log)


def selected_rows():
    rows = []
    for case in CASE_IDS:
        labels, data = list(REQUIRED.get(case, ())), {}
        if case in FONT_CASES:
            _, sheet, number, ui = case.split('-')
            data = dict(definition=sheet+'-'+number, ui=int(ui[2:])/100, font='Delight Coffee',
                        system_fallback=False, pitch=[24, 18], slots=[24, 18])
            labels = ['selected row pitch', 'selected column pitch', 'selected offline font',
                      'explicit Plex punctuation', 'explicit Plex punctuation']
        elif case in STROKE_IDS:
            n, dx, dy, button = STROKES[STROKE_IDS.index(case)]
            first = (0 if dx > 0 else n-1, 2) if dx else (2, 0 if dy > 0 else n-1)
            indices = [50*(first[1]+dy*i)+first[0]+dx*i for i in range(n)]
            cells = [-1]*2500
            for i in indices: cells[i] = 2-button
            history = [[dict(index=i, before=-1, after=2-button) for i in sorted(indices)]]
            data = dict(definition='T-06', model=cells_hash(cells), mini=cells_hash(cells),
                        saved_cells=cells_hash(cells), history=history, saved_history=deepcopy(history),
                        cursor=1, saved_cursor=1, completed=False, saved_completed=False,
                        save_sha256='a'*64, save_bytes=10000, processing=True,
                        effects=[[i, 1000000+(j*12000 if n <= 16 else round(j*180000/(n-1))),
                                  2-button, .21] for j, i in enumerate(indices)])
            after = deepcopy(data); after.update(effects=[], processing=False)
            data['after'] = after
            labels = list(WAVE_LABELS) + list(WAVE_CELL_LABELS)*(n-1)
        elif case.startswith('toggle-'):
            data = dict(definition=case.removeprefix('toggle-'), animations=False, checked=False)
            labels = ['session choice survives sheet/page/reset']
        rows.append(dict(id=case, checks=len(labels), failures=0, seconds=.1, data=data,
                         assertions=[dict(label=label, passed=True) for label in labels]))
    return rows


def selected_log(rows=None):
    rows = selected_rows() if rows is None else rows
    return '\n'.join('ZS2_CASE '+json.dumps(row) for row in rows) + (
        f'\nZS2_TESTS checks={sum(r["checks"] for r in rows)} failures=0\nZS2_TESTS_OK\n')


class SelectedZS2(unittest.TestCase):
    def test_selected_traces_reject_missing_duplicate_relabel_and_manipulation(self):
        original = selected_rows()
        self.assertEqual(validate_log(selected_log(original))['cases'], 24)
        mutations = [
            lambda r: r.pop(), lambda r: r.append(deepcopy(r[0])),
            lambda r: r[6].update(id=r[7]['id']),
            lambda r: r[6]['data']['effects'][0].__setitem__(1, 1000001),
            lambda r: r[6]['data'].update(model='0'*64),
            lambda r: r[6]['data'].update(mini='0'*64),
            lambda r: r[6]['data'].update(saved_cells='0'*64),
            lambda r: r[6]['data']['after'].update(save_sha256='b'*64),
            lambda r: r[6]['data']['after'].update(processing=True),
            lambda r: r[6]['data']['after'].update(completed=True),
            lambda r: r[6]['data']['history'][0][0].update(before=0),
            lambda r: r[6]['data']['saved_history'][0][0].update(index=101),
            lambda r: r[6]['data'].update(saved_cursor=True),
            lambda r: r[1]['data'].update(definition='T-02'),
            lambda r: r[1]['data'].update(ui=1.25),
            lambda r: r[1]['data'].update(system_fallback=True),
            lambda r: r[1]['data'].update(slots=[25, 18]),
            lambda r: r[21]['data'].update(checked=True),
            lambda r: r[0].update(failures=1),
            lambda r: r[0].update(checks=0),
            lambda r: r[0].update(seconds=float('nan')),
            lambda r: r[0]['assertions'][0].update(passed=False),
            lambda r: r[5]['assertions'][-1].update(label='removed completion check'),
            lambda r: r[6]['assertions'][-1].update(label='removed cell check'),
        ]
        for mutate in mutations:
            rows = deepcopy(original); mutate(rows)
            with self.subTest(mutation=mutations.index(mutate)), self.assertRaises(ValueError):
                validate_log(selected_log(rows))

    def test_original_summary_and_duplicate_json_fail_closed(self):
        log = selected_log()
        for changed in (log.replace('failures=0', 'failures=1'), log+'ZS2_TESTS_OK\n',
                        log.replace('"failures": 0', '"failures": 1, "failures": 0', 1),
                        log+'SCRIPT ERROR: failure\n', log.replace('ZS2_TESTS checks=', 'old checks=')):
            with self.assertRaises(ValueError): validate_log(changed)


if __name__ == '__main__':
    unittest.main()
