from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Order
from order.serializers import OrderSerializer, OrderDetailSerializer

from core.tests.user_test_utils import sample_user
from core.tests.order_test_utils import sample_order, sample_item, sample_tag

ORDER_URL_BASE = 'order:order-list'
ORDER_URL = reverse(ORDER_URL_BASE)


def order_detail_url(order_id):
    return reverse('order:order-detail', args=[order_id])


class PublicOrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_get_orders_success(self):
        sample_order(user=self.user, notes='Order notes 1')
        sample_order(user=self.user, notes='Order notes 2')

        orders = Order.objects.all().order_by('-id')
        serializer = OrderSerializer(orders, many=True)

        response = self.client.get(ORDER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_get_orders_user_specific(self):
        other_user = sample_user(email='test2@test.com')

        order = sample_order(user=self.user, notes='Order notes 1')
        sample_order(user=other_user, notes='Order notes 2')

        response = self.client.get(ORDER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['notes'], order.notes)

    def test_order_detail(self):
        order = sample_order(user=self.user, notes='Order notes 1')
        item_1 = sample_item(user=self.user)
        item_2 = sample_item(user=self.user, name='Item 2')
        tag = sample_tag(user=self.user)

        order.items.add(item_1)
        order.items.add(item_2)
        order.tags.add(tag)

        url = order_detail_url(order.id)

        response = self.client.get(url)

        serializer = OrderDetailSerializer(order)

        self.assertEqual(serializer.data, response.data)
