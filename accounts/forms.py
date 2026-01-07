from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'user_type']
    
    def __init__(self, *args, **kwargs):
        # If admin is creating staff, only show staff option
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = User.USER_TYPE_CHOICES  # Only staff can be created

class ProfilePictureUploadForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']