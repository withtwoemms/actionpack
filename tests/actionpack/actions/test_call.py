import pickle

from unittest import TestCase

from actionpack.action import Result
from actionpack.actions import Call
from actionpack.utils import Closure
from actionpack.utils import pickleable


class CallTest(TestCase):

    @classmethod
    def function(*args, **kwargs) -> tuple:
        return args[1:], kwargs

    def setUp(self):
        self.arg = 'arg'
        self.kwarg = 'kwarg'
        self.closure = Closure(self.function, self.arg, kwarg=self.kwarg)
        self.action = Call(closure=self.closure)

    def test_can_Call(self):
        result = self.action.perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, ((self.arg,), {self.kwarg: self.kwarg}))

    def test_Call_instantiation_accepts_only_Closure_objects(self):
        result = Call('not a closure').perform()
        self.assertFalse(result.successful)
        self.assertIsInstance(result.value, TypeError)

    def test_Call_can_handle_Closures_with_iterator_args(self):
        iterable = [1, 1, 1]
        closure = Closure(sum, iter(iterable))
        call = Call(closure)
        result = call.perform()
        new_result = call.perform()
        self.assertTrue(result.successful)
        self.assertEqual(sum(iterable), result.value)
        self.assertEqual(0, new_result.value)  # since iterable exhausted

    def test_serializes_as_expected(self):
        self.assertEqual(repr(self.action), '<Call(function)>')

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
