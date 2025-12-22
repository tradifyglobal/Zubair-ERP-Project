# Quick Test Guide - GL Integration

## 🎯 Test in 5 Minutes

### Step 1: Login
```
URL: http://192.168.2.69:8000
User: admin
Password: [your password]
```

### Step 2: Create ONE Test Transaction

**EASIEST TEST - Maintenance Module (Your NEW feature!):**

1. Go to: **Maintenance → Work Orders**
2. Click: **+ New Work Order**
3. Fill in ONLY these fields:
   - Work Order Number: `WO-TEST-001` (or auto-generated)
   - Asset: Select any (or create new: Asset Code=`ASSET-001`, Name=`Test Equipment`)
   - Task: Select any (or create new: Task Code=`TASK-001`, Name=`Test Maintenance`)
   - Priority: `MEDIUM`
   - Status: `SCHEDULED` ← Start here!
   - Scheduled Date: Today
   - Estimated Cost: `200.00`
   - Actual Cost: `250.00` ← Important!
4. Click **Save**
5. Click **Edit** on the work order you just created
6. Change:
   - Status: `COMPLETED` ← THIS TRIGGERS GL POSTING!
   - Completion Date: Today
   - Actual Start Date: Today
   - Actual End Date: Today
7. Click **Save**

### Step 3: Verify GL Entries

1. Go to: **Accounting → Ledger Entries**
2. Search for: `WO-TEST-001`
3. **Expected Result**: You should see 2 entries:
   ```
   Entry 1: DEBIT  - 6300 (Maintenance Expense) - $250.00
   Entry 2: CREDIT - 2000 (Accounts Payable)    - $250.00
   ```

## ✅ Success Indicators

If you see those 2 GL entries → **Maintenance integration is WORKING! 🎉**

## 🔍 Quick Verification via SSH

```bash
ssh zubair@192.168.2.69
cd /var/www/tradifyerp && source venv/bin/activate
python manage.py shell
```

```python
from accounting.models import LedgerEntry
LedgerEntry.objects.filter(reference_number__startswith='WO-').count()
# Should return: 2

# Show details
for e in LedgerEntry.objects.filter(reference_number__startswith='WO-'):
    print(f"{e.reference_number}: {e.entry_type} {e.account.account_number} {e.account.name} ${e.amount}")
```

---

## 📊 Test Other Modules

### Sales (2nd Easiest)
1. **Sales → Invoices → + New**
2. Status: **ISSUED** (key trigger!)
3. Check for: `INV-` entries

### Manufacturing (Needs 1350 account first!)
1. **Create Account 1350** (Finished Goods) first!
2. **Manufacturing → Production Orders → + New**
3. Status: **COMPLETE** (key trigger!)
4. Check for: `MFG-` entries

---

## ⚠️ Common Issues

**No entries created?**
- Check status is EXACTLY correct (case-sensitive)
- Check actual_cost has a value
- Check browser console (F12) for errors

**Missing accounts error?**
- Go to: Accounting → Chart of Accounts
- Create missing account (see GL_INTEGRATION_STATUS.md)

---

**That's it! Start with Maintenance - it's your NEW integration! 🚀**
