from django import forms
from .models import (
    MaintenanceAsset, MaintenanceTask, WorkOrder, SparePart, 
    WorkOrderSparePart, MaintenanceVendor, VendorContract,
    ComplianceStandard, ComplianceAudit, MaintenanceCost, DowntimeRecord
)
from accounting.models import Account


class MaintenanceAssetForm(forms.ModelForm):
    """Form for creating/editing maintenance assets."""
    
    purchase_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'help_text': 'Select the account from which this asset was purchased'
        }),
        help_text="Source account (e.g., Capital Investment account)"
    )
    
    class Meta:
        model = MaintenanceAsset
        fields = ['asset_code', 'asset_name', 'asset_type', 'description', 'location',
                  'manufacturer', 'model', 'serial_number', 'purchase_date', 'acquisition_cost',
                  'purchase_account', 'warranty_expiry', 'status', 'operational_hours', 'critical_asset']
        widgets = {
            'asset_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asset Code', 'required': 'required'}),
            'asset_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asset Name', 'required': 'required'}),
            'asset_type': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location', 'required': 'required'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Manufacturer'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Model'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serial Number'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'acquisition_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'operational_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'critical_asset': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter purchase accounts to show capital/equity accounts
        if self.instance and self.instance.entity:
            self.fields['purchase_account'].queryset = Account.objects.filter(
                entity=self.instance.entity,
                is_active=True
            ).exclude(account_type='EXPENSE').order_by('account_number')
        else:
            # If no entity context, get all active accounts
            self.fields['purchase_account'].queryset = Account.objects.filter(
                is_active=True
            ).exclude(account_type='EXPENSE').order_by('entity__name', 'account_number')


class MaintenanceTaskForm(forms.ModelForm):
    """Form for creating/editing maintenance tasks."""
    
    class Meta:
        model = MaintenanceTask
        fields = ['asset', 'task_code', 'task_name', 'task_type', 'description', 'instructions',
                  'frequency', 'estimated_duration_hours', 'estimated_cost', 'is_active']
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'task_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Code', 'required': 'required'}),
            'task_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Name', 'required': 'required'}),
            'task_type': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description', 'required': 'required'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instructions'}),
            'frequency': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estimated_duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class WorkOrderForm(forms.ModelForm):
    """Form for creating/editing work orders."""
    
    class Meta:
        model = WorkOrder
        fields = ['work_order_number', 'asset', 'maintenance_task', 'priority', 'status', 'assigned_to',
                  'description', 'scheduled_date', 'scheduled_start_time', 'scheduled_end_time',
                  'estimated_hours', 'estimated_cost', 'notes']
        widgets = {
            'work_order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WO Number', 'required': 'required'}),
            'asset': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'maintenance_task': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'status': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description', 'required': 'required'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'scheduled_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'scheduled_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }


class SparePartForm(forms.ModelForm):
    """Form for creating/editing spare parts."""
    
    class Meta:
        model = SparePart
        fields = ['part_code', 'part_name', 'description', 'unit_cost', 'current_stock',
                  'reorder_level', 'reorder_quantity', 'warehouse_location', 'supplier', 'lead_time_days']
        widgets = {
            'part_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Part Code', 'required': 'required'}),
            'part_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Part Name', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0', 'required': 'required'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0', 'required': 'required'}),
            'reorder_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0', 'required': 'required'}),
            'warehouse_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Warehouse Location'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
            'lead_time_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0', 'required': 'required'}),
        }


class MaintenanceVendorForm(forms.ModelForm):
    """Form for creating/editing maintenance vendors."""
    
    class Meta:
        model = MaintenanceVendor
        fields = ['vendor_code', 'vendor_name', 'vendor_type', 'contact_person', 'email', 'phone',
                  'address', 'city', 'state', 'postal_code', 'country', 'website', 'service_areas', 'is_active']
        widgets = {
            'vendor_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor Code', 'required': 'required'}),
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor Name', 'required': 'required'}),
            'vendor_type': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone', 'required': 'required'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address', 'required': 'required'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'required': 'required'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State', 'required': 'required'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code', 'required': 'required'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country', 'required': 'required'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website'}),
            'service_areas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Service Areas (comma-separated)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VendorContractForm(forms.ModelForm):
    """Form for creating/editing vendor contracts."""
    
    class Meta:
        model = VendorContract
        fields = ['vendor', 'contract_number', 'description', 'contract_value', 'start_date',
                  'end_date', 'service_level_agreement', 'response_time_hours', 'resolution_time_hours', 'status']
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contract Number', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description', 'required': 'required'}),
            'contract_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'service_level_agreement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'SLA Details'}),
            'response_time_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '24', 'min': '1', 'required': 'required'}),
            'resolution_time_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '72', 'min': '1', 'required': 'required'}),
            'status': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        }


class ComplianceStandardForm(forms.ModelForm):
    """Form for creating/editing compliance standards."""
    
    class Meta:
        model = ComplianceStandard
        fields = ['standard_code', 'standard_name', 'standard_type', 'description', 'requirements',
                  'audit_frequency_months', 'is_mandatory']
        widgets = {
            'standard_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Standard Code', 'required': 'required'}),
            'standard_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Standard Name', 'required': 'required'}),
            'standard_type': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description', 'required': 'required'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Requirements', 'required': 'required'}),
            'audit_frequency_months': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '12', 'min': '1', 'required': 'required'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MaintenanceCostForm(forms.ModelForm):
    """Form for recording maintenance costs."""
    
    class Meta:
        model = MaintenanceCost
        fields = ['work_order', 'cost_type', 'description', 'amount', 'cost_date', 'assigned_to', 'notes']
        widgets = {
            'work_order': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'cost_type': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cost Description', 'required': 'required'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'required': 'required'}),
            'cost_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assigned To'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes'}),
        }


class DowntimeRecordForm(forms.ModelForm):
    """Form for recording equipment downtime."""
    
    class Meta:
        model = DowntimeRecord
        fields = ['asset', 'start_time', 'end_time', 'reason', 'production_loss_estimate', 'affected_processes']
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'required': 'required'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'required': 'required'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for Downtime', 'required': 'required'}),
            'production_loss_estimate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'affected_processes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Affected Processes'}),
        }
