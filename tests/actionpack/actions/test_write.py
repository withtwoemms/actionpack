import pickle

from contextlib import redirect_stdout
from contextlib import redirect_stderr
from io import StringIO
from os import getcwd as cwd
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from actionpack import Action
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

    def test_can_Write_to_STDOUT(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            result = Write(Write.STDOUT, self.question).perform(should_raise=True)
            buffer.seek(0)  # return to beginning of "file"

        self.assertEqual(buffer.read(), self.question)
        self.assertIsInstance(result, Result)
        self.assertIsNone(result.value)

    def test_can_Write_to_STDERR(self):
        buffer = StringIO()
        with redirect_stderr(buffer):
            result = Write(Write.STDERR, self.question).perform(should_raise=True)
            buffer.seek(0)  # return to beginning of "file"

        self.assertEqual(buffer.read(), self.question)
        self.assertIsInstance(result, Result)
        self.assertIsNone(result.value)

    def test_can_only_write_string_or_bytes(self):
        with self.assertRaises(TypeError):
            Write('some/file', to_write=1.0).perform(should_raise=True)

    def test_cannot_Write_to_existing_file(self):
        with self.assertRaises(FileExistsError):
            Write(__file__, to_write='something').perform(should_raise=True)

    def test_cannot_Write_to_directory(self):
        write = Write(str(Path(__file__).parent), to_write='something')
        with self.assertRaises(IsADirectoryError):
            write.perform(should_raise=True)

    def test_Write_raises_when_given_an_Exception_to_write(self):
        exception = Exception('some error.')
        with self.assertRaises(type(exception)):
            Write(self.absfilepath, exception).perform(should_raise=True)

    def test_Write_does_not_raise_when_instantiated_with_unexpected_types(self):
        write1 = Write(self.absfilepath, to_write='data', prefix='prefix')
        self.assertIsInstance(write1, Write)

        write2 = Write(self.absfilepath, to_write=123, prefix='prefix')
        self.assertIsInstance(write2, Action.Construct)
        result2 = write2.perform()
        self.assertIsInstance(result2, Result)
        self.assertIsInstance(result2.value, TypeError)

        write3 = Write(self.absfilepath, to_write='123', prefix=123)
        self.assertIsInstance(write3, Action.Construct)
        result3 = write3.perform()
        self.assertIsInstance(result3, Result)
        self.assertIsInstance(result3.value, TypeError)

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

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.open')
    def test_can_make_directory_on_Write(self, mock_open, mock_exists, mock_mkdir):
        declaration = "I don't want him hurt."
        exclamation = " Jurgal's animal is insane!"
        file = FakeFile(declaration, mode='a')
        mock_mkdir.return_value = None
        mock_exists.side_effect = [False, True]
        mock_open.return_value = file
        filename = 'directory/file'
        action = Write(filename=filename, to_write=exclamation, overwrite=True, mkdir=True)
        result = action.perform()

        self.assertTrue(action.path.parent.exists())
        self.assertTrue(result.successful)

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
