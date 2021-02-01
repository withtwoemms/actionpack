from actionpack.actions import ReadBytes

from oslash import Left
from oslash import Right
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


class ReadInputTest(TestCase):

    contents = 'some file contents.'.encode()

    @patch('pathlib.Path.read_bytes')
    def test_can_ReadBytes(self, mock_input):
        mock_input.return_value = self.contents
        result = ReadBytes(__file__).perform()
        self.assertIsInstance(result, Right)
        self.assertEqual(result.value, self.contents)

    @patch('pathlib.Path.read_bytes')
    def test_can_ReadBytes_even_if_failure(self, mock_input):
        mock_input.return_value = self.contents

        invalid_file_result = ReadBytes('some/invalid/filepath').perform()
        self.assertIsInstance(invalid_file_result, Left)
        self.assertIsInstance(invalid_file_result.value, FileNotFoundError)

        directory_result = ReadBytes(Path(__file__).parent).perform()
        self.assertIsInstance(directory_result, Left)
        self.assertIsInstance(directory_result.value, IsADirectoryError)

