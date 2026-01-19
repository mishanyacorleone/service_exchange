from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile


class AccountViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_customer = User.objects.create_user(username='customer', password='qwerty123____')
        self.profile_customer = UserProfile.objects.create(user=self.user_customer, role='customer')

        self.user_executor = User.objects.create_user(username='executor', password='qwerty123____')
        self.profile_executor = UserProfile.objects.create(user=self.user_executor, role='executor')

    def test_register_view_GET(self):
        """GET запрос на /register"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Роль')

    def test_register_view_POST_valid(self):
        """Успешная регистрация и редирект на страницуу home"""
        response = self.client.post(reverse('register'), {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'qwerty123____',
            'password2': 'qwerty123____',
            'role': 'executor'
        })
        self.assertRedirects(response, reverse('home'))

        self.assertTrue(User.objects.filter(username='test').exists())
        test_user = User.objects.get(username='test')
        self.assertTrue(UserProfile.objects.filter(user=test_user).exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_view(self):
        """Проверка на доступность страницы логина для гостя"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_anonim(self):
        """Проверка на доступность страницы просмотра профиля анониму"""
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_profile_view_authenticated(self):
        """Доступность просмотра профиля авторизованномуу пользователю"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'customer')

    def test_profile_update_GET(self):
        """Доступность страницы /update для авторизованного пользователя"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.get(reverse('update'))
        self.assertEqual(response.status_code, 200)

    def test_profile_update_POST(self):
        """Доступность страницы POST запроса для /update"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.post(reverse('update'), {
            'first_name': 'Миша',
            'last_name': 'Кардаш',
            'email': 'difmail@example.com',
            'specialization': 'ML',
            'portfolio': 'https://example.com'
        })
        self.assertRedirects(response, reverse('profile'))

        self.user_customer.refresh_from_db()
        self.profile_customer.refresh_from_db()
        self.assertEqual(self.user_customer.first_name, 'Миша')
        self.assertEqual(self.user_customer.last_name, 'Кардаш')