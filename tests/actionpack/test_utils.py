from actionpack.utils import tally
from actionpack.utils import pickleable

from unittest import TestCase


class UtilsTest(TestCase):

    def test_tally(self):
        self.assertEqual(list(tally(0)), [])
        self.assertEqual(list(tally()), [1])
        self.assertEqual(list(tally(2)), [1, 1])

    def test_pickleable(self):
        self.assertTrue(pickleable(CanPickleMe()))
        self.assertFalse(pickleable(CannotPickleMe()))


class CanPickleMe: pass


class CannotPickleMe:
    def __init__(self):
        self.get_pickle_juice = lambda: 'here ya go'

