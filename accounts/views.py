from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import UserRegistrationForm, ProfilePictureUploadForm
from .models import User

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)


# registration form
@login_required
@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def register_staff(request):
    """Admin-only view to register new staff"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'staff'
            user.save()
            messages.success(request, f'Staff member {user.username} created successfully!')
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register_staff.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def user_list(request):
    """View to list all users (admin only)"""
    users = User.objects.all().order_by('-date_joined')

    staff_count = users.filter(user_type='staff').count()
    admin_count = users.filter(user_type='admin').count()
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'staff_count': staff_count,
        'admin_count': admin_count,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def user_profile(request, user_id):
    """View detailed user profile (admin only)"""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'accounts/user_profile.html', {'target_user': user})

@login_required
def upload_profile_picture(request, user_id):
    """View to handle profile picture upload"""
    target_user = get_object_or_404(User, id=user_id)
    
    # Check if the user is authorized to update this profile
    if not (request.user.is_superuser or request.user.user_type == 'admin' or request.user.id == target_user.id):
        messages.error(request, "You are not authorized to update this profile picture.")
        return redirect('user_profile', user_id=user_id)

    if request.method == 'POST':
        form = ProfilePictureUploadForm(request.POST, request.FILES, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture updated successfully!")
        else:
            messages.error(request, "Error updating profile picture. Please try again.")
            
    return redirect('user_profile', user_id=user_id)