from django.test import TestCase
from core import models
from core.tests.user_test_utils import sample_user


class ModelTests(TestCase):
    def test_item_representation(self):
        item_owner = sample_user()
        item = models.Item.objects.create(
            user=item_owner,
            name='Item'
        )

        self.assertEqual(str(item), item.name)
