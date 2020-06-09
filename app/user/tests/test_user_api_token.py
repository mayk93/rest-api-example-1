from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from user.tests.user_api_utils import create_user

TOKEN_URL = reverse('user:token')

payload = {
    'email': 'test@test.com',
    'password': 'password',
}


class PublicUserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_token_valid_credentials(self):
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials_email(self):
        create_user(**payload)

        bad_payload = payload.copy()
        bad_payload['email'] = 'not_the_right_email@email.com'

        response = self.client.post(TOKEN_URL, bad_payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_invalid_credentials_password(self):
        create_user(**payload)

        bad_payload = payload.copy()
        bad_payload['password'] = 'not_the_right_password'

        response = self.client.post(TOKEN_URL, bad_payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_invalid_credentials_missing_email(self):
        create_user(**payload)

        bad_payload = payload.copy()
        del bad_payload['email']

        response = self.client.post(TOKEN_URL, bad_payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_invalid_credentials_missing_password(self):
        create_user(**payload)

        bad_payload = payload.copy()
        del bad_payload['password']

        response = self.client.post(TOKEN_URL, bad_payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
