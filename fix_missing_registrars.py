import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "laundry_system.settings")
django.setup()

from laundry.models import Customer, LaundryOrder
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_missing_registrars():
    customers = Customer.objects.filter(registered_by__isnull=True)
    print(f"Found {customers.count()} customers with missing registrar.")
    
    updated_count = 0
    
    for customer in customers:
        # Find the first order for this customer
        first_order = LaundryOrder.objects.filter(customer=customer).order_by('registered_at').first()
        
        if first_order and first_order.staff:
            customer.registered_by = first_order.staff
            customer.save()
            print(f"Updated {customer.name} ({customer.customer_id}): Registered by {first_order.staff.username} (from order {first_order.order_number})")
            updated_count += 1
        else:
            print(f"Skipping {customer.name} ({customer.customer_id}): No orders or order has no staff.")

    print(f"Finished. Updated {updated_count} customers.")

if __name__ == "__main__":
    fix_missing_registrars()
