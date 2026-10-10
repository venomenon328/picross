"""Standard-library-only package trust and integration checks."""
import hashlib
import copy
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

import p1_preflight
import vs1_delivery

ROOT=Path(__file__).resolve().parents[1]


class DeliveryTests(unittest.TestCase):
    def test_reference_drawing_digest_uses_frozen_bytes(self):
        # A real isolated Git object proves frozen bytes versus a changed
        # worktree, without requiring an archived project in shallow CI.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'prototypes/p1/ui/board.gd'
            path.parent.mkdir(parents=True)
            frozen = b'frozen renderer fixture\n'
            path.write_bytes(frozen)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root,
                                               stderr=subprocess.STDOUT)
            git('init')
            git('add', '.')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '-m', 'Frozen renderer')
            reference = git('rev-parse', 'HEAD').decode().strip()
            path.write_bytes(b'changed renderer fixture\n')
            digest = vs1_delivery.drawing_digest(root, 'ui/board.gd', reference)
            self.assertEqual(digest, hashlib.sha256(frozen).hexdigest())
            self.assertNotEqual(digest, vs1_delivery.drawing_digest(root, 'ui/board.gd', None))

    def test_gf1_pairs_reject_missing_cases_changed_fit_and_inconsistent_budget(self):
        plan=json.loads((ROOT/'examples/vs1/gf1-plan.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            renders=Path(tmp)
            reports={side:dict(variant=side,failures=0,records=[],pictures=[]) for side in ('before','after')}
            for c in plan['comparisons']:
                old=dict(c,cell_pitch=18.77 if c['ui_scale']==1 else 17.06,zoom_ceiling=18.77 if c['ui_scale']==1 else 17.06,
                         raw_fit_ceiling=18.779,font_px=19,own_cells_sha256='cells',history_sha256='history',
                         reserve_slots=[8,7],column_clues=[100,0,40,126],grid=[100,126,750,750])
                new=copy.deepcopy(old)
                used=5*26*c['ui_scale']
                new.update(reserve_slots=[13,7],minimum_reserve_slots=[8,7],horizontal_budget_px=200,
                           horizontal_used_px=used,grid_fit=True,axis_counts={'row':{'hidden_numbers':0}})
                new['grid'][0]+=used
                new['column_clues'][0]+=used
                for side,record in (('before',old),('after',new)):
                    name=f"gf1-{side}-{c['id']}-u{round(c['ui_scale']*100)}.png"
                    (renders/name).write_bytes(b'native image fixture')
                    reports[side]['records'].append(record)
                    reports[side]['pictures'].append(dict(file=name,sha256=hashlib.sha256(b'native image fixture').hexdigest()))
            def write(data):
                for side,report in data.items(): (renders/f'gf1-{side}.json').write_text(json.dumps(report),encoding='utf-8')
            write(reports)
            self.assertEqual(len(vs1_delivery.verify_gf1_pairs(renders)['pairs']),4)
            for field,value in [('cell_pitch',17),('font_px',15),('minimum_reserve_slots',[7,7]),('horizontal_budget_px',10),('horizontal_used_px',0),('grid',[100,126,750,750]),('column_clues',[100,1,40,126])]:
                changed=copy.deepcopy(reports)
                changed['after']['records'][0][field]=value
                write(changed)
                with self.subTest(field=field),self.assertRaises(p1_preflight.PreflightError): vs1_delivery.verify_gf1_pairs(renders)
            changed=copy.deepcopy(reports)
            changed['before']['records'][2]=copy.deepcopy(changed['before']['records'][0])
            changed['after']['records'][2]=copy.deepcopy(changed['after']['records'][0])
            write(changed)
            with self.assertRaises(p1_preflight.PreflightError): vs1_delivery.verify_gf1_pairs(renders)
            write(reports)
            (renders/reports['after']['pictures'][0]['file']).write_bytes(b'tampered')
            with self.assertRaises(p1_preflight.PreflightError): vs1_delivery.verify_gf1_pairs(renders)

    def test_capture_preserves_native_wrapper_and_uses_one_real_script(self):
        native=['godot','--path','project','--rendering-driver','opengl3','--script','res://tests/capture.gd','--','--p1-capture']
        for prefix in ([],['xvfb-run','-a']):
            command=vs1_delivery.capture_command(prefix+native)
            self.assertEqual(command[:len(prefix)+1],prefix+['godot'])
            self.assertEqual(command[command.index('--script')+1],'res://tests/vs1_capture.gd')
            self.assertEqual(command[command.index('--')+1:],['--p1-capture'])
            self.assertEqual(command.count('--script'),1)
        with self.assertRaises(p1_preflight.PreflightError):vs1_delivery.capture_command(['godot','--headless'])

    def test_zip_audit_checks_actual_bytes_and_excludes_review_payload(self):
        files={'picross-vs1.exe':hashlib.sha256(b'player').hexdigest(),'picross-vs1.console.exe':hashlib.sha256(b'console').hexdigest()}
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/'player.zip'
            for mutated,extra in [(False,False),(True,False),(False,True)]:
                with zipfile.ZipFile(archive,'w') as z:
                    z.writestr('picross-vs1.exe',b'tampered' if mutated else b'player')
                    z.writestr('picross-vs1.console.exe',b'console')
                    if extra:z.writestr('solution.png',b'spoiler')
                if mutated or extra:
                    with self.assertRaises(p1_preflight.PreflightError):vs1_delivery.audit(archive,files)
                else:vs1_delivery.audit(archive,files)

    def test_normal_identity_catalog_and_filters_remain_separate(self):
        project=(ROOT/'prototypes/p1/project.godot').read_text(encoding='utf-8')
        preset=(ROOT/'prototypes/p1/export_presets.cfg').read_text(encoding='utf-8')
        self.assertIn('run/main_scene="res://main.tscn"',project)
        self.assertIn('config/name="picross · P1"',project)
        self.assertIn('exclude_filter="tests/*,data/*proof*,study/*,full_view_study/*"',preset)
        harness=(ROOT/'tools/p1_product.py').read_text(encoding='utf-8')
        # The archived study stays separate from the current CI product path.
        for operation in ('capture','export','package'):
            self.assertNotIn('vs1_delivery.'+operation+'(',harness)


if __name__=='__main__':unittest.main()
