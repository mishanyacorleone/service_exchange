from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from orders.models import Order


class XSSTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test',
            first_name='<script>alert("xss")</script>',
            last_name='test',
            email='test@example.com',
            password='qwerty123____'
        )

        UserProfile.objects.create(
            user=self.user,
            role='customer',
            specialization='"><img src=x onerror=alert(1)>',
            portfolio='<iframe src="javascript:alert(2)"></iframe>'
        )

        self.order = Order.objects.create(
            title='Order with <b>XSS</b>',
            description='Description with <script>console.log("xss")</script>',
            customer=self.user
        )

        self.client.login(username='test', password='qwerty123____')

    def test_xss_in_profile_page(self):
        """XSS-полезная нагрузка в профиле должна быть экранирована"""
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;', content)
        self.assertIn('&quot;&gt;&lt;img src=x onerror=alert(1)&gt;', content)
        self.assertIn('&lt;iframe src=&quot;javascript:alert(2)&quot;&gt;&lt;/iframe&gt;', content)

    def test_xss_in_order_detail(self):
        """XSS в заказе должен быть экранирован"""
        url = reverse('order_detail', kwargs={'order_id': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('Order with &lt;b&gt;XSS&lt;/b&gt;', content)
        self.assertIn('Description with &lt;script&gt;console.log(&quot;xss&quot;)&lt;/script&gt;', content)