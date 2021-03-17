from actionpack import Action
from actionpack import KeyedProcedure
from actionpack import Procedure
from tests.actionpack import FakeAction

from collections.abc import Iterable
from oslash import Left
from oslash import Right
from unittest import TestCase


success = FakeAction(name='success')
failure = FakeAction(name='failure',
                     exception=Exception('something went wrong :/'))


class ProcedureTest(TestCase):

    def assertIsIterable(self, x):
        return isinstance(x, Iterable)

    def setUp(self):
        self.procedure = Procedure(success, failure)

    def test_Procedure_is_Iterable_of_Actions(self):
        self.assertIsIterable(self.procedure)
        self.assertIsInstance(next(self.procedure), FakeAction)
        self.assertIsInstance(next(self.procedure), FakeAction)
        self.assertIs(next(self.procedure), None)

    def test_Procedure_execution_yields_results(self):
        results = self.procedure.execute()

        self.assertIsIterable(results)
        self.assertIsInstance(next(results), Right)
        self.assertIsInstance(next(results), Left)

    def test_Procedure_execution_can_raise(self):
        results = self.procedure.execute(should_raise=True)

        self.assertIsIterable(results)
        self.assertIsInstance(next(results), Right)
        with self.assertRaises(Exception):
            next(results)

    def test_can_validate_Procedure(self):
        with self.assertRaises(Procedure.NotAnAction):
            Procedure('wut.', failure).validate()

    # TODO (withtwoemms) -- add concurrency tests


class KeyedProcedureTest(TestCase):

    def test_can_create_KeyedProcedure(self):
        results = KeyedProcedure(success, failure).execute()
        results_dict = dict(results)

        self.assertIsInstance(results_dict[success.name], Right)

    def test_can_validate_KeyedProcedure(self):
        with self.assertRaises(KeyedProcedure.UnnamedAction):
            KeyedProcedure(FakeAction(), failure)

