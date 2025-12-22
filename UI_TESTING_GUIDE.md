# UI Testing Guide - GL Integration Verification

**Date**: December 19, 2025  
**Server**: http://192.168.20.10:8000  
**Purpose**: Test all module GL integrations via UI

---

## Prerequisites

1. **Login to TradifyERP**
   - URL: http://192.168.20.10:8000
   - Username: `admin` (or your admin user)
   - Password: Your admin password

2. **Select Entity**
   - After login, ensure you have an entity selected
   - Look for entity selector in the top menu
   - Select "Internal" or your default entity

---

## Module 1: Sales Module - Invoice Creation

### Step 1: Create a Customer (if needed)

1. Navigate to: **Sales → Customers**
   - URL: http://192.168.20.10:8000/sales/customers/

2. Click **"+ Add Customer"** or **"New Customer"**

3. Fill in the form:
   ```
   Customer Code: TEST-CUST-001
   Customer Name: Test Customer Inc
   Customer Type: Business
   Email: testcust@example.com
   Phone: 555-0001
   Credit Limit: 10,000.00
   Status: Active
   ```

4. Click **Save**

### Step 2: Create a Sales Order

1. Navigate to: **Sales → Sales Orders**
   - URL: http://192.168.20.10:8000/sales/sales-orders/

2. Click **"+ New Sales Order"**

3. Fill in the form:
   ```
   Customer: TEST-CUST-001 (select from dropdown)
   Order Date: Today's date
   Delivery Date: 7 days from now
   Status: CONFIRMED
   ```

4. Add Line Items:
   ```
   Product: (select any product or enter description)
   Quantity: 10
   Unit Price: 100.00
   ```

5. Click **Save**
   - Note the Sales Order number (e.g., SO-2025-001)

### Step 3: Create Invoice from Sales Order

1. Navigate to: **Sales → Invoices**
   - URL: http://192.168.20.10:8000/sales/invoices/

2. Click **"+ New Invoice"**
   - URL: http://192.168.20.10:8000/sales/invoices/new/

3. Fill in the form:
   ```
   Sales Order: Select the SO you just created
   Invoice Number: INV-TEST-001 (auto-generated or manual)
   Invoice Date: Today
   Due Date: 30 days from now
   Status: ISSUED ⚠️ IMPORTANT - This triggers GL posting!
   Subtotal: 1000.00
   Tax Amount: 0.00 (or add tax if needed)
   Total Amount: 1000.00
   ```

4. Click **Save**

### Step 4: Verify GL Entries Created

1. Navigate to: **Accounting → Ledger Entries**
   - URL: http://192.168.20.10:8000/accounting/ledger-entries/

2. Search for: `INV-TEST-001`

3. **Expected Results:**
   - You should see 2 GL entries:
     - **Entry 1**: DEBIT - Accounts Receivable (1200) - $1,000.00
     - **Entry 2**: CREDIT - Sales Revenue (4100) - $1,000.00
   - Reference Number: INV-TEST-001
   - Status: AUTHORIZED or POSTED

---

## Module 2: Manufacturing - Production Order

### Step 1: Verify Products Exist

1. Navigate to: **Manufacturing → Products**
   - URL: http://192.168.20.10:8000/manufacturing/products/

2. If no products exist, create one:
   ```
   Product Code: PROD-001
   Product Name: Test Product
   Category: (select any)
   Is Manufactured: Yes ✓
   Standard Cost: 50.00
   Selling Price: 100.00
   Unit of Measure: PCS
   ```

### Step 2: Create Production Order

1. Navigate to: **Manufacturing → Production Orders**
   - URL: http://192.168.20.10:8000/manufacturing/production-orders/

2. Click **"+ New Production Order"**
   - URL: http://192.168.20.10:8000/manufacturing/production-orders/new/

3. Fill in the form:
   ```
   Order Number: MFG-TEST-001 (auto-generated or manual)
   Product: Select the product created above
   Quantity: 100
   Planned Start Date: Today
   Planned End Date: 7 days from now
   Status: IN_PROGRESS (start with this)
   ```

4. Click **Save**

### Step 3: Complete the Production Order

1. Edit the production order you just created

2. Update fields:
   ```
   Status: COMPLETE ⚠️ IMPORTANT - This triggers GL posting!
   Actual Start Date: Today
   Actual End Date: Today
   Actual Quantity: 100
   ```

3. Click **Save**

### Step 4: Verify GL Entries Created

1. Navigate to: **Accounting → Ledger Entries**

2. Search for: `MFG-TEST-001`

3. **Expected Results:**
   - You should see 2 GL entries:
     - **Entry 1**: DEBIT - Finished Goods (1350) - $5,000.00
     - **Entry 2**: CREDIT - Work in Progress (1400) - $5,000.00
   - Reference Number: MFG-TEST-001
   - Status: AUTHORIZED or POSTED

---

## Module 3: Maintenance - Work Order

### Step 1: Create Asset (if needed)

1. Navigate to: **Maintenance → Assets**
   - URL: http://192.168.20.10:8000/maintenance/assets/

2. Click **"+ Add Asset"**

3. Fill in the form:
   ```
   Asset Code: ASSET-001
   Asset Name: Test Equipment
   Status: OPERATIONAL
   Location: Main Facility
   Purchase Date: 1 year ago
   Purchase Cost: 10,000.00
   ```

4. Click **Save**

### Step 2: Create Maintenance Task (if needed)

1. Navigate to: **Maintenance → Tasks**
   - URL: http://192.168.20.10:8000/maintenance/tasks/

2. Click **"+ Add Task"**

3. Fill in the form:
   ```
   Task Code: TASK-001
   Task Name: Regular Maintenance
   Task Type: PREVENTIVE
   Description: Regular maintenance check
   Estimated Duration: 2.00 hours
   ```

4. Click **Save**

### Step 3: Create Work Order

1. Navigate to: **Maintenance → Work Orders**
   - URL: http://192.168.20.10:8000/maintenance/work-orders/

2. Click **"+ New Work Order"**
   - URL: http://192.168.20.10:8000/maintenance/work-orders/new/

3. Fill in the form:
   ```
   Work Order Number: WO-TEST-001 (auto-generated or manual)
   Maintenance Task: Select the task created above
   Asset: Select the asset created above
   Priority: MEDIUM
   Status: SCHEDULED (start with this)
   Description: Test maintenance work
   Scheduled Date: Today
   Estimated Hours: 2.00
   Estimated Cost: 200.00
   ```

4. Click **Save**

### Step 4: Complete the Work Order

1. Edit the work order you just created

2. Update fields:
   ```
   Status: COMPLETED ⚠️ IMPORTANT - This triggers GL posting!
   Actual Start Date: Today
   Actual End Date: Today
   Actual Hours: 2.50
   Actual Cost: 250.00
   Completion Date: Today
   ```

3. Click **Save**

### Step 5: Verify GL Entries Created

1. Navigate to: **Accounting → Ledger Entries**

2. Search for: `WO-TEST-001`

3. **Expected Results:**
   - You should see 2 GL entries:
     - **Entry 1**: DEBIT - Maintenance Expense (6300) - $250.00
     - **Entry 2**: CREDIT - Accounts Payable (2000) - $250.00
   - Reference Number: WO-TEST-001
   - Status: AUTHORIZED or POSTED

---

## Module 4: Procurement - Goods Receipt

### Step 1: Create Vendor (if needed)

1. Navigate to: **Accounting → Vendors** or **Procurement → Vendors**

2. Create vendor with currency (required field)

### Step 2: Create Purchase Order

1. Navigate to: **Procurement → Purchase Orders**
   - URL: http://192.168.20.10:8000/procurement/purchase-orders/

2. Create PO with vendor, items, and status APPROVED

### Step 3: Create Goods Receipt

1. Navigate to: **Procurement → Goods Receipts**

2. Create GR linked to the PO

3. Set status to: **COMPLETED**

4. **Verify GL Entries**: Search for `GR-` or `PO-` prefix

---

## Module 5: Expenses - Employee Expense

### Step 1: Verify Employee Exists

1. Navigate to: **HR → Employees**

2. Ensure at least one employee exists

### Step 2: Create Expense Category

1. Navigate to: **Expenses → Categories**

2. Create category:
   ```
   Name: Travel
   Category Type: TRAVEL
   Expense Account: Select travel expense account (6100)
   Requires Receipt: Yes
   Requires Approval: Yes
   ```

### Step 3: Create Employee Expense

1. Navigate to: **Expenses → Employee Expenses**

2. Click **"+ New Expense"**

3. Fill in the form:
   ```
   Employee: Select employee
   Expense Date: Today
   Category: Travel
   Description: Test travel expense
   Amount: 250.00
   Status: APPROVED
   ```

4. Click **Save**

### Step 4: Post to GL

1. Find the expense you just created

2. Look for **"Post to GL"** button or action

3. Click to post

4. **Verify GL Entries**: Search for `EXP-` prefix

---

## Module 6: HR/Payroll - Payroll Posting

### Step 1: Create Payroll

1. Navigate to: **HR → Payroll**

2. Create or select a payroll record with status APPROVED

### Step 2: Post to GL

1. Look for **"Post to GL"** button on the payroll detail page

2. Click to post

3. **Verify GL Entries**: Search for `PAY-` prefix

---

## Quick Verification Script

After creating test transactions, run this to check all GL entries:

```python
# Via SSH to server
ssh zubair@192.168.20.10

cd /var/www/tradifyerp
source venv/bin/activate

python manage.py shell

# Then run:
from accounting.models import LedgerEntry

print("\n=== GL ENTRIES BY MODULE ===\n")

modules = [
    ('Sales', 'INV-'),
    ('Manufacturing', 'MFG-'),
    ('Procurement PO', 'PO-'),
    ('Procurement GR', 'GR-'),
    ('Expenses', 'EXP-'),
    ('Payroll', 'PAY-'),
    ('Maintenance', 'WO-'),
]

for name, prefix in modules:
    count = LedgerEntry.objects.filter(reference_number__startswith=prefix).count()
    print(f"{name:20} ({prefix}): {count} entries")
    
    if count > 0:
        entries = LedgerEntry.objects.filter(reference_number__startswith=prefix)[:3]
        for e in entries:
            print(f"  → {e.reference_number}: {e.entry_type} {e.account.code} ${e.amount}")

print("\n" + "="*50)
print(f"Total GL Entries: {LedgerEntry.objects.count()}")
```

---

## Troubleshooting

### No GL Entries Created?

1. **Check Invoice/Order Status**
   - Sales: Invoice must be status = **ISSUED**
   - Manufacturing: Production Order must be status = **COMPLETE**
   - Maintenance: Work Order must be status = **COMPLETED**

2. **Check for Errors**
   - Look at browser console (F12)
   - Check server logs: `tail -f /var/www/tradifyerp/logs/error.log`

3. **Check GL Accounts Exist**
   - Navigate to: Accounting → Chart of Accounts
   - Verify these accounts exist:
     - 1200 - Accounts Receivable
     - 1300 - Inventory
     - 1350 - Finished Goods
     - 1400 - Work in Progress
     - 2000 - Accounts Payable
     - 4100 - Sales Revenue
     - 6000 - Salary Expense
     - 6100 - Travel Expense
     - 6300 - Maintenance Expense

4. **Check Integration Code**
   - Sales: `sales/gl_integration.py` or `sales/integration.py`
   - Manufacturing: `manufacturing/signals.py`
   - Maintenance: `maintenance/signals.py`

---

## Expected Results Summary

After completing all tests, you should have:

| Module | Reference Prefix | GL Entry Count | Account Debited | Account Credited |
|--------|------------------|----------------|-----------------|------------------|
| Sales | INV- | 2 | AR (1200) | Revenue (4100) |
| Manufacturing | MFG- | 2 | Finished Goods (1350) | WIP (1400) |
| Maintenance | WO- | 2 | Maintenance Exp (6300) | AP (2000) |
| Procurement | GR-/PO- | 2+ | Inventory (1300) | AP (2000) |
| Expenses | EXP- | 2 | Travel Exp (6100) | AP-Employee |
| Payroll | PAY- | 2+ | Salary Exp (6000) | Payable |

---

## Next Steps

Once you've verified GL entries are created:

1. **Check Trial Balance**
   - Navigate to: Accounting → Reports → Trial Balance
   - Verify debits = credits

2. **Check Profit & Loss**
   - Navigate to: Accounting → Reports → Profit & Loss
   - Verify revenue and expenses appear

3. **Check Manufacturing Account**
   - Navigate to: Accounting → Reports → Trading & Manufacturing Account
   - Verify sales and purchases appear

---

**Need Help?**
- Check server logs: `/var/www/tradifyerp/logs/`
- Review error messages in browser console
- Verify all required fields are filled
- Ensure proper status is set (ISSUED, COMPLETE, COMPLETED, etc.)
