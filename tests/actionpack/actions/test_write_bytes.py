import pickle

from actionpack import Action
from actionpack.actions import WriteBytes
from actionpack.utils import pickleable

from functools import reduce
from io import BytesIO
from io import TextIOWrapper
from threading import Thread
from time import sleep
from unittest import TestCase
from unittest.mock import patch


class WriteBytesTest(TestCase):

    class FakeFile:
        def __init__(self, contents: bytes=bytes(), mode: str=None):
            self.buffer = BytesIO(contents)
            self.buffer.read()
            self.mode = mode

        def read(self):
            self.buffer.seek(0)
            return self.buffer.read()

        def write(self, data: bytes):
            if self.mode == 'wb':
                self.buffer.seek(0)
                self.buffer.truncate()
            self.buffer.write(data)
            return len(data)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.closed = True

    def setUp(self):
        self.salutation = 'Hello.'.encode()
        self.question = ' How are you?'.encode()
        self.action = WriteBytes('valid/path/to/file', self.question)

    @patch('pathlib.Path.open')
    def test_can_WriteBytes(self, mock_output):
        file = self.FakeFile(self.salutation)
        mock_output.return_value = file
        result = self.action.perform()

        self.assertEqual(file.read(), self.salutation + self.question)
        self.assertEqual(result.value, len(self.question))

    @patch('pathlib.Path.open')
    def test_can_overWriteBytes(self, mock_output):
        file = self.FakeFile(self.salutation, 'wb')
        mock_output.return_value = file
        action = WriteBytes('valid/path/to/file', self.question, overwrite=True)
        result = self.action.perform()

        self.assertEqual(file.read(), self.question)
        self.assertEqual(result.value, len(self.question))

    @patch('pathlib.Path.open')
    def test_can_WriteBytes_concurrently(self, mock_output):
        file = self.FakeFile(self.salutation, 'wb')
        mock_output.return_value = file
        initial_file_contents = file.read()
        filepath = 'valid/path/to/file'
        class DelayedWriteBytes(WriteBytes):
            def __init__(self, *args, delay: float, **kwargs):
                self.delay = delay
                super().__init__(*args, **kwargs)
            def instruction(self):
                result = super().instruction()
                sleep(self.delay)
                return result
        action1 = DelayedWriteBytes(filepath, self.question, overwrite=True, delay=0.2)
        action2 = DelayedWriteBytes(filepath, b' I hope you\'re well.', overwrite=True, delay=0.1)
        results = [initial_file_contents]
        def sleep_and_perform(action: Action, results: list):
            action.perform()
            results.append(file.read())
        thread1 = Thread(target=sleep_and_perform, args=(action1, results))
        thread2 = Thread(target=sleep_and_perform, args=(action2, results))
        threads = thread1, thread2
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
        self.assertEqual(
            reduce(lambda a, b: a + b, results),
            initial_file_contents + action1.bytes_to_write + action2.bytes_to_write
        )

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)

