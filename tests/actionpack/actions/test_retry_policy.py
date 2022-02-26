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
    def test_RetryPolicy_not_enacted_on_initial_success(self, mock_session_send):
        result = self.action.perform()

        self.assertIsInstance(result, Result)
        self.assertTrue(result.successful)

    @patch('requests.Session.send')
    def test_can_enact_RetryPolicy(self, mock_session_send):
        mock_session_send.side_effect = Exception('something went wrong :/')
        result = self.action.perform()

        self.assertEqual(self.action.retries, self.max_retries)
        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, RetryPolicy.Expired)

    @patch('requests.Session.send')
    def test_can_validate_RetryPolicy(self, mock_session_send):
        exceptions = [Exception('something went wrong :/')] * self.max_retries
        mock_session_send.side_effect = exceptions
        result = self.action.perform()
        validated_action = self.action.validate()

        self.assertIsInstance(result.value, RetryPolicy.Expired)
        self.assertEqual(validated_action.retries, self.max_retries)

    @patch('requests.Session.send')
    def test_can_enact_RetryPolicy_that_ultimately_succeeds(self, mock_session_send):
        mock_session_send.side_effect = [
            Exception('something went wrong :/'),
            FakeResponse('something went right :)'.encode())
        ]
        result = self.action.perform()

        self.assertIsInstance(result, Result)
        self.assertEqual(self.action.retries, 1)

    def test_no_retries_before_RetryPolicy_enacted(self):
        with self.assertRaises(AttributeError):
            self.action.entries

    def test_validate(self):
        invalid_num_retries = -1
        self.action.retries = invalid_num_retries
        validated_action = self.action.validate()

        self.assertEqual(validated_action.retries, invalid_num_retries)

    @patch('requests.Session.send')
    def test_can_record_retry_history(self, mock_session_send):
        exceptions = [Exception('something went wrong :/')] * (self.max_retries + 1)
        mock_session_send.side_effect = exceptions
        action = RetryPolicy(
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=self.max_retries,
            should_record=True
        )
        action.perform()

        for attempt in action.attempts:
            self.assertFalse(attempt.successful)
        self.assertListEqual([attempt.value for attempt in action.attempts], exceptions)

    def test_can_serialize(self):
        self.assertEqual(repr(self.action), '<RetryPolicy(2 x <MakeRequest>)>')

    @patch('requests.Session.send')
    def test_can_pickle(self, mock_session_send):
        mock_session_send.side_effect = NotImplemented
        self.assertTrue(pickleable(self.action))

        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
