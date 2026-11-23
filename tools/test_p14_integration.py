import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from p14_integration import ACCOUNT, DEVICE, EPOCH, HOST, PROFILE, OTHER_BYTES, FOREIGN, Oracle, build_plan, verify_evidence, validate_trace


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
        row['recent'] = {} if action['number'] < 3 else dict(format='picross-recent-puzzle-v1', id='T-06', revision=2)
        row['recent_id'] = row['recent'].get('id', '')
        rows.append(row)
        if action['kind'] == 'quit':
            (directory/(action['process']+'-save.json')).write_text(json.dumps({**oracle.state(),'view':dict(view)}), encoding='utf-8')
    def snapshot(row):
        return dict(schema=1, definition_id='T-06', definition_revision=2, width=50, height=50, completed=False,
                    **{k:row[k] for k in ('cells','history','cursor','undo_used','view')})
    first = snapshot(rows[10])
    body = json.dumps(dict(format='picross-sync/v1', operation='snapshot', request_seq=1, base_server_revision=0, save=first))
    request = dict(context='user://p1/accounts/'+PROFILE, device=DEVICE, generation=EPOCH, local=1,
                   seq=1, base=0, method='POST', path='/v1/puzzles/T-06/mutations', body=body)
    for stage, generation, index in [('writer',2,13),('reader',3,16)]:
        saved = snapshot(rows[index])
        (directory/(stage+'-account.json')).write_text(json.dumps(saved))
        payload = json.dumps(dict(context=dict(server=HOST,account=ACCOUNT,device=DEVICE),generation=EPOCH,
                                  local=generation,sequence=0,intent={},request=request,
                                  entries={'1':{'value':first},str(generation):{'value':saved}}))
        image = dict(format='picross-local-sync/v1',payload=payload,sha256=hashlib.sha256(payload.encode()).hexdigest())
        (directory/(stage+'-journal.json')).write_text(json.dumps(image))
    checkpoints = {11:(1,3),14:(2,2),15:(2,2),16:(3,3)}
    for row in rows:
        values = checkpoints.get(row['action']['number'])
        row['account'] = dict(local=values[0], cursor=values[1], seq=1,
                              body_sha256=hashlib.sha256(body.encode()).hexdigest()) if values else {}
    (directory/'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    (directory/'trace.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows), encoding='utf-8')
    hashes = {n:hashlib.sha256(v).hexdigest() for n,v in FOREIGN.items()}
    hashes['other-account/t06.json'] = hashlib.sha256(OTHER_BYTES).hexdigest()
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
            path = directory/'trace.jsonl'
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            for field, value in [('recent', {}), ('recent_id', 'foreign')]:
                original = rows[14][field]
                rows[14][field] = value
                path.write_text(''.join(json.dumps(row)+'\n' for row in rows), encoding='utf-8')
                with self.assertRaisesRegex(AssertionError, 'recent'):
                    validate_trace(build_plan(), path)
                rows[14][field] = original


    def test_missing_corrupt_and_rebound_account_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            evidence_fixture(directory)
            path = directory/'reader-journal.json'
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                verify_evidence(directory)
            for field, value in [('device',ACCOUNT),('local',2),('body','{}')]:
                image = json.loads(raw)
                state = json.loads(image['payload'])
                state['request'][field] = value
                image['payload'] = json.dumps(state)
                image['sha256'] = hashlib.sha256(image['payload'].encode()).hexdigest()
                path.write_text(json.dumps(image))
                with self.subTest(field=field), self.assertRaises(AssertionError):
                    verify_evidence(directory)


if __name__ == '__main__':
    unittest.main()
