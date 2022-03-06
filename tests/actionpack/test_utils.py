from datetime import datetime
from unittest import TestCase

from actionpack.utils import Closure
from actionpack.utils import first
from actionpack.utils import last
from actionpack.utils import microsecond_timestamp
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
        value = 'no good.'
        function = lambda: value
        self.assertEqual(function(), value)
        with self.assertRaises(Closure.LambdaNotAllowed):
            Closure(function, 'this', should='fail')

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
        self.assertEqual(CannotPickleMe().get_pickle_juice(), CannotPickleMe.juice)
        self.assertTrue(pickleable(CanPickleMe()))
        self.assertFalse(pickleable(CannotPickleMe()))

    def test_microsecond_timestamp(self):
        epoch = datetime(1970, 1, 1, 0, 0)  # 0 seconds since Epoch
        self.assertEqual(microsecond_timestamp(lambda: epoch), 0)

    def test_first(self):
        letters = list('abc')
        self.assertEqual(first(letters), 'a')

    def test_last(self):
        letters = list('abc')
        self.assertEqual(last(letters), 'c')


class CanPickleMe:
    pass


class CannotPickleMe:
    juice = 'here ya go'

    def __init__(self):
        self.get_pickle_juice = lambda: self.juice


def function(*args, **kwargs):
    return args, kwargs


arg = 'arg'
kwarg = 'kwarg'
