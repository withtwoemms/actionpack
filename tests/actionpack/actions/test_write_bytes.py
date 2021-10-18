import pickle

from os import getcwd as cwd
from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import WriteBytes
from actionpack.utils import pickleable
from tests.actionpack import FakeFile


class WriteBytesTest(TestCase):

    def setUp(self):
        self.salutation = 'Hello.'.encode()
        self.question = ' How are you?'.encode()
        self.absfilepath = f'{cwd()}/valid/path/to/file'
        self.action = WriteBytes(self.absfilepath, self.question)

    @patch('pathlib.Path.open')
    def test_can_WriteBytes(self, mock_output):
        file = FakeFile(self.salutation)
        mock_output.return_value = file
        result = self.action.perform()

        self.assertEqual(file.read(), self.salutation + self.question)
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, self.absfilepath)

    @patch('pathlib.Path.open')
    def test_can_overWriteBytes(self, mock_output):
        file = FakeFile(self.salutation, 'wb')
        mock_output.return_value = file
        result = self.action.perform()

        self.assertEqual(file.read(), self.question)
        self.assertEqual(result.value, self.absfilepath)

    @patch('pathlib.Path.open')
    def test_can_WriteBytes_in_append_mode(self, mock_output):
        file = FakeFile(self.salutation, mode='a')
        mock_output.return_value = file
        question = b' How are you?'
        action = WriteBytes(self.absfilepath, question, append=True)
        action.perform()
        action.perform()

        self.assertEqual(
            self.salutation + question + b'\n' + question + b'\n',
            file.read()
        )

    @patch('pathlib.Path.open')
    def test_cannot_overwrite_and_append(self, mock_output):
        file = FakeFile(self.salutation)
        mock_output.return_value = file
        action = WriteBytes(self.absfilepath, b'bytes to write', overwrite=True, append=True)

        with self.assertRaises(ValueError):
            action.validate()

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
