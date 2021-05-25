import pickle

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import ReadBytes
from actionpack.utils import pickleable


class ReadBytesTest(TestCase):

    contents = 'some file contents.'.encode()

    def setUp(self):
        self.action = ReadBytes(__file__)

    @patch('pathlib.Path.read_bytes')
    def test_can_ReadBytes(self, mock_input):
        mock_input.return_value = self.contents
        result = self.action.perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, self.contents)

    @patch('pathlib.Path.read_bytes')
    def test_can_ReadBytes_even_if_failure(self, mock_input):
        mock_input.return_value = self.contents

        invalid_file_result = ReadBytes('some/invalid/filepath').perform()
        self.assertIsInstance(invalid_file_result, Result)
        self.assertIsInstance(invalid_file_result.value, FileNotFoundError)

        directory_result = ReadBytes(Path(__file__).parent).perform()
        self.assertIsInstance(directory_result, Result)
        self.assertIsInstance(directory_result.value, IsADirectoryError)

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
