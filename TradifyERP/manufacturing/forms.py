"""
Manufacturing Module Forms
Form definitions for all manufacturing module operations.
"""

from django import forms
from django.contrib.auth.models import User
from .models import (
    ProductCategory, Product, RawMaterial,
    BillOfMaterials, BOMLine,
    WorkCenter, Routing, RoutingLine,
    ProductionOrder, QualityInspection, Equipment
)


class EntityField(forms.ModelChoiceField):
    """Custom field to handle entity selection with UserRole filtering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.none()


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'code', 'description', 'revenue_account', 'cogs_account', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Code'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'revenue_account': forms.Select(attrs={'class': 'form-select'}),
            'cogs_account': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_code', 'name', 'description', 'category',
            'is_manufactured', 'manufacturing_lead_time', 'standard_batch_size',
            'unit_of_measure', 'weight', 'dimensions',
            'standard_cost', 'selling_price',
            'inventory_account',
            'requires_inspection', 'inspection_level',
            'is_active'
        ]
        widgets = {
            'product_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., SKU-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_manufactured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manufacturing_lead_time': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'standard_batch_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., UNIT, KG, METER'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'L x W x H'}),
            'standard_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'inventory_account': forms.Select(attrs={'class': 'form-select'}),
            'requires_inspection': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'inspection_level': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = [
            'material_code', 'name', 'description', 'supplier',
            'unit_of_measure', 'reorder_quantity', 'reorder_point',
            'standard_unit_cost', 'inventory_account', 'is_active'
        ]
        widgets = {
            'material_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MAT-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., KG, METER, UNIT'}),
            'reorder_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reorder_point': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'standard_unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'inventory_account': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BOMLineForm(forms.ModelForm):
    class Meta:
        model = BOMLine
        fields = ['material', 'quantity_per_unit', 'scrap_percentage', 'unit_cost', 'is_active']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-select'}),
            'quantity_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'scrap_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BillOfMaterialsForm(forms.ModelForm):
    class Meta:
        model = BillOfMaterials
        fields = ['bom_code', 'product', 'version', 'effective_date', 'end_date', 'notes', 'is_active']
        widgets = {
            'bom_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., BOM-001'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'version': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class WorkCenterForm(forms.ModelForm):
    class Meta:
        model = WorkCenter
        fields = [
            'code', 'name', 'description',
            'standard_hours_per_day',
            'labor_cost_per_hour', 'machine_cost_per_hour',
            'labor_expense_account', 'machine_expense_account',
            'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., WC-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work Center Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'standard_hours_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'labor_cost_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'machine_cost_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'labor_expense_account': forms.Select(attrs={'class': 'form-select'}),
            'machine_expense_account': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoutingForm(forms.ModelForm):
    class Meta:
        model = Routing
        fields = ['product', 'version', 'effective_date', 'end_date', 'notes', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'version': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoutingLineForm(forms.ModelForm):
    class Meta:
        model = RoutingLine
        fields = ['work_center', 'sequence', 'estimated_hours', 'setup_hours', 'machine_parameters', 'is_active']
        widgets = {
            'work_center': forms.Select(attrs={'class': 'form-select'}),
            'sequence': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'setup_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'machine_parameters': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Speed, temperature, etc.'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoutingForm(forms.ModelForm):
    class Meta:
        model = Routing
        fields = ['product', 'version', 'effective_date', 'end_date', 'notes', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'version': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductionOrderForm(forms.ModelForm):
    class Meta:
        model = ProductionOrder
        fields = [
            'po_number', 'product', 'quantity_ordered',
            'start_date', 'due_date',
            'sales_order_number', 'bom', 'routing',
            'estimated_material_cost', 'estimated_labor_cost',
            'status'
        ]
        widgets = {
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated or custom'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity_ordered': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sales_order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional SO reference'}),
            'bom': forms.Select(attrs={'class': 'form-select'}),
            'routing': forms.Select(attrs={'class': 'form-select'}),
            'estimated_material_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Estimated material cost'}),
            'estimated_labor_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Estimated labor cost'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make routing optional
        self.fields['routing'].required = False
        self.fields['routing'].help_text = 'Optional - Create routing first if needed'
        # Make cost fields optional
        self.fields['estimated_material_cost'].required = False
        self.fields['estimated_labor_cost'].required = False


class QualityInspectionForm(forms.ModelForm):
    class Meta:
        model = QualityInspection
        fields = [
            'inspection_number', 'production_order', 'inspection_date', 'quantity_inspected',
            'status', 'defects_found', 'defect_count', 'notes'
        ]
        widgets = {
            'inspection_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., INS-001'}),
            'production_order': forms.Select(attrs={'class': 'form-select'}),
            'inspection_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'quantity_inspected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'defects_found': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe defects found'}),
            'defect_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'equipment_code', 'name', 'model', 'serial_number',
            'description',
            'acquisition_date', 'acquisition_cost',
            'status',
            'last_maintenance_date', 'next_maintenance_date', 'maintenance_interval_days',
            'fixed_asset_account', 'depreciation_account'
        ]
        widgets = {
            'equipment_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., EQ-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Equipment Name'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Model Number'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serial Number'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'acquisition_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acquisition_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'last_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'maintenance_interval_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'fixed_asset_account': forms.Select(attrs={'class': 'form-select'}),
            'depreciation_account': forms.Select(attrs={'class': 'form-select'}),
        }


# ============================================================================
# DISTRIBUTOR & AFTER-SALES SERVICE FORMS
# ============================================================================


class DistributorForm(forms.ModelForm):
    """Form for creating/editing distributors."""
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['Distributor']).Distributor
        fields = ['distributor_code', 'distributor_name', 'status', 'email', 'phone',
                  'website', 'address', 'city', 'state', 'postal_code', 'country',
                  'account_manager', 'region', 'territory', 'contract_start_date',
                  'contract_end_date', 'credit_limit', 'annual_sales_target',
                  'authorized_products']
        widgets = {
            'distributor_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distributor code',
                'required': 'required'
            }),
            'distributor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone',
                'type': 'tel',
                'required': 'required'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Website'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Street address',
                'required': 'required'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'required': 'required'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province',
                'required': 'required'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code',
                'required': 'required'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country',
                'required': 'required'
            }),
            'account_manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Region'
            }),
            'territory': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Territory'
            }),
            'contract_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'contract_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'annual_sales_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'authorized_products': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Product codes (comma-separated)'
            }),
        }


class DistributorContactForm(forms.ModelForm):
    """Form for managing distributor contacts."""
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['DistributorContact']).DistributorContact
        fields = ['distributor', 'first_name', 'last_name', 'job_title', 'department',
                  'email', 'phone', 'mobile', 'is_primary_contact',
                  'preferred_contact_method', 'next_follow_up']
        widgets = {
            'distributor': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
                'required': 'required'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job title',
                'required': 'required'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone',
                'type': 'tel',
                'required': 'required'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile',
                'type': 'tel'
            }),
            'is_primary_contact': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'next_follow_up': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class DistributorOrderForm(forms.ModelForm):
    """Form for creating distributor orders."""
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['DistributorOrder']).DistributorOrder
        fields = ['distributor', 'order_date', 'required_delivery_date', 'status',
                  'description', 'subtotal', 'discount_amount', 'tax_amount',
                  'total_amount', 'payment_terms']
        widgets = {
            'distributor': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'order_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'required_delivery_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Order details'
            }),
            'subtotal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'payment_terms': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def save(self, commit=True):
        """Auto-generate unique order_number if not already set."""
        import uuid
        from datetime import datetime
        
        instance = super().save(commit=False)
        
        # Generate order_number if not already set
        if not instance.order_number:
            # Format: ORD-{YYYY}{MM}{DD}-{random 6 chars}
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.order_number = f"ORD-{timestamp}-{unique_id}"
        
        if commit:
            instance.save()
        
        return instance


class CourierForm(forms.ModelForm):
    """Form for courier/carrier management."""
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['Courier']).Courier
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Courier Name (e.g., Delhivery)'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Short code (e.g., DEL)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description and details'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class OrderShipmentForm(forms.ModelForm):
    """Form for tracking order shipments."""
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['OrderShipment']).OrderShipment
        fields = ['order', 'shipment_date', 'expected_delivery', 'actual_delivery',
                  'courier', 'tracking_number', 'shipping_cost', 'status', 'notes']
        widgets = {
            'order': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'shipment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'expected_delivery': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'actual_delivery': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'courier': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Courier/Carrier'
            }),
            'tracking_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tracking number'
            }),
            'shipping_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes'
            }),
        }

    def save(self, commit=True):
        """Auto-generate unique shipment_number if not already set."""
        import uuid
        from datetime import datetime
        
        instance = super().save(commit=False)
        
        # Generate shipment_number if not already set
        if not instance.shipment_number:
            # Format: SHIP-{YYYY}{MM}{DD}-{random 6 chars}
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.shipment_number = f"SHIP-{timestamp}-{unique_id}"
        
        if commit:
            instance.save()
        
        return instance


class AfterSalesServiceForm(forms.ModelForm):
    """Form for after-sales service tickets."""
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['AfterSalesService']).AfterSalesService
        fields = ['distributor', 'service_type', 'status', 'priority', 'product_code',
                  'serial_number', 'purchase_date', 'issue_description', 'issue_date',
                  'is_under_warranty', 'warranty_expiry_date', 'assigned_to']
        widgets = {
            'distributor': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'product_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product code'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Serial number'
            }),
            'purchase_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'issue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the issue',
                'required': 'required'
            }),
            'issue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'is_under_warranty': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'warranty_expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def save(self, commit=True):
        """Auto-generate unique service_ticket_number if not already set."""
        import uuid
        from datetime import datetime
        
        instance = super().save(commit=False)
        
        # Generate service_ticket_number if not already set
        if not instance.service_ticket_number:
            # Format: TICKET-{YYYY}{MM}{DD}-{random 6 chars}
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.service_ticket_number = f"TICKET-{timestamp}-{unique_id}"
        
        if commit:
            instance.save()
        
        return instance


class WarrantyRegistrationForm(forms.ModelForm):
    """Form for warranty registration."""
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['WarrantyRegistration']).WarrantyRegistration
        fields = ['warranty_type', 'product_code', 'serial_number', 'distributor',
                  'end_customer_name', 'end_customer_email', 'end_customer_phone',
                  'purchase_date', 'coverage_start_date', 'coverage_end_date',
                  'coverage_description', 'terms_and_conditions']
        widgets = {
            'warranty_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'product_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product code',
                'required': 'required'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Serial number',
                'required': 'required'
            }),
            'distributor': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'end_customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer name'
            }),
            'end_customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer email'
            }),
            'end_customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer phone',
                'type': 'tel'
            }),
            'purchase_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'coverage_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'coverage_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'coverage_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What does warranty cover?',
                'required': 'required'
            }),
            'terms_and_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Terms and conditions'
            }),
        }

    def save(self, commit=True):
        """Auto-generate unique warranty_number if not already set."""
        import uuid
        from datetime import datetime
        
        instance = super().save(commit=False)
        
        # Generate warranty_number if not already set
        if not instance.warranty_number:
            # Format: WAR-{YYYY}{MM}{DD}-{random 6 chars}
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.warranty_number = f"WAR-{timestamp}-{unique_id}"
        
        if commit:
            instance.save()
        
        return instance


class DistributorPerformanceForm(forms.ModelForm):
    """Form for tracking distributor performance."""
    
    entity = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Entity',
        required=True
    )
    
    class Meta:
        model = __import__('manufacturing.models', fromlist=['DistributorPerformance']).DistributorPerformance
        fields = ['entity', 'distributor', 'performance_date', 'orders_count', 'total_sales',
                  'on_time_delivery_percentage', 'order_accuracy_percentage',
                  'return_rate_percentage', 'complaint_count',
                  'payment_on_time_percentage', 'overall_rating']
        widgets = {
            'distributor': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'performance_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'orders_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'total_sales': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'on_time_delivery_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'max': '100'
            }),
            'order_accuracy_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'max': '100'
            }),
            'return_rate_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'max': '100'
            }),
            'complaint_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'payment_on_time_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'max': '100'
            }),
            'overall_rating': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load all entities for the entity field
        from accounting.models import Entity
        self.fields['entity'].queryset = Entity.objects.all().order_by('name')

    def save(self, commit=True):
        """Auto-populate performance_month and performance_year from performance_date.
        Uses update_or_create to handle unique constraint on (distributor, month, year)."""
        instance = super().save(commit=False)
        
        # Extract month and year from performance_date
        if instance.performance_date:
            instance.performance_month = instance.performance_date.month
            instance.performance_year = instance.performance_date.year
        
        if commit:
            # Use update_or_create to handle the unique constraint
            # If a record exists for this distributor/month/year, update it
            # Otherwise, create a new one
            from manufacturing.models import DistributorPerformance
            
            obj, created = DistributorPerformance.objects.update_or_create(
                distributor=instance.distributor,
                performance_month=instance.performance_month,
                performance_year=instance.performance_year,
                defaults={
                    'entity_id': instance.entity_id,
                    'performance_date': instance.performance_date,
                    'orders_count': instance.orders_count,
                    'total_sales': instance.total_sales,
                    'average_order_value': instance.average_order_value,
                    'on_time_delivery_percentage': instance.on_time_delivery_percentage,
                    'order_accuracy_percentage': instance.order_accuracy_percentage,
                    'return_rate_percentage': instance.return_rate_percentage,
                    'complaint_count': instance.complaint_count,
                    'payment_on_time_percentage': instance.payment_on_time_percentage,
                    'overall_rating': instance.overall_rating,
                }
            )
            return obj
        return instance


# ===== NEW MANUFACTURING MASTERS FORMS =====

class WorkstationForm(forms.ModelForm):
    class Meta:
        from .models import Workstation
        model = Workstation
        fields = [
            'workstation_code', 'workstation_name', 'description',
            'workstation_type', 'capacity_per_hour',
            'plant_floor_section', 'status', 'hourly_rate', 'is_active'
        ]
        widgets = {
            'workstation_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., WS-001'}),
            'workstation_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Workstation Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'workstation_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CNC, Assembly'}),
            'capacity_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'plant_floor_section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section/Area'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OperationForm(forms.ModelForm):
    class Meta:
        from .models import Operation
        model = Operation
        fields = [
            'operation_code', 'operation_name', 'description',
            'workstation', 'standard_time_minutes', 'cost_per_unit', 'is_active'
        ]
        widgets = {
            'operation_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., OP-001'}),
            'operation_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Operation Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'workstation': forms.Select(attrs={'class': 'form-select'}),
            'standard_time_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StockEntryForm(forms.ModelForm):
    class Meta:
        from .models import StockEntry
        model = StockEntry
        fields = [
            'entry_type', 'item', 'quantity', 'unit_cost',
            'source_warehouse', 'destination_warehouse',
            'reference_type', 'remarks'
        ]
        widgets = {
            'entry_type': forms.Select(attrs={'class': 'form-select'}),
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'source_warehouse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Source Warehouse'}),
            'destination_warehouse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination Warehouse'}),
            'reference_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference Type'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class JobCardForm(forms.ModelForm):
    class Meta:
        from .models import JobCard
        model = JobCard
        fields = [
            'production_order', 'operation', 'workstation', 'assigned_to',
            'status', 'scheduled_start_date', 'scheduled_end_date',
            'quantity_to_produce', 'instructions', 'remarks'
        ]
        widgets = {
            'production_order': forms.Select(attrs={'class': 'form-select'}),
            'operation': forms.Select(attrs={'class': 'form-select'}),
            'workstation': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'scheduled_end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'quantity_to_produce': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DowntimeEntryForm(forms.ModelForm):
    class Meta:
        from .models import DowntimeEntry
        model = DowntimeEntry
        fields = [
            'job_card', 'workstation', 'downtime_reason',
            'start_time', 'end_time', 'description', 'corrective_action'
        ]
        widgets = {
            'job_card': forms.Select(attrs={'class': 'form-select'}),
            'workstation': forms.Select(attrs={'class': 'form-select'}),
            'downtime_reason': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'corrective_action': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
