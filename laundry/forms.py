# forms.py
from django import forms
from .models import Customer, LaundryOrder, OrderItem
from django.forms import inlineformset_factory
import random
import string

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    # This should be at the same level as the 'Meta' class
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Generate ID if it doesn't exist (e.g., CUST-5785)
        if not instance.customer_id:
            last_four = instance.phone[-4:] if instance.phone else "0000"
            random_suffix = ''.join(random.choices(string.digits, k=4))
            instance.customer_id = f"CUST-{last_four}-{random_suffix}"
        
        if commit:
            instance.save()
        return instance

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        # 1. Changed 'item_type' to 'clothing_type'
        # 2. Removed 'price_per_item' (it's now non-editable)
        fields = [
            'clothing_type', 
            'quantity', 
            'description', 
            'washing', 
            'ironing', 
            'dry_clean', 
            'stain_removal',
            'rewashing'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Color, fabric, brand, etc.'}),
        }

# Create a formset for multiple items
OrderItemFormSet = inlineformset_factory(
    LaundryOrder, 
    OrderItem, 
    form=OrderItemForm,
    extra=1,  # Show 3 empty item forms by default
    can_delete=True
)

class LaundryOrderForm(forms.ModelForm):
    expected_delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    class Meta:
        model = LaundryOrder
        fields = ['expected_delivery_date', 'special_instructions', 'is_urgent']
        widgets = {
            'special_instructions': forms.Textarea(attrs={'rows': 3}),
        }

class CustomerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = Customer
        fields = ['phone', 'whatsapp_number', 'alternate_phone', 'email', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_phone'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_whatsapp_number'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
        
        # Determine ID generation if saving new
        if commit:
            customer.save()
        return customer