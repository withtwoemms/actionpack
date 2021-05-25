from unittest import TestCase

from actionpack.utils import Closure
from actionpack.utils import pickleable
from actionpack.utils import tally


class UtilsTest(TestCase):

    def test_Closure_instantiation(self):
        closure = Closure(function, arg, kwarg=kwarg)
        args, kwargs = closure()
        self.assertIsInstance(args, tuple)
        self.assertEqual(args[0], arg)
        self.assertIsInstance(kwargs, dict)
        self.assertEqual(kwargs[kwarg], kwarg)

    def test_Closure_hashability(self):
        def another_function(*args, **kwargs):
            return args, kwargs
        self.assertEqual(another_function(*tuple(), **dict()), (tuple(), dict()))

        another_kwarg = 'another_kwarg'
        closure = Closure(function, arg, kwarg=kwarg)
        closure_duplicate = Closure(function, arg, kwarg=kwarg)
        extended_closure = Closure(function, arg, kwarg=kwarg, another_kwarg=another_kwarg)
        different_closure = Closure(another_function, 'different_arg', different_kwarg='different_kwarg')

        self.assertEqual(hash(closure), hash(closure_duplicate))
        self.assertNotEqual(hash(closure), hash(extended_closure))
        self.assertNotEqual(hash(closure), hash(different_closure))

    def test_Closure_repr_contains_params(self):
        closure = Closure(function, arg, kwarg=kwarg)
        self.assertIn(str(arg), repr(closure))
        self.assertIn(str(kwarg), repr(closure))

    def test_Closure_does_not_accept_lambdas(self):
        with self.assertRaises(Closure.LambdaNotAllowed):
            Closure(lambda: 'no good.', 'this', should='fail')

    def test_Closure_repr(self):
        closure = Closure(function, arg, kwarg=kwarg)
        self.assertIn(function.__name__, repr(closure))
        self.assertIn(str(arg), repr(closure))
        self.assertIn(str(kwarg), repr(closure))

    def test_tally(self):
        self.assertEqual(list(tally(0)), [])
        self.assertEqual(list(tally()), [1])
        self.assertEqual(list(tally(2)), [1, 1])

    def test_pickleable(self):
        self.assertTrue(pickleable(CanPickleMe()))
        self.assertFalse(pickleable(CannotPickleMe()))


class CanPickleMe:
    pass


class CannotPickleMe:
    def __init__(self):
        self.get_pickle_juice = lambda: 'here ya go'


def function(*args, **kwargs):
    return args, kwargs


arg = 'arg'
kwarg = 'kwarg'
