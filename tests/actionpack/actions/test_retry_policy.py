import pickle

from unittest import TestCase
from unittest.mock import patch

from actionpack.action import Result
from actionpack.actions import MakeRequest
from actionpack.actions import RetryPolicy
from actionpack.utils import pickleable
from tests.actionpack.actions import FakeResponse


class RetryPolicyTest(TestCase):

    def setUp(self):
        self.max_retries = 2
        self.action = RetryPolicy(MakeRequest('GET', 'http://localhost'), max_retries=self.max_retries)

    @patch('requests.Session.send')
    def test_can_enact_RetryPolicy(self, mock_session_send):
        mock_session_send.side_effect = Exception('something went wrong :/')
        result = self.action.perform()

        self.assertEqual(self.action.retries, self.max_retries)
        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, RetryPolicy.Expired)

    @patch('requests.Session.send')
    def test_can_enact_RetryPolicy_that_ultimately_succeeds(self, mock_session_send):
        mock_session_send.side_effect = [
            Exception('something went wrong :/'),
            FakeResponse('something went right :)'.encode())
        ]
        result = self.action.perform()

        self.assertIsInstance(result, Result)
        self.assertEqual(self.action.retries, 1)

    @patch('requests.Session.send')
    def test_can_pickle(self, mock_session_send):
        mock_session_send.side_effect = NotImplemented
        self.assertTrue(pickleable(self.action))

        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
