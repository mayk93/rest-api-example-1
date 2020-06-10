from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Item
from order.serializers import ItemSerializer
from core.tests.user_test_utils import create_user

ITEMS_URL = reverse('order:item-list')


class PublicItemAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(ITEMS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateItemAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'name': 'Name',
            'email': 'test@test.com',
            'password': 'password'
        }
        self.user = create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_get_items_success(self):
        Item.objects.create(user=self.user, name='Item 1')
        Item.objects.create(user=self.user, name='Item 2')

        items = Item.objects.all().order_by('-name')
        serializer = ItemSerializer(items, many=True)

        response = self.client.get(ITEMS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_get_items_user_specific(self):
        other_user_data = self.user_data.copy()
        other_user_data['email'] = 'other@test.com'
        other_user = create_user(**other_user_data)

        item = Item.objects.create(user=self.user, name='Item 1')
        Item.objects.create(user=other_user, name='Item 2')

        response = self.client.get(ITEMS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], item.name)
