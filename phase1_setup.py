#!/usr/bin/env python3
"""
Phase 1 Setup - Complete Implementation
Handles: settings update, admin creation, migrations, data load
"""

import os
import sys
import django
from pathlib import Path

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

from django.core.management import call_command
from raw_materials.models import (
    RawMaterialCategory, Supplier, RawMaterial, Stock
)
from decimal import Decimal

def step_1_add_to_settings():
    """Add app to INSTALLED_APPS if not already there"""
    print("\n[STEP 1] Checking INSTALLED_APPS...")
    settings_file = '/var/www/tradifyerp/TradifyERP/settings_production.py'
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    if "'raw_materials'" not in content:
        # Find ar.apps.ArConfig line and add after it
        old_line = "    'ar.apps.ArConfig',  # Accounts Receivable Module"
        new_section = old_line + "\n    'raw_materials',  # Raw Materials Management"
        
        if old_line in content:
            content = content.replace(old_line, new_section)
            with open(settings_file, 'w') as f:
                f.write(content)
            print("✓ Added 'raw_materials' to INSTALLED_APPS")
        else:
            print("! Could not find insertion point - app may already be registered")
    else:
        print("✓ 'raw_materials' already in INSTALLED_APPS")

def step_2_create_admin():
    """Create admin.py file"""
    print("\n[STEP 2] Creating admin.py...")
    admin_path = '/var/www/tradifyerp/raw_materials/admin.py'
    
    admin_content = '''from django.contrib import admin
from django.utils.html import format_html
from .models import (
    RawMaterialCategory, Supplier, RawMaterial, Stock, StockMovement,
    PurchaseOrder, GoodsReceiptNote, AutoReorderSetting, StockAlert, MaterialConsumption
)

@admin.register(RawMaterialCategory)
class RawMaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_code', 'name', 'city', 'quality_rating', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'supplier_code']

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'name', 'category', 'unit_of_measure', 'current_unit_price', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['product_code', 'name']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'quantity_on_hand', 'minimum_stock_level', 'status_color']
    search_fields = ['raw_material__name']
    def status_color(self, obj):
        if obj.quantity_on_hand == 0:
            color, text = 'red', 'Out'
        elif obj.quantity_on_hand < obj.minimum_stock_level:
            color, text = 'orange', 'Low'
        else:
            color, text = 'green', 'OK'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, text)
    status_color.short_description = 'Status'

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'raw_material', 'quantity_ordered', 'status']
    list_filter = ['status', 'po_date']
    search_fields = ['po_number', 'supplier__name']

@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'quantity_received', 'quality_check_passed']
    search_fields = ['grn_number']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'movement_type', 'quantity', 'created_at']
    list_filter = ['movement_type', 'created_at']

@admin.register(AutoReorderSetting)
class AutoReorderSettingAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'is_enabled', 'trigger_stock_level']
    list_filter = ['is_enabled']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'alert_type', 'severity', 'is_active']
    list_filter = ['is_active', 'alert_type', 'severity']

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'production_order', 'planned_quantity', 'actual_quantity']
    list_filter = ['consumption_date']
'''
    
    try:
        with open(admin_path, 'w') as f:
            f.write(admin_content)
        print("✓ admin.py created successfully")
    except Exception as e:
        print(f"! Error creating admin.py: {e}")

def step_3_run_migrations():
    """Run Django migrations"""
    print("\n[STEP 3] Running migrations...")
    try:
        call_command('makemigrations', 'raw_materials', verbosity=0)
        print("✓ Migrations created")
        call_command('migrate', 'raw_materials', verbosity=0)
        print("✓ Migrations applied")
    except Exception as e:
        print(f"! Migration error: {e}")

def step_4_load_data():
    """Load raw materials data"""
    print("\n[STEP 4] Loading raw materials data...")
    
    # Categories
    categories_data = [
        {'name': 'Polymer Base', 'description': 'PBAT, PLA'},
        {'name': 'Fiber/Filler', 'description': 'Additives'},
        {'name': 'Additive', 'description': 'Chemical additives'},
        {'name': 'Specialty', 'description': 'Specialty materials'},
        {'name': 'Packaging', 'description': 'Packaging materials'},
    ]
    
    for cd in categories_data:
        cat, created = RawMaterialCategory.objects.get_or_create(
            name=cd['name'],
            defaults={'description': cd['description'], 'is_active': True}
        )
    
    print(f"✓ Categories: {RawMaterialCategory.objects.count()}")
    
    # Suppliers
    suppliers_data = [
        {'code': 'SUP-001', 'name': 'ABC Polymers', 'city': 'Bangalore'},
        {'code': 'SUP-002', 'name': 'Natural Sources', 'city': 'Mumbai'},
        {'code': 'SUP-003', 'name': 'Mineral Suppliers', 'city': 'Delhi'},
        {'code': 'SUP-004', 'name': 'Color Masters', 'city': 'Pune'},
        {'code': 'SUP-005', 'name': 'Chemical House', 'city': 'Hyderabad'},
    ]
    
    suppliers = {}
    for sd in suppliers_data:
        code = sd.pop('code')
        sup, _ = Supplier.objects.get_or_create(
            supplier_code=code,
            defaults={**sd, 'country': 'India', 'is_active': True}
        )
        suppliers[code] = sup
    
    print(f"✓ Suppliers: {Supplier.objects.count()}")
    
    # Materials and Stock
    categories = {c.name: c for c in RawMaterialCategory.objects.all()}
    mat_data = [
        ('RM-PBAT-001', 'PBAT Granules', 'Polymer Base', 'KG', 'SUP-001', 450, 200, 1000, 500, 800),
        ('RM-PLA-002', 'PLA Granules', 'Polymer Base', 'KG', 'SUP-001', 520, 200, 1000, 500, 750),
        ('RM-CS-003', 'Corn Starch', 'Fiber/Filler', 'KG', 'SUP-002', 280, 150, 500, 250, 350),
        ('RM-TPS-004', 'Thermoplastic Starch', 'Fiber/Filler', 'KG', 'SUP-002', 350, 150, 500, 250, 300),
        ('RM-CACO3-005', 'Calcium Carbonate', 'Additive', 'KG', 'SUP-003', 120, 100, 300, 100, 200),
        ('RM-MB-006', 'Color Masterbatch', 'Additive', 'KG', 'SUP-004', 650, 50, 200, 75, 120),
        ('RM-TIO2-007', 'Titanium Dioxide', 'Additive', 'KG', 'SUP-003', 890, 25, 100, 50, 60),
        ('RM-PLAST-008', 'Glycerol Plasticizer', 'Additive', 'KG', 'SUP-005', 410, 50, 200, 100, 150),
        ('RM-STAB-009', 'Biodegradable Stabilizer', 'Additive', 'KG', 'SUP-005', 550, 50, 150, 75, 100),
        ('RM-MESH-010', 'Biodegradable Mesh', 'Specialty', 'KG', 'SUP-001', 880, 30, 100, 50, 75),
        ('RM-NWF-011', 'Non-woven PLA Fabric', 'Specialty', 'KG', 'SUP-002', 720, 25, 100, 50, 80),
        ('RM-PLAFILM-012', 'PLA Film Roll', 'Specialty', 'KG', 'SUP-001', 680, 20, 80, 40, 65),
        ('RM-PACK-013', 'Packaging Poly Roll', 'Packaging', 'KG', 'SUP-003', 180, 50, 200, 100, 150),
        ('RM-LABEL-014', 'Product Labels', 'Packaging', 'PCS', 'SUP-004', 2.5, 1000, 5000, 2000, 3500),
        ('RM-CARTON-015', 'Carton Boxes', 'Packaging', 'PCS', 'SUP-003', 4.75, 500, 2000, 1000, 1500),
    ]
    
    for code, name, cat_name, unit, sup_code, price, min_st, max_st, reord, curr in mat_data:
        mat, _ = RawMaterial.objects.get_or_create(
            product_code=code,
            defaults={
                'name': name,
                'category': categories[cat_name],
                'unit_of_measure': unit,
                'default_supplier': suppliers[sup_code],
                'current_unit_price': Decimal(str(price)),
                'is_active': True,
            }
        )
        Stock.objects.get_or_create(
            raw_material=mat,
            defaults={
                'quantity_on_hand': Decimal(str(curr)),
                'minimum_stock_level': Decimal(str(min_st)),
                'maximum_stock_level': Decimal(str(max_st)),
                'reorder_quantity': Decimal(str(reord)),
                'valuation_method': 'FIFO',
                'standard_cost': Decimal(str(price)),
            }
        )
    
    print(f"✓ Raw Materials: {RawMaterial.objects.count()}")
    print(f"✓ Stock Records: {Stock.objects.count()}")

def step_5_verify():
    """Verify setup"""
    print("\n[STEP 5] Verification...")
    print(f"  Categories: {RawMaterialCategory.objects.count()}")
    print(f"  Suppliers: {Supplier.objects.count()}")
    print(f"  Materials: {RawMaterial.objects.count()}")
    print(f"  Stock: {Stock.objects.count()}")
    
    mats = RawMaterial.objects.all()[:3]
    print(f"\n  Sample materials:")
    for m in mats:
        try:
            stock_qty = m.stock.quantity_on_hand
        except:
            stock_qty = "N/A"
        print(f"    ✓ {m.product_code}: {m.name}")

if __name__ == '__main__':
    print("="*50)
    print("Raw Materials Phase 1 - Complete Setup")
    print("="*50)
    
    try:
        step_1_add_to_settings()
        step_2_create_admin()
        step_3_run_migrations()
        step_4_load_data()
        step_5_verify()
        
        print("\n" + "="*50)
        print("✓ PHASE 1 COMPLETE!")
        print("="*50)
        print("\nNext steps:")
        print("  1. systemctl restart gunicorn")
        print("  2. Access http://192.168.20.10/admin")
        print("  3. Check Raw Materials section")
        
    except Exception as e:
        print(f"\n! Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
