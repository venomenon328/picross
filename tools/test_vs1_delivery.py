"""Standard-library-only package trust and integration checks."""
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

import p1_preflight
import vs1_delivery

ROOT=Path(__file__).resolve().parents[1]


class DeliveryTests(unittest.TestCase):
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
        for operation in ('capture','export','package'): self.assertIn('vs1_delivery.'+operation+'(',harness)


if __name__=='__main__':unittest.main()
