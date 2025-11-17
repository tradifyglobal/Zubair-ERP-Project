"""
Manufacturing Module Admin Interface
Registers all manufacturing models in Django admin.
"""

from django.contrib import admin
from .models import (
    ProductCategory, Product, RawMaterial,
    BillOfMaterials, BOMLine,
    WorkCenter, Routing, RoutingLine,
    ProductionOrder, QualityInspection, Equipment
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'name', 'category', 'standard_cost', 'selling_price', 'is_active']
    list_filter = ['is_active', 'category', 'requires_inspection']
    search_fields = ['product_code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('product_code', 'name', 'description', 'category')
        }),
        ('Manufacturing', {
            'fields': ('is_manufactured', 'manufacturing_lead_time', 'standard_batch_size', 'requires_inspection', 'inspection_level')
        }),
        ('Specifications', {
            'fields': ('unit_of_measure', 'weight', 'dimensions')
        }),
        ('Costing', {
            'fields': ('standard_cost', 'selling_price')
        }),
        ('GL Integration', {
            'fields': ('inventory_account',)
        }),
        ('System', {
            'fields': ('is_active', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['material_code', 'name', 'current_stock', 'reorder_point', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['material_code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('material_code', 'name', 'description', 'supplier')
        }),
        ('Inventory', {
            'fields': ('current_stock', 'reorder_quantity', 'reorder_point', 'unit_of_measure')
        }),
        ('Costing', {
            'fields': ('standard_unit_cost',)
        }),
        ('GL Integration', {
            'fields': ('inventory_account',)
        }),
        ('System', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class BOMLineInline(admin.TabularInline):
    model = BOMLine
    extra = 1
    fields = ['material', 'quantity_per_unit', 'scrap_percentage', 'unit_cost', 'is_active']


@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(admin.ModelAdmin):
    list_display = ['product', 'version', 'effective_date', 'is_active']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['product__name', 'product__product_code']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BOMLineInline]
    fieldsets = (
        ('Product', {
            'fields': ('product', 'version', 'effective_date', 'end_date')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('is_active', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkCenter)
class WorkCenterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'labor_cost_per_hour', 'machine_cost_per_hour', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('code', 'name', 'description')
        }),
        ('Capacity', {
            'fields': ('standard_hours_per_day',)
        }),
        ('Costing', {
            'fields': ('labor_cost_per_hour', 'machine_cost_per_hour')
        }),
        ('GL Integration', {
            'fields': ('labor_expense_account', 'machine_expense_account')
        }),
        ('System', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class RoutingLineInline(admin.TabularInline):
    model = RoutingLine
    extra = 1
    fields = ['sequence', 'work_center', 'estimated_hours', 'setup_hours', 'is_active']


@admin.register(Routing)
class RoutingAdmin(admin.ModelAdmin):
    list_display = ['product', 'version', 'effective_date', 'is_active']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['product__name', 'product__product_code']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RoutingLineInline]
    fieldsets = (
        ('Product', {
            'fields': ('product', 'version', 'effective_date', 'end_date')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('is_active', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'product', 'quantity_ordered', 'status', 'due_date']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['po_number', 'product__name']
    readonly_fields = ['created_at', 'updated_at', 'quantity_completed', 'quantity_scrapped']
    fieldsets = (
        ('Identification', {
            'fields': ('po_number', 'product', 'sales_order_number')
        }),
        ('Quantities', {
            'fields': ('quantity_ordered', 'quantity_completed', 'quantity_scrapped')
        }),
        ('Schedule', {
            'fields': ('start_date', 'due_date', 'completion_date')
        }),
        ('Routing & BOM', {
            'fields': ('bom', 'routing')
        }),
        ('Costing', {
            'fields': ('estimated_material_cost', 'estimated_labor_cost', 'actual_material_cost', 'actual_labor_cost'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'approved_date')
        }),
        ('System', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = ['production_order', 'status', 'quantity_inspected', 'defect_count', 'inspection_date']
    list_filter = ['status', 'inspection_date']
    search_fields = ['production_order__po_number']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Production Order', {
            'fields': ('production_order',)
        }),
        ('Inspection Details', {
            'fields': ('inspection_date', 'quantity_inspected', 'status')
        }),
        ('Defects', {
            'fields': ('defects_found', 'defect_count')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('inspected_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_code', 'name', 'status', 'last_maintenance_date', 'next_maintenance_date']
    list_filter = ['status', 'acquisition_date']
    search_fields = ['equipment_code', 'name', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('equipment_code', 'name', 'model', 'serial_number', 'description')
        }),
        ('Acquisition', {
            'fields': ('acquisition_date', 'acquisition_cost')
        }),
        ('Maintenance', {
            'fields': ('status', 'last_maintenance_date', 'next_maintenance_date', 'maintenance_interval_days')
        }),
        ('GL Integration', {
            'fields': ('fixed_asset_account', 'depreciation_account'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
