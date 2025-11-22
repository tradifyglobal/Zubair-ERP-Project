"""
Manufacturing Module Admin Interface
Registers all manufacturing models in Django admin.
"""

from django.contrib import admin
from .models import (
    ProductCategory, Product, RawMaterial,
    BillOfMaterials, BOMLine,
    WorkCenter, Routing, RoutingLine,
    ProductionOrder, QualityInspection, Equipment,
    Distributor, DistributorContact, DistributorOrder, OrderShipment, Courier,
    AfterSalesService, ServiceActivity, WarrantyRegistration, DistributorPerformance
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


# ============================================================================
# DISTRIBUTOR & AFTER-SALES SERVICE ADMIN
# ============================================================================


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ['distributor_code', 'distributor_name', 'status', 'region', 'email', 'phone']
    list_filter = ['status', 'region', 'date_onboarded']
    search_fields = ['distributor_code', 'distributor_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('distributor_code', 'distributor_name', 'status', 'entity')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Territory & Management', {
            'fields': ('region', 'territory', 'account_manager')
        }),
        ('Relationship', {
            'fields': ('date_onboarded', 'contract_start_date', 'contract_end_date')
        }),
        ('Financial', {
            'fields': ('credit_limit', 'annual_sales_target', 'ytd_sales')
        }),
        ('Products', {
            'fields': ('authorized_products',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DistributorContact)
class DistributorContactAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'distributor', 'job_title', 'email']
    list_filter = ['is_primary_contact', 'preferred_contact_method', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'distributor__distributor_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Distributor', {
            'fields': ('distributor',)
        }),
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'job_title', 'department')
        }),
        ('Communication', {
            'fields': ('email', 'phone', 'mobile', 'preferred_contact_method')
        }),
        ('Relationship', {
            'fields': ('is_primary_contact', 'last_contact_date', 'next_follow_up')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DistributorOrder)
class DistributorOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'distributor', 'order_date', 'status', 'total_amount']
    list_filter = ['status', 'order_date', 'distributor']
    search_fields = ['order_number', 'distributor__distributor_name', 'sales_order_reference']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'entity', 'distributor', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'required_delivery_date', 'actual_delivery_date')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Financial', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total_amount', 'payment_terms')
        }),
        ('Tracking', {
            'fields': ('is_posted', 'sales_order_reference')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Courier Information', {
            'fields': ('entity', 'name', 'code')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderShipment)
class OrderShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_number', 'order', 'shipment_date', 'status', 'courier']
    list_filter = ['status', 'shipment_date', 'courier']
    search_fields = ['shipment_number', 'tracking_number', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Shipment Information', {
            'fields': ('shipment_number', 'order', 'status')
        }),
        ('Dates', {
            'fields': ('shipment_date', 'expected_delivery', 'actual_delivery')
        }),
        ('Carrier & Tracking', {
            'fields': ('courier', 'tracking_number', 'shipping_cost')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AfterSalesService)
class AfterSalesServiceAdmin(admin.ModelAdmin):
    list_display = ['service_ticket_number', 'distributor', 'service_type', 'status', 'priority']
    list_filter = ['status', 'service_type', 'priority', 'issue_date']
    search_fields = ['service_ticket_number', 'serial_number', 'distributor__distributor_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Service Information', {
            'fields': ('service_ticket_number', 'entity', 'distributor', 'service_type', 'status', 'priority')
        }),
        ('Product Details', {
            'fields': ('product_code', 'serial_number', 'purchase_date')
        }),
        ('Issue', {
            'fields': ('issue_description', 'issue_date')
        }),
        ('Resolution', {
            'fields': ('resolution_description', 'resolution_date')
        }),
        ('Warranty', {
            'fields': ('is_under_warranty', 'warranty_expiry_date', 'warranty_covered')
        }),
        ('Cost & Assignment', {
            'fields': ('service_cost', 'assigned_to')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceActivity)
class ServiceActivityAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'service', 'performed_by', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['service__service_ticket_number', 'description']
    readonly_fields = ['created_at']


@admin.register(WarrantyRegistration)
class WarrantyRegistrationAdmin(admin.ModelAdmin):
    list_display = ['warranty_number', 'product_code', 'distributor', 'warranty_type', 'is_active', 'is_claimed']
    list_filter = ['warranty_type', 'is_active', 'is_claimed', 'coverage_start_date']
    search_fields = ['warranty_number', 'serial_number', 'product_code']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Warranty Information', {
            'fields': ('warranty_number', 'warranty_type', 'is_active', 'is_claimed')
        }),
        ('Product Details', {
            'fields': ('product_code', 'serial_number')
        }),
        ('Customer/Distributor', {
            'fields': ('distributor', 'end_customer_name', 'end_customer_email', 'end_customer_phone')
        }),
        ('Coverage', {
            'fields': ('purchase_date', 'coverage_start_date', 'coverage_end_date', 'coverage_description')
        }),
        ('Terms', {
            'fields': ('terms_and_conditions',),
            'classes': ('collapse',)
        }),
        ('Claims', {
            'fields': ('claims_count', 'total_claims_value')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DistributorPerformance)
class DistributorPerformanceAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'performance_month', 'performance_year', 'total_sales', 'overall_rating']
    list_filter = ['performance_year', 'performance_month', 'overall_rating']
    search_fields = ['distributor__distributor_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Period', {
            'fields': ('distributor', 'performance_date', 'performance_month', 'performance_year')
        }),
        ('Sales Metrics', {
            'fields': ('orders_count', 'total_sales', 'average_order_value')
        }),
        ('Fulfillment', {
            'fields': ('on_time_delivery_percentage', 'order_accuracy_percentage')
        }),
        ('Quality', {
            'fields': ('return_rate_percentage', 'complaint_count')
        }),
        ('Payment', {
            'fields': ('payment_on_time_percentage',)
        }),
        ('Rating', {
            'fields': ('overall_rating',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

