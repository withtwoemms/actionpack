import pickle

from io import BytesIO
from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import Remove
from actionpack.utils import pickleable
from tests.actionpack.actions import uncloseable


class RemoveTest(TestCase):

    contents = 'some file contents.'
    separator = '\n'
    other_contents = f'{contents}{separator}'

    def test_instantiate_given_invalid_output_type(self):
        result = Remove('some-file.name', output_type=100).perform()
        self.assertIsInstance(result.value, TypeError)

    @patch('builtins.open')
    def test_can_Remove_string(self, mock_file):
        num_repeats = 5
        with uncloseable(StringIO((self.other_contents * num_repeats).rstrip())) as buffer:
            mock_file.return_value = buffer

            action = Remove(__file__)
            result = action.perform()

            self.assertIsInstance(result, Result)
            self.assertTrue(result.successful)
            self.assertEqual(result.value, self.other_contents)

        remaining_contents = buffer.read().split(self.separator)
        self.assertEqual(len(remaining_contents), num_repeats - 1)
        self.assertTrue(remaining == self.contents for remaining in remaining_contents)

    @patch('builtins.open')
    def test_can_Remove_bytes(self, mock_file):
        num_repeats = 5
        with uncloseable(BytesIO((self.other_contents * num_repeats).rstrip().encode())) as buffer:
            mock_file.return_value = buffer

            action = Remove(__file__)
            result = action.perform()

            self.assertIsInstance(result, Result)
            self.assertTrue(result.successful)
            self.assertEqual(result.value, self.other_contents.encode())

        remaining_contents = buffer.read().split(self.separator.encode())
        self.assertEqual(len(remaining_contents), num_repeats - 1)
        self.assertTrue(remaining == self.contents.encode() for remaining in remaining_contents)

    @patch('builtins.open')
    def test_can_Remove_bytes_even_if_failure(self, mock_file):
        contents = self.contents.encode()
        mock_file.return_value = contents

        invalid_file_result = Remove('some/invalid/filepath').perform()
        self.assertIsInstance(invalid_file_result, Result)
        self.assertIsInstance(invalid_file_result.value, FileNotFoundError)

        directory_result = Remove(Path(__file__).parent).perform()
        self.assertIsInstance(directory_result, Result)
        self.assertIsInstance(directory_result.value, IsADirectoryError)

    def test_can_pickle(self):
        action = Remove(__file__)
        pickled = pickleable(action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(action))
        self.assertEqual(unpickled.__dict__, action.__dict__)
