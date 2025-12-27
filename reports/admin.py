from django.contrib import admin

# Register your models here.
from import_export import resources
from import_export.admin import ExportMixin
from laundry.models import LaundryOrder 

class OrderResource(resources.ModelResource):
    class Meta:
        model = LaundryOrder
        fields = ('order_number', 'customer__name', 'customer__phone', 
                 'total_amount', 'status', 'payment_status', 'registered_at')
        export_order = fields
    
    def dehydrate_status(self, order):
        return order.get_status_display()
    
    def dehydrate_payment_status(self, order):
        return order.get_payment_status_display()

# @admin.register(LaundryOrder)
# class LaundryOrderAdmin(ExportMixin, admin.ModelAdmin):
#     resource_class = OrderResource
#     list_display = ('order_number', 'customer', 'total_amount', 'status', 'payment_status')
#     list_filter = ('status', 'payment_status', 'registered_at')
#     search_fields = ('order_number', 'customer__name', 'customer__phone')