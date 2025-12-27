from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, register_staff, user_list

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_staff, name='register_staff'),
    path('users/', user_list, name='user_list'),
]