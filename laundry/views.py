from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Max, Q
from django.contrib.auth import get_user_model
from .models import Customer, LaundryOrder, OrderItem, ClothingType
from django.utils import timezone
from .forms import (
    CustomerForm, 
    LaundryOrderForm, 
    OrderCreateForm, 
    OrderItemFormSet, 
    CustomerRegistrationForm
)
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
    
    if request.user.user_type == 'admin' or request.user.is_superuser:
        # Admin dashboard
        total_orders = LaundryOrder.objects.count()
        pending_orders = LaundryOrder.objects.filter(payment_status='pending').count()
        today_orders = LaundryOrder.objects.filter(
            registered_at__date=timezone.now().date()
        ).count()
        total_revenue = LaundryOrder.objects.aggregate(
            total=Sum('total_price')
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
                quantity=int(quantity),
                washing=request.POST.get('washing') == 'on',
                ironing=request.POST.get('ironing') == 'on',
                rewashing=request.POST.get('rewashing') == 'on'
            )
            messages.success(request, f'Added {quantity} {clothing.name}(s) to order')
        
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'laundry/add_order_items.html', {
        'order': order,
        'clothing_items': clothing_items,
    })

@login_required
def order_list(request):
    # Use select_related to join the User (staff) table with the Order table
    if request.user.user_type == 'admin' or request.user.is_superuser:
        orders = LaundryOrder.objects.select_related('customer', 'staff').all().order_by('-order_date')
    else:
        orders = LaundryOrder.objects.select_related('customer', 'staff').filter(staff=request.user).order_by('-order_date')
    
    # Basic Text Search
    query = request.GET.get('q')
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) | 
            Q(customer__name__icontains=query) |
            Q(customer__phone__icontains=query)
        )

    # Status Filter
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Payment Filter
    payment_filter = request.GET.get('payment')
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)

    # Date Filter
    date_filter = request.GET.get('date')
    if date_filter:
        orders = orders.filter(order_date__date=date_filter)

    # Staff Filter (Admin Only)
    staff_filter = request.GET.get('staff')
    if staff_filter and (request.user.is_superuser or request.user.user_type == 'admin'):
        orders = orders.filter(staff__id=staff_filter)

    # Context data for filter dropdowns
    User = get_user_model()
    staff_list = User.objects.filter(is_active=True) if (request.user.is_superuser or request.user.user_type == 'admin') else None

    return render(request, 'laundry/order_list.html', {
        'orders': orders,
        'order_status_choices': LaundryOrder.ORDER_STATUS,
        'payment_status_choices': LaundryOrder.PAYMENT_STATUS,
        'staff_list': staff_list
    })

@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(LaundryOrder, id=order_id)
    
    # Check permission
    if not (request.user.is_superuser or request.user.user_type == 'admin' or order.staff == request.user):
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
    # Pre-select customer if passed in URL
    initial_customer = request.GET.get('customer')
    
    if request.method == 'POST':
        # Removed CustomerForm, using OrderCreateForm instead
        order_form = OrderCreateForm(request.POST, prefix='order')
        item_formset = OrderItemFormSet(request.POST, prefix='items')

        if order_form.is_valid() and item_formset.is_valid():
            # Get selected customer
            customer = order_form.cleaned_data['customer']

            # CREATE ORDER
            order = order_form.save(commit=False)
            order.customer = customer
            order.staff = request.user

            # Default delivery date
            if not order.expected_delivery_date:
                order.expected_delivery_date = timezone.now().date() + timezone.timedelta(days=3)

            order.save()

            # SAVE ORDER ITEMS
            item_formset.instance = order
            item_formset.save()

            # 🔥 SINGLE SOURCE OF TRUTH FOR PRICING
            order.calculate_totals()
            order.save()

            return redirect('order_detail', order_id=order.id)

    else:
        # Initialize form with customer if provided
        initial_data = {}
        if initial_customer:
            try:
                initial_data['customer'] = Customer.objects.get(id=initial_customer)
            except Customer.DoesNotExist:
                pass
                
        order_form = OrderCreateForm(prefix='order', initial=initial_data)
        order_form.fields['expected_delivery_date'].initial = timezone.now().date()
        item_formset = OrderItemFormSet(prefix='items')

    return render(request, 'laundry/create_order.html', {
        'order_form': order_form,
        'item_formset': item_formset,
    })

@login_required
@user_passes_test(is_staff)
def delete_order_item(request, item_id):
    """Delete an item from an order"""
    item = get_object_or_404(OrderItem, id=item_id)
    order_id = item.order.id
    
    # Delete the item (this will trigger OrderItem.delete() which updates the order total)
    item.delete()
    
    messages.success(request, 'Item removed successfully')
    return redirect('order_detail', order_id=order_id)

# @login_required
# def create_order(request):
#     if request.method == 'POST':
#         customer_form = CustomerForm(request.POST, prefix='customer')
#         order_form = LaundryOrderForm(request.POST, prefix='order')
#         item_formset = OrderItemFormSet(request.POST, prefix='items')
        
#         if customer_form.is_valid() and order_form.is_valid() and item_formset.is_valid():
#             # GET OR CREATE logic: Finds existing customer by phone
#             phone = customer_form.cleaned_data.get('phone')
#             customer, created = Customer.objects.get_or_create(
#                 phone=phone,
#                 defaults={
#                     'name': customer_form.cleaned_data.get('name'),
#                     'email': customer_form.cleaned_data.get('email'),
#                     'address': customer_form.cleaned_data.get('address'),
#                 }
#             )
            
#             # Create order
#             order = order_form.save(commit=False)
#             order.customer = customer
#             order.staff = request.user
#             order.save()
            
#             # Calculate delivery date
#             if not order.expected_delivery_date:
#                 order.expected_delivery_date = timezone.now() + timezone.timedelta(days=3)
            
#             order.save()
            
#             # Save order items
#             item_formset.instance = order
#             item_formset.save()
#             total_items = 0
#             total_price = 0
#             order.calculate_totals()
#             order.save()
#             for item in items:
#                 item.order = order
#                 if item.clothing_type:
#                     item.price_per_item = item.clothing_type.price
                
#                 # Safety check: Use 0 if values are missing to prevent crash
#                 current_price = item.price_per_item or 0
#                 current_qty = item.quantity or 0
                
#                 item.total_price = current_qty * current_price
#                 item.save()
                
#                 total_items += current_qty
#                 total_price += item.total_price
            
#             # Update order totals
#             order.total_items = total_items
#             order.total_price = total_price
#             order.balance = total_price - order.amount_paid
#             order.save()
            
#             return redirect('order_detail', order_id=order.id)
#     else:
#         customer_form = CustomerForm(prefix='customer')
#         order_form = LaundryOrderForm(prefix='order')
#         order_form.fields['expected_delivery_date'].initial = timezone.now().date()
#         item_formset = OrderItemFormSet(prefix='items')
    
#     return render(request, 'laundry/create_order.html', {
#         'customer_form': customer_form,
#         'order_form': order_form,
#         'item_formset': item_formset,
#     })

@login_required
def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.registered_by = request.user
            customer.save()
            messages.success(request, f'Customer {customer.name} registered successfully!')
            return redirect('customer_list')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'laundry/register_customer.html', {'form': form})

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-registration_date')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(customer_id__icontains=query) |
            Q(registered_by__username__icontains=query) |
            Q(registration_date__icontains=query)
        )
    
    # Calculate ranking base
    max_spent = customers.aggregate(max_val=Max('total_spent'))['max_val'] or 0
    
    for customer in customers:
        # Calculate rank: 1-5 stars
        if max_spent > 0:
            # Formula: (customer_spent / max_spent) * 5
            # We use float() for division and round() for nearest integer
            rank = round((float(customer.total_spent) / float(max_spent)) * 5)
            # Ensure at least 1 star if they have spent anything, else 0? 
            # Requirement says "customer with highest order ranks 5 stars"
            # Let's say: 0 spent = 0 stars (or 1). 
            # If max_spent is high, low spenders get 0 or 1.
            # Let's clamp to 1-5 for non-zero spenders? Or just pure ratio.
            customer.rank = int(rank) if rank > 0 else (1 if customer.total_spent > 0 else 0)
        else:
            customer.rank = 0
            
        # Range for template loop (e.g. range(customer.rank))
        customer.star_range = range(customer.rank)
        customer.empty_star_range = range(5 - customer.rank)
        
    return render(request, 'laundry/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    orders = customer.orders.select_related('staff').order_by('-order_date')
    
    return render(request, 'laundry/customer_detail.html', {
        'customer': customer,
        'orders': orders
    })