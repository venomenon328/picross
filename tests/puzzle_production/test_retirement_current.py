"""PW-PERF-E selected current authorities, real Git proofs and read traps."""
from collections import Counter
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.catalog_fixtures import registered
from tests.puzzle_production.test_editor_change import current_fixture
from tests.puzzle_production.test_catalog_images import png, SVG, capability
from tests.puzzle_production.background_catalog_fixtures import prepare
from tools.puzzle_production import integrated_content as retirement, catalog_io as io
from tools.puzzle_production import editor_change as edit, content_registry as cr
from tools.puzzle_production import catalog_background as bg, reveal_source as reveal
from tools.puzzle_production import catalog_transaction as tx, retirement_scope
from tools.puzzle_production.contract import load_json, write_json, digest


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(),p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}


class CurrentRetirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = tempfile.TemporaryDirectory(prefix='retirement-current-base-')
        cls.addClassCleanup(cls.home.cleanup)
        cls.fixture = Path(cls.home.name)
        registered(cls.fixture,stem='retirement_current',save_slot='retirement_current')
        owner=unittest.TestCase();cls.addClassCleanup(owner.doCleanups)
        cls.background=prepare(owner,'selected',registered=True)

    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='retirement-current-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)/'checkout'
        shutil.copytree(self.fixture/'full-base',self.root)
        self.entry=load_json(self.root/cr.REGISTRY)['entries'][0]
        self.identifier=self.entry['id']
        write_json(self.root/retirement.INDEX,{'format':'picross-authoring-index-v1','entries':[]})
        directory='content/authoring/'+self.identifier+'/'+self.entry['production']['revision']
        write_json(self.root/directory/'record.json',{'format':'picross-authoring-record-v2','puzzle_id':self.identifier,
                   'revision':self.entry['production']['revision'],'state':'registered','blockers':[]})
        write_json(self.root/retirement.INDEX,{'format':'picross-authoring-index-v1','entries':[
                   {'puzzle_id':self.identifier,'revision':self.entry['production']['revision'],'record':directory+'/record.json'}]})
        self.git('init','-q');self.git('config','core.autocrlf','false')

    def git(self,*args):
        return subprocess.check_output(['git','-c','user.name=TEST ONLY','-c','user.email=test@example.invalid',
                                       '-c','commit.gpgsign=false',*args],cwd=self.root,stderr=subprocess.PIPE).decode().strip()

    def commit(self):
        self.git('add','.');self.git('commit','-qm','TEST ONLY synthetic integration')
        commit=self.git('rev-parse','HEAD');self.git('update-ref','refs/remotes/origin/main',commit)
        return commit

    def migrate(self,status='standard',extension='.svg'):
        value=load_json(self.root/cr.REGISTRY)
        value['backgrounds']=[];write_json(self.root/cr.REGISTRY,value)
        current_fixture(self.root)
        value=load_json(self.root/cr.REGISTRY);runtime=load_json(self.root/cr.RUNTIME)
        entry=value['entries'][0];row=runtime['entries'][0]
        asset=Path('game/'+entry['reveal']).with_suffix(extension).as_posix()
        old=self.root/'game'/entry['reveal']
        raw=png() if extension=='.png' else SVG
        if old != self.root/asset and old.exists(): old.unlink()
        (self.root/asset).write_bytes(raw)
        record=load_json(self.root/reveal.path(entry['id']))
        record['current']['asset']=bg.ref(asset,raw)
        record['record_hash']=digest({k:v for k,v in record.items() if k!='record_hash'})
        write_json(self.root/reveal.path(entry['id']),record);row['reveal']=asset.removeprefix('game/')
        image=bg.asset_path(entry['id'])
        active={'image_revision':1,'status':status,'asset':None}
        if status=='selected':
            raw=png((2304,576));(self.root/image).parent.mkdir(parents=True,exist_ok=True)
            (self.root/image).write_bytes(raw);active['asset']=bg.ref(image,raw)
        elif (self.root/image).exists(): (self.root/image).unlink()
        record=load_json(self.root/bg.path(entry['id']));record['current']=active
        record['record_hash']=digest({k:v for k,v in record.items() if k!='record_hash'})
        write_json(self.root/bg.path(entry['id']),record)
        value['backgrounds']=[{'id':entry['id'],'source':bg.ref(bg.path(entry['id']),edit.encoded(record))}]
        row['background']=deepcopy(active)
        if row['background']['asset']: row['background']['asset']['file']=image.removeprefix('game/')
        capability(self.root)
        write_json(self.root/cr.REGISTRY,value);write_json(self.root/cr.RUNTIME,runtime)

    def test_current_preferences_png_svg_original_anchor_and_noop(self):
        imported=self.commit();self.migrate('selected','.png');main=self.commit()
        before=snapshot(self.root);counts=Counter();raw_read=io._read
        def counted(root,name,limit,**kw):
            path=(Path(root)/name).relative_to(self.root).as_posix();counts[path]+=1
            return raw_read(root,name,limit,**kw)
        with patch.object(io,'_read',side_effect=counted),patch.object(tx,'capture',side_effect=AssertionError('whole capture')),patch.object(cr,'check_checkout',side_effect=AssertionError('whole audit')):
            result=retirement.retire(self.root,[self.identifier],imported)
        self.assertEqual(result['status'],'production_retired')
        prefix=self.entry['production']['package']
        self.assertTrue(all(n==1 for name,n in counts.items() if name.startswith(prefix+'/') and not name.endswith('/manifest.json')))
        receipt=load_json(self.root/prefix/'manifest.json')
        self.assertEqual(receipt['format'],retirement.CURRENT_FORMAT)
        self.assertEqual(receipt['entry'],self.entry)
        self.assertEqual(receipt['provenance']['main_commit'],main)
        after=snapshot(self.root)
        allowed={cr.REGISTRY,retirement.INDEX}|{name for name in before if name.startswith((prefix+'/','content/authoring/'+self.identifier+'/'))}
        self.assertEqual({k:v for k,v in before.items() if k not in allowed},{k:v for k,v in after.items() if k not in allowed})
        with patch.object(bg,'build',side_effect=AssertionError('retired ZIP')):
            self.assertEqual(retirement.retire(self.root,[self.identifier],imported)['status'],'no-op')
            cr.check_checkout(self.root)
        self.assertEqual(after,snapshot(self.root))
        # Current sources may subsequently choose none/standard and SVG; the
        # already compact technical receipt remains the original export anchor.
        for status in ('none','standard'):
            self.migrate(status,'.svg');self.commit()
            before=snapshot(self.root)
            self.assertEqual(retirement.retire(self.root,[self.identifier],imported)['status'],'no-op')
            self.assertEqual(before,snapshot(self.root))

    def test_v6_original_rights_and_distinct_import_source(self):
        # Separate non-main source commit, then import the same package objects.
        for p in self.root.iterdir():
            if p.name!='.git':
                if p.is_dir(): shutil.rmtree(p)
                else:p.unlink()
        shutil.copytree(self.background.checkout,self.root,dirs_exist_ok=True)
        self.entry=load_json(self.root/cr.REGISTRY)['entries'][0];self.identifier=self.entry['id']
        revision=self.entry['production']['revision'];directory='content/authoring/'+self.identifier+'/'+revision
        write_json(self.root/directory/'record.json',{'format':'picross-authoring-record-v2','puzzle_id':self.identifier,'revision':revision,'state':'registered','blockers':[]})
        write_json(self.root/retirement.INDEX,{'format':'picross-authoring-index-v1','entries':[{'puzzle_id':self.identifier,'revision':revision,'record':directory+'/record.json'}]})
        source=self.commit()
        shutil.rmtree(self.root/directory)
        write_json(self.root/retirement.INDEX,{'format':'picross-authoring-index-v1','entries':[]})
        imported=self.commit();self.migrate('none');main=self.commit()
        with self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],imported,source_commits={self.identifier:'f'*40})
        with self.assertRaisesRegex(ValueError,'original registered authoring'):retirement.retire(self.root,[self.identifier],imported)
        before=snapshot(self.root)
        retirement.retire(self.root,[self.identifier],imported,source_commits={self.identifier:source})
        value=load_json(self.root/self.entry['production']['package']/'manifest.json')
        self.assertEqual(value['provenance']['source_commit'],source)
        self.assertEqual(value['integrated_commit'],imported)
        self.assertEqual(value['provenance']['main_commit'],main)
        original=value['provenance']['background']
        self.assertEqual(original['provenance']['rights_status'],'resolved')
        self.assertEqual(original['origin']['export_manifest_sha256'],self.entry['production']['package_sha256'])
        for name,(raw,stamp) in before.items():
            if name.startswith(('game/','content/backgrounds/','content/reveals/')):
                self.assertEqual((raw,stamp),snapshot(self.root)[name])
        cr.check_checkout(self.root)

    def test_unrelated_file_reads_and_inventories_are_forbidden(self):
        # An indexed second ID with deliberately absent sources must not be read.
        value=load_json(self.root/cr.REGISTRY);runtime=load_json(self.root/cr.RUNTIME)
        other=deepcopy(value['entries'][0]);other['id']=other['key']='pz-unrelated';other['save_slot']='unrelated'
        other['definition']='data/content/unrelated.json';other['reveal']='art/content/unrelated.svg'
        other['production']['package']='content/packages/pz-unrelated/'+other['production']['revision']
        value['entries'].append(other);value['metadata'].append({'id':other['id'],'name':'Unrelated','category_id':other['category_id']})
        row=deepcopy(runtime['entries'][0]);row.update({k:other[k] for k in ('id','key','save_slot','definition','reveal')});row['name']='Unrelated';runtime['entries'].append(row)
        value['entries'].sort(key=lambda r:r['id']);value['metadata'].sort(key=lambda r:r['id']);runtime['entries'].sort(key=lambda r:r['id'])
        write_json(self.root/cr.REGISTRY,value);write_json(self.root/cr.RUNTIME,runtime)
        imported=self.commit();read=io._read;rglob=Path.rglob
        def trap(root,name,limit,**kw):
            self.assertNotIn('unrelated',str(Path(root)/name));return read(root,name,limit,**kw)
        def inventory(path,pattern):
            self.assertNotIn('unrelated',str(path));self.assertNotEqual(path,self.root/'content/packages');return rglob(path,pattern)
        with patch.object(io,'_read',side_effect=trap),patch.object(Path,'rglob',inventory):
            self.assertEqual(retirement.retire(self.root,[self.identifier],imported)['status'],'production_retired')

    def test_missing_rights_open_unindexed_staged_and_current_main_block(self):
        self.migrate();commit=self.commit();prefix=self.entry['production']['package']
        notice=self.root/prefix/'runtime'/Path(self.entry['reveal']).with_suffix('.txt')
        raw=notice.read_bytes();notice.unlink();before=snapshot(self.root)
        with self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],commit)
        self.assertEqual(before,snapshot(self.root));notice.write_bytes(raw)
        foreign=self.root/('content/authoring/'+self.identifier+'/open/file.txt');foreign.parent.mkdir(parents=True);foreign.write_text('open')
        before=snapshot(self.root)
        with self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],commit)
        self.assertEqual(before,snapshot(self.root));shutil.rmtree(foreign.parent)
        path=self.root/cr.RUNTIME;raw=path.read_bytes();path.write_bytes(raw+b' ');self.git('add',cr.RUNTIME);path.write_bytes(raw)
        with self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],commit)
        self.git('reset','-q','HEAD','--',cr.RUNTIME)
        (self.root/edit.LOCK).write_bytes(b'foreign lock')
        before=snapshot(self.root)
        with self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],commit)
        self.assertEqual(before,snapshot(self.root))

    def test_same_mtime_changes_and_partial_delete_are_not_hidden(self):
        self.migrate();commit=self.commit();original=retirement_scope.Reads.recheck;done=[]
        name=self.entry['production']['package']+'/approval.json';target=self.root/name;saved=target.read_bytes()
        def change(scope):
            if not done:
                done.append(True);stamp=target.stat();target.write_bytes(b' '+target.read_bytes()[1:])
                os.utime(target,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
            return original(scope)
        with patch.object(retirement_scope.Reads,'recheck',change),self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],commit)
        target.write_bytes(saved)
        # Restore exactly the fixture's own saved bytes before the independent failure case.
        before=snapshot(self.root);unlink=Path.unlink;deleted=[]
        def fail(path,*args,**kw):
            if path.is_relative_to(self.root/self.entry['production']['package']):
                if deleted:raise OSError('controlled second deletion failure')
                deleted.append(path)
            return unlink(path,*args,**kw)
        with patch.object(Path,'unlink',fail),self.assertRaisesRegex(ValueError,'remaining paths:'):
            retirement.retire(self.root,[self.identifier],commit)
        self.assertEqual(len(deleted),1);self.assertFalse(deleted[0].exists())
        with self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],commit)
        self.assertEqual(before[cr.REGISTRY],snapshot(self.root)[cr.REGISTRY])

    def test_editor_raster_v2_is_live_authority_and_not_compacted(self):
        self.migrate()
        request={'id':self.identifier,'metadata':None,'text':'1 1 1\n0 0 0','profile':'line','reveal':None,'background':None}
        edit.apply(self.root,edit.plan(self.root,request,work=self.root.parent))
        entry=load_json(self.root/cr.REGISTRY)['entries'][0]
        self.assertEqual(load_json(self.root/entry['production']['package']/'manifest.json')['format'],edit.RASTER)
        commit=self.commit();before=snapshot(self.root)
        with patch('tools.puzzle_production.verifier.verify',side_effect=AssertionError('proof replay')):
            self.assertEqual(retirement.retire(self.root,[self.identifier],commit)['status'],'no-op')
        self.assertEqual(before,snapshot(self.root))

    def test_unknown_main_and_global_identity_collision_block_all_ids(self):
        self.migrate();commit=self.commit();before=snapshot(self.root)
        for ids,source in (([self.identifier],'f'*40),([self.identifier,'pz-missing'],commit)):
            with self.assertRaises(ValueError):retirement.retire(self.root,ids,source)
            self.assertEqual(before,snapshot(self.root))
        value=load_json(self.root/cr.REGISTRY);other=deepcopy(value['entries'][0])
        other['id']=other['key']='pz-z-collision';value['entries'].append(other)
        value['metadata'].append({'id':other['id'],'name':'collision','category_id':other['category_id']})
        write_json(self.root/cr.REGISTRY,value);before=snapshot(self.root)
        with self.assertRaises(ValueError):retirement.retire(self.root,[self.identifier],commit)
        self.assertEqual(before,snapshot(self.root))
