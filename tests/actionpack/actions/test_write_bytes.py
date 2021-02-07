import pickle

from actionpack.actions import WriteBytes
from actionpack.utils import pickleable

from io import BytesIO
from io import TextIOWrapper
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

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)

