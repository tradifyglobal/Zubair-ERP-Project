from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from .models import (
    PurchaseOrder, POLineItem, GoodsReceipt, GoodsReceiptLineItem,
    ThreeWayMatching, RequestForQuotation, VendorQuotation
)
from raw_materials.models import RawMaterial, Supplier as RawMaterialSupplier


class PurchaseOrderForm(forms.ModelForm):
    """Form for creating/updating purchase orders."""
    
    class Meta:
        model = PurchaseOrder
        fields = ('vendor', 'entity', 'po_number', 'expected_delivery_date', 'total_amount')
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO Number'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        expected_delivery_date = cleaned_data.get('expected_delivery_date')
        
        if expected_delivery_date and expected_delivery_date < timezone.now().date():
            raise ValidationError('Expected delivery date cannot be in the past.')
        
        return cleaned_data


class POLineItemForm(forms.ModelForm):
    """Form for creating/updating PO line items."""
    
    class Meta:
        model = POLineItem
        fields = ('po', 'description', 'quantity_ordered', 'unit_price', 'inventory_product', 'expense_account')
        widgets = {
            'po': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Description'}),
            'quantity_ordered': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'inventory_product': forms.Select(attrs={'class': 'form-select'}),
            'expense_account': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        quantity_ordered = cleaned_data.get('quantity_ordered')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity_ordered and quantity_ordered <= 0:
            raise ValidationError('Ordered quantity must be greater than zero.')
        
        if unit_price and unit_price < 0:
            raise ValidationError('Unit price cannot be negative.')
        
        return cleaned_data


class GoodsReceiptForm(forms.ModelForm):
    """Form for creating/updating goods receipts."""
    
    class Meta:
        model = GoodsReceipt
        fields = ('po', 'receipt_number', 'status', 'carrier', 'tracking_number')
        widgets = {
            'po': forms.Select(attrs={'class': 'form-select'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Receipt Number'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'carrier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., FedEx, UPS'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tracking Number'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        po = cleaned_data.get('po')
        
        if po and po.status not in ['SENT', 'ACKNOWLEDGED', 'PARTIAL']:
            raise ValidationError('Goods can only be received for POs in SENT, ACKNOWLEDGED, or PARTIAL status.')
        
        return cleaned_data


class GoodsReceiptLineItemForm(forms.ModelForm):
    """Form for creating/updating goods receipt line items."""
    
    class Meta:
        model = GoodsReceiptLineItem
        fields = ('receipt', 'po_line', 'quantity_received', 'quantity_accepted', 'quantity_rejected', 'rejection_reason')
        widgets = {
            'receipt': forms.Select(attrs={'class': 'form-select'}),
            'po_line': forms.Select(attrs={'class': 'form-select'}),
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_accepted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_rejected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        quantity_received = cleaned_data.get('quantity_received')
        quantity_accepted = cleaned_data.get('quantity_accepted')
        quantity_rejected = cleaned_data.get('quantity_rejected')
        
        if quantity_accepted and quantity_rejected:
            total_received = quantity_accepted + quantity_rejected
            if quantity_received and total_received != quantity_received:
                raise ValidationError('Accepted + Rejected quantity must equal received quantity.')
        
        return cleaned_data


class RequestForQuotationForm(forms.ModelForm):
    """Form for creating/updating RFQs."""
    
    class Meta:
        model = RequestForQuotation
        fields = ('entity', 'rfq_number', 'response_deadline', 'vendors')
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'rfq_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RFQ Number'}),
            'response_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vendors': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        vendors = cleaned_data.get('vendors')
        
        if not vendors:
            raise ValidationError('At least one vendor must be selected for RFQ.')
        
        return cleaned_data


class VendorQuotationForm(forms.ModelForm):
    """Form for creating/updating vendor quotations."""
    
    class Meta:
        model = VendorQuotation
        fields = ('rfq', 'vendor', 'quote_number', 'quote_date', 'quote_amount', 'delivery_days', 'payment_terms', 'evaluation_notes')
        widgets = {
            'rfq': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'quote_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quote Number'}),
            'quote_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quote_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Net 30'}),
            'evaluation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        quote_amount = cleaned_data.get('quote_amount')
        delivery_days = cleaned_data.get('delivery_days')
        
        if quote_amount and quote_amount <= 0:
            raise ValidationError('Quote amount must be greater than zero.')
        
        if delivery_days and delivery_days < 0:
            raise ValidationError('Delivery days cannot be negative.')
        
        return cleaned_data


class QuoteSelectionForm(forms.Form):
    """Form for selecting the best quote from RFQ responses."""
    
    rfq = forms.ModelChoiceField(
        queryset=RequestForQuotation.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='RFQ'
    )
    
    selected_quote = forms.ModelChoiceField(
        queryset=VendorQuotation.objects.all(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Select Quote'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        rfq = cleaned_data.get('rfq')
        selected_quote = cleaned_data.get('selected_quote')
        
        if rfq and selected_quote and selected_quote.rfq != rfq:
            raise ValidationError('Selected quote does not belong to the selected RFQ.')
        
        return cleaned_data


class ThreeWayMatchingForm(forms.ModelForm):
    """Form for reviewing and resolving 3-way matching discrepancies."""
    
    class Meta:
        model = ThreeWayMatching
        fields = ('po', 'resolved', 'resolution_notes')
        widgets = {
            'po': forms.Select(attrs={'class': 'form-select'}),
            'resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BulkPurchaseOrderForm(forms.Form):
    """Form for bulk uploading purchase orders (CSV/Excel)."""
    
    file = forms.FileField(
        label='Upload POs File (CSV or Excel)',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv, .xlsx'}),
        help_text='File must contain columns: vendor_name, po_number, po_date, expected_delivery_date, total_amount'
    )
    
    entity = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Entity'
    )
    
    def __init__(self, *args, **kwargs):
        from accounting.models import Entity
        super().__init__(*args, **kwargs)
        self.fields['entity'].queryset = Entity.objects.all()


class RawMaterialPurchaseOrderForm(forms.ModelForm):
    """Specialized form for creating POs for raw materials"""
    
    supplier = forms.ModelChoiceField(
        queryset=RawMaterialSupplier.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_supplier',
            'required': 'required'
        }),
        label='Supplier',
        required=True
    )
    
    # Product dropdown - shows what this supplier supplies (informational, optional)
    supplier_products = forms.ModelChoiceField(
        queryset=RawMaterial.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_supplier_products',
        }),
        label='Products from Supplier',
        required=False,
        help_text='View products this supplier supplies (line items added after PO creation)'
    )
    
    class Meta:
        model = PurchaseOrder
        fields = ('supplier', 'entity', 'po_number', 'expected_delivery_date', 'payment_terms', 'total_amount')
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PO-RM-2026-001'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Net 30'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set vendor from raw material supplier if provided
        if 'supplier' in self.initial:
            supplier = self.initial.get('supplier')
            # Try to match with Vendor if exists
            from accounting.models import Vendor
            try:
                vendor = Vendor.objects.get(name__iexact=supplier.name)
                self.initial['vendor'] = vendor
            except Vendor.DoesNotExist:
                pass
    
    def save(self, commit=True):
        # Get or create vendor from supplier
        from accounting.models import Vendor
        supplier = self.cleaned_data.get('supplier')
        
        vendor, _ = Vendor.objects.get_or_create(
            name=supplier.name,
            defaults={
                'vendor_code': supplier.supplier_code,
                'email': supplier.email,
                'phone': supplier.phone,
                'address': supplier.address,
            }
        )
        
        self.instance.vendor = vendor
        return super().save(commit)


class RawMaterialPOLineItemForm(forms.ModelForm):
    """Form for adding raw material items to a PO"""
    
    raw_material = forms.ModelChoiceField(
        queryset=RawMaterial.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_raw_material'}),
        label='Raw Material',
        required=True
    )
    
    class Meta:
        model = POLineItem
        fields = ('raw_material', 'quantity_ordered', 'unit_price')
        widgets = {
            'quantity_ordered': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': 'Quantity'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Unit Price'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.raw_material:
            self.fields['unit_price'].initial = self.instance.raw_material.current_unit_price
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        raw_material = self.cleaned_data.get('raw_material')
        
        # Set description from raw material
        instance.description = f"{raw_material.product_code} - {raw_material.name} ({raw_material.unit_of_measure})"
        
        # Calculate line total
        quantity = self.cleaned_data.get('quantity_ordered', 0)
        unit_price = self.cleaned_data.get('unit_price', 0)
        instance.line_total = quantity * unit_price
        
        if commit:
            instance.save()
        return instance
