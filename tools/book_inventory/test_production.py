"""Check actual delivery, not a second set of manufactured examples."""
import unittest
import copy
import xml.etree.ElementTree as ET
from book_inventory.production import OUT, layouts, verify, verify_geometry, verify_navigation, verify_mask


class ProductionDelivery(unittest.TestCase):
    def test_committed_delivery(self):
        verify()

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
        with self.assertRaises(AssertionError):
            verify_mask('f02-1280-crop',[[0,0,1280,720]])


if __name__ == '__main__':
    unittest.main()
