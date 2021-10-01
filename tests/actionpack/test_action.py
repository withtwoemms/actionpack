import pickle

from functools import reduce
from threading import Thread
from unittest import TestCase

from actionpack import Action
from actionpack.action import Result
from actionpack.utils import pickleable
from tests.actionpack import FakeAction
from tests.actionpack import FakeFile
from tests.actionpack.actions import FakeWriteBytes


class ActionTest(TestCase):

    def setUp(self) -> None:
        self.exception = Exception('something went wrong :/')

    def test_Action_produces_Result_result_when_performed(self):
        result = FakeAction().perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, FakeAction.result)

    def test_Action_produces_Result_if_exception_raised_when_performed(self):
        result = FakeAction(exception=self.exception).perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, self.exception)

    def test_Action_can_raise_exception(self):
        with self.assertRaises(type(self.exception)):
            FakeAction(exception=self.exception).perform(should_raise=True)

    def test_can_determine_if_Result_was_successful(self):
        success = FakeAction().perform()
        failure = FakeAction(exception=self.exception).perform()

        self.assertTrue(success.successful)
        self.assertFalse(failure.successful)

    def test_Result_success_is_immutable(self):
        success = FakeAction().perform()
        failure = FakeAction(exception=self.exception).perform()

        with self.assertRaises(AttributeError):
            success.successful = 'nah.'

        with self.assertRaises(AttributeError):
            failure.successful = 'maybe?'

    def test_Action_can_be_serialized(self):
        action = FakeAction()
        pickled = pickle.dumps(action)
        unpickled = pickle.loads(pickled)

        self.assertEqual(pickleable(action), pickled)
        self.assertEqual(unpickled.result, action.result)
        self.assertEqual(unpickled.state, action.state)

    def test_can_safely_perform_Actions_concurrently(self):
        file = FakeFile(b'Hello.', 'wb')

        def perform_and_collect(action: Action, results: list):
            action.perform()
            results.append(file.read())

        initial_file_contents = file.read()
        action1 = FakeWriteBytes(file, b' How are you?', delay=0.2)
        action2 = FakeWriteBytes(file, b' I hope you\'re well.', delay=0.1)
        results = [initial_file_contents]
        thread1 = Thread(target=perform_and_collect, args=(action1, results))
        thread2 = Thread(target=perform_and_collect, args=(action2, results))
        threads = thread1, thread2
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        self.assertEqual(
            reduce(lambda a, b: a + b, results),
            initial_file_contents + action1.bytes_to_write + action2.bytes_to_write
        )

    def test_Action_can_be_renamed(self):
        action = FakeAction()
        self.assertIsNone(action.name)
        name1 = 'new'
        action.set(name=name1)
        self.assertEqual(action.name, name1)
        name2 = 'different name'
        action.name = name2
        self.assertEqual(action.name, name2)
