from os import getcwd as cwd
from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import Pipeline
from actionpack.actions import ReadInput
from actionpack.actions import Read
from actionpack.actions import Write
from actionpack.actions.pipeline import Call
from actionpack.utils import Closure
from tests.actionpack import FakeFile


class PipelineTest(TestCase):

    @patch('pathlib.Path.open')
    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_Pipeline(self, mock_input, mock_exists, mock_file):
        filename = 'this/file.txt'
        contents = b"What's wrong with him? ...My first thought would be, 'a lot'."
        file = FakeFile(contents)

        mock_file.return_value = file
        mock_exists.return_value = True
        mock_input.return_value = filename

        pipeline = Pipeline(ReadInput('Which file?'), Read)
        result = pipeline.perform()

        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, contents)

    @patch('pathlib.Path.open')
    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_Pipeline_Fitting(self, mock_input, mock_exists, mock_file):
        filename = 'this/file.txt'
        file = FakeFile()
        question = b'How are you?'
        reply = 'I\'m fine.'

        mock_file.return_value = file
        mock_exists.return_value = True
        mock_input.side_effect = [filename, reply]

        read_input = ReadInput('Which file?')
        action_types = [
            Pipeline.Fitting(
                action=Write,
                reaction=Call(Closure(bytes.decode)),
                **{'append': True, 'to_write': question},
            ),
            Read,  # retrieve question from FakeFile
            ReadInput   # pose question to user
        ]
        pipeline = Pipeline(read_input, *action_types, should_raise=True)
        result = pipeline.perform(should_raise=True)

        self.assertEqual(file.read(), question + b'\n')
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, reply)

    @patch('pathlib.Path.open')
    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_Pipeline_Receiver(self, mock_input, mock_exists, mock_file):
        filename = 'this/file.txt'
        file = FakeFile()
        reply = b"I'd like to record this."

        mock_file.return_value = file
        mock_exists.return_value = True
        mock_input.return_value = reply

        read_input = ReadInput('What would you like to record?')
        action_types = [
            Pipeline.Fitting(
                action=Write,
                reaction=Call(Closure(bytes.decode)),
                **{'append': True, 'filename': filename, 'to_write': Pipeline.Receiver},
            )
        ]
        pipeline = Pipeline(read_input, *action_types, should_raise=True)
        result = pipeline.perform(should_raise=True)

        self.assertEqual(file.read(), reply + b'\n')
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, f'{cwd()}/{filename}')
