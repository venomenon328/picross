"""Cheap failure/isolation controls for the ZA-1 preparation snapshot."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_results import bind_files
from p1_preflight import PreflightError
from za1_product import prepare_imports, require_inventory


class ImportedInputs(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.base = self.root / 'base'
        (self.base / '.godot/imported').mkdir(parents=True)
        (self.base / '.godot/imported/fixture.ctex').write_bytes(b'imported texture')
        (self.base / 'project.godot').write_bytes(b'project')
        self.copy = self.root / 'za1-checkout/game'

    def test_snapshot_has_no_shared_writable_files(self):
        inventory, report = prepare_imports(self.base, self.root)
        self.assertEqual(bind_files(self.copy), inventory)
        self.assertEqual(report['files'], 2)
        # Later RP6 writes cannot change the pending ZA-1 snapshot or vice versa.
        (self.base / '.godot/imported/fixture.ctex').write_bytes(b'later base cache')
        require_inventory(self.copy, inventory)
        (self.copy / 'project.godot').write_bytes(b'ZA-1 registration')
        self.assertEqual((self.base / 'project.godot').read_bytes(), b'project')

    def test_copy_corruption_or_source_race_is_rejected(self):
        original = shutil.copytree
        for target in ('copy', 'source'):
            with self.subTest(target=target):
                destination = self.root / target
                def corrupt(source, copy, *args, **kwargs):
                    original(source, copy, *args, **kwargs)
                    if Path(source) == self.base:
                        ((copy if target == 'copy' else source) / 'project.godot').write_bytes(b'corrupt')
                with patch('za1_product.shutil.copytree', side_effect=corrupt):
                    with self.assertRaisesRegex(PreflightError, 'inventory differs'):
                        prepare_imports(self.base, destination)

    def test_pending_snapshot_changes_are_rejected_before_registration(self):
        inventory, _ = prepare_imports(self.base, self.root)
        original = self.copy / 'project.godot'
        for mutation in ('same-size-bytes', 'missing', 'extra'):
            with self.subTest(mutation=mutation):
                original.write_bytes(b'project')
                if mutation == 'same-size-bytes':
                    original.write_bytes(b'changed')
                elif mutation == 'missing':
                    original.unlink()
                else:
                    (self.copy / 'unexpected').write_bytes(b'extra')
                with self.assertRaisesRegex(PreflightError, 'inventory differs'):
                    require_inventory(self.copy, inventory)
