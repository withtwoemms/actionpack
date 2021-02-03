from actionpack.actions import MakeRequest
from tests.actionpack.actions import FakeResponse

from requests import Response
from requests.exceptions import MissingSchema
from oslash import Left
from oslash import Right
from unittest import TestCase
from unittest.mock import patch
from validators import ValidationFailure


class MakeRequestTest(TestCase):

    @patch('requests.Session.send')
    def test_can_MakeRequest(self, mock_session_send):
        mock_session_send.return_value = FakeResponse()
        action = MakeRequest('GET', 'http://localhost')
        result = action.perform()

        self.assertIsInstance(result, Right)

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

    def test_failed_MakeRequest_construction_raises(self):
        with self.assertRaises(MissingSchema):
            MakeRequest('GET', 'localhost')

