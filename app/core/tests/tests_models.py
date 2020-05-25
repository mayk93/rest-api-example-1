from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class ModelTests(TestCase):
    def test_creat_with_email_successful(self):
        email = 'test@test.com'
        password = 'password'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalization(self):
        email = 'test@TEST.com'

        user = get_user_model().objects.create_user(email=email)

        self.assertEqual(user.email, email.lower())

    def test_email_validation_success(self):
        email = 'test@test.com'
        user = get_user_model().objects.create_user(email=email)
        self.assertEqual(user.email, email)

    def test_email_validation_fail(self):
        email = ''
        self.assertRaises(
            ValidationError,
            get_user_model().objects.create_user,
            email
        )
