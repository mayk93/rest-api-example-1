from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

admin_email = 'admin@test.com'
admin_password = 'password'

regular_email = 'regular@test.com'
regular_password = 'password'
regular_name = 'Name'


class AdminTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            email=admin_email,
            password=admin_password
        )
        self.regular_user = get_user_model().objects.create_superuser(
            email=regular_email,
            password=regular_password,
            name=regular_name
        )

        self.client.force_login(self.admin_user)
        self.client.force_login(self.admin_user)

    def test_users_listed(self):
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.regular_user.name)
        self.assertContains(response, self.regular_user.email)

    def test_user_change_page(self):
        url = reverse('admin:core_user_change', args=[self.regular_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
