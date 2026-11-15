"""PW-PERF-D-B01 temporary boundary probe; TEST ONLY, no owner decision.
Uses real v5 snapshot capture/Package and freshly calculated negative palette inputs.
Only exception_record is exercised with a synthetic final-approval hash;
this does not claim actual human approval or full negative export admission.
"""
import sys, unittest, json, hashlib
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
from tests.puzzle_production.test_authoring_workflow import WorkflowFixture
from tests.puzzle_production.test_background_content import BackgroundContentTests
from tools.puzzle_production import palette_gate as gate, target_adapter as adapter
from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import InvalidInput, write_json

class Boundary(unittest.TestCase):
    def test_negative_v5_exception_generation_and_bindings(self):
        original=BackgroundContentTests.content
        def negative(helper, **kw):
            if kw.get('mode')=='color': kw['colors']=['#447799','#487b9d']
            return original(helper,**kw)
        with patch.object(BackgroundContentTests,'content',negative):
            f=WorkflowFixture(self,mode='color')
        f.split_rulebook()
        from tools.puzzle_production.za1_fixtures import seal
        # Construct a sealed diagnostic original, never a qualified Builder offer.
        seal(f.helper.source,f.request['handoff'])
        archive=f.helper.content.archive(f.helper.source)
        before=hashlib.sha256(archive.read_bytes()).hexdigest()
        with open_package(archive,allow_background=True) as package:
            report=adapter.inspect(package,allow_background=True)[0]
            pg=report['palette_gate']; a=pg['assessment']; binding=pg['binding']
            self.assertEqual(package.handoff['format'],'picross-authoring-handoff-v5')
            self.assertEqual(a['status'],'negative'); self.assertEqual(len(a['negative_pairs']),1)
            self.assertEqual(binding['rulebook'],f.request['handoff']['rulebook'])
            self.assertEqual(binding['rulebook']['format'],'picross-authoring-rulebook-v2')
            self.assertEqual(len(binding['rulebook']['sources']),8)
            approval={'sha256':hashlib.sha256(b'TEST ONLY synthetic final approval').hexdigest()}
            record={'format':'picross-palette-editorial-exception-v2','binding':binding,
                    'negative_pairs':a['negative_pairs'],'actor':'TEST ONLY',
                    'timestamp_utc':'2026-11-15T12:00:00Z','statement':'TEST ONLY synthetic declaration',
                    'reason':'Generation boundary only, no real owner decision',
                    'approval_sha256':approval['sha256'],'test_only':True}
            path=f.root/'exception.json'
            def read(value,actual_approval=approval):
                write_json(path,value)
                return gate.exception_record(package,path,binding,a,actual_approval)
            self.assertEqual(read(record)['record'],record)
            with self.assertRaisesRegex(InvalidInput,'Unsupported palette exception'):
                read({**record,'format':gate.EXCEPTION})
            with self.assertRaisesRegex(InvalidInput,'Stale palette exception binding'):
                read({**record,'binding':{**binding,'rulebook':{**binding['rulebook'],'sources':binding['rulebook']['sources'][:-1]}}})
            with self.assertRaisesRegex(InvalidInput,'every negative pair'):
                read({**record,'negative_pairs':[]})
            with self.assertRaisesRegex(InvalidInput,'actual final approval'): read(record,None)
            with self.assertRaisesRegex(InvalidInput,'final approval differs'):
                read({**record,'approval_sha256':'0'*64})
            self.assertEqual(a['status'],'negative')
            print(json.dumps({'handoff':package.handoff['format'],'assessment':a['status'],
                'negative_pairs':a['negative_pairs'],'rulebook_sources':len(binding['rulebook']['sources']),
                'v2':'accepted','v1':'rejected','missing_rule_source':'rejected',
                'missing_pair':'rejected','missing_approval':'rejected','wrong_approval_hash':'rejected'},ensure_ascii=False))
        self.assertEqual(before,hashlib.sha256(archive.read_bytes()).hexdigest())

unittest.main(argv=[sys.argv[0], 'Boundary'],verbosity=2)
