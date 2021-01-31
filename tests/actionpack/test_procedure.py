from actionpack import Action
from actionpack import Procedure
from tests.actionpack import FakeAction

from collections.abc import Iterable
from oslash import Left
from oslash import Right
from unittest import TestCase


class ProcedureTest(TestCase):

    def assertIsIterable(self, x):
        return isinstance(x, Iterable)

    def setUp(self):
        success = FakeAction()
        failure = FakeAction(exception=Exception('something went wrong :/'))
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

    # TODO (withtwoemms) -- add concurrency tests

