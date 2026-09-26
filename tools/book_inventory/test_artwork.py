"""BP-2 delivery and independent pixel/transform examples."""
import unittest
from book_inventory.artwork import montage, resample, verify


class ArtworkDelivery(unittest.TestCase):
    def test_delivered_artwork(self):
        verify()

    def test_source_over_keeps_transparent_and_opaque_ui(self):
        bg = (3, 1, 3, bytes([20, 40, 60]*3))
        ui = (3, 1, 4, bytes([200, 100, 0, 0, 200, 100, 0, 255, 200, 100, 0, 128]))
        self.assertEqual(montage(bg, ui)[3], bytes([20, 40, 60, 200, 100, 0, 110, 70, 30]))

    def test_proportional_half_size_uses_pixel_centres(self):
        source = (2, 2, 3, bytes([0, 0, 0, 40, 40, 40, 80, 80, 80, 120, 120, 120]))
        self.assertEqual(resample(source, (1, 1)), (1, 1, 3, bytes([60]*3)))

    def test_rejects_stretch_and_ui_resize(self):
        with self.assertRaises(AssertionError):
            resample((2, 2, 3, bytes(12)), (2, 1))
        with self.assertRaises(AssertionError):
            montage((2, 2, 3, bytes(12)), (1, 1, 4, bytes(4)))
