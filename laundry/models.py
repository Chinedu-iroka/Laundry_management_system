from django.db import models
from django.conf import settings
from django.utils import timezone 
from django.contrib.auth.models import User
from django.db.models import Max

# Create your models here.
class ClothingType(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Shirt", "Jeans", "Blouse"
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL
        on_delete=models.SET_NULL, 
        null=True
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"

class Customer(models.Model):
    customer_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.name} ({self.customer_id})"


class LaundryOrder(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('washing', 'Washing'),
        ('ironing', 'Ironing'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('partial', 'Partial Payment'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    
    
    # Order details
    express_service = models.BooleanField(default=False)
    express_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Pricing
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Financials (Keep only ONE set of these)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status tracking
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='registered')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Dates
    order_date = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateTimeField(null=True, blank=True)

    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    estimated_ready = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    special_instructions = models.TextField(blank=True)
    complaints = models.TextField(blank=True)
    
    # Status
    # status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    # payment_status = models.CharField(max_length=20, choices=[
    #     ('pending', 'Pending'),
    #     ('partial', 'Partially Paid'),
    #     ('paid', 'Fully Paid')
    # ], default='pending')
    
    is_urgent = models.BooleanField(default=False)
    

    class Meta:
        ordering = ['-registered_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: LAU-YYYYMMDD-XXXX
            date_str = timezone.now().strftime('%Y%m%d')
            last_order = LaundryOrder.objects.filter(
                order_number__contains=date_str
            ).count()
            self.order_number = f"LAU-{date_str}-{last_order+1:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    ITEM_TYPES = [
        ('shirt', 'Shirt'),
        ('pant', 'Pant'),
        ('trouser', 'Trouser'),
        ('jeans', 'Jeans'),
        ('tshirt', 'T-Shirt'),
        ('sweater', 'Sweater'),
        ('jacket', 'Jacket'),
        ('coat', 'Coat'),
        ('kurta', 'Kurta'),
        ('saree', 'Saree'),
        ('blanket', 'Blanket'),
        ('bedsheet', 'Bed Sheet'),
        ('pillow_cover', 'Pillow Cover'),
        ('towel', 'Towel'),
        ('other', 'Other'),
    ]
    
    order = models.ForeignKey(LaundryOrder, on_delete=models.CASCADE, related_name='items')
    # Change: Point this to the ClothingType model the Admin manages
    clothing_type = models.ForeignKey(ClothingType, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    description = models.CharField(max_length=200, blank=True, null=True)
    
    # We keep these to "lock in" the price at the time of the order
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Service types
    washing = models.BooleanField(default=True)
    ironing = models.BooleanField(default=False)
    dry_clean = models.BooleanField(default=False)
    stain_removal = models.BooleanField(default=False)
    
    # Status for individual items
    # is_wrong_item = models.BooleanField(default=False)
    # is_deleted = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # 1. Automatically grab the price from the Admin's ClothingType
        if not self.price_per_item:
            self.price_per_item = self.clothing_type.price
            
        # 2. Automatically calculate the total
        self.total_price = self.quantity * self.price_per_item
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.clothing_type.name}"

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile Money'),
        ('transfer', 'Bank Transfer'),
    )
    
    order = models.ForeignKey(LaundryOrder, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    transaction_id = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)


class ProcessingQueue(models.Model):
    order = models.OneToOneField(LaundryOrder, on_delete=models.CASCADE)
    position = models.IntegerField()
    current_stage = models.CharField(max_length=20)  # washing, ironing, packing
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
    
    @classmethod
    def add_to_queue(cls, order):
        last_position = cls.objects.aggregate(Max('position'))['position__max'] or 0
        queue_item = cls.objects.create(
            order=order,
            position=last_position + 1,
            current_stage='registered'
        )
        return queue_item
    
    @classmethod
    def get_next_in_queue(cls, stage):
        return cls.objects.filter(current_stage=stage).first()

