import os
import tempfile
from PIL import Image

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


def order_image_url(order_id):
    return reverse('order:order-upload-image', args=[order_id])


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

    def test_post_order_basic_success(self):
        payload = {
            'notes': 'New Order',
            'delivery_time': 5,
            'price': 10.0,
            'link': 'link'
        }
        self.order_post_test(payload)

    def test_post_order_extra_success(self):
        item = sample_item(user=self.user)
        tag = sample_tag(user=self.user)
        payload = {
            'notes': 'New Order',
            'delivery_time': 5,
            'price': 10.0,
            'link': 'link',
            'items': [item.id],
            'tags': [tag.id]
        }

        self.order_post_test(payload)

    def order_post_test(self, payload):
        initial_exists = Order.objects.filter(
            user=self.user,
        ).exists()

        response = self.client.post(ORDER_URL, payload)

        exists = Order.objects.filter(
            user=self.user,
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(initial_exists)
        self.assertTrue(exists)

        order = Order.objects.get(id=response.data['id'])

        for key in payload.keys():
            if key not in ['items', 'tags']:
                self.assertEqual(payload[key], getattr(order, key))
            else:
                items = order.items.all()
                tags = order.tags.all()

                if payload['items']:
                    self.assertEqual(payload['items'], [i.id for i in items])
                if payload['tags']:
                    self.assertEqual(payload['tags'], [t.id for t in tags])

    def test_post_order_fail(self):
        payload = {
            'notes': 'New Order',
            'delivery_time': 8,
            'price': 10.0,
            'link': 'link'
        }

        response = self.client.post(ORDER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_success(self):
        patch_payload = {
            'notes': 'Update Order',
        }

        order = sample_order(self.user)

        self.assertNotEqual(order.notes, patch_payload['notes'])

        response = self.client.patch(order_detail_url(order.id), patch_payload)
        order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.notes, patch_payload['notes'])

    def test_filter_order_by_tags(self):
        order_1 = sample_order(self.user)
        order_2 = sample_order(self.user)

        tag_1 = sample_tag(user=self.user)
        tag_2 = sample_tag(user=self.user)

        order_1.tags.add(tag_1)
        order_2.tags.add(tag_2)

        response_1 = self.client.get(ORDER_URL, {'tags': tag_1.id})
        response_2 = self.client.get(ORDER_URL, {'tags': tag_2.id})

        order_1_serializer = OrderSerializer(order_1)
        order_2_serializer = OrderSerializer(order_2)

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_1.data), 1)
        self.assertEqual(
            response_1.data[0]['tags'], order_1_serializer.data['tags']
        )

        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_2.data), 1)
        self.assertEqual(
            response_2.data[0]['tags'], order_2_serializer.data['tags']
        )

    def test_filter_order_by_items(self):
        order_1 = sample_order(self.user)
        order_2 = sample_order(self.user)

        item_1 = sample_item(user=self.user)
        item_2 = sample_item(user=self.user)

        order_1.items.add(item_1)
        order_2.items.add(item_2)

        response_1 = self.client.get(ORDER_URL, {'items': item_1.id})
        response_2 = self.client.get(ORDER_URL, {'items': item_2.id})

        order_1_serializer = OrderSerializer(order_1)
        order_2_serializer = OrderSerializer(order_2)

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_1.data), 1)
        self.assertEqual(
            response_1.data[0]['items'], order_1_serializer.data['items']
        )

        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_2.data), 1)
        self.assertEqual(
            response_2.data[0]['items'], order_2_serializer.data['items']
        )


class OrderImageAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

        self.order = sample_order(self.user)
        self.order_image_url = order_image_url(self.order.id)

    def tearDown(self):
        self.order.image.delete()

    def test_image_success(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            test_image = Image.new('RGB', (10, 10))
            test_image.save(ntf, format='JPEG')
            ntf.seek(0)

            payload = {'image': ntf}

            response = self.client.post(
                self.order_image_url,
                payload,
                format='multipart'
            )

            self.order.refresh_from_db()

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn('image', response.data)
            self.assertTrue(os.path.exists(self.order.image.path))

    def test_image_fail(self):
        payload = {'image': None}
        response = self.client.post(
            self.order_image_url,
            payload,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
