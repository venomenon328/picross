"""Small geometry/navigation/mask regressions; old delivery is archived."""
import unittest
import copy
import tempfile
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET
from book_inventory.artwork import png_write
from book_inventory.production import OUT, layouts, verify_geometry, verify_navigation, verify_mask


class ProductionHelpers(unittest.TestCase):
    def test_fold_cannot_enter_working_page(self):
        case=copy.deepcopy(layouts()[0])
        case['rects']['fold'][0]=case['rects']['grid'][0]+100
        with self.assertRaises(AssertionError):
            verify_geometry(case)

    def test_720_status_must_stay_inside_page(self):
        case=copy.deepcopy(layouts()[-1])
        case['rects']['status'][0]+=60
        with self.assertRaises(AssertionError):
            verify_geometry(case)

    def test_navigation_cannot_overlay_clues(self):
        case=copy.deepcopy(layouts()[0])
        case['actions'][-1]['rect']=case['rects']['column_hints'][:]
        with self.assertRaises(AssertionError):
            verify_geometry(case)

    def test_actual_svg_must_name_correct_target(self):
        case=layouts()[0]
        root=ET.parse(OUT/'svg'/f'{case["name"]}-ui.svg').getroot()
        node=next(n for n in root.iter() if n.get('data-action')=='nav-information')
        node.set('data-target','album')
        with self.assertRaises(AssertionError):
            verify_navigation(root,case['actions'])

    def test_mask_must_not_protect_wrong_crop(self):
        # Exercise the mask oracle without requiring a historical 720p render.
        # The single white centre pixel is the only protected area.
        black = bytes([0, 0, 0])
        pixels = black * 4 + bytes([255, 255, 255]) + black * 4
        with tempfile.TemporaryDirectory(prefix='bp-mask-test-') as temporary:
            folder = Path(temporary)
            (folder / 'png').mkdir()
            png_write(folder / 'png/sample.png', (3, 3, 3, pixels))
            with patch('book_inventory.production.OUT', folder):
                verify_mask('sample', [[1, 1, 1, 1]])
                with self.assertRaises(AssertionError):
                    verify_mask('sample', [[0, 0, 3, 3]])


if __name__ == '__main__':
    unittest.main()
