from django.contrib import admin
from .models import ClothingType, Customer, LaundryOrder, OrderItem
# Register your models here.

@admin.register(ClothingType)
class ClothingTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    list_editable = ('price', 'is_active') # Change prices directly from the list!

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'total_spent')
    search_fields = ('name', 'phone')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price_per_item', 'total_price')

@admin.register(LaundryOrder)
class LaundryOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'total_price', 'registered_at')
    list_filter = ('status', 'payment_status')
    inlines = [OrderItemInline]

    class Media:
        js = ('js/admin_payment_sync.js',)