from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import Pipeline
from actionpack.actions import ReadInput
from actionpack.actions import ReadBytes
from actionpack.actions import WriteBytes
from actionpack.actions.pipeline import Call
from actionpack.actions.pipeline import Fitting
from actionpack.utils import Closure
from tests.actionpack import FakeFile


class PipelineTest(TestCase):

    @patch('pathlib.Path.open')
    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_Pipeline(self, mock_input, mock_exists, mock_file):
        filename = 'this/file.txt'
        file = FakeFile()
        question = b'How are you?'
        reply = 'I\'m fine.'
        mock_file.return_value = file
        mock_exists.return_value = True
        mock_input.side_effect = [filename, reply]

        read_input = ReadInput('Which file?')
        action_types = [
            # TODO (withtwoemms) -- convert Fitting to an ActionType
            Fitting(
                WriteBytes, **{'append': True, 'bytes_to_write': question},
                reaction=Call(Closure(bytes.decode))
            ),
            ReadBytes,  # retrieve question from FakeFile
            ReadInput   # pose question to user
        ]
        pipeline = Pipeline(read_input, *action_types)
        result = pipeline.perform(should_raise=True)

        self.assertEqual(file.read(), question + b'\n')
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, reply)
