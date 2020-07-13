from django.test import TestCase
from django.core.exceptions import ValidationError
from django.conf import settings
from core import models
from core.tests.user_test_utils import sample_user
from unittest.mock import patch
import random


class ModelTests(TestCase):
    def test_order_representation(self):
        order_owner = sample_user()
        order = models.Order.objects.create(
            user=order_owner,
            notes='Order notes',
            delivery_time=5,
            price=10.0,
        )

        self.assertEqual(str(order), f'Order ID: {order.id}')

    def test_create_order_success(self):
        order_owner = sample_user()
        other_owner = sample_user(email='test2@test.com')
        third_owner = sample_user(email='test3@test.com')

        notes = 'Order notes'
        delivery_time = 5
        price = 10.0
        link = 'link to order'

        item1 = models.Item.objects.create(
            user=order_owner,
            name='Item 1'
        )
        item2 = models.Item.objects.create(
            user=other_owner,
            name='Item 2'
        )
        tag1 = models.Tag.objects.create(
            user=order_owner,
            name='Tag 1'
        )
        tag2 = models.Tag.objects.create(
            user=third_owner,
            name='Tag 2'
        )

        order = models.Order.objects.create(
            user=order_owner,
            notes=notes,
            delivery_time=delivery_time,
            price=price,
            link=link,
        )

        order.items.add(item1.id)
        order.items.add(item2.id)
        order.tags.add(tag1.id)
        order.tags.add(tag2.id)

        self.assertEqual(order.notes, notes)
        self.assertEqual(order.delivery_time, delivery_time)
        self.assertEqual(order.price, price)
        self.assertEqual(order.link, link)
        self.assertEqual(len(order.items.all()), 2)
        self.assertEqual(len(order.tags.all()), 2)

    def test_create_order_fail(self):
        order_owner = sample_user()
        notes = 'Order notes'
        delivery_time = 2
        price = 10.0
        link = 'link to order'

        order = models.Order.objects.create(
            user=order_owner,
            notes=notes,
            delivery_time=delivery_time,
            price=price,
            link=link,
        )

        self.assertRaises(
            ValidationError,
            order.full_clean,
        )

    @patch('uuid.uuid4')
    def test_order_image_file_name(self, mock_uuid):
        uuid = 'test'
        mock_uuid.return_value = uuid
        extension = random.choice(['jpg', 'png', 'svg'])

        file_path = models.order_image_file_name(None, f'image.{extension}')
        expected_path = f'{settings.BASE_UPLOAD_PATH}/{uuid}.{extension}'

        self.assertEqual(file_path, expected_path)

