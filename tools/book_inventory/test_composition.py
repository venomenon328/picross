"""BP-3 actual delivery plus focused corruption tests; no renderer required."""
import copy
import unittest
import xml.etree.ElementTree as ET
from book_inventory import composition as c


class CompositionDelivery(unittest.TestCase):
    def test_delivery(self):
        c.verify()

    def content(self):
        g=c.p.read('layout.json')['cases'][0]
        return g,ET.parse(c.OUT/'svg'/f'{g["name"]}-content.svg').getroot()

    def test_reject_changed_clue(self):
        g,root=self.content()
        root.find('.//s:text[@data-clue]',c.p.NS).text='999'
        with self.assertRaises(AssertionError):c.verify_data(root,g)

    def test_reject_solution_instead_of_own_miniature(self):
        g,root=self.content()
        mini=root.find('.//s:g[@id="miniature"]',c.p.NS)
        cell=next(v for v in mini.iter() if v.get('data-cell'))
        cell.set('data-cell','0,0,4')
        with self.assertRaises(AssertionError):c.verify_data(root,g)

    def test_reject_shifted_hit_and_wrong_navigation(self):
        g,root=self.content()
        bad=copy.deepcopy(root)
        bad.find('.//s:rect[@data-hit="true"]',c.p.NS).set('x','0')
        with self.assertRaises(AssertionError):c.verify_actions(bad,g)
        root.find('.//s:g[@data-action="nav-information"]',c.p.NS).set('data-target','album')
        with self.assertRaises(AssertionError):c.verify_actions(root,g)

    def test_reject_wrong_layer_pixels_and_alpha(self):
        clear=(1,1,4,bytes([0,0,0,0]))
        white=(1,1,4,bytes([255,255,255,255]))
        c.verify_layer_pixels(clear,white,white)
        for broken in (clear,(1,1,4,bytes([200,255,255,255]))):
            with self.assertRaises(AssertionError):c.verify_layer_pixels(clear,white,broken)

    def test_actual_substrate_minimum_not_average(self):
        record={'file':'synthetic','texts':[{'text':'Test','clue':False,'fill':'rgb(41, 62, 61)','box':[0,0,2,1]}]}
        bg=(2,1,3,bytes([255,250,240,41,62,61]))
        with self.assertRaises(AssertionError):c.contrast(bg,record)


if __name__=='__main__':unittest.main()
