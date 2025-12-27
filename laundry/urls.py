from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/add-items/', views.add_order_items, name='add_order_items'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('manage/clothing/', views.manage_clothing, name='manage_clothing'),
    path('order/new/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]