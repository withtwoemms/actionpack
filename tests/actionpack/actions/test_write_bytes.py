import pickle

from actionpack import Action
from actionpack.actions import WriteBytes
from actionpack.utils import pickleable
from tests.actionpack import FakeFile

from unittest import TestCase
from unittest.mock import patch


class WriteBytesTest(TestCase):

    def setUp(self):
        self.salutation = 'Hello.'.encode()
        self.question = ' How are you?'.encode()
        self.action = WriteBytes('valid/path/to/file', self.question)

    @patch('pathlib.Path.open')
    def test_can_WriteBytes(self, mock_output):
        file = FakeFile(self.salutation)
        mock_output.return_value = file
        result = self.action.perform()

        self.assertEqual(file.read(), self.salutation + self.question)
        self.assertEqual(result.value, len(self.question))

    @patch('pathlib.Path.open')
    def test_can_overWriteBytes(self, mock_output):
        file = FakeFile(self.salutation, 'wb')
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

