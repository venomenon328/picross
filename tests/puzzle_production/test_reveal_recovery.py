"""AT-S05/S06: publication boundaries, foreign data, exact journal generations."""
from copy import deepcopy
from pathlib import Path
import os
import subprocess
import sys
import signal
import time
from unittest.mock import patch
import unittest

from tools.puzzle_production import catalog_publication as pub, catalog_reveal as at, catalog_transaction as tx
from tools.puzzle_production import content_registry as cr, catalog_io as io, reveal_source as source
from tools.puzzle_production.contract import InvalidInput, canonical_bytes
try:
    from test_catalog_reveal import RevealTests, snapshot
except ImportError:
    from tests.puzzle_production.test_catalog_reveal import RevealTests, snapshot


class RecoveryTests(unittest.TestCase):
    setUpClass = classmethod(RevealTests.setUpClass.__func__)
    tearDownClass = classmethod(RevealTests.tearDownClass.__func__)
    setUp = RevealTests.setUp
    request = RevealTests.request
    make_plan = RevealTests.make_plan

    def interrupt(self, phase, plan):
        def stop(actual, name=None):
            if actual == phase: raise InterruptedError('TEST ONLY '+phase)
        with patch.object(pub, 'checkpoint', side_effect=stop), self.assertRaises(InterruptedError):
            at.adopt(self.checkout, plan)

    def test_all_forward_phases_and_repeated_recovery_preserve_original_bytes(self):
        import shutil
        original = {n:b for n,(b,_) in snapshot(self.checkout).items()}
        plan = self.make_plan(append='TEST ONLY attribution\n')
        for phase in ('P0','journal-complete','P1','P2','temp-prefix','temp-complete','P3','P4','P6'):
            with self.subTest(phase=phase):
                self.interrupt(phase, plan)
                if phase != 'P0': cr.recover(self.checkout)
                current = {n:b for n,(b,_) in snapshot(self.checkout).items()}
                self.assertEqual(original,current)
                cr.check_checkout(self.checkout)
        self.interrupt('P4',plan)
        def stop_recovery(phase,name=None):
            if phase == 'R1-binary': raise InterruptedError('TEST ONLY recovery interruption')
        with patch.object(pub,'checkpoint',side_effect=stop_recovery), self.assertRaises(InterruptedError): cr.recover(self.checkout)
        self.assertTrue((self.checkout/tx.LOCK).exists())
        cr.recover(self.checkout)
        self.assertEqual(original,{n:b for n,(b,_) in snapshot(self.checkout).items()})

    def test_foreign_binary_text_lock_and_temp_block_before_rollback_mutation(self):
        plan = self.make_plan()
        self.interrupt('P4',plan)
        lock = self.checkout/tx.LOCK
        raw = lock.read_bytes(); journal = io.json_bytes(raw,pub.LIMIT)
        targets = ['game/'+self.entry['reveal'], source.path(self.identifier), tx.LOCK]
        for name in targets:
            path = self.checkout/name; old = path.read_bytes(); path.write_bytes(b'FOREIGN DATA')
            before = snapshot(self.checkout)
            with self.subTest(name=name), self.assertRaises((ValueError,OSError)): cr.recover(self.checkout)
            self.assertEqual(before,snapshot(self.checkout)); path.write_bytes(old)
        temporary = next(iter(pub.inventory(journal,raw).values()))
        target = self.checkout/temporary; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(b'FOREIGN TEMP')
        before=snapshot(self.checkout)
        with self.assertRaises(ValueError): cr.recover(self.checkout)
        self.assertEqual(before,snapshot(self.checkout)); target.unlink()
        cr.recover(self.checkout)

    def test_hard_kill_and_rekill_use_real_processes_and_same_journal(self):
        plan = self.make_plan()
        original = {n:b for n,(b,_) in snapshot(self.checkout).items()}
        marker=self.root/'checkpoint.txt'
        code = '''
import sys,time,os
from pathlib import Path
from tools.puzzle_production import catalog_publication as p, catalog_reveal as a, content_registry as c
root,plan,marker,phase,mode=map(str,sys.argv[1:])
def checkpoint(actual,name=None):
    if actual==phase:
        Path(marker).write_text(str(os.getpid()),encoding='utf-8')
        while True: time.sleep(0.1)
p.checkpoint=checkpoint
if mode=='adopt': a.adopt(Path(root),Path(plan))
else: c.recover(Path(root))
'''
        def kill_at(phase,mode):
            marker.unlink(missing_ok=True)
            process=subprocess.Popen([sys.executable,'-c',code,str(self.checkout),str(plan),str(marker),phase,mode],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                deadline=time.monotonic()+300
                while not marker.exists() and process.poll() is None and time.monotonic()<deadline: time.sleep(0.05)
                if not marker.exists():
                    out,err=process.communicate(timeout=5);self.fail((out+err).decode(errors='replace'))
                os.kill(int(marker.read_text()),getattr(signal,'SIGKILL',signal.SIGTERM));process.wait(timeout=20)
                self.assertNotEqual(process.returncode,0)
            finally:
                if process.poll() is None: process.kill();process.wait()
                process.stdout.close();process.stderr.close()
        kill_at('P4','adopt'); raw=(self.checkout/tx.LOCK).read_bytes()
        kill_at('R1-binary','recover')
        self.assertEqual(raw,(self.checkout/tx.LOCK).read_bytes())
        cr.recover(self.checkout)
        self.assertEqual(original,{n:b for n,(b,_) in snapshot(self.checkout).items()})

    def test_journal_dispatch_and_base64_canonicality(self):
        for value in ({'sha256':'0'*64,'bytes':True,'base64':'YQ=='},
                      {'sha256':io.checksum(b'a'),'bytes':1,'base64':'YR=='},
                      {'sha256':io.checksum(b'a'),'bytes':1,'base64':'YQ=\n'}):
            with self.assertRaises(ValueError): pub.decode_binary(value)
        self.assertEqual(pub.decode_binary(pub.binary(b'abc')),b'abc')
        lock=self.checkout/tx.LOCK
        with lock.open('wb') as f:
            f.write(b'{"format":"picross-catalog-metadata-journal-v2",');f.truncate(pub.NORMAL_LIMIT+1)
        before=lock.stat().st_mtime_ns
        with self.assertRaisesRegex(ValueError,'Only reveal'): pub.read_journal(self.checkout)
        self.assertEqual(lock.stat().st_mtime_ns,before)
        lock.unlink()

    def test_multiple_ids_every_binary_text_and_recovery_boundary(self):
        import shutil
        from tools.puzzle_production.za1_fixtures import FIXTURES, approve, difficulty_for_export
        from tools.puzzle_production.target_adapter import export
        from tools.puzzle_production.contract import load_json,write_json
        approval=self.root/'color-approval.json';approve(FIXTURES/'direct-color',approval)
        exported=self.root/'color-export'
        export(FIXTURES/'direct-color',exported,name='TEST ONLY',revision=1,stem='at_color',save_slot='at_color',
               approval_path=approval,category_id='voegel',categories_path=self.checkout/'content/categories.json')
        cr.registration(exported,self.checkout,apply=True,difficulty=difficulty_for_export(exported))
        first=self.request(1,'TEST ONLY first attribution\n')
        self.identifier='pz-test-direct-color'
        second=self.request(2,'TEST ONLY second attribution\n')
        combined=self.root/'combined';combined.mkdir();requests=[]
        for index,path in enumerate((first,second)):
            row=load_json(path)['entries'][0];name=f'image-{index}.png'
            shutil.copyfile(path.parent/row['image'],combined/name);row['image']=name;requests.append(row)
        write_json(combined/'request.json',{'format':at.REQUEST,'entries':requests})
        target=self.root/'multi-plan';at.plan(self.checkout,[r['id'] for r in requests],combined/'request.json',target)
        plan=target/'plan.json';value=load_json(plan)
        original={n:b for n,(b,_) in snapshot(self.checkout).items()}
        boundaries=[('P3' if w['kind']=='binary-replace' else 'P4',w['path']) for w in value['writes']]
        for phase,name in boundaries:
            def stop(actual,path=None):
                if (actual,path)==(phase,name): raise InterruptedError('TEST ONLY multi-target boundary')
            with self.subTest(phase=phase,name=name),patch.object(pub,'checkpoint',side_effect=stop),self.assertRaises(InterruptedError):at.adopt(self.checkout,plan)
            cr.recover(self.checkout)
            self.assertEqual(original,{n:b for n,(b,_) in snapshot(self.checkout).items()})
        self.interrupt('P6',plan)
        raw=(self.checkout/tx.LOCK).read_bytes();journal=io.json_bytes(raw,pub.LIMIT)
        recovery=[('R0',None),*[('R1-binary',n) for n in journal['replacements']],
                  *[('R1-text',w['path']) for w in value['writes'] if w['kind']!='binary-replace'],('R1-runtime',None),('R2',None)]
        for phase,name in recovery:
            def stop(actual,path=None):
                if (actual,path)==(phase,name):raise InterruptedError('TEST ONLY repeated recovery boundary')
            with self.subTest(phase=phase,name=name),patch.object(pub,'checkpoint',side_effect=stop),self.assertRaises(InterruptedError):cr.recover(self.checkout)
            self.assertEqual(raw,(self.checkout/tx.LOCK).read_bytes())
        cr.recover(self.checkout)
        self.assertEqual(original,{n:b for n,(b,_) in snapshot(self.checkout).items()})

    def test_exact_limit_dispatch_before_json_decode_and_large_binary_chunks(self):
        from tools.puzzle_production.contract import Aborted
        lock=self.checkout/tx.LOCK
        for prefix,limit in ((b'{"format":"picross-catalog-metadata-journal-v2",',pub.NORMAL_LIMIT),(pub.PREFIX,pub.LIMIT)):
            for size in (limit-1,limit,limit+1):
                with self.subTest(prefix=prefix,size=size):
                    with lock.open('wb') as stream:stream.write(prefix);stream.truncate(size)
                    with patch.object(io,'read',return_value=b'bounded-test') as read:
                        if size>limit:
                            with self.assertRaises((ValueError,Aborted)):pub.read_journal(self.checkout)
                            read.assert_not_called()
                        else:self.assertEqual(pub.read_journal(self.checkout),b'bounded-test');read.assert_called_once()
                    lock.unlink()
        raw=b'x'*source.IMAGE_LIMIT;value=pub.binary(raw)
        self.assertEqual(pub.decode_binary(value),raw)
        self.assertTrue(all(len(c)<=io.CHUNK for c in pub.binary_chunks(value)))
        for changes in ({'bytes':source.IMAGE_LIMIT+1},{'base64':value['base64']+'AAAA'},{'sha256':'0'*64}):
            with self.assertRaises(ValueError):pub.decode_binary({**value,**changes})

    def test_two_real_png_sides_at_32_mib_and_aggregate_limit_before_decode(self):
        from tools.puzzle_production.contract import Aborted
        from tests.puzzle_production.test_catalog_reveal import synthetic_image
        image=self.root/'large.png';synthetic_image(image)
        raw=image.read_bytes()
        sides={kind:pub.binary(raw+padding*(source.IMAGE_LIMIT-len(raw))) for kind,padding in (('old',b'a'),('new',b'b'))}
        journal={'operation':'reveal-adoption','replacements':{'game/'+self.entry['reveal']:sides}}
        pub.validate_replacements(journal,{'entries':[self.entry]})
        other=deepcopy(self.entry);other['reveal']='art/content/another.png'
        journal['replacements']['game/'+other['reveal']]=sides
        with patch.object(pub,'binary_chunks',side_effect=AssertionError('Decoded before total byte guard')):
            with self.assertRaises(Aborted):pub.validate_replacements(journal,{'entries':[self.entry,other]})

    def test_partial_journal_and_foreign_phase_are_preserved(self):
        plan=self.make_plan();original=snapshot(self.checkout)
        self.interrupt('journal-prefix',plan)
        before=snapshot(self.checkout)
        # A small journal can already be complete at the first chunk boundary;
        # explicitly truncate its own staging to model a partial OS write.
        stage=next((self.checkout/'content').glob('.registration-journal-*.tmp'))
        stage.write_bytes(stage.read_bytes()[:17]);before=snapshot(self.checkout)
        with self.assertRaises(ValueError):cr.recover(self.checkout)
        self.assertEqual(before,snapshot(self.checkout));stage.unlink()
        altered=self.checkout/'game'/self.entry['reveal'];old=altered.read_bytes()
        def foreign(phase,name=None):
            if phase=='P3':altered.write_bytes(old)
        with patch.object(pub,'checkpoint',side_effect=foreign),self.assertRaisesRegex(ValueError,'phase changed'):at.adopt(self.checkout,plan)
        # The ordinary failure uses guarded recovery, restoring the old checkout.
        self.assertEqual({n:b for n,(b,_) in original.items()},{n:b for n,(b,_) in snapshot(self.checkout).items()})

    def test_pre_at_registration_and_metadata_generations_keep_exact_wire_contracts(self):
        import shutil,json
        from tools.puzzle_production import catalog_added as added
        from tools.puzzle_production.za1_fixtures import isolated_checkout,difficulty_for_export
        empty=isolated_checkout(self.root/'registration')
        with self.assertRaises(InterruptedError):cr.registration(self.exported,empty,apply=True,difficulty=difficulty_for_export(self.exported),fail_step='crash-index')
        original=io.json_bytes((empty/tx.LOCK).read_bytes(),pub.LIMIT)
        for format in (tx.LEGACY_FORMATS['registration'],tx.PREVIOUS_FORMATS['registration']):
            root=self.root/format;shutil.copytree(empty,root);j=deepcopy(original)
            j['format']=format;j.pop('replacements')
            legacy=format==tx.LEGACY_FORMATS['registration']
            for side in ('old','new'):
                j[side].pop(source.path(self.identifier))
                if legacy:j[side].pop(added.path(self.identifier))
                registry=json.loads(j[side][tx.REGISTRY])
                j[side][tx.RUNTIME]=tx.projection(j[side],registry,version=3 if legacy else 4).decode()
            if legacy:
                (root/added.path(self.identifier)).unlink(missing_ok=True)
                (root/tx.RUNTIME).write_text(j['old'][tx.RUNTIME],encoding='utf-8',newline='\n')
            (root/tx.LOCK).write_bytes(canonical_bytes(j)+b'\n')
            foreign=root/source.path(self.identifier);foreign.parent.mkdir(exist_ok=True);foreign.write_bytes(b'foreign AT\n')
            before=snapshot(root)
            with self.subTest(format=format),self.assertRaises(ValueError):cr.recover(root)
            self.assertEqual(before,snapshot(root));foreign.unlink()
            cr.recover(root);self.assertEqual(cr.check_checkout(root)['entries'],[])
            self.assertEqual(json.loads((root/tx.RUNTIME).read_bytes())['format'],'picross-runtime-registry-v4')
        # Legacy metadata v1 and current metadata v1/v2 are distinct dispatches.
        for format in (tx.LEGACY_FORMATS['sync'],tx.PREVIOUS_FORMATS['sync'],tx.FORMATS['sync']):
            root=self.root/format;shutil.copytree(self.checkout,root)
            legacy=format==tx.LEGACY_FORMATS['sync']
            if legacy:(root/added.path(self.identifier)).unlink();cr.sync_runtime(root)
            captured=tx.capture(root);j=tx.prepare(root,captured,{},operation='sync')
            j['format']=format
            if format!=tx.FORMATS['sync']:
                j.pop('replacements');j['retained']=tx.historical_snapshot(captured)['retained']
                for side in ('old','new'):
                    j[side].pop(source.path(self.identifier))
                    if legacy:
                        j[side].pop(added.path(self.identifier))
                        j[side][tx.RUNTIME]=tx.projection(j[side],captured['registry'],version=3).decode()
                if legacy:(root/tx.RUNTIME).write_text(j['old'][tx.RUNTIME],encoding='utf-8',newline='\n')
            raw=pub.journal_bytes(j) if tx.modern(j) else canonical_bytes(j)+b'\n'
            (root/tx.LOCK).write_bytes(raw)
            cr.recover(root);cr.check_checkout(root)
            self.assertEqual(json.loads((root/tx.RUNTIME).read_bytes())['format'],'picross-runtime-registry-v4')


del RevealTests  # Imported fixture owner is not a second discovered test suite.


class PackageTemporaryTests(unittest.TestCase):
    def test_real_kill_cannot_leave_unverifiable_package_prefix(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);marker=root/'ready';target='package/data.bin';temporary='package/.registration-'+('a'*64)+'-0.tmp'
            code='''
import sys,time,os
from pathlib import Path
from tools.puzzle_production import catalog_publication as p
root=Path(sys.argv[1])
def checkpoint(phase,name=None):
 if phase=='temp-prefix':
  (root/'ready').write_text(str(os.getpid()))
  while True:time.sleep(.1)
p.checkpoint=checkpoint
p.write(root,sys.argv[2],b'x'*(3*1024*1024),sys.argv[3],lambda:None,package_addition=True)
'''
            process=subprocess.Popen([sys.executable,'-c',code,str(root),target,temporary],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                deadline=time.monotonic()+30
                while not marker.exists() and process.poll() is None and time.monotonic()<deadline:time.sleep(.05)
                self.assertTrue(marker.exists(),'Writer did not reach actual partial package write')
                os.kill(int(marker.read_text()),getattr(signal,'SIGKILL',signal.SIGTERM));process.wait(timeout=10)
            finally:
                if process.poll() is None:process.kill();process.wait()
                process.stdout.close();process.stderr.close()
            self.assertFalse((root/temporary).exists());self.assertFalse((root/target).exists())
            pub.write(root,target,b'complete',temporary,lambda:None,package_addition=True)
            self.assertEqual((root/target).read_bytes(),b'complete');self.assertFalse((root/temporary).exists())

if __name__=='__main__': unittest.main()
