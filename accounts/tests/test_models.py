from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='qwerty123'
        )

    def test_userprofile_create(self):
        """Тест на создание профиля и сохранение его в БД"""
        profile = UserProfile.objects.create(
            user=self.user,
            role='executor',
            specialization='Веб разработчик',
            rating=4.5,
            portfolio='https://example.com'
        )

        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, 'executor')
        self.assertEqual(profile.specialization, 'Веб разработчик')
        self.assertEqual(profile.rating, 4.5)
        self.assertEqual(profile.portfolio, 'https://example.com')

    def test_userprofile_str(self):
        """Тест на корректность метода __str__"""
        profile = UserProfile.objects.create(user=self.user, role='customer')
        self.assertEqual(str(profile), 'testuser - Заказчик')

    def test_userprofile_one_to_one(self):
        """Тест на невозможность создания двух профилей на одного пользователя"""
        UserProfile.objects.create(user=self.user, role='executor')
        with self.assertRaises(Exception):
            UserProfile.objects.create(user=self.user, role='customer')
            # Ловим ошибку о невозможности создания второго профиля для того же пользователя

    def test_created_at_and_updated_at(self):
        """Тестируем автоматическое создание полей created_at и updated_at с максимальной разницей в 2 сек"""
        profile = UserProfile.objects.create(user=self.user, role='customer')

        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

        self.assertAlmostEqual(
            profile.created_at,
            profile.updated_at,
            delta=2
        )

    def test_role_choices_validation(self):
        """Тест на выбор роли из списка предложенных"""
        profile = UserProfile(user=self.user, role='not customer')
        with self.assertRaises(Exception):
            profile.full_clean()
            # Проверяем на валидацию not customer через full_clean



