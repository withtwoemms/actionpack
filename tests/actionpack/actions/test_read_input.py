import pickle

from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import ReadInput
from actionpack.utils import pickleable


class ReadInputTest(TestCase):

    def setUp(self):
        self.action = ReadInput('How are you?')

    @patch('builtins.input')
    def test_can_ReadInput(self, mock_input):
        reply = 'I\'m fine.'
        mock_input.return_value = reply
        result = self.action.perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, reply)

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
