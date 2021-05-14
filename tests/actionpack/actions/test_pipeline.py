from actionpack.actions import Pipeline
from actionpack.actions import ReadInput
from actionpack.actions import ReadBytes
from actionpack.actions import WriteBytes
from actionpack.actions.pipeline import Fitting
from actionpack.actions.pipeline import FittingType
from tests.actionpack import FakeFile

from oslash import Right
from unittest import TestCase
from unittest.mock import patch


class PipelineTest(TestCase):

    @patch('pathlib.Path.open')
    @patch('builtins.input')
    def test_Pipeline(self, mock_input, mock_output):
        file = FakeFile(b'How are you?')
        filename = 'this/file.txt'
        reply = 'I\'m fine.'
        mock_output.return_value = file
        mock_input.side_effect = [filename, reply]

        read_input = ReadInput('Which file?')
        #actions = [ReadBytes, ReadInput]
        #actions = [ReadBytes, ReadInput, Fitting(WriteBytes)]
        #def __init__(self, filename: str, bytes_to_write: bytes, overwrite: bool=False):
        actions = [ReadBytes, ReadInput, FittingType(keywords={'bytes_to_write', filename}), WriteBytes]
        pipeline = Pipeline(read_input, *(action for action in actions))
        result = pipeline.perform()
        print('RESULT ->', result)
        print('RESULT ->', result.value)
        self.assertIsInstance(result, Right)
        self.assertEqual(result.value, reply)

