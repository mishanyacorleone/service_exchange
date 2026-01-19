from django.test import TestCase
from django.contrib.auth.models import User
from orders.forms import OrderForm, BidForm
from orders.models import Order


class OrderFormTest(TestCase):
    def test_order_form_valid_data(self):
        """Тестирование формы заказа с корректными данными"""
        form_data = {
            'title': 'Название',
            'description': 'Описание',
            'deadline': '2026-12-31 23:59:59',
            'budget': '15000.00'
        }

        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_order_form_without_title(self):
        form_data = {
            'description': 'Описание',
            'deadline': '2025-12-31 23:59:59',
            'budget': '15000.00'
        }

        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        pass

    def test_order_form_with_invalid_budget(self):
        form_data = {
            'title': 'Название',
            'description': 'Описание',
            'deadline': '2025-12-31 23:59:59',
            'budget': '-500000000000.00'
        }

        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        pass

    def test_order_form_with_invalid_data(self):
        form_data = {
            'title': 'Название',
            'description': 'Описание',
            'deadline': '2025-12-31 23:59:59',
            'budget': '15000.00'
        }

        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        pass


class BidFormTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='qwerty123')
        self.order = Order.objects.create(
            title='Название',
            description='Описание',
            customer=self.customer
        )

    def test_bid_form_valid_data(self):
        """Тестирование на форму с валидными данными"""
        form_data = {
            'message': 'Сообщение',
            'price_proposal': '5000.00'
        }
        form = BidForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_bid_form_negative_price(self):
        """Тестирование с отрицательной ценой"""
        form_data = {
            'message': 'Сообщение',
            'price_proposal': '-5000.00'
        }
        form = BidForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_bid_form_without_message_and_price(self):
        form_data = {}
        form = BidForm(data=form_data)
        self.assertTrue(form.is_valid())