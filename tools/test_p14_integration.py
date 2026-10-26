import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from p14_integration import FOREIGN, Oracle, build_plan, verify_evidence, validate_trace


def evidence_fixture(directory):
    """Synthetic evidence for adversarial gate tests; never a native T01 claim."""
    directory.mkdir(parents=True, exist_ok=True)
    plan, rows, oracle = build_plan(), [], Oracle()
    view = dict(active_color=1, tool='fill', zoom=24, overview=False, center=[25,25],
                row_clue_reads=[{'anchor':'start'}]*50, column_clue_reads=[{'anchor':'start'}]*50)
    for action in plan:
        changes = oracle.step(action)
        view.update(active_color=oracle.color, tool=oracle.tool)
        if action['kind'] == 'zoom': view['zoom'] = 22
        row = dict(action=action, changes=changes, **oracle.state(), view=dict(view),
                   actual_cell=view['zoom'], fit_ceiling=24, pid=1 if action['process'] == 'writer' else 2, elapsed_us=1)
        rows.append(row)
        if action['kind'] == 'quit':
            (directory/(action['process']+'-save.json')).write_text(json.dumps({**oracle.state(),'view':dict(view)}), encoding='utf-8')
    (directory/'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    (directory/'trace.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows), encoding='utf-8')
    hashes = {n:hashlib.sha256(v).hexdigest() for n,v in FOREIGN.items()}
    (directory/'foreign-slots.json').write_text(json.dumps({s:hashes for s in ('before','writer','reader')}), encoding='utf-8')
    summary = verify_evidence(directory)
    (directory/'summary.json').write_text(json.dumps(summary), encoding='utf-8')
    return summary


class IntegrationContractTests(unittest.TestCase):
    def test_full_budget_and_independent_known_final_state(self):
        plan, oracle = build_plan(), Oracle()
        self.assertEqual(len(plan),17)
        self.assertEqual([a['number'] for a in plan],list(range(1,18)))
        for action in plan:
            oracle.step(action)
            if action['number'] == 11:
                self.assertEqual(oracle.cursor,3)
                self.assertEqual(len(oracle.history),3)
                self.assertEqual([c['index'] for c in oracle.history[-1]],[160,161,162])
            if action['number'] == 14:
                self.assertEqual(oracle.cursor,2)
                self.assertEqual(len(oracle.history),3)
        expected = [-1]*2500
        expected[102:106] = [2]*4
        expected[106:110] = [0]*4
        expected[160:163] = [2]*3
        self.assertEqual(oracle.cells,expected)
        self.assertEqual(oracle.transactions,4)
        self.assertTrue(oracle.undo_used)

    def test_positive_negative_and_foreign_saved_view_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            summary = evidence_fixture(directory)
            self.assertEqual(summary['negative_controls'],['changed cell rejected','incomplete trace rejected'])
            for filename,key,value in [('writer-save.json','cursor',3),('reader-save.json','undo_used',False),
                                       ('foreign-slots.json','reader',{}),('writer-save.json','view',{})]:
                path = directory/filename
                original = path.read_bytes()
                data = json.loads(original); data[key] = value
                path.write_text(json.dumps(data),encoding='utf-8')
                with self.subTest(filename=filename,key=key),self.assertRaises(AssertionError):
                    verify_evidence(directory)
                path.write_bytes(original)
            with self.assertRaisesRegex(AssertionError,'complete fixed'):
                validate_trace(build_plan()[:-1],directory/'trace.jsonl')


if __name__ == '__main__':
    unittest.main()
