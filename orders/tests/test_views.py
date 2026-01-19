from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from orders.models import Order, Bid
from accounts.models import UserProfile


class OrdersViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(username='customer', password='qwerty123____')
        UserProfile.objects.create(user=self.customer, role='customer')

        self.executor = User.objects.create_user(username='executor', password='qwerty123____')
        UserProfile.objects.create(user=self.executor, role='executor')

        self.order = Order.objects.create(
            title='Название',
            description='Описание',
            customer=self.customer,
            status='open',
            deadline='2026-12-31 23:59:59',
            budget=5000.00
        )

    def test_order_list_anonymous(self):
        """Проверка возможности гостя видеть список заказов"""
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Название')

    def test_executor_list_anonymous(self):
        """Проверка возможности гостя видеть список исполнителей"""
        response = self.client.get(reverse('executor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'executor')

    def test_my_orders_anonymous(self):
        """Проверка доступности у гостя его заказов"""
        response = self.client.get(reverse('my_orders'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('my_orders')}")

    def test_orders_non_customer(self):
        """При входе в my_orders исполнителя, вылетает 403 статус код"""
        self.client.login(username='executor', password='qwerty123____')
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 403)

    def test_orders_customer(self):
        """При входе в my_orders заказчика, вылетает 200 статус код"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Название')

    def test_assigned_orders_executor(self):
        """Исполнитель видит назначенные ему заказы"""
        self.order.assigned_executor = self.executor
        self.order.status = 'in_progress'
        self.order.save()

        self.client.login(username='executor', password='qwerty123____')
        response = self.client.get(reverse('my_assigned_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Название')

    def test_assigned_orders_customer(self):
        """Заказчик не может войти в назначенные заказы"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.get(reverse('my_assigned_orders'))
        self.assertEqual(response.status_code, 403)

    def test_order_detail_anonymous(self):
        """Гость не может видеть детали заказа"""
        response = self.client.get(reverse('order_detail', kwargs={'order_id': self.order.id}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('order_detail', kwargs={'order_id': self.order.id})}")

    def test_create_order_anonymous(self):
        """Гость не может создать заказ"""
        response = self.client.post(reverse('create_order'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('create_order')}")

    def test_create_order_executor(self):
        """Исполнитель не может создать заказ"""
        self.client.login(username='executor', password='qwerty123____')
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 403)

    def test_create_order_customer_GET(self):
        """GET запрос на создание заказа от заказчика"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 200)

    def test_create_order_customer_POST(self):
        """POST запрос на создание заказа от заказчика"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.post(reverse('create_order'), {
            'title': 'Название2',
            'description': 'Описание',
            'deadline': '2026-12-31 23:59:59',
            'budget': '15000.00'
        })
        self.assertRedirects(response, reverse('my_orders'))
        self.assertTrue(Order.objects.filter(title='Название2').exists())

    def test_edit_order_owner(self):
        """Владелец заказа может редактировать заказ"""
        self.client.login(username='customer', password='qwerty123____')
        response = self.client.post(reverse('edit_order', kwargs={'order_id': self.order.id}), {
            'title': 'Обновлённый заказ',
            'description': 'Новое описание',
            'deadline': '2026-12-31 23:59:59',
            'budget': '20000.00'
        })
        self.assertRedirects(response, reverse('order_detail', kwargs={'order_id': self.order.id}))

        self.order.refresh_from_db()
        self.assertEqual(self.order.title, 'Обновлённый заказ')

    def test_edit_order_no_owner(self):
        """Попытка редактирования чужого заказа"""
        other_user = User.objects.create_user(username='other', password='qwerty123____')
        UserProfile.objects.create(user=other_user, role='customer')
        self.client.login(username='other', password='qwerty123____')
        response = self.client.get(reverse('edit_order', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 403)

    def test_bid_submission_by_executor(self):
        """Исполнитель отправляет отклик"""
        self.client.login(username='executor', password='qwerty123____')
        response = self.client.post(reverse('order_detail', kwargs={'order_id': self.order.id}),
                                    {'message': 'Сообщение', 'price_proposal': '4500.00'})
        self.assertRedirects(response, reverse('order_detail', kwargs={'order_id': self.order.id}))
        self.assertTrue(Bid.objects.filter(order=self.order, executor=self.executor).exists())

    def test_bid_duplicate_not_allowed(self):
        """Проверка на то, что второй отклик не создается"""
        Bid.objects.create(order=self.order, executor=self.executor, message='Сообщение')
        self.client.login(username='executor', password='qwerty123____')

        response = self.client.post(
            reverse('order_detail', kwargs={'order_id': self.order.id}),
            {'message': 'Сообщение', 'price_proposal': '4500.00'}
        )

    def test_assigned_executor_by_customer(self):
        """Проверка на логику назначения статуса in_progress"""
        Bid.objects.create(order=self.order, executor=self.executor)

        self.client.login(username='customer', password='qwerty123____')
        response = self.client.post(
            reverse('order_detail', kwargs={'order_id': self.order.id}),
            {'assign_executor': '1', 'executor_id': self.executor.id}
        )
        self.assertRedirects(response, reverse('order_detail', kwargs={'order_id': self.order.id}))

        self.order.refresh_from_db()
        self.assertEqual(self.order.assigned_executor, self.executor)
        self.assertEqual(self.order.status, 'in_progress')
