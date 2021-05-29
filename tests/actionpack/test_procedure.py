from collections.abc import Iterable
from unittest import TestCase

from actionpack import KeyedProcedure
from actionpack import Procedure
from actionpack.action import Result
from tests.actionpack import FakeAction
from tests.actionpack import FakeFile
from tests.actionpack.actions import FakeWriteBytes


success = FakeAction(name='success')
failure = FakeAction(name='failure',
                     exception=Exception('something went wrong :/'))


def assertIsIterable(possible_collection):
    return isinstance(possible_collection, Iterable)


class ProcedureTest(TestCase):

    def setUp(self):
        self.procedure = Procedure(success, failure)

    def test_Procedure_is_Iterable_of_Actions(self):
        assertIsIterable(self.procedure)
        self.assertIsInstance(next(self.procedure), FakeAction)
        self.assertIsInstance(next(self.procedure), FakeAction)
        self.assertIs(next(self.procedure), None)

    def test_Procedure_execution_yields_results(self):
        results = self.procedure.execute()

        assertIsIterable(results)
        self.assertIsInstance(next(results), Result)
        self.assertIsInstance(next(results), Result)

    def test_Procedure_execution_can_raise(self):
        results = self.procedure.execute(should_raise=True)

        assertIsIterable(results)
        self.assertIsInstance(next(results), Result)
        with self.assertRaises(Exception):
            next(results)

    def test_can_validate_Procedure(self):
        with self.assertRaises(Procedure.NotAnAction):
            Procedure('wut.', failure).validate()

    def test_can_execute_Procedure_asynchronously(self):
        file = FakeFile(mode='w')

        question = b' How are you?'
        wellwish = b' I hope you\'re well.'

        action1 = FakeWriteBytes[str, int](file, question, delay=0.2)
        action2 = FakeWriteBytes[str, int](file, wellwish, delay=0.1)

        procedure = Procedure[str, int](*[action1, action2])
        results = procedure.execute(should_raise=True, synchronously=False)

        assertIsIterable(results)
        self.assertIsInstance(next(results), Result)
        self.assertIsInstance(next(results), Result)

        # NOTE: the wellwish precedes since the question took longer
        self.assertEqual(file.read(), wellwish + question)


class KeyedProcedureTest(TestCase):

    def test_can_create_KeyedProcedure(self):
        results = KeyedProcedure[str, str](success, failure).execute()
        results_dict = dict(results)

        self.assertIsInstance(results_dict[success.name], Result)

    def test_KeyedProcedure_execution_can_raise(self):
        results = KeyedProcedure(success, failure).execute(should_raise=True)

        assertIsIterable(results)
        self.assertIsInstance(next(results), tuple)
        with self.assertRaises(Exception):
            next(results)

    def test_can_create_KeyedProcedure_from_Actions_named_using_any_scriptable_type(self):
        action1 = FakeAction[int, str]()
        action2 = FakeAction[bool, str](exception=Exception())
        action3 = FakeAction[float, str]()

        key1, key2, key3 = 1, False, 1.01

        results = KeyedProcedure(
            action1.set(name=key1),
            action2.set(name=key2),
            action3.set(name=key3)
        ).execute()
        results_dict = dict(results)

        self.assertIsInstance(results_dict[key1].value, str)
        self.assertIsInstance(results_dict[key2].value, Exception)
        self.assertIsInstance(results_dict[key3].value, str)

    def test_can_validate_KeyedProcedure(self):
        with self.assertRaises(KeyedProcedure.UnnamedAction):
            KeyedProcedure(FakeAction(), failure)
