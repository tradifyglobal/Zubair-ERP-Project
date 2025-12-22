# 🚀 CASH ACCOUNT SETUP - SUPER SIMPLE

## This is all you need to do:

### Step 1: SSH to Database Server
```bash
ssh zubair@192.168.2.59
# Password: sql
```

### Step 2: Connect to Database
```bash
psql -U zubair -d tradifyerp_db
```

### Step 3: Copy & Paste This SQL

```sql
INSERT INTO accounting_account (account_number,name,account_type,description,entity_id,currency_id,is_active,opening_balance,parent_account_id,created_at,updated_at) SELECT '100001','Cash','ASSET','Cash account for receiving cash from shareholders',ae.id,ac.id,true,0.00,NULL,NOW(),NOW() FROM accounting_entity ae, accounting_currency ac WHERE ae.code='INT001' AND ac.code='INR' AND NOT EXISTS (SELECT 1 FROM accounting_account WHERE account_number='100001');
```

### Step 4: Verify It Worked

```sql
SELECT account_number, name, account_type FROM accounting_account WHERE account_number='100001';
```

Should show:
```
 account_number │ name │ account_type
────────────────┼──────┼──────────────
 100001         │ Cash │ ASSET
```

### Step 5: Exit

```sql
\q
```

---

## That's it! ✅

Your Cash Account is now configured and ready to use.

Go to: https://192.168.2.69/accounting/cash-receipts/create/

Start creating cash receipts!

---

## Need Help?

See: `CASH_ACCOUNT_MANUAL_SETUP.md` for detailed instructions

All files: `CASH_ACCOUNT_MASTER_INDEX.md`
