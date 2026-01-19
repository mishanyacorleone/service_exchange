# accounts/tests/test_security.py
from django.test import TestCase
from django.contrib.auth.models import User


class PasswordSecurityTest(TestCase):
    def test_password_is_hashed(self):
        """Пароль должен быть хеширован, а не храниться в открытом виде"""
        password = "admin123"
        user = User.objects.create_user(
            username='test',
            password=password
        )

        self.assertNotEqual(user.password, password)

        self.assertTrue(user.check_password(password))

        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))