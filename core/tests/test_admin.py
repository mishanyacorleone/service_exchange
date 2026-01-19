from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from orders.models import Order, Bid


class AdminAccessTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='test', password='qwerty123____')
        UserProfile.objects.create(user=self.user, role='customer')

        self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123____')

        self.order = Order.objects.create(title='Название', description='Описание', customer=self.user, status='open')

    def test_admin_login_page_accessible(self):
        """Страница входа в админку не доступна гостю"""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_access_admin(self):
        """Проверка на то что обычный пользователь не может войти в админку"""
        self.client.login(username='test', password='qwerty123____')
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django administration')

    def test_superuser_can_access_admin(self):
        """Проверка на то что суперпользователь может войти в админку"""
        self.client.login(username='admin', password='admin123____')
        response = self.client.get('/admin/auth/user/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')
        self.assertContains(response, 'admin')

    def test_superuser_can_view_userprofile_list(self):
        """Проверка на то что админ видит профили пользователей"""
        self.client.login(username='admin', password='admin123____')
        response = self.client.get('/admin/accounts/userprofile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'customer')

    def test_superuser_can_view_order_list(self):
        """Проверка на то что админ видит список заказов"""
        self.client.login(username='admin', password='admin123____')
        response = self.client.get('/admin/orders/order/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Название')

    def test_superuser_can_view_bid_list(self):
        """Проверка на то что админ видит отклики"""
        self.client.login(username='admin', password='admin123____')
        response = self.client.get('/admin/orders/bid/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_export_userprofile(self):
        """Проверка наличия кнопки экспорта через админку"""
        self.client.login(username='admin', password='admin123____')
        response = self.client.get('/admin/accounts/userprofile/')
        self.assertContains(response, 'export')

    def test_superuser_can_export_order(self):
        """Проверка наличия кнопки экспорта через админку уже в заказах"""
        self.client.login(username='admin', password='admin123____')
        response = self.client.get('/admin/orders/order/')
        self.assertContains(response, 'export')
