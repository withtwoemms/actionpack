from actionpack.actions import ReadInput

from unittest import TestCase
from unittest.mock import patch


class ReadInputTest(TestCase):

    @patch('builtins.input')
    def test_can_ReadInput(self, mock_input):
        reply = 'I\'m fine.'
        mock_input.return_value = reply
        action = ReadInput('How are you?')
        self.assertEqual(action.perform().value, reply)

