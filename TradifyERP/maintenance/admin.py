from django.contrib import admin
from .models import (
    MaintenanceAsset, MaintenanceTask, WorkOrder, SparePart,
    WorkOrderSparePart, MaintenanceVendor, VendorContract,
    ComplianceStandard, ComplianceAudit, MaintenanceCost, DowntimeRecord
)


@admin.register(MaintenanceAsset)
class MaintenanceAssetAdmin(admin.ModelAdmin):
    list_display = ['asset_code', 'asset_name', 'asset_type', 'status', 'location', 'critical_asset']
    list_filter = ['asset_type', 'status', 'critical_asset', 'entity']
    search_fields = ['asset_code', 'asset_name', 'serial_number']
    ordering = ['asset_code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('entity', 'asset_code', 'asset_name', 'asset_type', 'description')
        }),
        ('Details', {
            'fields': ('location', 'manufacturer', 'model', 'serial_number')
        }),
        ('Financial', {
            'fields': ('purchase_date', 'acquisition_cost', 'warranty_expiry')
        }),
        ('Maintenance', {
            'fields': ('status', 'operational_hours', 'last_maintenance_date', 'next_scheduled_maintenance', 'critical_asset')
        }),
    )


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ['task_code', 'task_name', 'asset', 'task_type', 'frequency', 'is_active']
    list_filter = ['task_type', 'frequency', 'is_active', 'entity']
    search_fields = ['task_code', 'task_name', 'asset__asset_name']
    ordering = ['asset', 'task_code']


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['work_order_number', 'asset', 'status', 'priority', 'scheduled_date', 'assigned_to']
    list_filter = ['status', 'priority', 'scheduled_date', 'entity']
    search_fields = ['work_order_number', 'asset__asset_name']
    ordering = ['-scheduled_date']
    fieldsets = (
        ('Basic Information', {
            'fields': ('entity', 'work_order_number', 'asset', 'maintenance_task')
        }),
        ('Assignment & Status', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'scheduled_start_time', 'scheduled_end_time')
        }),
        ('Execution', {
            'fields': ('actual_start_date', 'actual_end_date', 'actual_hours')
        }),
        ('Costs', {
            'fields': ('estimated_cost', 'actual_cost', 'estimated_hours')
        }),
        ('Notes', {
            'fields': ('description', 'notes')
        }),
    )


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ['part_code', 'part_name', 'current_stock', 'reorder_level', 'unit_cost']
    list_filter = ['entity']
    search_fields = ['part_code', 'part_name', 'supplier']
    ordering = ['part_code']


@admin.register(WorkOrderSparePart)
class WorkOrderSparePartAdmin(admin.ModelAdmin):
    list_display = ['work_order', 'spare_part', 'quantity_used', 'total_cost']
    list_filter = ['work_order__scheduled_date']
    search_fields = ['work_order__work_order_number', 'spare_part__part_code']


@admin.register(MaintenanceVendor)
class MaintenanceVendorAdmin(admin.ModelAdmin):
    list_display = ['vendor_code', 'vendor_name', 'vendor_type', 'email', 'performance_rating', 'is_active']
    list_filter = ['vendor_type', 'is_active', 'entity']
    search_fields = ['vendor_code', 'vendor_name', 'email']
    ordering = ['vendor_code']


@admin.register(VendorContract)
class VendorContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'vendor', 'contract_value', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'start_date', 'entity']
    search_fields = ['contract_number', 'vendor__vendor_name']
    ordering = ['-start_date']


@admin.register(ComplianceStandard)
class ComplianceStandardAdmin(admin.ModelAdmin):
    list_display = ['standard_code', 'standard_name', 'standard_type', 'is_mandatory']
    list_filter = ['standard_type', 'is_mandatory', 'entity']
    search_fields = ['standard_code', 'standard_name']
    ordering = ['standard_code']


@admin.register(ComplianceAudit)
class ComplianceAuditAdmin(admin.ModelAdmin):
    list_display = ['standard', 'audit_date', 'auditor_name', 'audit_result', 'next_audit_date']
    list_filter = ['audit_result', 'audit_date', 'entity']
    search_fields = ['standard__standard_name', 'auditor_name']
    ordering = ['-audit_date']


@admin.register(MaintenanceCost)
class MaintenanceCostAdmin(admin.ModelAdmin):
    list_display = ['work_order', 'cost_type', 'amount', 'cost_date']
    list_filter = ['cost_type', 'cost_date', 'entity']
    search_fields = ['work_order__work_order_number']
    ordering = ['-cost_date']


@admin.register(DowntimeRecord)
class DowntimeRecordAdmin(admin.ModelAdmin):
    list_display = ['asset', 'start_time', 'duration_hours', 'reason']
    list_filter = ['start_time', 'entity']
    search_fields = ['asset__asset_name', 'reason']
    ordering = ['-start_time']
