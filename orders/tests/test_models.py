from django.test import TestCase
from django.contrib.auth.models import User
from orders.models import Order, Bid


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='cust', password='123')
        self.executor = User.objects.create_user(username='exec', password='123')
        self.order = Order.objects.create(
            title='Fix bug',
            description='Urgent fix',
            customer=self.customer,
            status='open'
        )

    def test_order_creation(self):
        self.assertEqual(self.order.title, 'Fix bug')
        self.assertEqual(self.order.customer.username, 'cust')
        self.assertIsNotNone(self.order.created_at)

    def test_bid_unique_together(self):
        Bid.objects.create(order=self.order, executor=self.executor, price_proposal=100)
        with self.assertRaises(Exception):
            Bid.objects.create(order=self.order, executor=self.executor, price_proposal=200)

    def test_allowed_status_transitions(self):
        self.assertIn('in_progress', dict(self.order.get_allowed_status_transitions()).keys())