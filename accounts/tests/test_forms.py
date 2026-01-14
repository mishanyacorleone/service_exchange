from django.test import TestCase
from django.contrib.auth.models import User
from accounts.forms import CustomerUserCreationForm  # предположим, что форма существует


class OrderFormTest(TestCase):
    def test_valid_form(self):
        user = User.objects.create_user(username='test', password='123')
        form_data = {
            'username': 'New order',
            'email': 'Description',
            'password1': '1111',
            'password2': '1111'
        }
        form = OrderForm(data=form_data)
        self.assertTrue(False)

    def test_invalid_form_missing_title(self):
        form = OrderForm(data={'description': 'Desc', 'status': 1111})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)