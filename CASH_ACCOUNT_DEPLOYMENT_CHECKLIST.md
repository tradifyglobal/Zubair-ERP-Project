# CASH ACCOUNT SETUP - DEPLOYMENT CHECKLIST

## Pre-Deployment Verification

- [ ] Verified App Server (192.168.2.69) is reachable via SSH
- [ ] Verified Database Server (192.168.2.59) is reachable via SSH
- [ ] Django project is running and accessible
- [ ] PostgreSQL database is running and accessible
- [ ] All required fields exist in CashReceiptLine model

## Deployment Steps

### Step 1: Verify Code Files (Local)
- [x] Created `setup_cash_account.py` - Django management command
- [x] Created `setup_cash_account.sql` - SQL setup script
- [x] Created `deploy_cash_account_setup.sh` - Deployment script
- [x] Created `CASH_ACCOUNT_IMPLEMENTATION_GUIDE.md` - Documentation

### Step 2: Deploy Management Command to App Server
```bash
# Run from local machine
scp TradifyERP/accounting/management/commands/setup_cash_account.py \
    zubair@192.168.2.69:/home/zubair/tradifyerp/TradifyERP/accounting/management/commands/
```

- [ ] File copied successfully

### Step 3: Run Setup Command on App Server
```bash
ssh zubair@192.168.2.69
cd /home/zubair/tradifyerp
source venv/bin/activate
python manage.py setup_cash_account
```

Expected output:
- [ ] "CASH ACCOUNT SETUP" section completed
- [ ] "✅ CREATED: Cash Account" or "✓ ALREADY EXISTS"
- [ ] "CAPITAL ACCOUNT VERIFICATION" section shows existing accounts
- [ ] "CASH RECEIPT LINE MODEL VERIFICATION" shows all required fields
- [ ] "✅ ALL CHECKS PASSED - System is ready for Cash Receipts!"

### Step 4: Verify Database Setup
```bash
# Connect to database server
psql -h 192.168.2.59 -U zubair -d tradifyerp_db

# Run verification queries
SELECT * FROM accounting_account WHERE account_number='100001';
SELECT * FROM accounting_account WHERE account_number IN ('3000', '3100');
```

- [ ] Cash Account (100001) exists in database
- [ ] Capital Account (3000) exists
- [ ] Shareholder Investment Account (3100) exists

### Step 5: Restart Application
```bash
ssh zubair@192.168.2.69
sudo systemctl restart gunicorn-tradifyerp
```

- [ ] Gunicorn restarted successfully

### Step 6: Test Application
```bash
# Navigate to app in browser
https://192.168.2.69/accounting/dashboard/

# Try creating a cash receipt
https://192.168.2.69/accounting/cash-receipts/create/
```

- [ ] Dashboard loads without errors
- [ ] Cash Receipt creation form loads
- [ ] Can select capital account (3100-01)
- [ ] Can enter amounts
- [ ] Receipt can be submitted

### Step 7: Test GL Posting Workflow
1. Create cash receipt (status: DRAFT)
2. Approve the receipt (status: APPROVED)
3. Authorize & post (status: AUTHORIZED/POSTED)
4. Check General Ledger for GL entries
   - [ ] DEBIT entry to 3100-01 visible
   - [ ] CREDIT entry to 100001 visible
   - [ ] Reference number: CASH-RECEIPT-{id}
   - [ ] Status: AUTHORIZED

### Step 8: Verify Shareholder Sync
- [ ] Stakeholder field is linked to cash receipt
- [ ] Capital contribution amount is tracked
- [ ] Shareholder dashboard shows contribution

## Post-Deployment Verification

### Database Checks
```sql
-- Check Cash Account
SELECT id, account_number, name, account_type FROM accounting_account WHERE account_number='100001';

-- Check recent cash receipts
SELECT id, account_id, credit_account_id, debit_amount, status, workflow_status 
FROM accounting_cashreceiptline 
ORDER BY created_at DESC LIMIT 5;

-- Check GL entries
SELECT id, account_id, entry_type, amount, reference_number, workflow_status 
FROM accounting_ledgerentry 
WHERE reference_number LIKE 'CASH-RECEIPT-%' 
ORDER BY entry_date DESC LIMIT 10;
```

- [ ] All queries execute successfully
- [ ] Cash Account exists
- [ ] GL entries appear for authorized receipts

### Application Checks
- [ ] No errors in application logs
- [ ] Cash receipt workflow is functioning
- [ ] GL entries are being created on authorization
- [ ] Shareholder information is being captured

## Rollback Plan (if needed)

If issues occur:

1. **Disable Cash Receipt Creation**:
   ```python
   # In accounting/views.py, comment out cash receipt URLs
   ```

2. **Delete Test Accounts** (if created):
   ```sql
   DELETE FROM accounting_ledgerentry WHERE reference_number LIKE 'CASH-RECEIPT-%';
   DELETE FROM accounting_cashreceiptline WHERE status != 'POSTED';
   DELETE FROM accounting_account WHERE account_number='100001' AND opening_balance=0;
   ```

3. **Restart Application**:
   ```bash
   sudo systemctl restart gunicorn-tradifyerp
   ```

## Sign-Off

| Item | Status | Date | Notes |
|------|--------|------|-------|
| Pre-Deployment Checks | [ ] | | |
| Code Deployment | [ ] | | |
| Database Setup | [ ] | | |
| Application Restart | [ ] | | |
| Functionality Tests | [ ] | | |
| Documentation Review | [ ] | | |
| **DEPLOYMENT COMPLETE** | [ ] | | |

---

## Support Information

- **App Server**: 192.168.2.69 (zubair / erp)
- **DB Server**: 192.168.2.59 (zubair / sql)
- **Documentation**: CASH_ACCOUNT_IMPLEMENTATION_GUIDE.md
- **Management Command**: python manage.py setup_cash_account

## Completion Status

**Date**: December 15, 2025
**Status**: ✅ Ready for Deployment
**Last Updated**: [Current Timestamp]
