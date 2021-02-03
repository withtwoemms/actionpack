from actionpack.actions import MakeRequest
from actionpack.actions import RetryPolicy
from tests.actionpack.actions import FakeResponse

from oslash import Left
from oslash import Right
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch


class RetryPolicyTest(TestCase):

    @patch('requests.Session.send')
    def test_can_enact_RetryPolicy(self, mock_session_send):
        mock_session_send.side_effect = Exception('something went wrong :/')
        max_retries = 2
        action = RetryPolicy(MakeRequest('GET', 'http://localhost'), max_retries=max_retries)
        result = action.perform()

        self.assertEqual(action.retries, max_retries)
        self.assertIsInstance(result, Left)
        self.assertIsInstance(result.value, RetryPolicy.Expired)

    @patch('requests.Session.send')
    def test_can_enact_RetryPolicy_that_ultimately_succeeds(self, mock_session_send):
        mock_session_send.side_effect = [
            Exception('something went wrong :/'),
            FakeResponse('something went right :)'.encode())
        ]
        max_retries = 2
        action = RetryPolicy(MakeRequest('GET', 'http://localhost'), max_retries=max_retries)
        result = action.perform()

        self.assertEqual(action.retries, 1)
        self.assertIsInstance(result, Right)
