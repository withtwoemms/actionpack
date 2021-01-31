from actionpack import Action

from oslash import Left
from oslash import Right
from unittest import TestCase


class ActionTest(TestCase):

    class FakeAction(Action):

        result = f'Performing Action.'

        def __init__(self, exception=None):
            self.exception = exception
            self.instruction = lambda: self.result

        def validate(self):
            if self.exception:
                raise self.exception
            return super().validate()

    def test_Action_produces_Right_result_when_performed(self):
        result = self.FakeAction().perform()
        self.assertIsInstance(result, Right)
        self.assertEqual(result._value, self.FakeAction.result)

    def test_Action_produces_Left_if_exception_raised_when_performed(self):
        exception = Exception('something went wrong :/')
        result = self.FakeAction(exception=exception).perform()
        self.assertIsInstance(result, Left)
        self.assertEqual(result._error, exception)

