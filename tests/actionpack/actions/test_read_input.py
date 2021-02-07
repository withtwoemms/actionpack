import pickle

from actionpack.actions import ReadInput
from actionpack.utils import pickleable

from unittest import TestCase
from unittest.mock import patch


class ReadInputTest(TestCase):

    def setUp(self):
        self.action = ReadInput('How are you?')

    @patch('builtins.input')
    def test_can_ReadInput(self, mock_input):
        reply = 'I\'m fine.'
        mock_input.return_value = reply
        self.assertEqual(self.action.perform().value, reply)

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)

