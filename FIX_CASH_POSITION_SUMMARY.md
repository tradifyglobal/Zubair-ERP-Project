# CASH POSITION DOUBLE-AMOUNT FIX

## Problem

Cash position page showed 200 INR when only 100 INR cash receipt was created.

## Root Cause

**CashReceiptLine model had auto-default logic in save() method:**

```python
def save(self, *args, **kwargs):
    if not self.credit_account and self.account:
        self.credit_account = self.account  # ← BUG!
```

When a cash receipt was created without explicitly setting credit_account, the save() method auto-populated it with the debit_account (e.g., 3000-01).

Later, during authorization, the code checked `if receipt.credit_account:` and found it to be the customer account instead of the cash account, causing both GL entries to be created on the SAME account.

**Example:**
- User creates: debit_account=3000-01, debit=100, credit=100, credit_account=None
- Model.save() changes it to: credit_account=3000-01
- Authorization creates: DEBIT 3000-01 (100), CREDIT 3000-01 (100)
- Cash account 100001 never gets credited!

## Solution

**1. Removed problematic auto-default from CashReceiptLine.save():**
- File: `accounting/models.py`
- Removed the auto-population of credit_account
- Now credit_account stays NULL unless explicitly set

**2. Authorization view already handles the NULL case correctly:**
- File: `accounting/cash_workflow_views.py`
- When credit_account is None, it correctly uses cash account 100001

## Files Modified

1. `TradifyERP/accounting/models.py` - CashReceiptLine.save() method

## Verification

After deploying and restarting Gunicorn:

1. Create new cash receipt: 100 INR from customer
2. Authorize it
3. Check GL entries:
   - DEBIT 3000-01: 100 ✓
   - CREDIT 100001: 100 ✓
4. Check /accounting/cash-position/
   - Should show -100 or proper balance (NOT 200)

## Deployment Steps

3. Test cash receipt creation and authorization

