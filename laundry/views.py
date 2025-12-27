from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum
from .models import Customer, LaundryOrder
from .models import Customer, LaundryOrder, ClothingType, OrderItem
from django.utils import timezone
from .forms import CustomerForm, LaundryOrderForm, OrderItemFormSet
import random
import string

# Create your views here.
# Helper functions for permission checks
def is_staff(user):
    if not user.is_authenticated:
        return False
    # Access if: Selected 'staff' OR Selected 'admin' OR Django Staff box is checked
    return (user.user_type == 'staff' or 
            user.user_type == 'admin' or 
            user.is_staff or 
            user.is_superuser)

def is_admin(user):
    if not user.is_authenticated:
        return False
    # Access if: Selected 'admin' OR Django Superuser box is checked
    return (user.user_type == 'admin' or user.is_superuser)

@login_required
def dashboard(request):
    """Main dashboard view for all users"""
    context = {}
    
    if request.user.user_type == 'admin':
        # Admin dashboard
        total_orders = LaundryOrder.objects.count()
        pending_orders = LaundryOrder.objects.filter(payment_status='pending').count()
        today_orders = LaundryOrder.objects.filter(
            registered_at__date=timezone.now().date()
        ).count()
        total_revenue = LaundryOrder.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        context.update({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'today_orders': today_orders,
            'total_revenue': total_revenue,
            'recent_orders': LaundryOrder.objects.all()[:10],
        })
    else:
        # Staff dashboard
        staff_orders = LaundryOrder.objects.filter(staff=request.user).count()
        staff_pending = LaundryOrder.objects.filter(
            staff=request.user,
            payment_status='pending'
        ).count()
        
        context.update({
            'staff_orders': staff_orders,
            'staff_pending': staff_pending,
            'my_orders': LaundryOrder.objects.filter(staff=request.user)[:10],
        })
    
    return render(request, 'laundry/dashboard.html', context)

# @login_required
# @user_passes_test(is_staff)
# def create_order(request):
#     """View for creating new laundry orders"""
#     if request.method == 'POST':
#         customer_name = request.POST.get('customer_name')
#         customer_phone = request.POST.get('customer_phone')
        
#         # Create or get customer
#         customer, created = Customer.objects.get_or_create(
#             phone=customer_phone,
#             defaults={
#                 'name': customer_name,
#                 'customer_id': f"CUST-{customer_phone[-4:]}"
#             }
#         )
        
#         # Create order
#         order = LaundryOrder.objects.create(
#             customer=customer,
#             staff=request.user,
#         )
        
#         messages.success(request, f'Order #{order.order_number} created for {customer.name}')
#         return redirect('add_order_items', order_id=order.id)
    
#     return render(request, 'laundry/create_order.html')

@login_required
@user_passes_test(is_staff)
def add_order_items(request, order_id):
    """View for adding items to an order"""
    order = get_object_or_404(LaundryOrder, id=order_id)
    clothing_items = ClothingType.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Handle item selection (simplified for now)
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity', 1)
        
        if item_id and int(quantity) > 0:
            clothing = ClothingType.objects.get(id=item_id)
            OrderItem.objects.create(
                order=order,
                clothing_type=clothing,
                quantity=quantity,
                unit_price=clothing.price
            )
            messages.success(request, f'Added {quantity} {clothing.name}(s) to order')
        
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'laundry/add_order_items.html', {
        'order': order,
        'clothing_items': clothing_items,
    })

@login_required
def order_list(request):
    """View all orders"""
    if request.user.user_type == 'admin':
        orders = LaundryOrder.objects.all()
    else:
        orders = LaundryOrder.objects.filter(staff=request.user)
    
    return render(request, 'laundry/order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(LaundryOrder, id=order_id)
    
    # Check permission
    if request.user.user_type != 'admin' and order.staff != request.user:
        messages.error(request, 'You do not have permission to view this order')
        return redirect('order_list')
    
    return render(request, 'laundry/order_detail.html', {
        'order': order,
        'items': order.items.all()
    })

@login_required
@user_passes_test(is_admin)
def manage_clothing(request):
    """Admin view to manage clothing types"""
    clothing_items = ClothingType.objects.all()
    return render(request, 'laundry/manage_clothing.html', {
        'clothing_items': clothing_items
    })


def generate_order_number():
    """Generate unique order number like LAU-2024-00123"""
    date_part = timezone.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"LAU-{date_part}-{random_part}"

@login_required
def create_order(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST, prefix='customer')
        order_form = LaundryOrderForm(request.POST, prefix='order')
        item_formset = OrderItemFormSet(request.POST, prefix='items')
        
        if customer_form.is_valid() and order_form.is_valid() and item_formset.is_valid():
            # Save customer
            customer = customer_form.save()
            
            # Create order
            order = order_form.save(commit=False)
            order.customer = customer
            order.staff = request.user
            order.order_number = generate_order_number()
            
            # Calculate delivery date
            if order.expected_delivery_date:
                order.expected_delivery_date = order.expected_delivery_date
            
            order.save()
            
            # Save order items
            items = item_formset.save(commit=False)
            total_items = 0
            total_price = 0
            
            for item in items:
                item.order = order
                item.total_price = item.quantity * item.price_per_item
                item.save()
                total_items += item.quantity
                total_price += item.total_price
            
            # Update order totals
            order.total_items = total_items
            order.total_price = total_price
            order.balance = total_price - order.amount_paid
            order.save()
            
            return redirect('order_detail', order_id=order.id)
    else:
        customer_form = CustomerForm(prefix='customer')
        order_form = LaundryOrderForm(prefix='order')
        order_form.fields['expected_delivery_date'].initial = timezone.now().date()
        item_formset = OrderItemFormSet(prefix='items')
    
    return render(request, 'laundry/create_order.html', {
        'customer_form': customer_form,
        'order_form': order_form,
        'item_formset': item_formset,
    })