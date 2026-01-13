from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
# Create your models here.

USER_ROLE_CHOICES = [
    ('customer', 'Заказчик'),
    ('executor', 'Исполнитель')
]


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, verbose_name='Роль пользователя')

    specialization = models.CharField(max_length=255, blank=True, null=True, verbose_name='Специализация')
    rating = models.FloatField(default=0.0, verbose_name='Рейтинг')
    portfolio = models.TextField(blank=True, verbose_name='Портфолио')

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
