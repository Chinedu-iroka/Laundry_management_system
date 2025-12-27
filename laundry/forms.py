# forms.py
from django import forms
from .models import Customer, LaundryOrder, OrderItem
from django.forms import inlineformset_factory

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

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
            'stain_removal'
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