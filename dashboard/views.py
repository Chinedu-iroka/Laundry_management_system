from django.shortcuts import render

# Create your views here.
class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/admin_dashboard.html'
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Today's statistics
        today = timezone.now().date()
        context['today_orders'] = LaundryOrder.objects.filter(
            registered_at__date=today
        ).count()
        context['today_revenue'] = Payment.objects.filter(
            payment_date__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Pending orders
        context['pending_orders'] = LaundryOrder.objects.filter(
            payment_status='pending'
        ).count()
        
        # Recent activities
        context['recent_orders'] = LaundryOrder.objects.all()[:10]
        
        # Staff performance
        context['top_staff'] = User.objects.filter(
            user_type='staff'
        ).annotate(
            order_count=Count('laundryorder')
        ).order_by('-order_count')[:5]
        
        return context