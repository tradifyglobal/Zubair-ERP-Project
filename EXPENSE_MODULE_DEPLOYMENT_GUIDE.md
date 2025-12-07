# Employee Expense Module - Deployment Guide

## Overview
This document provides step-by-step instructions for deploying the Employee Expense Tracking Module to the production environment.

**Production Server**: 192.168.2.185 (Ubuntu 24.04)  
**App Location**: `/var/www/tradifyerp/TradifyERP/`  
**App User**: gunicorn  
**Web Server**: Nginx  

## Deployment Status

### ✅ Completed
1. **Module Development** - Complete implementation with 6 models, 15 views, forms, templates
2. **Navigation Integration** - Added to both vertical and horizontal navigation menus
3. **Django Configuration** - Added to INSTALLED_APPS and URL patterns
4. **Git Commits** - All changes committed and pushed to `changes` branch
   - Commit a11634a: Initial module creation
   - Commit d0d6f59: Navigation and configuration integration

### ⏳ Pending
1. Copy module files to production server
2. Run database migrations
3. Restart Gunicorn service
4. Verify navigation appears correctly

## Step-by-Step Deployment Instructions

### Step 1: Connect to Production Server

```bash
# SSH into production server
ssh root@192.168.2.185

# Switch to app directory
cd /var/www/tradifyerp/TradifyERP/
```

### Step 2: Copy Module Files

Copy the complete expenses module directory to production:

```bash
# From local development machine (PowerShell/Bash)
# Using SCP or rsync to copy the expenses directory

# Option A: Using SCP (from local machine)
scp -r TradifyERP/expenses root@192.168.2.185:/var/www/tradifyerp/TradifyERP/

# Option B: Using rsync for better progress tracking
rsync -avz --progress TradifyERP/expenses root@192.168.2.185:/var/www/tradifyerp/TradifyERP/

# OR manually pull latest from Git on production server
cd /var/www/tradifyerp/TradifyERP/
git pull origin changes
```

### Step 3: Verify File Structure

On production server, verify the expenses module is in place:

```bash
ls -la /var/www/tradifyerp/TradifyERP/expenses/

# Expected output:
# __init__.py
# admin.py
# apps.py
# forms.py
# migrations/
# models.py
# templates/
# urls.py
# views.py
```

### Step 4: Verify Django Configuration

```bash
cd /var/www/tradifyerp/TradifyERP/

# Check settings.py for expenses in INSTALLED_APPS
grep -n "expenses" TradifyERP/settings.py

# Expected output:
# 'expenses.apps.ExpensesConfig',  # Employee Expense Tracking Module

# Check urls.py for expenses URL pattern
grep -n "expenses" TradifyERP/urls.py

# Expected output:
# path('expenses/', include('expenses.urls')),
```

### Step 5: Run Database Migrations

```bash
cd /var/www/tradifyerp/TradifyERP/

# Activate virtual environment (if using venv)
source venv/bin/activate  # For Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # For Windows PowerShell

# Run migrations for expenses module
python manage.py migrate expenses

# Expected output:
# Running migrations:
#   Applying expenses.0001_initial... OK
```

### Step 6: Collect Static Files (if needed)

```bash
python manage.py collectstatic --noinput
```

### Step 7: Verify Navigation Templates

Confirm that navigation files have been updated on production:

```bash
# Check vertical sidebar
grep -A 5 "expenses" /var/www/tradifyerp/TradifyERP/templates/partials/sidebar.html

# Check horizontal navbar
grep -A 5 "expenses" /var/www/tradifyerp/TradifyERP/templates/partials/hori-sidebar.html
```

### Step 8: Restart Gunicorn Service

```bash
# Restart Gunicorn to load new configuration
systemctl restart gunicorn

# Verify service is running
systemctl status gunicorn

# Check logs for any errors
tail -f /var/log/gunicorn/gunicorn.log

# Alternative: restart all web services
systemctl restart gunicorn nginx
```

### Step 9: Test Application

1. Navigate to `http://192.168.2.185/expenses/`
2. Verify navigation menu displays "Expenses" between "Accounting" and "Shareholder Management"
3. Test dashboard loads: `http://192.168.2.185/expenses/dashboard/`
4. Verify vertical and horizontal navigation both display the menu

## Troubleshooting

### Issue: Module not appearing in navigation
**Solution**: 
- Verify navigation templates have been copied/updated to production
- Clear browser cache (Ctrl+Shift+Delete)
- Restart Gunicorn service

### Issue: URL pattern not found (404 error)
**Solution**:
- Verify `expenses/` is in main `urls.py`
- Verify `expenses.urls` file exists in module directory
- Restart Gunicorn service

### Issue: Database migration errors
**Solution**:
```bash
# Check for any outstanding migrations
python manage.py showmigrations expenses

# If migration already exists, mark as applied
python manage.py migrate expenses --fake 0001_initial

# Then run actual migrations
python manage.py migrate expenses
```

### Issue: Permission errors (403)
**Solution**:
- Verify file permissions: `chmod -R 755 /var/www/tradifyerp/TradifyERP/expenses/`
- Verify Gunicorn user ownership: `chown -R gunicorn:gunicorn /var/www/tradifyerp/`

### Issue: Gunicorn won't restart
**Solution**:
```bash
# Check for syntax errors
python manage.py check

# Check logs
journalctl -u gunicorn -n 50

# Try restarting manually
pkill -f gunicorn
systemctl restart gunicorn
```

## Post-Deployment Verification

### 1. Test Module Access
```bash
# Test dashboard endpoint
curl http://192.168.2.185/expenses/dashboard/

# Should return HTML page, not 404
```

### 2. Verify Database Tables
```bash
# Connect to PostgreSQL database
psql -U tradify -d tradifyerp_db -c "\dt expenses_*"

# Expected output: Should list all expense-related tables
```

### 3. Check Admin Interface
- Navigate to `http://192.168.2.185/admin/`
- Should see "Expenses" app with all models listed

### 4. Verify Module Permissions
- Create a test user or use existing user
- Ensure user has module permission for 'expenses'
- Test navigation appears correctly for authorized users

## Configuration After Deployment

### 1. Create Expense Categories
1. Go to `/admin/expenses/expensecategory/`
2. Click "Add Expense Category"
3. Create categories (e.g., "Travel", "Meals", "Office Supplies")
4. Assign GL accounts for each category

### 2. Configure Approval Workflows (Optional)
- Set up approval hierarchies in admin
- Define who approves expenses for each department

### 3. Set Budget Limits
- Create budget entries for employees/departments
- Define monthly/quarterly limits per category

## Rollback Instructions (if needed)

If deployment fails and rollback is needed:

```bash
# Remove the module
rm -rf /var/www/tradifyerp/TradifyERP/expenses/

# Remove from INSTALLED_APPS in settings.py
# Remove from URL patterns in urls.py

# Rollback migrations (if migrations were applied)
python manage.py migrate expenses zero

# Restart services
systemctl restart gunicorn nginx

# Revert to previous Git commit
git checkout d0d6f59^  # Go to commit before expenses integration
```

## File Checklist

Verify these files are present in production:

```
/var/www/tradifyerp/TradifyERP/
├── expenses/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templates/
│       └── expenses/
│           └── dashboard.html
├── templates/partials/
│   ├── sidebar.html (UPDATED - contains expenses menu)
│   └── hori-sidebar.html (UPDATED - contains expenses menu)
├── TradifyERP/
│   ├── settings.py (UPDATED - includes 'expenses' in INSTALLED_APPS)
│   └── urls.py (UPDATED - includes expenses URL pattern)
```

## Next Steps

1. **User Training**: Educate users on expense reporting process
2. **GL Account Setup**: Map expense categories to appropriate GL accounts
3. **Approval Hierarchy**: Configure approval workflows in admin
4. **Budget Configuration**: Set up employee/department budgets
5. **Testing**: Conduct comprehensive testing with sample expense reports
6. **Documentation**: Provide user guide for expense submission

## Support

For issues or questions:
- Check logs: `tail -f /var/log/gunicorn/gunicorn.log`
- Review migrations: `python manage.py showmigrations`
- Test views manually: `python manage.py runserver`
- Check Django errors: `python manage.py check`

---

**Deployment Date**: [INSERT DATE]  
**Deployed By**: [INSERT NAME]  
**Version**: 1.0.0  
**Status**: Ready for Production
