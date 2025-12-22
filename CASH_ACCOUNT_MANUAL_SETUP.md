# ✅ MANUAL CASH ACCOUNT SETUP - STEP BY STEP

## Option 1: Via SSH to Database Server (Recommended)

### Step 1: SSH to Database Server
```bash
ssh zubair@192.168.2.59
```
Password: `sql`

### Step 2: Connect to PostgreSQL
```bash
psql -U zubair -d tradifyerp_db
```

### Step 3: Create Cash Account

Run this SQL command:

```sql
INSERT INTO accounting_account (
    account_number,
    name,
    account_type,
    description,
    entity_id,
    currency_id,
    is_active,
    opening_balance,
    parent_account_id,
    created_at,
    updated_at
) SELECT
    '100001',
    'Cash',
    'ASSET',
    'Cash account for receiving cash from shareholders and other receipts',
    ae.id,
    ac.id,
    true,
    0.00,
    NULL,
    NOW(),
    NOW()
FROM accounting_entity ae, accounting_currency ac
WHERE ae.code = 'INT001' 
  AND ac.code = 'INR'
  AND NOT EXISTS (SELECT 1 FROM accounting_account WHERE account_number='100001');
```

### Step 4: Verify Setup

```sql
-- Check Cash Account
SELECT account_number, name, account_type FROM accounting_account WHERE account_number='100001';

-- Check Capital Accounts
SELECT account_number, name, account_type FROM accounting_account WHERE account_number IN ('3000','3100','3100-01');
```

---

## Option 2: Via pgAdmin (Web Interface)

### Step 1: Open pgAdmin
Navigate to: http://192.168.2.59:5050/ (or your pgAdmin URL)

### Step 2: Connect to Database
- Server: tradifyerp_db
- Database: tradifyerp_db
- User: zubair

### Step 3: Run Query
Click "Tools" → "Query Tool"

Paste the SQL from Option 1, Step 3 above

Click "Execute"

---

## Option 3: Via DBeaver (Desktop Tool)

### Step 1: Create Connection
- Host: 192.168.2.59
- Port: 5432
- Database: tradifyerp_db
- User: zubair
- Password: sql

### Step 2: New SQL Query
Right-click database → New SQL Query

### Step 3: Paste and Execute
Paste the SQL from Option 1, Step 3 above

Press Ctrl+Enter or click Execute

---

## ✅ Verification Queries

Run these to verify setup was successful:

```sql
-- 1. Check Cash Account exists
SELECT id, account_number, name, account_type, is_active 
FROM accounting_account 
WHERE account_number='100001';

-- 2. Check Capital Accounts
SELECT account_number, name, account_type 
FROM accounting_account 
WHERE account_number IN ('3000','3100','3100-01')
ORDER BY account_number;

-- 3. Count all accounts by type
SELECT account_type, COUNT(*) as count
FROM accounting_account
GROUP BY account_type
ORDER BY account_type;
```

Expected Results:
- ✓ Cash Account (100001) should exist with type ASSET
- ✓ Capital Accounts (3000, 3100) should exist with type EQUITY
- ✓ Sub-account (3100-01) should exist under 3100

---

## 🚀 After Database Setup

Once the Cash Account is created in database:

### 1. Test the Application

Navigate to: `https://192.168.2.69/accounting/cash-receipts/create/`

You should see a form with:
- Date field
- Account dropdown (should show 3100-01)
- Debit Amount field
- Credit Amount field
- Description field
- Stakeholder field

### 2. Create Test Receipt

1. Fill in the form:
   - Account: 3100-01
   - Debit Amount: 100000
   - Credit Amount: 100000
   - Description: "Test cash receipt"

2. Click "Save & Submit"

3. Receipt should appear with status: **DRAFT**

### 3. Approve Receipt

Click the **Approve** (✓) button next to the receipt

Status should change to: **APPROVED**

### 4. Authorize & Post

Click the **Authorize & Post** (→) button

System will create GL entries:
- DEBIT: 3100-01
- CREDIT: 100001

### 5. Verify GL Entries

Navigate to: `https://192.168.2.69/accounting/general-ledger/`

Filter by: `CASH-RECEIPT-`

You should see both entries:
- Debit entry to account 3100-01
- Credit entry to account 100001

---

## ❌ If Something Goes Wrong

### Error: "Account already exists"
- This is fine - means the account is already set up
- Continue to testing steps

### Error: "Account not found in form dropdown"
- Restart Django: `sudo systemctl restart gunicorn-tradifyerp`
- Refresh browser (Ctrl+Shift+R)

### Error: "GL entries not appearing"
- Make sure receipt is AUTHORIZED (not just APPROVED)
- Check database for entries:
  ```sql
  SELECT * FROM accounting_ledgerentry 
  WHERE reference_number LIKE 'CASH-RECEIPT-%';
  ```

### Error: "Entity or Currency not found"
- Use these queries to find correct IDs:
  ```sql
  SELECT id, code FROM accounting_entity WHERE is_active=true;
  SELECT id, code FROM accounting_currency WHERE is_active=true;
  ```
- Update the INSERT statement with correct IDs

---

## 📋 Checklist

- [ ] SSH to database server (192.168.2.59)
- [ ] Connect to PostgreSQL
- [ ] Run the INSERT query from Option 1, Step 3
- [ ] Verify Cash Account exists with SELECT queries
- [ ] Navigate to cash receipts form
- [ ] Create test receipt
- [ ] Approve receipt
- [ ] Authorize & post
- [ ] Verify GL entries appear

---

## 📞 Quick Help

**Database Connection:**
```
Host: 192.168.2.59
Port: 5432
User: zubair
Password: sql
Database: tradifyerp_db
```

**Application URLs:**
- Dashboard: https://192.168.2.69/accounting/dashboard/
- Cash Receipts: https://192.168.2.69/accounting/cash-receipts/
- General Ledger: https://192.168.2.69/accounting/general-ledger/

---

## ✨ Success!

When complete, you'll have:
✅ Cash Account (100001) configured
✅ GL posting automation working
✅ Shareholder tracking enabled
✅ Complete audit trail

Everything is ready to use! 🎉
