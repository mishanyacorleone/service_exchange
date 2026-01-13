from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
# Create your models here.


ORDER_STATUS_CHOICES = [
    ('open', 'Открыт'),
    ('in_progress', 'В работе'),
    ('completed', 'Завершен'),
    ('cancelled', 'Отменен')
]


class Order(BaseModel):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_orders', verbose_name='Заказчик')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='open', verbose_name='Статус')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Бюджет')
    assigned_executor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        verbose_name='Назначенный исполнитель'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_allowed_status_transitions(self):
        transitions = {
            'open': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled', 'open'],
            'completed': ['open'],
            'cancelled': ['open']
        }

        current_status = self.status

        allowed_destinations = transitions.get(current_status, [])

        all_relevant_statuses = allowed_destinations + [current_status]

        result = [(value, label) for value, label in ORDER_STATUS_CHOICES if value in all_relevant_statuses]

        return result


class Bid(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='bids', verbose_name='Заказ')
    executor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids', verbose_name='Исполнитель')
    message = models.TextField(blank=True, verbose_name='Сообщение от исполнителя')
    price_proposal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Предлагаемая цена')

    class Meta:
        unique_together = ('order', 'executor')
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
