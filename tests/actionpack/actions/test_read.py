import pickle

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import Read
from actionpack.utils import pickleable


class ReadTest(TestCase):

    contents = 'some file contents.'

    @patch('pathlib.Path.read_bytes')
    def test_can_Read_bytes(self, mock_input):
        contents = self.contents.encode()
        mock_input.return_value = contents
        action = Read(__file__, output_type=bytes)
        result = action.perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, contents)

    @patch('pathlib.Path.read_text')
    def test_can_Read_string(self, mock_input):
        mock_input.return_value = self.contents
        action = Read(__file__, output_type=str)
        result = action.perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, self.contents)

    @patch('pathlib.Path.read_bytes')
    def test_can_ReadBytes_even_if_failure(self, mock_input):
        contents = self.contents.encode()
        mock_input.return_value = contents

        invalid_file_result = Read('some/invalid/filepath').perform()
        self.assertIsInstance(invalid_file_result, Result)
        self.assertIsInstance(invalid_file_result.value, FileNotFoundError)

        directory_result = Read(Path(__file__).parent).perform()
        self.assertIsInstance(directory_result, Result)
        self.assertIsInstance(directory_result.value, IsADirectoryError)

    def test_can_pickle(self):
        action = Read(__file__)
        pickled = pickleable(action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(action))
        self.assertEqual(unpickled.__dict__, action.__dict__)
