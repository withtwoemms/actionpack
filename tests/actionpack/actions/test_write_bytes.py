from actionpack.actions import WriteBytes

from io import BytesIO
from io import TextIOWrapper
from unittest import TestCase
from unittest.mock import patch


class WriteBytesTest(TestCase):

    class FakeFile:
        def __init__(self, contents: bytes=bytes(), mode: str=None):
            self.buffer = BytesIO(contents)
            self.buffer.read()
            self.mode = mode

        def read(self):
            self.buffer.seek(0)
            return self.buffer.read()

        def write(self, data: bytes):
            if self.mode == 'wb':
                self.buffer.seek(0)
            self.buffer.write(data)
            return len(data)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.closed = True

    @patch('pathlib.Path.open')
    def test_can_WriteBytes(self, mock_output):
        salutation = 'Hello.'.encode()
        question = ' How are you?'.encode()

        file = self.FakeFile(salutation)
        mock_output.return_value = file
        action = WriteBytes('valid/path/to/file', question)
        result = action.perform()

        self.assertEqual(file.read(), salutation + question)
        self.assertEqual(result.value, len(question))

    @patch('pathlib.Path.open')
    def test_can_overWriteBytes(self, mock_output):
        salutation = 'Hello.'.encode()
        question = ' How are you?'.encode()

        file = self.FakeFile(salutation, 'wb')
        mock_output.return_value = file
        action = WriteBytes('valid/path/to/file', question, overwrite=True)
        result = action.perform()

        self.assertEqual(file.read(), question)
        self.assertEqual(result.value, len(question))

