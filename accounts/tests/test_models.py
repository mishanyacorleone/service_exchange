from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_profile_creation(self):
        profile = UserProfile.objects.create(
            user=self.user,
            role='customer',
            specialization='Web dev'
        )
        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.role, 'customer')
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

    def test_str_method(self):
        profile = UserProfile.objects.create(user=self.user, role='executor')
        self.assertEqual(str(profile), 'testuser - Исполнитель')

    def test_rating_default(self):
        profile = UserProfile.objects.create(user=self.user, role='customer')
        self.assertEqual(profile.rating, 0.0)