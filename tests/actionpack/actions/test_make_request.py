import pickle

from actionpack.actions import MakeRequest
from actionpack.utils import pickleable
from tests.actionpack.actions import FakeResponse

from requests import Response
from requests.exceptions import MissingSchema
from oslash import Left
from oslash import Right
from unittest import TestCase
from unittest.mock import patch
from validators import ValidationFailure


class MakeRequestTest(TestCase):

    def setUp(self):
        self.action = MakeRequest('GET', 'http://localhost')

    @patch('requests.Session.send')
    def test_can_MakeRequest(self, mock_session_send):
        mock_session_send.return_value = FakeResponse()
        self.assertIsInstance(self.action.perform(), Right)

    @patch('requests.Session.send')
    def test_can_MakeRequest_even_if_failure(self, mock_session_send):
        mock_session_send.return_value = FakeResponse(status=500)

        first_action = MakeRequest('SUP', 'http://localhost')
        first_result = first_action.perform()
        self.assertIsInstance(first_result, Left)
        self.assertIsInstance(first_result.value, ValueError)

        second_action = MakeRequest('GET', 'http://some/invalid/url')
        second_result = second_action.perform()
        self.assertIsInstance(second_result, Left)
        self.assertIsInstance(second_result.value, ValidationFailure)

    def test_can_pickle(self):
        pickled = pickleable(self.action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(self.action))
        self.assertEqual(unpickled.__dict__, self.action.__dict__)

