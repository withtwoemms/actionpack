from actionpack.utils import tally

from unittest import TestCase


class UtilsTest(TestCase):

    def test_tally(self):
        self.assertEqual(list(tally(0)), [])
        self.assertEqual(list(tally()), [1])
        self.assertEqual(list(tally(2)), [1, 1])

