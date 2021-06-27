import pickle

from types import ModuleType
from unittest import TestCase
from unittest.mock import patch
from validators import ValidationFailure

from actionpack.action import Result
from actionpack.actions import MakeRequest
from actionpack.utils import pickleable
from tests.actionpack.actions import FakeResponse


class MakeRequestTest(TestCase):

    def setUp(self):
        self.action = MakeRequest('GET', 'http://localhost')

    @patch('requests.Session.send')
    def test_can_MakeRequest(self, mock_session_send):
        mock_session_send.return_value = FakeResponse()
        self.assertIsInstance(self.action.perform(), Result)

    @patch('requests.Session.send')
    def test_can_MakeRequest_even_if_failure(self, mock_session_send):
        mock_session_send.return_value = FakeResponse(status=500)

        first_action = MakeRequest('SUP', 'http://localhost')
        first_result = first_action.perform()
        self.assertIsInstance(first_result, Result)
        self.assertIsInstance(first_result.value, ValueError)

        second_action = MakeRequest('GET', 'http://some/invalid/url')
        second_result = second_action.perform()
        self.assertIsInstance(second_result, Result)
        self.assertIsInstance(second_result.value, ValidationFailure)

    @patch('requests.Session.send')
    def test_MakeRequest_has_portable_dependency(self, mock_session_send):
        mock_session_send.return_value = FakeResponse(status=500)

        self.action.perform()
        self.assertIsInstance(self.action.requests, ModuleType)

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)
