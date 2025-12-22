# 💳 Payment Workflows - Deployment & Implementation Guide

**Document Version**: 1.0  
**Date**: December 17, 2025  
**Status**: Ready for Implementation  
**Target Environment**: Production (192.168.2.69)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Database Models Deployment](#database-models-deployment)
4. [Database Migrations](#database-migrations)
5. [Code Deployment](#code-deployment)
6. [URL Configuration](#url-configuration)
7. [Permissions Setup](#permissions-setup)
8. [Testing](#testing)
9. [Production Deployment](#production-deployment)
10. [Rollback Procedures](#rollback-procedures)

---

## 🎯 Overview

### What We're Deploying

**4 New Models**:
- CashPaymentVoucher (Header)
- CashPaymentLine (Line Items)
- BankPaymentVoucher (Header)
- BankPaymentLine (Line Items)

**8 New Views**:
- 4 Cash Payment Views (List, Detail, Create, Approval/Authorization)
- 4 Bank Payment Views (List, Detail, Create, Approval/Authorization)
- 1 Payment Dashboard

**2 Signal Handlers**:
- Auto GL posting on cash payment authorization
- Auto GL posting on bank payment authorization

**Templates**:
- Cash payment list/detail
- Bank payment list/detail
- Payment dashboard

**URLs**:
- 10 new URL patterns for payment workflows

### Workflow Summary

```
Cash/Bank Payment Request
    ↓
DRAFT (Maker creates voucher)
    ↓
SUBMITTED (Submit for approval)
    ↓
CHECKED (Checker reviews → approve/reject)
    ↓
AUTHORIZED (Approver authorizes → GL posted)
    ↓
GL_POSTED (Ledger updated, cash/bank balance changed)
```

---

## ✅ Pre-Deployment Checklist

- [ ] Backup production database
- [ ] Backup production code
- [ ] Review all model definitions
- [ ] Review all views code
- [ ] Review signal logic
- [ ] Test migrations locally
- [ ] Verify URL patterns don't conflict
- [ ] Get approval from team lead
- [ ] Schedule deployment window
- [ ] Prepare rollback plan

---

## 🗄️ Database Models Deployment

### Step 1: Add Models to production/accounting/models.py

**Location**: `/var/www/tradifyerp/accounting/models.py`

**Action**: Append the following models before the RBAC imports:

From file: `MODELS_PAYMENT_VOUCHERS.py` (lines 1-450)

**Models to Add**:
1. CashPaymentVoucher
2. CashPaymentLine
3. BankPaymentVoucher
4. BankPaymentLine

**Important**: 
- Insert **before** any RBAC model imports
- Ensure proper indentation
- Check for field name conflicts with existing models

**Verification**:
```bash
# Login to production server
ssh zubair@192.168.2.69

# Test model imports
source /var/www/tradifyerp/venv/bin/activate
cd /var/www/tradifyerp
python manage.py shell
>>> from accounting.models import CashPaymentVoucher, BankPaymentVoucher
>>> print("Models imported successfully!")
```

---

## 🔄 Database Migrations

### Step 1: Create Migrations

**Command**:
```bash
python manage.py makemigrations accounting
```

**Expected Output**:
```
Migrations for 'accounting':
  accounting/migrations/0024_cashpaymentvoucher_cashpaymentline_bankpaymentvoucher_bankpaymentline.py
    - Create model CashPaymentVoucher
    - Create model CashPaymentLine
    - Create model BankPaymentVoucher
    - Create model BankPaymentLine
```

### Step 2: Review Migration File

**Location**: `/var/www/tradifyerp/accounting/migrations/0024_*.py`

**Check**:
- All 4 models are included
- Foreign keys are correct
- Indexes are defined
- No conflicts with existing migrations

### Step 3: Apply Migrations

**Command**:
```bash
python manage.py migrate accounting
```

**Expected Output**:
```
Running migrations:
  Applying accounting.0024_cashpaymentvoucher_cashpaymentline_bankpaymentvoucher_bankpaymentline... OK
```

### Step 4: Verify Tables Created

**Command**:
```bash
python manage.py shell
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE 'accounting_cashpayment%'
""")
>>> print(cursor.fetchall())
```

**Expected Output**:
```
[
    ('accounting_cashpaymentvoucher',),
    ('accounting_cashpaymentline',),
    ('accounting_bankpaymentvoucher',),
    ('accounting_bankpaymentline',)
]
```

---

## 💾 Code Deployment

### Step 1: Transfer Views File

**Local**:
```bash
# From Windows machine
$content = Get-Content "f:\ERP-Production\Zubair-ERP-Project\VIEWS_PAYMENT_VOUCHERS.py" -Raw
echo $content | plink -ssh -l zubair -pw erp -batch 192.168.2.69 "cat > /tmp/views_payment.py"
```

**Production**:
```bash
# Deploy to production location
sudo cp /tmp/views_payment.py /var/www/tradifyerp/accounting/views_payment.py
sudo chown www-data:www-data /var/www/tradifyerp/accounting/views_payment.py
sudo chmod 644 /var/www/tradifyerp/accounting/views_payment.py
```

### Step 2: Transfer Signals File

**Local**:
```bash
$content = Get-Content "f:\ERP-Production\Zubair-ERP-Project\SIGNALS_PAYMENT_VOUCHERS.py" -Raw
echo $content | plink -ssh -l zubair -pw erp -batch 192.168.2.69 "cat > /tmp/signals_payment.py"
```

**Production**:
```bash
# Append signals to existing signals.py file
cat /tmp/signals_payment.py >> /var/www/tradifyerp/accounting/signals.py
sudo chown www-data:www-data /var/www/tradifyerp/accounting/signals.py
```

### Step 3: Verify File Permissions

**Command**:
```bash
ls -la /var/www/tradifyerp/accounting/views_payment.py
ls -la /var/www/tradifyerp/accounting/signals_payment.py
```

**Expected Output**:
```
-rw-r--r-- 1 www-data www-data xxxxx Dec 17 xx:xx views_payment.py
-rw-r--r-- 1 www-data www-data xxxxx Dec 17 xx:xx signals.py
```

---

## 🔗 URL Configuration

### Step 1: Add Payment URLs to urls.py

**Location**: `/var/www/tradifyerp/accounting/urls.py`

**Action**: Add import and URL patterns

From file: `URLS_PAYMENT_VOUCHERS.py` (lines 1-100)

**Add to existing urlpatterns**:
```python
# Add to imports
from accounting.views_payment import (
    CashPaymentListView, CashPaymentDetailView, CashPaymentCreateView,
    CashPaymentApprovalView, CashPaymentAuthorizationView,
    BankPaymentListView, BankPaymentDetailView, BankPaymentCreateView,
    BankPaymentApprovalView, BankPaymentAuthorizationView,
    PaymentDashboardView,
)

# Add to urlpatterns
urlpatterns += [
    path('cash-payments/', CashPaymentListView.as_view(), name='cash_payment_list'),
    path('cash-payment/create/', CashPaymentCreateView.as_view(), name='cash_payment_create'),
    path('cash-payment/<int:pk>/', CashPaymentDetailView.as_view(), name='cash_payment_detail'),
    path('cash-payment/<int:pk>/approve/', CashPaymentApprovalView.as_view(), name='cash_payment_approval'),
    path('cash-payment/<int:pk>/authorize/', CashPaymentAuthorizationView.as_view(), name='cash_payment_authorization'),
    path('bank-payments/', BankPaymentListView.as_view(), name='bank_payment_list'),
    path('bank-payment/create/', BankPaymentCreateView.as_view(), name='bank_payment_create'),
    path('bank-payment/<int:pk>/', BankPaymentDetailView.as_view(), name='bank_payment_detail'),
    path('bank-payment/<int:pk>/approve/', BankPaymentApprovalView.as_view(), name='bank_payment_approval'),
    path('bank-payment/<int:pk>/authorize/', BankPaymentAuthorizationView.as_view(), name='bank_payment_authorization'),
    path('payment-dashboard/', PaymentDashboardView.as_view(), name='payment_dashboard'),
]
```

### Step 2: Verify URLs

**Command**:
```bash
python manage.py show_urls | grep payment
```

**Expected Output**:
```
accounting:cash_payment_list
accounting:cash_payment_create
accounting:cash_payment_detail
...
accounting:payment_dashboard
```

---

## 🔐 Permissions Setup

### Step 1: Create Permissions (Auto-created)

**Command**:
```bash
python manage.py migrate auth
```

**This will auto-create**:
- view_cashpaymentvoucher
- add_cashpaymentvoucher
- change_cashpaymentvoucher
- delete_cashpaymentvoucher
- can_approve_cash_payment
- can_authorize_cash_payment
- can_reverse_cash_payment
- (Similar for bank payments)

### Step 2: Assign Permissions to User Groups

**Django Admin**:
1. Login to http://192.168.2.69:8000/admin/
2. Go to Auth → Groups
3. Create/Edit groups:
   - **Finance Maker**: add_cashpaymentvoucher, add_bankpaymentvoucher
   - **Finance Checker**: can_approve_cash_payment, can_approve_bank_payment
   - **Finance Approver**: can_authorize_cash_payment, can_authorize_bank_payment, can_reverse_cash_payment, can_reverse_bank_payment

### Step 3: Assign Users to Groups

**Django Admin**:
1. Go to Auth → Users
2. Select user
3. Move to appropriate group(s)

---

## 🧪 Testing

### Test 1: Model Import Test

```python
from accounting.models import (
    CashPaymentVoucher, CashPaymentLine,
    BankPaymentVoucher, BankPaymentLine
)

# Test creating objects
cpv = CashPaymentVoucher(
    voucher_number='CPV/2025/0001',
    payee_name='Test Payee',
    total_amount=1000
)
print("Cash payment voucher created successfully")
```

### Test 2: View Import Test

```python
from accounting.views_payment import (
    CashPaymentListView, BankPaymentListView, PaymentDashboardView
)

print("All views imported successfully")
```

### Test 3: Signal Registration Test

```python
from accounting.signals import post_cash_payment_gl_entries, post_bank_payment_gl_entries
from django.dispatch import receiver

# Verify signal decorators are registered
print("Signals registered successfully")
```

### Test 4: URL Routing Test

```bash
# In Django shell
from django.urls import resolve
result = resolve('/accounting/cash-payments/')
print(f"View: {result.func.view_class.__name__}")  # Should print: CashPaymentListView
```

### Test 5: Workflow End-to-End Test

1. **Create Cash Payment**:
   - Navigate to /accounting/cash-payment/create/
   - Fill form with test data
   - Save

2. **Submit for Approval**:
   - Click "Submit for Approval"
   - Status changes to SUBMITTED_FOR_APPROVAL

3. **Approve**:
   - Login as checker user
   - Navigate to voucher
   - Click "Approve"
   - Status changes to CHECKED

4. **Authorize** (GL Posting):
   - Login as approver user
   - Click "Authorize"
   - Status changes to AUTHORIZED → GL_POSTED
   - Verify GL entries created in JournalEntry

5. **Verify Ledger**:
   - Check GL account balances updated
   - Verify debit/credit balance

---

## 🚀 Production Deployment

### Step 1: Pre-Deployment Backup

```bash
# Backup database
pg_dump -h 192.168.2.59 -U tradifyerp_user -d tradifyerp_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup code
tar -czf accounting_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/tradifyerp/accounting/
```

### Step 2: Deploy Models & Migrations

```bash
# SSH to production
ssh zubair@192.168.2.69

# Activate environment
source /var/www/tradifyerp/venv/bin/activate
cd /var/www/tradifyerp

# Create migration
python manage.py makemigrations accounting

# Apply migration
python manage.py migrate accounting

# Collect static files
python manage.py collectstatic --noinput
```

### Step 3: Deploy Code

```bash
# Deploy views
sudo cp /tmp/views_payment.py /var/www/tradifyerp/accounting/views_payment.py

# Deploy signals (append to existing)
cat /tmp/signals_payment.py >> /var/www/tradifyerp/accounting/signals.py

# Deploy templates
mkdir -p /var/www/tradifyerp/accounting/templates/accounting/payments/
sudo cp /tmp/payment_templates.html /var/www/tradifyerp/accounting/templates/accounting/payments/

# Set permissions
sudo chown -R www-data:www-data /var/www/tradifyerp/accounting/
```

### Step 4: Restart Services

```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Verify Gunicorn is running
sudo systemctl status gunicorn

# Check for errors
tail -50 /var/www/tradifyerp/gunicorn.log
```

### Step 5: Verify Deployment

```bash
# Test models
python manage.py shell -c "from accounting.models import CashPaymentVoucher; print('✅ Models loaded')"

# Test views
python manage.py shell -c "from accounting.views_payment import CashPaymentListView; print('✅ Views loaded')"

# Test URLs
python manage.py show_urls | grep payment | head -5

# Test signals
python manage.py shell -c "from accounting.signals import post_cash_payment_gl_entries; print('✅ Signals loaded')"
```

### Step 6: Browser Test

1. Open http://192.168.2.69:8000/accounting/payment-dashboard/
2. Verify dashboard loads
3. Click "New Cash Payment Voucher"
4. Test form validation
5. Create test voucher

---

## 🔙 Rollback Procedures

### If Deployment Fails

**Step 1**: Stop Gunicorn
```bash
sudo systemctl stop gunicorn
```

**Step 2**: Restore from backup
```bash
# Restore code
tar -xzf accounting_backup_YYYYMMDD_HHMMSS.tar.gz -C /var/www/tradifyerp/

# Set permissions
sudo chown -R www-data:www-data /var/www/tradifyerp/accounting/
```

**Step 3**: Revert migration
```bash
source /var/www/tradifyerp/venv/bin/activate
cd /var/www/tradifyerp
python manage.py migrate accounting 0023  # Go back to previous migration
```

**Step 4**: Restart Gunicorn
```bash
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

**Step 5**: Verify old version is running
```bash
# Test old views still work
python manage.py show_urls | grep shareholder
```

### Database Rollback

If database needs restoration:
```bash
# Restore database from backup
psql -h 192.168.2.59 -U tradifyerp_user -d tradifyerp_db < backup_YYYYMMDD_HHMMSS.sql
```

---

## 📊 Post-Deployment Verification

### Checklist

- [ ] All 4 models exist in production
- [ ] All tables created in PostgreSQL
- [ ] All 8 views working
- [ ] All URLs registered
- [ ] Signal handlers active
- [ ] GL posting working (test end-to-end)
- [ ] Permissions properly configured
- [ ] Templates rendering correctly
- [ ] No errors in Gunicorn logs
- [ ] Users can access payment pages

### Monitoring

**Daily**:
- Check for payment voucher errors
- Verify GL posting is happening
- Check ledger balances

**Weekly**:
- Review pending payments
- Verify approval workflow
- Check for any rejections

---

## 📝 Quick Reference

### File Locations

| Component | Location |
|-----------|----------|
| Models | `/var/www/tradifyerp/accounting/models.py` |
| Views | `/var/www/tradifyerp/accounting/views_payment.py` |
| Signals | `/var/www/tradifyerp/accounting/signals.py` (appended) |
| URLs | `/var/www/tradifyerp/accounting/urls.py` (updated) |
| Templates | `/var/www/tradifyerp/accounting/templates/accounting/payments/` |
| Migrations | `/var/www/tradifyerp/accounting/migrations/` |

### Useful Commands

```bash
# Test everything
python manage.py check

# List all URLs
python manage.py show_urls | grep payment

# Django admin
http://192.168.2.69:8000/admin/auth/group/

# Check signals
python manage.py shell -c "from django.core.signals import request_finished; from accounting.signals import *; print('Signals loaded')"

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if needed
python manage.py createsuperuser
```

---

## 🆘 Troubleshooting

### Issue: Models not found

**Solution**:
```bash
# Ensure models are in the right file
grep -n "class CashPaymentVoucher" /var/www/tradifyerp/accounting/models.py

# Re-create migrations
python manage.py makemigrations accounting
python manage.py migrate accounting
```

### Issue: URLs not working

**Solution**:
```bash
# Clear URL cache
sudo systemctl restart gunicorn

# Verify imports in urls.py
grep -n "from accounting.views_payment import" /var/www/tradifyerp/accounting/urls.py

# Test URL resolution
python manage.py shell
>>> from django.urls import resolve
>>> resolve('/accounting/cash-payments/')
```

### Issue: GL not posting

**Solution**:
```bash
# Check signal registration
grep -n "@receiver" /var/www/tradifyerp/accounting/signals.py

# Check for errors in logs
tail -100 /var/www/tradifyerp/gunicorn.log | grep -i error

# Test signal directly
python manage.py shell
>>> from accounting.models import CashPaymentVoucher
>>> cpv = CashPaymentVoucher.objects.first()
>>> cpv.status = 'AUTHORIZED'
>>> cpv.save()  # Should trigger signal
```

---

**Ready for Deployment** ✅

---

**Next Steps**:
1. Review all files
2. Get team approval
3. Schedule deployment
4. Follow deployment steps
5. Run verification tests
6. Monitor production
7. Train users
