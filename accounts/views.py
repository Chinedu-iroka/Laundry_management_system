from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import UserRegistrationForm
from .models import User
# Create your views here.

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

def user_list(request):
    """View to list all users (admin only)"""
    users = User.objects.all()

    # Calculate counts here in Python
    staff_count = users.filter(user_type='staff').count()
    admin_count = users.filter(user_type='admin').count()
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'staff_count': staff_count,
        'admin_count': admin_count,
    })