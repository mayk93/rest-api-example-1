from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def get_user(**params):
    return get_user_model().objects.get(**params)


def get_user_exists(email):
    return get_user_model().objects.filter(email=email).exists()


payload = {
    'email': 'test@test.com',
    'password': 'password',
    'name': 'name'
}


class PublicUserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_valid_payload_does_not_exist_success(self):
        response = self.client.post(CREATE_USER_URL, payload)
        user = get_user(**response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.email, payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_create_user_valid_payload_already_exists_fail(self):
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_payload_fail(self):
        bad_payload = payload.copy()
        del bad_payload['password']

        response = self.client.post(CREATE_USER_URL, bad_payload)
        user_exists = get_user_exists(bad_payload['email'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    def test_create_user_short_password(self):
        bad_payload = payload.copy()
        bad_payload['password'] = 'pw'

        response = self.client.post(CREATE_USER_URL, bad_payload)
        user_exists = get_user_exists(bad_payload['email'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)
