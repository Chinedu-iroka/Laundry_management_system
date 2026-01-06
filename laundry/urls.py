from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Orders
    path('order/new/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/edit/', views.create_order, name='order_update'), # Reusing view for edits
    
    # Items & Management
    path('order/<int:order_id>/add-items/', views.add_order_items, name='add_order_items'),
    path('item/<int:item_id>/delete/', views.delete_order_item, name='delete_order_item'),
    path('manage/clothing/', views.manage_clothing, name='manage_clothing'),
    path('customers/register/', views.register_customer, name='register_customer'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/', views.customer_list, name='customer_list'),
]