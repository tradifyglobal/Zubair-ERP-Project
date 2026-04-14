# Phase 1 Quick Reference - Copy/Paste Commands
## 10-15 Minute Execution Guide

---

## STEP 1: Register App (2 min)
```bash
ssh root@192.168.20.10
nano /var/www/tradifyerp/TradifyERP/settings_production.py

# Find this line (around 132):
#     'ar.apps.ArConfig',  # Accounts Receivable Module

# Add after it:
#     'raw_materials',  # Raw Materials Management

# Save: CTRL+O, Enter, CTRL+X
```

Verify:
```bash
grep 'raw_materials' /var/www/tradifyerp/TradifyERP/settings_production.py
```

---

## STEP 2: Deploy Admin (2 min)

Copy the entire content of **raw_materials_admin.py** from your workspace.

On server:
```bash
nano /var/www/tradifyerp/raw_materials/admin.py
# Paste the entire admin.py content
# Save: CTRL+O, Enter, CTRL+X
```

Verify:
```bash
wc -l /var/www/tradifyerp/raw_materials/admin.py
# Should show ~350 lines
```

---

## STEP 3: Create Management Command (2 min)

```bash
mkdir -p /var/www/tradifyerp/raw_materials/management/commands
touch /var/www/tradifyerp/raw_materials/management/__init__.py
touch /var/www/tradifyerp/raw_materials/management/commands/__init__.py
```

Copy the entire content of **load_raw_materials.py** from your workspace.

On server:
```bash
nano /var/www/tradifyerp/raw_materials/management/commands/load_raw_materials.py
# Paste the entire load_raw_materials.py content
# Save: CTRL+O, Enter, CTRL+X
```

Verify:
```bash
ls -la /var/www/tradifyerp/raw_materials/management/commands/
```

---

## STEP 4: Run Migrations (3 min)

```bash
cd /var/www/tradifyerp
./venv/bin/python manage.py makemigrations raw_materials
./venv/bin/python manage.py migrate raw_materials
```

Should see:
```
Migrations for 'raw_materials':
  raw_materials/migrations/0001_initial.py
    - Create model RawMaterialCategory
    - Create model Supplier
    ...

Operations to perform:
  Apply all migrations: raw_materials
  [OK] 0001_initial
```

---

## STEP 5: Load Data (3 min)

```bash
cd /var/www/tradifyerp
./venv/bin/python manage.py load_raw_materials
```

Should see:
```
=== Loading Raw Materials ===

✓ Categories: 5
✓ Suppliers: 5
✓ Materials: 15
✓ Stock: 15

✓ Data loaded successfully!
```

---

## STEP 6: Restart Service (1 min)

```bash
systemctl restart gunicorn
```

Verify:
```bash
systemctl status gunicorn
# Should show: active (running)
```

---

## STEP 7: Verify in Browser (2 min)

1. Open browser: `http://192.168.20.10/admin`
2. Login with your admin credentials
3. Look for "Raw Materials Management" section
4. Click "Raw Materials" → should see 15 items:
   - RM-PBAT-001
   - RM-PLA-002
   - RM-CS-003
   - ... etc

5. Click "Suppliers" → should see 5 suppliers
6. Click "Stock" → should see color coding (green/orange/red)

---

## ✅ SUCCESS INDICATORS

- [x] INSTALLED_APPS contains 'raw_materials'
- [x] Admin section appears in Django admin
- [x] 15 raw materials visible
- [x] Stock colors working
- [x] All 5 suppliers loaded
- [x] All 5 categories loaded

**If all above are checked = Phase 1 COMPLETE**

---

## 🆘 TROUBLESHOOTING (Quick Fixes)

### "raw_materials not found in INSTALLED_APPS"
```bash
# Check the line was added (check line numbers around 132-135)
sed -n '130,140p' /var/www/tradifyerp/TradifyERP/settings_production.py
```

### "ModuleNotFoundError for raw_materials"
```bash
# Restart Gunicorn
systemctl restart gunicorn
systemctl restart nginx
```

### "Table doesn't exist" error
```bash
# Redo migrations
cd /var/www/tradifyerp
./venv/bin/python manage.py migrate raw_materials
```

### "Data not loading"
```bash
# Check if command is found
cd /var/www/tradifyerp
./venv/bin/python manage.py help load_raw_materials
```

---

## 📞 IF YOU GET STUCK

1. Check this report: `PHASE_1_FINAL_STATUS_REPORT.md`
2. Full manual guide: `PHASE_1_MANUAL_EXECUTION_GUIDE.md`
3. Status checklist: `PHASE_1_IMPLEMENTATION_STATUS.md`

---

**Expected Total Time**: 10-15 minutes  
**Starting Time**: [Your current time]  
**Expected Completion**: [Your time + 15 minutes]

Now you can copy-paste each step as you go. **You've got this!** ✨

