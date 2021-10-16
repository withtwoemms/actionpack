from actionpack.action import Result
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

    @patch('pathlib.Path.read_bytes')
    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_Pipeline(self, mock_input, mock_exists, mock_output):
        file = FakeFile(b'How are you?')
        file_contents = 'How are you?'
        filename = 'this/file.txt'
        reply = 'I\'m fine.'
        mock_output.return_value = file_contents
        mock_exists.return_value = True
        # mock_input.side_effect = [filename, reply, reply, reply]
        mock_input.side_effect = [filename]

        read_input = ReadInput('Which file?')
        #actions = [ReadBytes, ReadInput]
        #actions = [ReadBytes, ReadInput, Fitting(WriteBytes)]
        #def __init__(self, filename: str, bytes_to_write: bytes, overwrite: bool=False):
        # action_types = [ReadBytes, ReadInput, FittingType(keywords={'bytes_to_write': filename}), WriteBytes]
        # action_types = [ReadBytes, ReadInput, FittingType(dct={'action': WriteBytes}, keywords={'bytes_to_write': filename})]
        action_types = [ReadBytes, Fitting(WriteBytes, **{'append': True, 'bytes_to_write': b'sup'})]
        # action_types = [ReadBytes, ReadInput, FittingType, WriteBytes]
        # action_types = [ReadBytes, ReadInput, WriteBytes]
        pipeline = Pipeline(read_input, *(action_type for action_type in action_types))
        result = pipeline.perform()
        print('RESULT ->', result)
        print('RESULT ->', result.value)
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, reply)