"""
Inventory Management Forms
Forms for creating and editing inventory items, stock levels, warehouses, etc.
"""

from django import forms
from .models import Category, Product, Warehouse, Stock, StockMovement, InventoryReconciliation


class CategoryForm(forms.ModelForm):
    """Form for creating/editing product categories."""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Category name',
            'required': 'required'
        }),
        label='Category Name'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Category description'
        }),
        label='Description'
    )
    
    class Meta:
        model = Category
        fields = ['name', 'description']


class ProductForm(forms.ModelForm):
    """Form for creating/editing products."""
    
    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'category', 'cost_price', 'selling_price', 
                  'reorder_level', 'reorder_quantity', 'status']
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SKU code',
                'required': 'required'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Product description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10',
                'min': '0',
                'required': 'required'
            }),
            'reorder_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '50',
                'min': '0',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')
        selling_price = cleaned_data.get('selling_price')
        
        if cost_price and selling_price and selling_price < cost_price:
            raise forms.ValidationError("Selling price cannot be less than cost price.")
        
        return cleaned_data


class WarehouseForm(forms.ModelForm):
    """Form for creating/editing warehouses."""
    
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'contact_person', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Warehouse name',
                'required': 'required'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full location address',
                'required': 'required'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manager name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
                'type': 'tel'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class StockForm(forms.ModelForm):
    """Form for updating stock levels."""
    
    class Meta:
        model = Stock
        fields = ['product', 'warehouse', 'quantity_on_hand', 'quantity_reserved', 'quantity_available']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'quantity_on_hand': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'required': 'required'
            }),
            'quantity_reserved': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'quantity_available': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'readonly': 'readonly'
            }),
        }


class StockMovementForm(forms.ModelForm):
    """Form for recording stock movements (inbound/outbound)."""
    
    class Meta:
        model = StockMovement
        fields = ['stock', 'movement_type', 'quantity', 'reference_number', 'notes']
        widgets = {
            'stock': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'movement_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0.01',
                'step': '0.01',
                'required': 'required'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PO/GR/Invoice number'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }


class InventoryReconciliationForm(forms.ModelForm):
    """Form for physical inventory count reconciliation."""
    
    class Meta:
        model = InventoryReconciliation
        fields = ['warehouse', 'reconciliation_date', 'notes', 'status']
        widgets = {
            'warehouse': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'reconciliation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reconciliation notes'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class BulkStockUpdateForm(forms.Form):
    """Form for bulk updating stock levels via CSV/Excel."""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
            'required': 'required'
        }),
        label='Upload CSV/Excel file',
        help_text='File should contain: SKU, Warehouse, Quantity'
    )
    
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Default Warehouse (if not in file)'
    )
    
    overwrite = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Overwrite existing quantities',
        help_text='Unchecked = add to current quantities'
    )
