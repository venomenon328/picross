"""Cheap isolation and corruption controls for EA imported inputs."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ea_product import copy_imported_base
from native_results import bind_files
from p1_preflight import PreflightError


class ImportedInputs(unittest.TestCase):
    def test_copy_preserves_imports_without_sharing_writable_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / 'base'
            (base / '.godot/imported').mkdir(parents=True)
            (base / '.godot/imported/fixture.ctex').write_bytes(b'imported texture')
            (base / 'project.godot').write_bytes(b'project')
            inventory, report = copy_imported_base(base, root / 'copy')
            self.assertEqual(bind_files(root / 'copy'), inventory)
            self.assertEqual(report['files'], 2)
            (root / 'copy/.godot/imported/fixture.ctex').write_bytes(b'changed')
            self.assertEqual(bind_files(base), inventory)

    def test_corrupt_import_copy_is_rejected_before_native_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / 'base'
            base.mkdir()
            (base / 'project.godot').write_bytes(b'project')
            original_copy = shutil.copytree
            def corrupt(source, destination):
                original_copy(source, destination)
                (destination / 'project.godot').write_bytes(b'corrupt')
            with patch('ea_product.shutil.copytree', side_effect=corrupt):
                with self.assertRaisesRegex(PreflightError, 'base copy differs'):
                    copy_imported_base(base, root / 'copy')
