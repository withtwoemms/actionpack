from actionpack.utils import Closure
from actionpack.utils import pickleable
from actionpack.utils import tally

from unittest import TestCase


class UtilsTest(TestCase):

    def test_Closure(self):
        def function(*args, **kwargs):
            return args, kwargs

        arg = 'arg1'
        kwarg = 'kwarg1'
        closure = Closure(function, arg, kwarg1=kwarg)
        args, kwargs = closure()
        self.assertIsInstance(args, tuple)
        self.assertEqual(args[0], arg)
        self.assertIsInstance(kwargs, dict)
        self.assertEqual(kwargs[kwarg], kwarg)

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

