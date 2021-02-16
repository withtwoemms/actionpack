import pickle

from actionpack import Action
from actionpack.utils import pickleable
from tests.actionpack import FakeAction
from tests.actionpack import FakeFile
from tests.actionpack.actions import FakeWriteBytes

from functools import reduce
from oslash import Left
from oslash import Right
from threading import Thread
from unittest import TestCase
from unittest.mock import patch


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

    def test_Action_can_raise_exception(self):
        exception = Exception('This is fine :|')
        with self.assertRaises(type(exception)):
            FakeAction(exception=exception).perform(should_raise=True)

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
            thing = action.perform()
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

