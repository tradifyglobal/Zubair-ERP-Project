# Cash Receipt & Capital Contribution Integration - Quick Test Guide

## 🎯 Quick Summary
Cash receipts from shareholders can now automatically create capital contribution records and appear in shareholder reports.

## ✅ Pre-Test Checklist
- [ ] Logged into production system
- [ ] Have credentials for test stakeholder (e.g., "Syed Safi")
- [ ] Know the capital account code (e.g., "3000-16")
- [ ] Browser cache cleared
- [ ] Access to reports section

## 🧪 5-Minute Test

### Test Case 1: Basic Cash Receipt with Stakeholder

**Setup:**
- Entity: Your test entity
- Stakeholder: "Syed Safi" (or any active shareholder)
- Capital Account: 3000-16 (Syed Safi - Capital)

**Steps:**
1. Navigate to **Accounting > Cash Management > Cash Receipts**
2. Click **Create New Cash Receipt**
3. Fill Form:
   - **Date:** Today
   - **Main Account:** 3000 (Shareholders' Capital)
   - **Sub-Account:** 3000-16 (Syed Safi - Capital)
   - **Stakeholder:** Syed Safi ← *Should appear in dropdown*
   - **Currency:** USD
   - **Description:** Test investment from shareholder
   - **Debit Amount:** 5000.00
   - **Credit Amount:** 5000.00
4. Click **Save Draft**

**Expected Result:**
- Form saves without errors
- Status shows "DRAFT"
- Stakeholder field retained (not cleared)

**Pass/Fail:** ☐ PASS / ☐ FAIL

---

### Test Case 2: Approval Workflow

**Setup:** Have a DRAFT cash receipt from Test Case 1

**Steps:**
1. Open the draft receipt
2. Click **Approve** button
3. Confirm action if prompted

**Expected Result:**
- Status changes to "APPROVED"
- Stakeholder value retained
- No errors

**Pass/Fail:** ☐ PASS / ☐ FAIL

---

### Test Case 3: Authorization & GL Creation

**Setup:** Have an APPROVED cash receipt from Test Case 2

**Steps:**
1. Open the approved receipt
2. Click **Authorize** button
3. Confirm if prompted
4. Wait for page to reload

**Expected Result:**
- Status changes to "AUTHORIZED"
- No error message
- Receipt shows as POSTED in list
- Page doesn't show any red error alerts

**Pass/Fail:** ☐ PASS / ☐ FAIL

---

### Test Case 4: GL Entries Verification

**Setup:** Have an AUTHORIZED cash receipt from Test Case 3

**Steps:**
1. Navigate to **Accounting > General Ledger**
2. Search for reference: `CASH-RECEIPT-{receipt_id}`
   - Get ID from the receipt detail page
3. Look for two entries:
   - Debit entry (to capital account)
   - Credit entry (to cash account 1000)

**Expected Result:**
- 2 GL entries found
- Debit amount = Credit amount
- Both dated correctly
- Both show status "POSTED" or "AUTHORIZED"

**Pass/Fail:** ☐ PASS / ☐ FAIL

**GL Entry Details Expected:**
```
Entry 1:
  Account: 3000-16 (Syed Safi - Capital)
  Type: DEBIT
  Amount: 5000.00
  Date: {receipt date}
  Reference: CASH-RECEIPT-{id}

Entry 2:
  Account: 1000 (Cash)
  Type: CREDIT
  Amount: 5000.00
  Date: {receipt date}
  Reference: CASH-RECEIPT-{id}
```

---

### Test Case 5: Capital Contribution Creation

**Setup:** Have an AUTHORIZED cash receipt from Test Case 3

**Steps:**
1. Navigate to **Accounting > Capital Contributions**
2. Search for "Syed Safi" or filter by stakeholder
3. Look for recent contribution with:
   - Reference: `CASH-RECEIPT-{receipt_id}`
   - Amount: 5000.00
   - Status: "COMPLETED"

**Expected Result:**
- Capital contribution record exists
- Amount matches receipt amount
- Stakeholder is "Syed Safi"
- Reference number matches cash receipt
- Status shows "COMPLETED"

**Pass/Fail:** ☐ PASS / ☐ FAIL

---

### Test Case 6: Shareholder Report Display

**Setup:** Have an AUTHORIZED cash receipt from Test Case 3

**Steps:**
1. Navigate to **Reports > Shareholder Report**
2. Find "Syed Safi" in the report
3. Look for "Investments" or "Capital Contributions" section
4. Find the 5000.00 entry with today's date

**Expected Result:**
- Shareholder shows beginning balance
- Shows "+5000.00" for cash receipt/contribution
- Ending balance increased by 5000.00
- Date matches receipt date

**Pass/Fail:** ☐ PASS / ☐ FAIL

**Expected Report Line:**
```
Shareholder: Syed Safi
Beginning Balance:    XXXXX.00
+ Contributions:      +5000.00  ← THIS SHOULD APPEAR
- Distributions:         -0.00
Ending Balance:       XXXXX.00 + 5000
```

---

### Test Case 7: Cash Receipt WITHOUT Stakeholder

**Setup:** Create a new cash receipt without selecting a stakeholder

**Steps:**
1. Navigate to **Accounting > Cash Management > Cash Receipts**
2. Click **Create New Cash Receipt**
3. Fill Form (SAME as Test Case 1 BUT):
   - **Stakeholder:** Leave BLANK (no selection)
   - Everything else the same
4. Save, Approve, Authorize (repeat Test Cases 2-3)

**Expected Result:**
- All workflow steps work normally
- GL entries created correctly
- NO CapitalContribution created (since no stakeholder)
- No error about missing stakeholder

**Pass/Fail:** ☐ PASS / ☐ FAIL

**Verification:**
- Check Capital Contributions list - should NOT have new entry
- Check GL - should still have the debit/credit entries
- This confirms stakeholder is truly optional

---

## 📊 Summary Checklist

| Test Case | Description | Result |
|-----------|-------------|--------|
| 1 | Create receipt with stakeholder | ☐ PASS / ☐ FAIL |
| 2 | Approve receipt | ☐ PASS / ☐ FAIL |
| 3 | Authorize receipt | ☐ PASS / ☐ FAIL |
| 4 | Verify GL entries | ☐ PASS / ☐ FAIL |
| 5 | Verify CapitalContribution | ☐ PASS / ☐ FAIL |
| 6 | Verify shareholder report | ☐ PASS / ☐ FAIL |
| 7 | Test without stakeholder | ☐ PASS / ☐ FAIL |

## 🚨 If Tests Fail

### Issue: Stakeholder field not visible
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh page (Ctrl+Shift+R)
3. Check browser console (F12) for JS errors
4. Verify file deployed: `ssh zubair@192.168.2.69 "grep -n stakeholder /var/www/tradifyerp/accounting/cash_forms.py" | head -5`

### Issue: CapitalContribution not created
1. Verify stakeholder was selected (check receipt detail)
2. Check stakeholder is marked "Active" in system
3. Check Django logs:
   ```bash
   ssh zubair@192.168.2.69 "sudo tail -50 /var/log/gunicorn/error.log"
   ```

### Issue: GL entries not showing
1. Verify receipt status is "POSTED" or "AUTHORIZED"
2. Check receipt reference number
3. Search GL with correct reference: `CASH-RECEIPT-{id}`
4. Verify cash account (1000) exists

### Issue: Shareholder report not showing contribution
1. Check capital contribution exists (Test Case 5)
2. Verify stakeholder is the correct one
3. Check if report has filters applied
4. Try different date range

## 📞 Test Report Template

```
Test Date: _______________
Tested By: _______________
Entity: _______________

Test Results:
- Test 1 (Create): PASS / FAIL
- Test 2 (Approve): PASS / FAIL
- Test 3 (Authorize): PASS / FAIL
- Test 4 (GL): PASS / FAIL
- Test 5 (CapitalContrib): PASS / FAIL
- Test 6 (Report): PASS / FAIL
- Test 7 (Optional): PASS / FAIL

Issues Found:
1. _______________
2. _______________

Notes:
_______________
_______________
```

## ✅ All Tests Pass?

**Congratulations!** The cash receipt to capital contribution integration is working correctly.

### What This Means:
- ✅ Cash receipts from shareholders create proper GL entries
- ✅ Cash receipts automatically create capital contribution records
- ✅ Shareholder reports now include cash receipts as investments
- ✅ System maintains audit trail from source to report
- ✅ Optional stakeholder field doesn't break non-shareholder receipts

### Next Steps:
1. Document any unique behaviors observed
2. Train users on new stakeholder field
3. Create cash receipts for historical shareholder investments (if needed)
4. Monitor reports for accuracy
