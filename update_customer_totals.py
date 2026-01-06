
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laundry_system.settings')
django.setup()

from laundry.models import Customer
from django.db.models import Sum

print("Updating customer totals...")
customers = Customer.objects.all()
for customer in customers:
    customer.update_total_spent()
    print(f"Updated {customer.name}: {customer.total_spent}")

print("Done.")
