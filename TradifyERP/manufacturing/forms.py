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
