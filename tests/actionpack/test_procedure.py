from collections.abc import Iterable
from textwrap import dedent
from unittest import TestCase

from actionpack import KeyedProcedure
from actionpack import Procedure
from actionpack.action import Result
from tests.actionpack import FakeAction
from tests.actionpack import FakeFile
from tests.actionpack.actions import FakeWrite


def raise_failure():
    raise Exception('something went wrong :/')


success = FakeAction(name='success')
failure = FakeAction(
    name='failure',
    instruction_provider=raise_failure
)


def assertIsIterable(possible_collection):
    return isinstance(possible_collection, Iterable)


class ProcedureTest(TestCase):

    def setUp(self):
        self.procedure = Procedure((success, failure))

    def test_cannot_instantiate_without_Actions(self):
        with self.assertRaises(TypeError):
            Procedure(actions=FakeAction())
            Procedure(actions=None)

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
        self.procedure.validate()
        with self.assertRaises(Procedure.NotAnAction):
            Procedure(('wut.', failure)).validate()

    def test_Procedure_can_handle_being_given_no_Actions(self):
        empty_sync_results = list(Procedure(actions=list()).execute(synchronously=True))
        self.assertFalse(empty_sync_results)
        empty_async_results = list(Procedure(actions=list()).execute(synchronously=False))
        self.assertFalse(empty_async_results)

    def test_Procedure_has_readable_representation(self):
        expected_short_result = dedent("""
        Procedure for performing the following Actions:
          * <FakeAction|name="success">
          * <FakeAction|name="failure">""")
        self.assertEqual(repr(self.procedure), expected_short_result)
        procedure = Procedure([success] * 5)
        expected_result = dedent("""
        Procedure for performing the following Actions:
          * <FakeAction|name="success">
          * <FakeAction|name="success">
          * <FakeAction|name="success">
          * <FakeAction|name="success">
          * <FakeAction|name="success">""")
        self.assertEqual(repr(procedure), expected_result)
        longer_procedure = Procedure([success] * 6)
        expected_long_result = dedent("""
        Procedure for performing the following Actions:
          * <FakeAction|name="success">
          * <FakeAction|name="success">
          * <FakeAction|name="success">
          * <FakeAction|name="success">
          * <FakeAction|name="success">
          ...
        """)
        self.assertEqual(repr(longer_procedure), expected_long_result)

    def test_can_execute_Procedure_asynchronously(self):
        file = FakeFile()

        question = b' How are you?'
        wellwish = b' I hope you\'re well.'

        action1 = FakeWrite[str, int](file, question, delay=0.2)
        action2 = FakeWrite[str, int](file, wellwish, delay=0.1)

        procedure = Procedure[str, int]((action1, action2))
        results = procedure.execute(should_raise=True, synchronously=False)

        assertIsIterable(results)
        self.assertIsInstance(next(results), Result)
        self.assertIsInstance(next(results), Result)

        # NOTE: the wellwish precedes since the question took longer
        self.assertEqual(file.read(), wellwish + question)


class KeyedProcedureTest(TestCase):

    def test_cannot_instantiate_without_Actions(self):
        with self.assertRaises(TypeError):
            KeyedProcedure(actions=FakeAction())
            KeyedProcedure(actions=None)

    def test_can_handle_being_given_no_Actions(self):
        empty_sync_results = list(KeyedProcedure(actions=list()).execute(synchronously=True))
        self.assertFalse(empty_sync_results)
        empty_async_results = list(KeyedProcedure(actions=list()).execute(synchronously=False))
        self.assertFalse(empty_async_results)

    def test_can_create_KeyedProcedure(self):
        results = KeyedProcedure[str, str]((success, failure)).execute()
        results_dict = dict(results)

        self.assertIsInstance(results_dict[success.name], Result)

    def test_KeyedProcedure_execution_can_raise(self):
        results = KeyedProcedure((success, failure)).execute(should_raise=True)

        assertIsIterable(results)
        self.assertIsInstance(next(results), tuple)
        with self.assertRaises(Exception):
            next(results)

    def test_can_execute_asynchronously(self):
        results = KeyedProcedure((success, failure)).execute(synchronously=False)

        assertIsIterable(results)
        results = dict(results)
        self.assertIn('success', results.keys())
        self.assertIn('failure', results.keys())

    def test_can_create_KeyedProcedure_from_Actions_named_using_any_scriptable_type(self):
        action1 = FakeAction[int, str]()
        action2 = FakeAction[bool, str](instruction_provider=raise_failure)
        action3 = FakeAction[float, str]()

        key1, key2, key3 = 1, False, 1.01

        results = KeyedProcedure(
            (
                action1.set(name=key1),
                action2.set(name=key2),
                action3.set(name=key3)
            )
        ).execute()
        results_dict = dict(results)

        self.assertIsInstance(results_dict[key1].value, str)
        self.assertIsInstance(results_dict[key2].value, Exception)
        self.assertIsInstance(results_dict[key3].value, str)

    def test_can_validate_KeyedProcedure(self):
        with self.assertRaises(KeyedProcedure.UnnamedAction):
            KeyedProcedure((FakeAction(), failure)).validate()
        with self.assertRaises(KeyedProcedure.NotAnAction):
            KeyedProcedure[str, str]((success, 'not an action',)).validate()
        self.assertFalse(list(KeyedProcedure(actions=list()).validate()))
