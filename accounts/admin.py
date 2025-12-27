from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class CustomUserAdmin(BaseUserAdmin):
    # What shows up in the main list of users
    list_display = ('username', 'email', 'user_type', 'is_active_staff', 'is_staff')
    list_filter = ('user_type', 'is_active_staff')
    
    # This controls the layout when you EDIT a user
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'address', 'is_active_staff')}),
    )
    
    # This controls the layout when you CREATE a new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Permissions', {'fields': ('user_type',)}),
    )

# Register your custom User with the custom Admin class
admin.site.register(User, CustomUserAdmin)


class UserAdmin(BaseUserAdmin):
    # This adds the 'user_type' field to the User edit page in Admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Permissions', {'fields': ('user_type',)}),
    )
    # This adds 'user_type' to the User creation page
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Permissions', {'fields': ('user_type',)}),
    )
    list_display = BaseUserAdmin.list_display + ('user_type',)