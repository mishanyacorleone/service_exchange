from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from accounts.forms import CustomerUserCreationForm, ProfileUpdateForm
from accounts.models import UserProfile


class CustomerUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        """Тестирование формы с валидными данными"""
        form_data = {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'qwerty123____',
            'password2': 'qwerty123____',
            'role': 'customer'
        }
        form = CustomerUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_password(self):
        """Тестирование формы с невалидными данными"""
        form_data = {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'qwerty123____',
            'password2': 'qwerty123_____',
            'role': 'customer'
        }
        form = CustomerUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertIn('The two password fields didn’t match.', form.errors['password2'])

    def test_form_without_role(self):
        """Тестирование формы без роли"""
        form_data = {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'qwerty123____',
            'password2': 'qwerty123_____',
        }
        form = CustomerUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)

    def test_form_save_method(self):
        """Тестирование метода save() на создание User и UserProfile"""
        form_data = {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'qwerty123____',
            'password2': 'qwerty123____',
            'role': 'customer'
        }

        form = CustomerUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        profile = user.profile
        self.assertEqual(profile.role, 'customer')
        self.assertEqual(user.email, 'test@example.com')


class ProfileUpdateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            first_name='Миша',
            last_name='Кардаш',
            email='test@example.com'
        )
        self.profile = UserProfile.objects.create(user=self.user, role='executor')

    def test_form_valid_data(self):
        """Тестируем форму обновления профиля с корректными данными"""
        form_data = {
            'first_name': 'Михаил',
            'last_name': 'Не Кардаш',
            'email': 'difmail@example.com',
            'specialization': 'ML',
            'portfolio': 'https://example.com'
        }

        form = ProfileUpdateForm(data=form_data, profile_instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """Тестируем форму обновления профиля с невалидными данными"""
        form_data = {
            'first_name': 'М'*151,
            'last_name': 'Не Кардаш',
            'email': 'difmail@example.com',
            'specialization': 'ML',
            'portfolio': 'https://example.com'
        }

        form = ProfileUpdateForm(data=form_data, profile_instance=self.profile)
        self.assertFalse(form.is_valid())

    def test_form_save_method(self):
        """Тестирование метода save()"""
        form_data = {
            'first_name': 'Михаил',
            'last_name': 'Не Кардаш',
            'email': 'difmail@example.com',
            'specialization': 'ML',
            'portfolio': 'https://example.com'
        }

        form = ProfileUpdateForm(data=form_data, profile_instance=self.profile)
        self.assertTrue(form.is_valid())
        user = form.save()
        user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(user.first_name, 'Михаил')
        self.assertEqual(user.last_name, 'Не Кардаш')
        self.assertEqual(user.email, 'difmail@example.com')
        self.assertEqual(self.profile.specialization, 'ML')
        self.assertEqual(self.profile.portfolio, 'https://example.com')
