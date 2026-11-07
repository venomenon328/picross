"""Cheap isolation and corruption controls for EA imported inputs."""
import shutil
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ea_product import copy_imported_base
from native_results import bind_files, validate_completion_cases
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


def completion_report():
    rows = []
    for w,h,u,columns,lines,count in [(1280,720,1.25,5,5,1),(1920,1080,1.,40,40,4),
            (2560,1440,1.25,50,30,8),(1600,900,1.,50,30,8),(1280,720,1.25,50,50,4)]:
        colors = ['343f42','edca78','bd604a','6c9aab','7c589e','529574','e28a45','b35280'][:count]
        palette = [dict(id=i+1,color='#'+c) for i,c in enumerate(colors)]
        cells = [0,-1]+list(range(1,count+1))+[-1]*(columns*lines-count-2)
        samples = [dict(value=v,actual=[int(colors[v-1][i:i+2],16)/255 for i in (0,2,4)] if v>0 else [1,1,1],paper=[1,1,1]) for v in set(cells)]
        rows.append(dict(window=[w,h,u],width=columns,height=lines,palette=palette,cells=cells,
            samples=samples,gated=True,initial_image=True,retained=True,reentry_image=True,unchanged=True,
            selections=[False,True,False,True],state_before='a'*64,state_after='a'*64,
            slots_before={'test.json':'b'*64},slots_after={'test.json':'b'*64},line_pixels=[.2]*8,
            control='single-rectangular-toggle',hatch_count=28,hatch_pixels=[100,200],slider_positions=[87.5,128.5,87.5,128.5],
            area=[10,10,columns*10,lines*10],raster=[10,10,columns*10,lines*10],step=10,lod='small',
            fill_count=count,line_count=columns+lines+2))
    return dict(ar_measurements=rows)


class CompletionReader(unittest.TestCase):
    def test_current_original_protocol(self):
        validate_completion_cases(completion_report())

    def test_corrupt_state_color_and_geometry_are_rejected(self):
        changes = [lambda r:r.pop(),lambda r:r[0].update(gated=False),
            lambda r:r[0]['samples'][0].update(actual=[0,0,0]),
            lambda r:r[0]['palette'][0].update(color='#ffffff'),
            lambda r:r[0].update(state_after='c'*64),
            lambda r:r[0]['slots_after'].update({'test.json':'c'*64}),
            lambda r:r[0].update(line_pixels=[0]*8),
            lambda r:r[0].update(control='two-buttons'),
            lambda r:r[0].update(hatch_pixels=[100,0]),
            lambda r:r[0].update(slider_positions=[87.5]*4),
            lambda r:r[0].update(raster=[10,10,10,10]),
            lambda r:r[0].update(selections=[True]*4)]
        for change in changes:
            report = copy.deepcopy(completion_report())
            change(report['ar_measurements'])
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_completion_cases(report)
