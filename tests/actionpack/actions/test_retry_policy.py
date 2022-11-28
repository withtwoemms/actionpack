import pickle

from datetime import datetime
from unittest import TestCase
from unittest.mock import ANY
from unittest.mock import patch

from actionpack import Action
from actionpack.action import Result
from actionpack.actions import MakeRequest
from actionpack.actions import RetryPolicy
from actionpack.utils import pickleable
from tests.actionpack.actions import FakeResponse


class RetryPolicyTest(TestCase):

    def setUp(self):
        self.max_retries = 2
        self.action = RetryPolicy[str, str](
            MakeRequest('GET', 'http://localhost'),
            max_retries=self.max_retries
        )

    @patch('requests.Session.send')
    def test_RetryPolicy_can_succeed(self, mock_session_send):
        result = self.action.perform(should_raise=True)

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
    def test_can_handle_inappropriately_enacted_RetryPolicy(self, mock_session_send):
        mock_session_send.side_effect = Exception('something went wrong :/')
        with self.assertRaises(RetryPolicy.Invalid):
            self.action.enact(counter=-10)

    @patch('requests.Session.send')
    def test_can_validate_expired_RetryPolicy(self, mock_session_send):
        exceptions = [Exception('something went wrong :/')] * self.max_retries
        mock_session_send.side_effect = exceptions
        result = self.action.perform()

        self.assertIsInstance(result.value, RetryPolicy.Expired)
        with self.assertRaises(RetryPolicy.Expired):
            self.action.validate()

    @patch('requests.Session.send')
    @patch('actionpack.actions.RetryPolicy.enacted')
    def test_can_validate_enacted_RetryPolicy(self, mock_validation, mock_session_send):
        exceptions = [Exception('something went wrong :/'), ANY]
        mock_session_send.side_effect = exceptions
        mock_validation.side_effect = [ANY, RetryPolicy.Enacted('already started.')]
        result = self.action.perform()

        self.assertIsInstance(result.value, RetryPolicy.Enacted)
        with self.assertRaises(RetryPolicy.Enacted):
            self.action.validate()

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
        self.action._retries = invalid_num_retries
        validated_action = self.action.validate()

        self.assertEqual(validated_action.retries, invalid_num_retries)

    @patch('requests.Session.send')
    def test_can_record_retry_history_if_not_successful(self, mock_session_send):
        exceptions = [Exception('something went wrong :/')] * (self.max_retries + 1)
        mock_session_send.side_effect = exceptions
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=self.max_retries,
            should_record=True
        )
        action.perform()

        for attempt in action.attempts:
            self.assertFalse(attempt.successful)
        self.assertListEqual([attempt.value for attempt in action.attempts], exceptions)

    @patch('requests.Session.send')
    def test_can_record_retry_history_if_successful(self, mock_session_send):
        results = ['SUCCEEDED!']
        mock_session_send.side_effect = results
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=self.max_retries,
            should_record=True
        )
        action.perform()

        for attempt in action.attempts:
            self.assertTrue(attempt.successful)
        self.assertListEqual([attempt.value for attempt in action.attempts], results)

    @patch('requests.Session.send')
    def test_can_show_effort_if_successful(self, mock_session_send):
        outcomes = ['SUCCEEDED!']
        mock_session_send.side_effect = outcomes
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=self.max_retries,
            should_record=True,
            should_show_effort=True,
        )
        result = action.perform()
        effort = result.value

        self.assertIsInstance(effort, RetryPolicy.Effort)
        self.assertIsInstance(effort.culmination, Result)
        self.assertIsInstance(effort.culmination.value, str)
        self.assertEqual(repr(effort), '<Effort:succeeded>')
        for attempt in result.value.attempts:
            self.assertTrue(attempt.successful)
        self.assertListEqual([attempt.value for attempt in action.attempts], outcomes)

    @patch('requests.Session.send')
    def test_can_show_effort_if_unsuccessful(self, mock_session_send):
        outcomes = [Exception('failed.')] * (self.max_retries + 1)
        mock_session_send.side_effect = outcomes
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=self.max_retries,
            should_record=True,
            should_show_effort=True,
        )
        result = action.perform()
        effort = result.value

        self.assertIsInstance(effort, RetryPolicy.Effort)
        self.assertIsInstance(effort.culmination, Result)
        self.assertIsInstance(effort.culmination.value, RetryPolicy.Expired)
        self.assertEqual(repr(effort), '<Effort:failed:retries>')
        for attempt in effort.attempts:
            self.assertFalse(attempt.successful)
        self.assertListEqual([attempt.value for attempt in action.attempts], outcomes)

    @patch('requests.Session.send')
    def test_can_enact_with_linear_backoff(self, mock_session_send):
        delay = 0.2  # seconds
        delay_microseconds = delay * 1E6
        mock_session_send.side_effect = [Exception('failed.')] * (self.max_retries + 1)
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=4,
            delay_between_attempts=delay,
            backoff='LINEAR',
            should_record=True,
        )
        result = action.perform(timestamp_provider=lambda: round(datetime.now().timestamp()))
        times = [
            attempt.produced_at - action.attempts[i - 1].produced_at
            for i, attempt in reversed(list(enumerate(action.attempts))) if i != 0
        ]

        self.assertFalse(result.successful)
        expected_target_factors = [4.0, 3.0, 2.0, 1.0]  # linear sequence
        actual_target_factors = []
        for time in times:
            fraction = time / delay_microseconds
            target_factor = round(fraction) * delay_microseconds
            actual_target_factors.append(target_factor // delay_microseconds)
            actual_jitter_percentage = time / (target_factor * delay_microseconds)
            self.assertLessEqual(actual_jitter_percentage, action.jitter_percentage)
        self.assertListEqual(actual_target_factors, expected_target_factors)

    @patch('requests.Session.send')
    def test_can_enact_with_exponential_backoff(self, mock_session_send):
        delay = 0.2  # seconds
        delay_microseconds = delay * 1E6
        mock_session_send.side_effect = [Exception('failed.')] * (self.max_retries + 1)
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=4,
            delay_between_attempts=delay,
            backoff='EXPONENTIAL',
            should_record=True,
        )
        result = action.perform(timestamp_provider=lambda: round(datetime.now().timestamp()))
        times = [
            attempt.produced_at - action.attempts[i - 1].produced_at
            for i, attempt in reversed(list(enumerate(action.attempts))) if i != 0
        ]

        self.assertFalse(result.successful)
        expected_target_factors = [8.0, 4.0, 2.0, 1.0]  # exponential sequence
        actual_target_factors = []
        for time in times:
            fraction = time / delay_microseconds
            target_factor = round(fraction) * delay_microseconds
            actual_target_factors.append(target_factor // delay_microseconds)
            actual_jitter_percentage = time / (target_factor * delay_microseconds)
            self.assertLessEqual(actual_jitter_percentage, action.jitter_percentage)
        self.assertListEqual(actual_target_factors, expected_target_factors)

    @patch('requests.Session.send')
    def test_delay_is_bypassed_after_expiration(self, mock_session_send):
        results = ['SUCCEEDED!']
        delay = 300  # seconds
        mock_session_send.side_effect = results
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=0,
            delay_between_attempts=delay,
            should_record=True,
        )
        timestamp_provider = lambda: round(datetime.now().timestamp())
        result = action.perform(timestamp_provider=timestamp_provider)
        assert result.produced_at < timestamp_provider() + delay

    def test_instantiation_fails_given_invalid_max_retries(self):
        action = RetryPolicy[str, str](action=MakeRequest('GET', 'http://localhost'), max_retries=-1)
        self.assertIsInstance(action, Action.Construct)
        result = action.perform()
        self.assertFalse(result.successful)
        self.assertIsInstance(result.value, RetryPolicy.Invalid)

    @patch('requests.Session.send')
    def test_can_serialize(self, mock_session_send):
        action = RetryPolicy[str, str](
            action=MakeRequest('GET', 'http://localhost'),
            max_retries=0,
        )
        self.assertEqual(repr(action), '<RetryPolicy(1 x <MakeRequest>)>')
        self.assertEqual(repr(self.action), '<RetryPolicy(3 x <MakeRequest>)>')

    @patch('requests.Session.send')
    def test_can_pickle(self, mock_session_send):
        mock_session_send.side_effect = NotImplemented
        self.assertTrue(pickleable(self.action))

        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
