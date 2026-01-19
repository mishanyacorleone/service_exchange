from django.test import TestCase
from django.contrib.auth.models import User
from orders.models import Order, Bid


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='pass')
        self.executor = User.objects.create_user(username='executor', password='pass')

    def test_create_order(self):
        """Тест на создание заказа"""
        order = Order.objects.create(
            title='Заказ',
            description='Описание',
            customer=self.customer,
            status='open',
            budget=5000.00
        )

        self.assertIsInstance(order, Order)
        self.assertEqual(order.title, 'Заказ')
        self.assertEqual(order.description, 'Описание')
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, 'open')
        self.assertEqual(order.budget, 5000.00)

    def test_order_str(self):
        """Проверка переопределенного метода __str__"""
        order = Order.objects.create(title='Название', description='Описание', customer=self.customer)
        self.assertEqual(str(order), 'Название')

    def test_order_foreign_key_customer(self):
        """Проверка на связь ForeignKey c заказчиком"""
        order = Order.objects.create(title='Название', description='Описание', customer=self.customer)
        self.assertEqual(order.customer.username, 'customer')

    def test_order_assigned_executor_is_null(self):
        """Тест на то что исполнитель может быть null"""
        order = Order.objects.create(title='Название', description='Описание', customer=self.customer)
        self.assertIsNone(order.assigned_executor)

    def test_order_status_transition_method(self):
        """Проверка созданного метода get_allowed_status_transitions"""
        order = Order.objects.create(title='Название', description='Описание', customer=self.customer, status='open')
        allowed = dict(order.get_allowed_status_transitions())
        self.assertIn('open', allowed)
        self.assertIn('in_progress', allowed)
        self.assertIn('cancelled', allowed)
        self.assertNotIn('completed', allowed)

    def test_created_at_and_updated_at(self):
        order = Order.objects.create(title='Название', description='Описание', customer=self.customer, status='open')
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)
        self.assertAlmostEqual(
            order.created_at,
            order.updated_at,
            delta=2
        )


class BidModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='pass')
        self.executor = User.objects.create_user(username='executor', password='pass')
        self.order = Order.objects.create(
            title='Название',
            description='Описание',
            customer=self.customer,
            status='open',
            budget=5000.00
        )

    def test_bid_create(self):
        """Проверка на создание отзыва"""
        bid = Bid.objects.create(order=self.order, executor=self.executor, message='Сообщение', price_proposal=4500.00)
        self.assertIsInstance(bid, Bid)
        self.assertEqual(bid.order, self.order)
        self.assertEqual(bid.executor, self.executor)
        self.assertEqual(bid.message, 'Сообщение')
        self.assertEqual(bid.price_proposal, 4500.00)

    def test_bid_unique_together_constraint(self):
        """Проверка на возможность отправки 2 отзывов на 1 заказ"""
        Bid.objects.create(order=self.order, executor=self.executor, message='Сообщение', price_proposal=4500.00)
        with self.assertRaises(Exception):
            Bid.objects.create(order=self.order, executor=self.executor, message='Сообщение', price_proposal=4000.00)

    def test_bid_foreign_keys(self):
        """Проверка на связь Order и User"""
        bid = Bid.objects.create(order=self.order, executor=self.executor, message='Сообщение', price_proposal=4500.00)
        self.assertEqual(bid.order.title, 'Название')
        self.assertEqual(bid.executor.username, 'executor')

    def test_bid_created_at_and_updated_at(self):
        bid = Bid.objects.create(order=self.order, executor=self.executor, message='Сообщение', price_proposal=4500.00)
        self.assertIsNotNone(bid.created_at)
        self.assertIsNotNone(bid.updated_at)
        self.assertAlmostEqual(
            bid.created_at,
            bid.updated_at,
            delta=2
        )
