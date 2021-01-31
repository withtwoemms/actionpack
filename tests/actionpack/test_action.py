from actionpack import Action
from tests.actionpack import FakeAction

from oslash import Left
from oslash import Right
from unittest import TestCase


class ActionTest(TestCase):

    def test_Action_produces_Right_result_when_performed(self):
        result = FakeAction().perform()
        self.assertIsInstance(result, Right)
        self.assertEqual(result.value, FakeAction.result)

    def test_Action_produces_Left_if_exception_raised_when_performed(self):
        exception = Exception('something went wrong :/')
        result = FakeAction(exception=exception).perform()
        self.assertIsInstance(result, Left)
        self.assertEqual(result.value, exception)

