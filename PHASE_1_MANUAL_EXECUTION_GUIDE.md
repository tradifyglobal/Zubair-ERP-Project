# Phase 1 Implementation - Manual Execution Steps
## Raw Materials Management System Setup

**Date**: April 8, 2026  
**Status**: Ready for Manual Execution  
**Time Estimate**: 10-15 minutes

---

## 📋 CURRENT STATUS

✅ **COMPLETED (Automated)**:
- [x] Django app created: `/var/www/tradifyerp/raw_materials/`
- [x] Models deployed: `models.py` (10 models, 121 lines)
- [x] All admin interfaces prepared: `raw_materials_admin.py` locally
- [x] Management command ready: `load_raw_materials.py` locally

⏳ **REMAINING (Manual Steps Required)**:
- [ ] Add app to INSTALLED_APPS
- [ ] Deploy admin.py
- [ ] Create management directory and load command
- [ ] Run migrations
- [ ] Load data  
- [ ] Verify in Django Admin

---

## 🚀 STEP-BY-STEP EXECUTION GUIDE

### STEP 1: Add raw_materials to INSTALLED_APPS (2 minutes)

**Command**: SSH to app server and edit settings file

```bash
ssh root@192.168.20.10
```

**Edit the file**:
```bash
nano /var/www/tradifyerp/TradifyERP/settings_production.py
```

**Find line with** (around line 132):
```python
    'ar.apps.ArConfig',  # Accounts Receivable Module
```

**Add this line after it**:
```python
    'raw_materials',  # Raw Materials Management
```

**Result** (should look like):
```python
    'ar.apps.ArConfig',  # Accounts Receivable Module
    'raw_materials',  # Raw Materials Management
    'expenses.apps.ExpensesConfig',
```

**Save**: `Ctrl+O`, then `Enter`, then `Ctrl+X`

**Verify**:
```bash
grep 'raw_materials' /var/www/tradifyerp/TradifyERP/settings_production.py
# Should show: 'raw_materials',  # Raw Materials Management
```

---

### STEP 2: Deploy admin.py (2 minutes)

**Create admin.py**:
```bash
cat > /var/www/tradifyerp/raw_materials/admin.py << 'EOF'
from django.contrib import admin
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

@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'quantity_received', 'quality_check_passed']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'movement_type', 'quantity', 'created_at']
    list_filter = ['movement_type']

@admin.register(AutoReorderSetting)
class AutoReorderSettingAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'is_enabled', 'trigger_stock_level']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'alert_type', 'severity', 'is_active']
    list_filter = ['is_active', 'alert_type', 'severity']

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'production_order', 'planned_quantity', 'actual_quantity']
EOF
```

**Verify**:
```bash
wc -l /var/www/tradifyerp/raw_materials/admin.py
# Should show: ~100 lines
```

---

### STEP 3: Setup Management Command (2 minutes)

**Create directories**:
```bash
mkdir -p /var/www/tradifyerp/raw_materials/management/commands
touch /var/www/tradifyerp/raw_materials/management/__init__.py
touch /var/www/tradifyerp/raw_materials/management/commands/__init__.py
```

**Create load command** (this is long - paste all of it):
```bash
cat > /var/www/tradifyerp/raw_materials/management/commands/load_raw_materials.py << 'EOFLOAD'
from django.core.management.base import BaseCommand
from raw_materials.models import RawMaterialCategory, Supplier, RawMaterial, Stock
from decimal import Decimal

class Command(BaseCommand):
    help = 'Load initial raw materials data'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Loading Raw Materials ===\n'))
        
        # Categories
        categories_data = [
            {'name': 'Polymer Base', 'description': 'PBAT, PLA'},
            {'name': 'Fiber/Filler', 'description': 'Fiber additives'},
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
        
        # Materials
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
        print(f"✓ Materials: {RawMaterial.objects.count()}")
        print(f"✓ Stock: {Stock.objects.count()}")
        self.stdout.write(self.style.SUCCESS('\n✓ Data loaded!\n'))
EOFLOAD
```

---

### STEP 4: Run Migrations (3 minutes)

**Create migrations**:
```bash
cd /var/www/tradifyerp
./venv/bin/python manage.py makemigrations raw_materials
```

**Expected output**:
```
Migrations for 'raw_materials':
  raw_materials/migrations/0001_initial.py
    - Create model RawMaterialCategory
    ...
```

**Apply migrations**:
```bash
./venv/bin/python manage.py migrate raw_materials
```

**Expected output**:
```
Running migrations:
  Applying raw_materials.0001_initial... OK
```

---

### STEP 5: Load Data (3 minutes)

**Execute load command**:
```bash
cd /var/www/tradifyerp
./venv/bin/python manage.py load_raw_materials
```

**Expected output**:
```
=== Loading Raw Materials ===

✓ Categories: 5
✓ Suppliers: 5
✓ Materials: 15
✓ Stock: 15

✓ Data loaded!
```

---

### STEP 6: Restart Services (2 minutes)

**Restart Gunicorn**:
```bash
systemctl restart gunicorn
```

**Verify status**:
```bash
systemctl status gunicorn
```

---

### STEP 7: Verify in Django Admin (2 minutes)

**Open browser**:
- URL: `http://192.168.20.10/admin`
- Login with your superuser credentials

**Check**:
1. ✓ Can you see "Raw Materials Management" section?
2. ✓ Click "Raw Material Categories" - see 5 categories?
3. ✓ Click "Raw Materials" - see 15 materials?
4. ✓ Click "Suppliers" - see 5 suppliers?
5. ✓ Click "Stock" - see color-coded status (green/orange/red)?

---

## ✅ SUCCESS CHECKLIST

After completing all steps, you should have:

- [ ] `'raw_materials'` in INSTALLED_APPS
- [ ] `/raw_materials/admin.py` deployed (80+ lines)
- [ ] `/raw_materials/management/commands/load_raw_materials.py` created
- [ ] Migrations created and applied
- [ ] 15 raw materials loaded
- [ ] 5 suppliers configured
- [ ] 5 categories created
- [ ] Django admin accessible with Raw Materials section visible
- [ ] All 15 materials visible in admin with correct stock levels

---

## 🎯 Estimated Total Time: 10-15 minutes

**Current Progress**: 60%  
**Remaining**: 40% (manual steps)

---

## 📞 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: raw_materials` | Ensure app is in INSTALLED_APPS and settings file is saved |
| `No module named 'raw_materials'` | Run migrations first: `python manage.py makemigrations raw_materials` |
| Admin shows no Raw Materials section | Restart Gunicorn: `systemctl restart gunicorn` |
| Data won't load | Check if migrations were applied: `python manage.py showmigrations raw_materials` |

---

**Files Ready in Your Workspace**:
- ✅ `raw_materials_admin.py` - Admin interface code
- ✅ `load_raw_materials.py` - Data load command
- ✅ `phase1_setup.py` - Python setup script
- ✅ `setup_raw_materials.sh` - Bash setup script
- ✅ `PHASE_1_IMPLEMENTATION_STATUS.md` - Detailed checklist

Copy these commands and execute them on your app server (`ssh root@192.168.20.10`).

