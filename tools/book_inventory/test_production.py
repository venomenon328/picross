"""Check actual delivery, not a second set of manufactured examples."""
import unittest
from book_inventory.production import verify


class ProductionDelivery(unittest.TestCase):
    def test_committed_delivery(self):
        verify()


if __name__ == '__main__':
    unittest.main()
