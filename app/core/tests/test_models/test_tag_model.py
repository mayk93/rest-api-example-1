from django.test import TestCase
from core import models
from core.tests.user_test_utils import sample_user


class ModelTests(TestCase):
    def test_tag_representation(self):
        tag_owner = sample_user()
        tag = models.Tag.objects.create(
            user=tag_owner,
            name='Priority'
        )

        self.assertEqual(str(tag), tag.name)
