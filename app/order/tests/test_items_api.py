from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Item
from order.serializers import ItemSerializer
from core.tests.user_test_utils import create_user
from core.tests.order_test_utils import sample_order, sample_item

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

    def test_post_item_success(self):
        payload = {'name': 'Item'}

        response = self.client.post(ITEMS_URL, payload)

        exists = Item.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_post_item_fail(self):
        payload = {}

        response = self.client.post(ITEMS_URL, payload)

        exists = Item.objects.filter(
            user=self.user,
            name=None
        ).exists()

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertFalse(exists)

    def test_filter_items_by_assignment(self):
        order = sample_order(user=self.user)

        item_1 = sample_item(user=self.user, name='Item 1')
        item_2 = sample_item(user=self.user, name='Item 2')

        order.items.add(item_1)

        response_1 = self.client.get(ITEMS_URL, {'assigned': 1})
        response_2 = self.client.get(ITEMS_URL)

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response_1.data), 1)
        self.assertEqual(len(response_2.data), 2)

        self.assertEqual(response_1.data[0]['name'], item_1.name)

        item_1_name_match = \
            response_2.data[0]['name'] == item_1.name or \
            response_2.data[1]['name'] == item_1.name
        item_2_name_match = \
            response_2.data[0]['name'] == item_2.name or \
            response_2.data[1]['name'] == item_2.name

        self.assertTrue(item_1_name_match)
        self.assertTrue(item_2_name_match)

    def test_filter_items_by_assignment_unique(self):
        order_1 = sample_order(user=self.user)
        order_2 = sample_order(user=self.user)

        item = sample_item(user=self.user, name='Item 1')
        sample_item(user=self.user, name='Item 2')

        order_1.items.add(item)
        order_2.items.add(item)

        response = self.client.get(ITEMS_URL, {'assigned': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
