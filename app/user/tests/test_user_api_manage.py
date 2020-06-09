from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from user.tests.user_api_utils import create_user

MANAGE_URL = reverse('user:manage')


class PublicUserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(MANAGE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'name': 'Name',
            'email': 'test@test.com',
            'password': 'password'
        }
        self.user = create_user(**self.user_data)

        self.client.force_authenticate(user=self.user)

    def test_get_profile_success(self):
        response = self.client.get(MANAGE_URL)
        expected_response = self.user_data.copy()
        del expected_response['password']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_path_profile_success(self):
        patch_payload = {
            'name': 'New name',
            'email': 'new@test.com',
            'password': 'new password'
        }
        patch_payload_no_password = patch_payload.copy()
        del patch_payload_no_password['password']

        response = self.client.patch(MANAGE_URL, patch_payload)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key, value in patch_payload_no_password.items():
            self.assertEqual(value, getattr(self.user, key))

        self.assertTrue(self.user.check_password(patch_payload['password']))

    def test_post_not_allowed(self):
        response = self.client.post(MANAGE_URL)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
