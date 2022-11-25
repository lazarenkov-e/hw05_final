from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create()
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        users_count = User.objects.count()
        form_data = {
            'first_name': 'John',
            'last_name': 'Lennon',
            'username': 'test_name',
            'email': 'test@yandex.ru',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(username='test_name').exists())
        self.assertEqual(response.status_code, 200)
