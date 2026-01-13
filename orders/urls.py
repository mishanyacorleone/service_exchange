from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('executors/', views.executor_list, name='executor_list'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('my_assigned_orders/', views.my_assigned_orders, name='my_assigned_orders'),
    path('create_order/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/edit/', views.edit_order, name='edit_order')
]