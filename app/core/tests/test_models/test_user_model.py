from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.tests.user_test_utils import create_user


class ModelTests(TestCase):
    def test_create_user_success(self):
        email = 'test@test.com'
        password = 'password'

        user = create_user(**{
            'email': email,
            'password': password
        })

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_success(self):
        email = 'superuser@test.com'
        password = 'password'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_email_normalization(self):
        email = 'test@TEST.com'

        user = create_user(**{'email': email})

        self.assertEqual(user.email, email.lower())

    def test_email_validation_success(self):
        email = 'test@test.com'
        user = create_user(**{'email': email})
        self.assertEqual(user.email, email)

    def test_email_validation_fail(self):
        email = ''
        self.assertRaises(
            ValidationError,
            create_user,
            **{'email': email}
        )
