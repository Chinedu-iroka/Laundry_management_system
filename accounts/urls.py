from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, register_staff, user_list, user_profile, upload_profile_picture

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_staff, name='register_staff'),
    path('users/', user_list, name='user_list'),
    path('users/<int:user_id>/profile/', user_profile, name='user_profile'),
    path('users/<int:user_id>/upload-photo/', upload_profile_picture, name='upload_profile_picture'),
]