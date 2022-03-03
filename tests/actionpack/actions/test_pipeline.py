from os import getcwd as cwd
from unittest import TestCase
from unittest.mock import patch

from actionpack import Action
from actionpack.action import Result
from actionpack.actions import Pipeline
from actionpack.actions import ReadInput
from actionpack.actions import Read
from actionpack.actions import Write
from actionpack.actions.pipeline import Call
from actionpack.utils import Closure
from tests.actionpack import FakeAction
from tests.actionpack import FakeFile


class PipelineTest(TestCase):

    def test_instantiation_fails_with_invalid_action_types(self):
        pipeline = Pipeline(ReadInput('Which file?'), 'not an ActionType')
        self.assertIsInstance(pipeline, Action.Construct)
        self.assertIsInstance(pipeline.failure, TypeError)

    def test_can_Pipeline_constitutes_iterator_over_Action_types(self):
        action_types = [FakeAction] * 3
        pipeline = Pipeline(FakeAction(), *action_types)
        self.assertEqual(list(pipeline), action_types)

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
    def test_can_perform_Pipeline_repeatedly(self, mock_input, mock_exists, mock_file):
        filename = 'this/file.txt'
        contents = b'Look at the little Om. Isn\'t he sweet?'
        file = FakeFile(contents)

        mock_file.return_value = file
        mock_exists.return_value = True
        mock_input.return_value = filename

        pipeline = Pipeline(ReadInput('Which file?'), Read)
        result = pipeline.perform()

        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, contents)
        self.assertEqual(file.read(), contents)

        second_result = pipeline.perform()

        self.assertIsInstance(second_result, Result)
        self.assertEqual(second_result.value, contents)
        self.assertEqual(file.read(), contents)

    @patch('pathlib.Path.exists')
    def test_first_Pipeline_failure_prevents_further_execution(self, mock_exists):
        bad_filename = 'bad/filename.txt'

        mock_exists.return_value = False

        pipeline = Pipeline(Read(bad_filename), ReadInput)
        result = pipeline.perform()

        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, FileNotFoundError)
        self.assertEqual(str(result.value), bad_filename)

    def test_Pipeline_Fitting_defines_constructor_replacement(self):
        self.assertIsNone(Pipeline.Fitting.init(FakeAction))

    def test_Pipeline_Fitting_defines_instruction_replacement(self):
        result = Pipeline.Fitting.instruction(Pipeline.Fitting(FakeAction()))
        self.assertTrue(result.successful)
        result = Pipeline.Fitting.instruction(Pipeline.Fitting(FakeAction(), reaction=FakeAction()))
        self.assertTrue(result.successful)

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

    @patch('pathlib.Path.open')
    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_can_repeatedly_perform_Pipeline_with_Receiver(self, mock_input, mock_exists, mock_file):
        filename = 'this/file.txt'
        file = FakeFile()
        reply = b'The machines have worked perfectly up till now.'

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

        second_result = pipeline.perform(should_raise=True)

        self.assertEqual(file.read(), reply + b'\n' + reply + b'\n')
        self.assertIsInstance(second_result, Result)
        self.assertEqual(second_result.value, f'{cwd()}/{filename}')

    def test_can_Pipeline_multiple_calls(self):
        response = "We can't leave him here. May I keep him?"

        def first_function(param):
            return 'first', param

        def second_function(param):
            return 'second', param

        action = FakeAction(instruction_provider=lambda: response)
        action_types = [
            Pipeline.Fitting(
                action=Call,
                enclose=first_function,
            ),
            Pipeline.Fitting(
                action=Call,
                enclose=second_function,
            )
        ]
        pipeline = Pipeline(action, *action_types, should_raise=True)
        result = pipeline.perform(should_raise=True)

        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, ('second', ('first', response)))
