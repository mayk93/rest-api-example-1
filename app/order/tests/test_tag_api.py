from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
from order.serializers import TagSerializer
from core.tests.user_test_utils import create_user

TAG_URL = reverse('order:tag-list')


class PublicTagAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'name': 'Name',
            'email': 'test@test.com',
            'password': 'password'
        }
        self.user = create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_get_tags_success(self):
        Tag.objects.create(user=self.user, name='Priority')
        Tag.objects.create(user=self.user, name='VIP')

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        response = self.client.get(TAG_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_get_tags_user_specific(self):
        other_user_data = self.user_data.copy()
        other_user_data['email'] = 'other@test.com'
        other_user = create_user(**other_user_data)

        tag = Tag.objects.create(
            user=self.user,
            name='First User Tag'
        )
        Tag.objects.create(user=other_user, name='Other User Tag')

        response = self.client.get(TAG_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_post_tag_success(self):
        payload = {'name': 'Priority'}

        response = self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_post_tag_fail(self):
        payload = {}

        response = self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=None
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(exists)
