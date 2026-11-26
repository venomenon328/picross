"""PE-APP-A regressions using the existing PW state machine and API fixtures."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from tools.app_products import PW, PE
from tools.production_workspace import payload, release_channel as channel, update_verifier as verifier
from tools.production_workspace.release import release
from tools.production_workspace.update_diagnostic import test_identity
from tools import test_production_installer as fixtures
from tools.production_workspace.build_installer import NS, wix_source

class EditorInstallerTests(unittest.TestCase):
    def test_product_signatures_assets_and_versions(self):
        for app in (PW, PE):
            with self.subTest(app=app.key), tempfile.TemporaryDirectory() as folder:
                self.root=Path(folder); self.api=fixtures.MemoryGitHub(app=app)
                self.trust,self.secret=test_identity(app=app)
                planned,manifest=fixtures.AppReleaseTests.candidate(self,app=app)
                files={n:(self.root/n).read_bytes() for n in manifest['assets']}
                raw,sig=verifier._sign(manifest,files,self.secret,self.trust,app=app)
                candidate=verifier._verify(raw,sig,files,self.trust,app=app)
                self.assertEqual(verifier.assess_update(candidate,app.anchor,app=app),'update')
                self.assertEqual(verifier.assess_update(candidate,candidate.version,candidate.binding,app=app),'noop')
                for version,binding in ((candidate.version,None),(candidate.version,'a'*64),(app.anchor[:-1]+'2',None)):
                    with self.assertRaises(ValueError): verifier.assess_update(candidate,version,binding,app=app)
                other=PE if app==PW else PW
                with self.assertRaises(ValueError): verifier._verify(raw,sig,files,self.trust,app=other)
                for name in files:
                    with self.assertRaises(ValueError): verifier._verify(raw,sig,{**files,name:files[name]+b'x'},self.trust,app=app)
                bad={**manifest,'product_code':release(app=other)['product_code']}
                with self.assertRaises(ValueError): verifier._sign(bad,files,self.secret,self.trust,app=app)
                with self.assertRaises(ValueError): verifier.verify_candidate(raw,sig,files,app=app)

    def test_pe_release_recovery_noop_and_source_gates(self):
        with tempfile.TemporaryDirectory() as folder:
            self.root=Path(folder);self.api=fixtures.MemoryGitHub(app=PE)
            self.trust,self.secret=test_identity(app=PE)
            plan,manifest=fixtures.AppReleaseTests.candidate(self,app=PE)
            def publish(): return channel.publish(self.api,self.root,plan,enabled=True,signing_enabled=True,secret=self.secret,app=PE)
            with patch.object(verifier,'production_trust',return_value=self.trust):
                self.api.fail_upload='START.txt'
                with self.assertRaises(RuntimeError): publish()
                self.assertTrue(self.api.entries[0]['draft'])
                publish();self.assertEqual(len(self.api.entries),1)
                previous=channel.authority(self.api,app=PE)
                self.assertIsNone(channel.next_version({'sha256':plan['payload_fingerprint']},previous,app=PE))
                self.assertEqual(channel.next_version({'sha256':'new'},previous,app=PE),'0.2.2')
                self.assertIsNone(channel.authority(self.api,app=PW))
                with self.assertRaises(ValueError): publish()
                self.api.entries=[];self.api.tags={};self.api.blobs={}
                for key,value in [('event','pull_request'),('event','workflow_dispatch'),('conclusion','failure'),('head_branch','feature')]:
                    before=self.api.run[key];self.api.run[key]=value
                    with self.assertRaises(ValueError): publish()
                    self.api.run[key]=before
                with self.assertRaises(ValueError): channel.authorize(self.api,self.root,{**plan,'diagnostic':True},enabled=True,signing_enabled=True,app=PE)
                with self.assertRaises(ValueError): channel.authorize(self.api,self.root,plan,enabled=False,signing_enabled=True,app=PE)
                self.assertEqual(self.api.entries,[])
                self.api.change_main_after_upload=True
                with self.assertRaises(ValueError): publish()
                self.assertTrue(self.api.entries[0]['draft'])

    def test_inputs_and_actual_analysis(self):
        for name in ['tools/puzzle_editor/README.md','tools/puzzle_editor/ui/app.js','tools/puzzle_production/editor_change.py',
                     'tools/puzzle_production/current_content.py','tools/puzzle_production/sd2_method_0_4.json',
                     'game/book/paper.png','game/art/drawing/margins/water.png','tools/production_workspace/packaging/Guard.cs']:
            self.assertTrue(payload.selected(name,app=PE),name)
        for name in ['content/puzzles/pz-test.json','game/art/backgrounds/pz-test.png','game/data/content/pz-test.json',
                     'game/ui/root.gd','docs/tools/PUZZLE_EDITOR.md','tools/puzzle_production/za1_fixtures.py']:
            self.assertFalse(payload.selected(name,app=PE),name)
        with self.assertRaises(ValueError): payload.selected('tools/puzzle_editor/unknown.dat',app=PE)
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def git(*args): return subprocess.check_output(['git','-C',str(root),*args])
            git('init','-q');git('config','core.autocrlf','false')
            entry=root/'tools/puzzle_editor/desktop_entry.py';entry.parent.mkdir(parents=True);entry.write_bytes(b'# entry')
            git('add','.');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','first')
            first=payload.fingerprint(root,app=PE)
            work_refs=root/'tools/work_refs.py';work_refs.write_bytes(b'REPOSITORY = "test/example"\n')
            git('add','.');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','reader dependency')
            reader_inputs=payload.fingerprint(root,app=PE)
            self.assertNotEqual(first['sha256'],reader_inputs['sha256'])
            self.assertIn('tools/work_refs.py',{row['file'] for row in reader_inputs['files']})
            toc=root/'analysis.toc';toc.write_text(repr([str(entry),str(work_refs)]),encoding='utf-8')
            payload.audit_analysis(root,toc,reader_inputs,[],app=PE)
            work_refs.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'differs from committed input'):
                payload.audit_analysis(root,toc,reader_inputs,[],app=PE)
            work_refs.write_bytes(b'REPOSITORY = "test/example"\n')
            entry.rename(entry.with_name('renamed.py'));git('add','-A');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','rename')
            self.assertNotEqual(reader_inputs['sha256'],payload.fingerprint(root,app=PE)['sha256'])
            entry.write_bytes(b'# entry');toc.write_text(repr([str(entry)]),encoding='utf-8')
            payload.audit_analysis(root,toc,first,[],app=PE)
            foreign=root/'tests/foreign.py';foreign.parent.mkdir();foreign.write_bytes(b'bad')
            toc.write_text(repr([str(entry),str(foreign)]),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'absent from fingerprint'): payload.audit_analysis(root,toc,first,[],app=PE)

    def test_pe_msi_and_workflow_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            image=Path(folder);(image/(PE.executable+'.exe')).write_bytes(b'test')
            value=wix_source(image,release(version='0.2.1',app=PE),image/'Guard.exe',app=PE)
            text=__import__('xml.etree.ElementTree',fromlist=['tostring']).tostring(value.getroot()).decode()
            self.assertIn('Programs\\PicrossPuzzleEditor',text);self.assertNotIn('PicrossProductionWorkspace',text)
            self.assertNotEqual(release(app=PW)['upgrade_code'],release(app=PE)['upgrade_code'])
        root=Path(__file__).resolve().parents[1]
        workflow=(root/'.github/workflows/pe-installer.yml').read_text(encoding='utf-8')
        self.assertEqual(workflow.count('contents: write'),1);self.assertEqual(workflow.count('environment: pe-app-release'),1)
        self.assertNotIn('secrets.',workflow.split('  publish:')[0]);self.assertNotIn('PW_',workflow)
        self.assertIn("vars.PE_UPDATE_SIGNING_ENABLED == 'true'",workflow)
        self.assertIn("github.event_name == 'workflow_run' && github.ref == 'refs/heads/main'",workflow)

    def test_icon_binding_is_product_specific(self):
        for app, other, path in ((PE, PW, 'assets/editor.ico'), (PW, PE, 'assets/launcher.ico')):
            with self.subTest(app=app.key), tempfile.TemporaryDirectory() as folder:
                image = Path(folder)
                icon_path = app.package + '/' + path
                self.assertTrue(payload.selected(icon_path, app=app))
                self.assertFalse(payload.selected(icon_path, app=other))
                tree = wix_source(image, release(app=app), image / 'Guard.exe', app=app)
                ns = {'w': NS}
                icon = tree.find('.//w:Icon[@Id="AppIcon"]', ns)
                self.assertEqual(Path(icon.get('SourceFile')), app.source / path)
                self.assertTrue(Path(icon.get('SourceFile')).is_file())
                self.assertEqual(tree.find('.//w:Property[@Id="ARPPRODUCTICON"]', ns).get('Value'), 'AppIcon')
                self.assertEqual([link.get('Icon') for link in tree.findall('.//w:Shortcut', ns)], ['AppIcon', 'AppIcon'])

    @unittest.skipUnless(os.name=='nt','Windows liveness event')
    def test_pe_product_wide_liveness(self):
        from tools.production_workspace.install_interlock import InstallInterlock
        a,b=InstallInterlock(app=PE),InstallInterlock(app=PE)
        try:
            a.acquire();b.acquire();self.assertTrue(a.handle and b.handle)
            a.close();self.assertTrue(b.handle);self.assertNotEqual(PE.marker,PW.marker)
        finally: a.close();b.close()
