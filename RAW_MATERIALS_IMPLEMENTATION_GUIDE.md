# Raw Materials Module - Implementation Guide
## Step-by-Step Integration into TradifyERP

**Date**: April 7, 2026  
**Module Name**: raw_materials  
**Status**: Ready for Development

---

## 🚀 QUICK START

### Step 1: Create the Django App

```bash
ssh root@192.168.20.10
cd /var/www/tradifyerp

python manage.py startapp raw_materials

# Output:
# Created new app 'raw_materials' with models, views, urls, admin, tests, etc.
```

### Step 2: Copy Models File

```bash
# Copy the models from RAW_MATERIALS_MODELS.py to:
# /var/www/tradifyerp/raw_materials/models.py
```

### Step 3: Add to INSTALLED_APPS

Edit `/var/www/tradifyerp/TradifyERP/settings_production.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'manufacturing',
    'sales',
    'inventory',
    'ap',
    'procurement',
    'accounting',
    'shareholder',
    'crm',
    'ar',
    'expenses',
    'maintenance',
    'cash_management',
    'projects',
    
    # ✨ ADD THIS NEW LINE:
    'raw_materials',  # Raw Materials Management Module
]
```

### Step 4: Create Migrations

```bash
cd /var/www/tradifyerp

# Create migration files
python manage.py makemigrations raw_materials

# Apply migrations to database
python manage.py migrate raw_materials
```

### Step 5: Create Admin Interface

Create `/var/www/tradifyerp/raw_materials/admin.py`:

```python
from django.contrib import admin
from .models import (
    RawMaterialCategory, Supplier, RawMaterial, Stock,
    StockMovement, PurchaseOrder, GoodsReceiptNote,
    AutoReorderSetting, StockAlert, MaterialConsumption
)

@admin.register(RawMaterialCategory)
class RawMaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_code', 'name', 'city', 'quality_rating', 'is_active']
    search_fields = ['name', 'supplier_code']
    list_filter = ['is_active', 'city']
    fieldsets = (
        ('Basic Info', {'fields': ('supplier_code', 'name', 'contact_person')}),
        ('Contact', {'fields': ('email', 'phone', 'address', 'city', 'state', 'country')}),
        ('Payment Terms', {'fields': ('payment_terms', 'credit_limit', 'currency')}),
        ('Performance', {'fields': ('quality_rating', 'delivery_rating', 'price_competitiveness')}),
        ('Certifications', {'fields': ('iso_certified', 'quality_certifications')}),
    )

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'name', 'category', 'unit_of_measure', 'current_unit_price', 'is_active']
    search_fields = ['product_code', 'name']
    list_filter = ['category', 'is_active', 'unit_of_measure']
    fieldsets = (
        ('Basic Info', {'fields': ('product_code', 'name', 'description', 'category')}),
        ('Specifications', {'fields': ('unit_of_measure', 'density', 'hsn_code', 'biodegradability_days')}),
        ('Supplier & Cost', {'fields': ('default_supplier', 'current_unit_price')}),
        ('Settings', {'fields': ('is_active', 'is_hazardous', 'is_recyclable')}),
    )

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'quantity_on_hand', 'minimum_stock_level', 'needs_reorder']
    search_fields = ['raw_material__name']
    list_filter = ['valuation_method']
    readonly_fields = ['updated_at']
    fieldsets = (
        ('Material', {'fields': ('raw_material',)}),
        ('Stock Quantities', {'fields': ('quantity_on_hand', 'quantity_reserved', 'quantity_damaged')}),
        ('Thresholds', {'fields': ('minimum_stock_level', 'maximum_stock_level', 'reorder_quantity')}),
        ('Lead Time & Location', {'fields': ('lead_time_days', 'warehouse_location')}),
        ('Valuation', {'fields': ('valuation_method', 'standard_cost', 'actual_cost')}),
    )

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'raw_material', 'quantity_ordered', 'status', 'expected_delivery_date']
    search_fields = ['po_number', 'supplier__name']
    list_filter = ['status', 'po_date']
    readonly_fields = ['po_date', 'created_at', 'updated_at']
    fieldsets = (
        ('PO Details', {'fields': ('po_number', 'po_date', 'supplier')}),
        ('Line Item', {'fields': ('raw_material', 'quantity_ordered', 'unit_price', 'line_total')}),
        ('Delivery', {'fields': ('expected_delivery_date', 'actual_delivery_date', 'warehouse_location')}),
        ('Status & Approval', {'fields': ('status', 'approval_date', 'approved_by')}),
        ('Tracking', {'fields': ('quantity_received', 'quantity_rejected')}),
        ('Notes', {'fields': ('notes',)}),
    )
    actions = ['approve_po', 'mark_ordered']
    
    def approve_po(self, request, queryset):
        for po in queryset:
            po.approve(request.user)
        self.message_user(request, f"{queryset.count()} POs approved")
    approve_po.short_description = "Approve selected POs"
    
    def mark_ordered(self, request, queryset):
        queryset.update(status='ORDERED')
        self.message_user(request, f"{queryset.count()} POs marked as ordered")
    mark_ordered.short_description = "Mark as ordered with supplier"

@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'receipt_date', 'quantity_received', 'quality_check_passed']
    search_fields = ['grn_number', 'purchase_order__po_number']
    list_filter = ['quality_check_passed', 'receipt_date']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'alert_type', 'severity', 'is_active', 'created_at']
    search_fields = ['raw_material__name']
    list_filter = ['alert_type', 'severity', 'is_active']
    actions = ['acknowledge_alert', 'resolve_alert']
    
    def acknowledge_alert(self, request, queryset):
        for alert in queryset:
            alert.acknowledge(request.user)
        self.message_user(request, f"{queryset.count()} alerts acknowledged")
    acknowledge_alert.short_description = "Acknowledge selected alerts"
    
    def resolve_alert(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} alerts resolved")
    resolve_alert.short_description = "Resolve selected alerts"

# Register remaining models
admin.site.register(AutoReorderSetting)
admin.site.register(StockMovement)
admin.site.register(MaterialConsumption)
```

### Step 6: Create Initial Data

Create `/var/www/tradifyerp/raw_materials/management/commands/load_raw_materials.py`:

```bash
# Create the directory structure first
mkdir -p /var/www/tradifyerp/raw_materials/management/commands
touch /var/www/tradifyerp/raw_materials/management/__init__.py
touch /var/www/tradifyerp/raw_materials/management/commands/__init__.py
```

Then create the import script:

```python
from django.core.management.base import BaseCommand
from raw_materials.models import RawMaterialCategory, RawMaterial, Supplier

class Command(BaseCommand):
    help = 'Load initial raw materials data'

    def handle(self, *args, **options):
        # Create categories
        categories = {
            'polymer': 'Polymer Base Materials',
            'fiber': 'Fiber & Filler Materials',
            'additive': 'Additives & Colorants',
            'specialty': 'Specialty Materials',
            'packaging': 'Packaging Materials',
        }
        
        cat_objects = {}
        for key, name in categories.items():
            cat, created = RawMaterialCategory.objects.get_or_create(name=name)
            cat_objects[key] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {name}'))
        
        # Create raw materials
        materials_data = [
            ('RM-PBAT-001', 'PBAT Granules', 'Flexible biodegradable polymer for film blowing', 'polymer', 'KG'),
            ('RM-PLA-002', 'PLA Granules', 'Plant-based biodegradable plastic from starch', 'polymer', 'KG'),
            # ... Add all 15 materials
        ]
        
        for code, name, desc, category_key, unit in materials_data:
            obj, created = RawMaterial.objects.get_or_create(
                product_code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'category': cat_objects[category_key],
                    'unit_of_measure': unit,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created material: {code}'))
        
        self.stdout.write(self.style.SUCCESS('✓ All raw materials loaded!'))
```

Run the command:

```bash
cd /var/www/tradifyerp
python manage.py load_raw_materials
```

---

## 🔧 CREATE URLS & VIEWS

### Step 7: Create URLs

Create `/var/www/tradifyerp/raw_materials/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'raw_materials'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Raw Materials
    path('materials/', views.material_list, name='material_list'),
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    path('materials/create/', views.material_create, name='material_create'),
    
    # Stock Management
    path('stock/<int:pk>/', views.stock_detail, name='stock_detail'),
    path('stock/update/<int:pk>/', views.stock_update, name='stock_update'),
    
    # Purchase Orders
    path('purchase-orders/', views.po_list, name='po_list'),
    path('purchase-orders/create/', views.po_create, name='po_create'),
    path('purchase-orders/<int:pk>/approve/', views.po_approve, name='po_approve'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    
    # Alerts
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<int:pk>/acknowledge/', views.alert_acknowledge, name='alert_acknowledge'),
    
    # Reports
    path('reports/stock-valuation/', views.report_stock_valuation, name='report_stock_valuation'),
    path('reports/consumption/', views.report_consumption, name='report_consumption'),
]
```

---

## 📊 DATABASE INTEGRATION

### Integration with Existing Modules

**1. Link to Procurement Module**
```python
# In PurchaseOrder model, link to Procurement.ProcurementOrder
procurement_order = models.ForeignKey(
    'procurement.ProcurementOrder',
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)
```

**2. Link to Manufacturing Module**
```python
# In MaterialConsumption, track which Manufacturing order consumed material
from manufacturing.models import ProductionOrder
production_order_link = models.ForeignKey(
    ProductionOrder,
    on_delete=models.PROTECT
)
```

**3. Link to Accounting Module**
```python
# Track material costs in GL
# Create GL entry when material is consumed
def post_consumption(self):
    from accounting.models import JournalEntry
    JournalEntry.objects.create(
        account='Raw Materials - In Production Consumed',
        debit=self.total_cost,
        description=f'Material: {self.raw_material.name}'
    )
```

**4. Link to AP Module**
```python
# Create AP invoice when goods are received
def post_grn(self):
    from ap.models import Vendor Bill
    VendorBill.objects.create(
        vendor=self.purchase_order.supplier,
        amount=self.purchase_order.line_total,
        reference_po=self.purchase_order.po_number
    )
```

---

## 📋 DATA IMPORT TEMPLATE

Import your 15 raw materials using this CSV template:

```csv
product_code,name,description,category,unit_of_measure,default_supplier,current_unit_price,is_recyclable,biodegradability_days
RM-PBAT-001,PBAT Granules,Flexible biodegradable polymer for film blowing,Polymer Base Materials,KG,,0.00,TRUE,180
RM-PLA-002,PLA Granules,Plant-based biodegradable plastic from starch,Polymer Base Materials,KG,,0.00,TRUE,180
RM-CS-003,Corn Starch,Natural starch for biodegradable polymer blends,Fiber & Filler Materials,KG,,0.00,TRUE,90
RM-TPS-004,Thermoplastic Starch,Modified starch in compostable plastics,Fiber & Filler Materials,KG,,0.00,TRUE,90
RM-CACO3-005,Calcium Carbonate,Filler material to improve strength & reduce cost,Additives & Colorants,KG,,0.00,FALSE,0
RM-MB-006,Color Masterbatch,Color additive for biodegradable plastics,Additives & Colorants,KG,,0.00,FALSE,0
RM-TIO2-007,Titanium Dioxide,White pigment for plastic film color,Additives & Colorants,KG,,0.00,FALSE,0
RM-PLAST-008,Glycerol Plasticizer,Plasticizer to improve flexibility,Additives & Colorants,KG,,0.00,FALSE,0
RM-STAB-009,Biodegradable Stabilizer,Improves polymer processing stability,Additives & Colorants,KG,,0.00,FALSE,0
RM-MESH-010,Biodegradable Mesh Material,Used for breathable produce bags,Specialty Materials,KG,,0.00,TRUE,180
RM-NWF-011,Non-woven PLA Fabric,Used for aprons and salon capes,Specialty Materials,KG,,0.00,TRUE,180
RM-PLAFILM-012,PLA Film Roll,Film material for ponchos and covers,Specialty Materials,KG,,0.00,TRUE,180
RM-PACK-013,Packaging Poly Roll,Roll for packing finished products,Packaging Materials,KG,,0.00,FALSE,0
RM-LABEL-014,Product Labels,Printed labels for product packaging,Packaging Materials,PCS,,0.00,FALSE,0
RM-CARTON-015,Carton Boxes,Boxes for shipping products,Packaging Materials,PCS,,0.00,FALSE,0
```

**Import using Django admin or import-export:**

```bash
python manage.py shell

from raw_materials.models import RawMaterial, RawMaterialCategory
import csv

with open('raw_materials.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat, _ = RawMaterialCategory.objects.get_or_create(name=row['category'])
        RawMaterial.objects.get_or_create(
            product_code=row['product_code'],
            defaults={
                'name': row['name'],
                'description': row['description'],
                'category': cat,
                'unit_of_measure': row['unit_of_measure'],
                'is_recyclable': row['is_recyclable'] == 'TRUE',
                'biodegradability_days': int(row['biodegradability_days']) or None,
                'current_unit_price': float(row['current_unit_price']),
            }
        )

print("✓ All raw materials imported!")
```

---

## ✅ VERIFICATION CHECKLIST

After implementation:

- [ ] Module created: `raw_materials`
- [ ] Models migrated to database
- [ ] Admin interface working
- [ ] 15 raw materials imported
- [ ] Stock levels configured
- [ ] Suppliers added with pricing
- [ ] Auto-reorder settings configured
- [ ] Alert system activated
- [ ] Links to Manufacturing working
- [ ] Links to Procurement working
- [ ] Dashboard showing stock status
- [ ] Purchase orders generating
- [ ] GRN workflow operational

---

## 🚀 TESTING

### Create Test Data

```bash
cd /var/www/tradifyerp
python manage.py shell

from raw_materials.models import *
from django.contrib.auth.models import User

# Create test supplier
supplier = Supplier.objects.create(
    supplier_code='SUPP-001',
    name='ABC Polymers Ltd',
    email='sales@abcpolymers.com',
    payment_terms='NET30'
)

# Create stock for PBAT
material = RawMaterial.objects.get(product_code='RM-PBAT-001')
stock = Stock.objects.create(
    raw_material=material,
    quantity_on_hand=1000,
    minimum_stock_level=200,
    maximum_stock_level=5000,
    reorder_quantity=1000,
    lead_time_days=7,
    warehouse_location='A-001-01'
)

# Create auto-reorder
AutoReorderSetting.objects.create(
    raw_material=material,
    is_enabled=True,
    trigger_stock_level=200,
    auto_reorder_quantity=1000,
    preferred_supplier=supplier
)

print("✓ Test data created!")
```

### Test Low Stock Alert

```python
# Check if alert triggers when stock low
stock.quantity_on_hand = 150
stock.save()

# Should create alert via signal
alert = StockAlert.objects.filter(raw_material=material).first()
print(f"Alert Created: {alert.message}")
```

---

## 📞 NEXT STEPS

1. ✅ Review and approve this implementation plan
2. ✅ Set up the module following steps 1-7
3. ✅ Import the 15 raw materials
4. ✅ Configure suppliers and pricing
5. ✅ Test the system with sample orders
6. ✅ Train team on new module
7. ✅ Go live with production data

---

**Implementation Difficulty**: Medium  
**Time Required**: 5-8 days  
**Team Needed**: 1-2 Backend Developers  
**Testing Time**: 2-3 days

**You have a restore point ready at**: `/backups/restore_points/tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz`
