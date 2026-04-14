#!/bin/bash
# Raw Materials Management System - Phase 1 Complete Setup Script
# Executes all remaining Phase 1 tasks automatically
# Usage: bash /tmp/setup_raw_materials.sh

set -e

APP_DIR="/var/www/tradifyerp"
VENV="$APP_DIR/venv/bin/python"
SETTINGS="$APP_DIR/TradifyERP/settings_production.py"

echo "=========================================="
echo "Raw Materials Phase 1 - Complete Setup"
echo "=========================================="
echo ""

# =====================================================================
# STEP 1: Add app to INSTALLED_APPS
# =====================================================================
echo "[1/5] Adding 'raw_materials' to INSTALLED_APPS..."

if ! grep -q "'raw_materials'" "$SETTINGS"; then
    # Find the line with ar.apps.ArConfig and add raw_materials after it
    sed -i "/    'ar\.apps\.ArConfig',/a\\    'raw_materials',  # Raw Materials Management" "$SETTINGS"
    echo "✓ Added 'raw_materials' to INSTALLED_APPS"
else
    echo "✓ 'raw_materials' already in INSTALLED_APPS"
fi
echo ""

# =====================================================================
# STEP 2: Deploy admin.py
# =====================================================================
echo "[2/5] Deploying admin.py..."

# Create admin.py with full content
cat > "$APP_DIR/raw_materials/admin.py" << 'EOF'
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    RawMaterialCategory, Supplier, RawMaterial, Stock, StockMovement,
    PurchaseOrder, GoodsReceiptNote, AutoReorderSetting, StockAlert, MaterialConsumption
)

@admin.register(RawMaterialCategory)
class RawMaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_code', 'name', 'city', 'quality_rating', 'is_active']
    list_filter = ['is_active', 'country', 'iso_certified']
    search_fields = ['name', 'supplier_code']

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'name', 'category', 'unit_of_measure', 'current_unit_price', 'is_active']
    list_filter = ['is_active', 'category', 'unit_of_measure']
    search_fields = ['product_code', 'name']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'quantity_on_hand', 'minimum_stock_level', 'status_color']
    search_fields = ['raw_material__name']
    def status_color(self, obj):
        if obj.quantity_on_hand == 0:
            color = 'red'
            text = 'Out'
        elif obj.quantity_on_hand < obj.minimum_stock_level:
            color = 'orange'
            text = 'Low'
        else:
            color = 'green'
            text = 'OK'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, text)
    status_color.short_description = 'Status'

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'raw_material', 'quantity_ordered', 'status']
    list_filter = ['status', 'po_date']
    search_fields = ['po_number', 'supplier__name']

@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'quantity_received', 'quality_check_passed']
    list_filter = ['quality_check_passed', 'receipt_date']
    search_fields = ['grn_number']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'movement_type', 'quantity', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['raw_material__name']

@admin.register(AutoReorderSetting)
class AutoReorderSettingAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'is_enabled', 'trigger_stock_level']
    list_filter = ['is_enabled', 'auto_generate_po']
    search_fields = ['raw_material__name']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'alert_type', 'severity', 'is_active', 'created_at']
    list_filter = ['is_active', 'alert_type', 'severity']
    search_fields = ['raw_material__name']

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'production_order', 'planned_quantity', 'actual_quantity']
    list_filter = ['consumption_date']
    search_fields = ['raw_material__name', 'production_order']
EOF

echo "✓ admin.py deployed successfully"
echo ""

# =====================================================================
# STEP 3: Create management command directory
# =====================================================================
echo "[3/5] Setting up management command..."

mkdir -p "$APP_DIR/raw_materials/management/commands"
touch "$APP_DIR/raw_materials/management/__init__.py"
touch "$APP_DIR/raw_materials/management/commands/__init__.py"

# Create the load command
cat > "$APP_DIR/raw_materials/management/commands/load_raw_materials.py" << 'EOFCMD'
from django.core.management.base import BaseCommand
from raw_materials.models import RawMaterialCategory, Supplier, RawMaterial, Stock
from decimal import Decimal

class Command(BaseCommand):
    help = 'Load initial raw materials and data'
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Loading Raw Materials ===\n'))
        categories_data = [
            {'name': 'Polymer Base', 'description': 'PBAT, PLA'},
            {'name': 'Fiber/Filler', 'description': 'Additives'},
            {'name': 'Additive', 'description': 'Chemical additives'},
            {'name': 'Specialty', 'description': 'Specialty materials'},
            {'name': 'Packaging', 'description': 'Packaging materials'},
        ]
        for cat_data in categories_data:
            cat, created = RawMaterialCategory.objects.get_or_create(name=cat_data['name'], defaults={'description': cat_data['description'], 'is_active': True})
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {cat.name}")
        suppliers_data = [
            {'code': 'SUP-001', 'name': 'ABC Polymers', 'city': 'Bangalore', 'country': 'India'},
            {'code': 'SUP-002', 'name': 'Natural Sources', 'city': 'Mumbai', 'country': 'India'},
            {'code': 'SUP-003', 'name': 'Mineral Suppliers', 'city': 'Delhi', 'country': 'India'},
            {'code': 'SUP-004', 'name': 'Color Masters', 'city': 'Pune', 'country': 'India'},
            {'code': 'SUP-005', 'name': 'Chemical House', 'city': 'Hyderabad', 'country': 'India'},
        ]
        suppliers = {}
        for sup_data in suppliers_data:
            code = sup_data.pop('code')
            sup, created = Supplier.objects.get_or_create(supplier_code=code, defaults={**sup_data, 'is_active': True})
            suppliers[code] = sup
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {sup.name}")
        categories = {cat.name: cat for cat in RawMaterialCategory.objects.all()}
        materials_data = [
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
        created_count = 0
        for code, name, cat_name, unit, sup_code, price, min_st, max_st, reord_qty, curr_st in materials_data:
            mat, created = RawMaterial.objects.get_or_create(product_code=code, defaults={'name': name, 'category': categories[cat_name], 'unit_of_measure': unit, 'default_supplier': suppliers[sup_code], 'current_unit_price': Decimal(str(price)), 'is_active': True})
            stock, _ = Stock.objects.get_or_create(raw_material=mat, defaults={'quantity_on_hand': Decimal(str(curr_st)), 'minimum_stock_level': Decimal(str(min_st)), 'maximum_stock_level': Decimal(str(max_st)), 'reorder_quantity': Decimal(str(reord_qty)), 'valuation_method': 'FIFO', 'standard_cost': Decimal(str(price))})
            if created:
                created_count += 1
                self.stdout.write(f"  Created: {code} - {name}")
        self.stdout.write(self.style.SUCCESS(f'\n✓ Raw Materials: {created_count} created'))
        self.stdout.write(f'Total Materials: {RawMaterial.objects.count()}')
        self.stdout.write(f'Total Stock: {Stock.objects.count()}\n')
EOFCMD

echo "✓ Management command created"
echo ""

# =====================================================================
# STEP 4: Run migrations
# =====================================================================
echo "[4/5] Running migrations..."

cd "$APP_DIR"

# Create migrations
$VENV manage.py makemigrations raw_materials 2>&1 | grep -v "^Migrations\|^  " || true
echo "✓ Migrations created"

# Apply migrations
$VENV manage.py migrate raw_materials 2>&1 | grep "Applying\|OK" || true
echo "✓ Migrations applied"
echo ""

# =====================================================================
# STEP 5: Load data
# =====================================================================
echo "[5/5] Loading initial data..."

$VENV manage.py load_raw_materials 2>&1 | tail -20
echo ""

# =====================================================================
# VERIFICATION
# =====================================================================
echo "=========================================="
echo "✓ Phase 1 Setup Complete!"
echo "=========================================="
echo ""

$VENV manage.py shell << 'EOFSHELL'
from raw_materials.models import RawMaterial, RawMaterialCategory, Supplier, Stock
print(f"\nDatabase Summary:")
print(f"  Categories: {RawMaterialCategory.objects.count()}")
print(f"  Suppliers: {Supplier.objects.count()}")
print(f"  Raw Materials: {RawMaterial.objects.count()}")
print(f"  Stock Records: {Stock.objects.count()}")
print(f"\nFirst 5 Materials:")
for m in RawMaterial.objects.all()[:5]:
    stock = m.stock.quantity_on_hand if hasattr(m, 'stock') else 'N/A'
    print(f"  ✓ {m.product_code} - {m.name} (Stock: {stock} {m.unit_of_measure})")
print("")
EOFSHELL

echo "Next steps:"
echo "  1. Restart Gunicorn: systemctl restart gunicorn"
echo "  2. Access Django Admin: http://192.168.20.10/admin"
echo "  3. Verify Raw Materials section is visible"
echo ""
