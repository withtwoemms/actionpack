import pickle

from os import getcwd as cwd
from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import Write
from actionpack.utils import pickleable
from tests.actionpack import FakeFile


class WriteTest(TestCase):

    def setUp(self):
        self.salutation = 'Hello.'
        self.question = ' How are you?'
        self.absfilepath = f'{cwd()}/valid/path/to/file'

    @patch('pathlib.Path.open')
    def test_can_Write_bytes(self, mock_output):
        file = FakeFile(self.salutation.encode())
        mock_output.return_value = file
        result = Write(self.absfilepath, self.question.encode()).perform(should_raise=True)

        self.assertEqual(file.read(), f'{self.salutation + self.question}'.encode())
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, self.absfilepath)

    @patch('pathlib.Path.open')
    def test_can_Write_string(self, mock_output):
        file = FakeFile(self.salutation)
        mock_output.return_value = file
        result = Write(self.absfilepath, self.question).perform(should_raise=True)
        self.assertEqual(file.read(), self.salutation + self.question)
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, self.absfilepath)

    def test_can_Write_raises_when_given_an_Exception_to_write(self):
        exception = Exception('some error.')
        with self.assertRaises(type(exception)):
            Write(self.absfilepath, exception).perform(should_raise=True)

    def test_can_Write_raises_when_given_an_prefix_of_different_type(self):
        Write(self.absfilepath, to_write='data', prefix='prefix')  # should not fail
        with self.assertRaises(TypeError):
            Write(self.absfilepath, to_write=123, prefix='prefix')
        with self.assertRaises(TypeError):
            Write(self.absfilepath, to_write=123, prefix=123)

    @patch('pathlib.Path.open')
    def test_can_overWrite_bytes(self, mock_output):
        file = FakeFile(self.salutation.encode(), 'wb')
        mock_output.return_value = file
        result = Write(self.absfilepath, self.question.encode()).perform(should_raise=True)

        self.assertEqual(file.read(), self.question.encode())
        self.assertEqual(result.value, self.absfilepath)

    @patch('pathlib.Path.open')
    def test_can_overWrite_string(self, mock_output):
        file = FakeFile(self.salutation, 'w')
        mock_output.return_value = file
        result = Write(self.absfilepath, self.question).perform(should_raise=True)

        self.assertEqual(file.read(), self.question)
        self.assertEqual(result.value, self.absfilepath)

    @patch('pathlib.Path.open')
    def test_can_Write_bytes_in_append_mode(self, mock_output):
        file = FakeFile(self.salutation.encode(), mode='a')
        mock_output.return_value = file
        question = b' How are you?'
        action = Write(self.absfilepath, question, append=True)
        action.perform(should_raise=True)
        action.perform()

        self.assertEqual(
            self.salutation.encode() + question + b'\n' + question + b'\n',
            file.read()
        )

    @patch('pathlib.Path.open')
    def test_can_Write_string_in_append_mode(self, mock_output):
        file = FakeFile(self.salutation, mode='a')
        mock_output.return_value = file
        question = ' How are you?'
        action = Write(self.absfilepath, question, append=True)
        action.perform(should_raise=True)
        action.perform()

        self.assertEqual(
            self.salutation + question + '\n' + question + '\n',
            file.read()
        )

    @patch('pathlib.Path.open')
    def test_cannot_overwrite_and_append(self, mock_output):
        file = FakeFile(self.salutation)
        mock_output.return_value = file
        action = Write(self.absfilepath, b'bytes to write', overwrite=True, append=True)

        with self.assertRaises(ValueError):
            action.validate()

    def test_can_pickle(self):
        action = Write(self.absfilepath, self.question)
        pickled = pickleable(action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(action))
        self.assertEqual(unpickled.__dict__, action.__dict__)
