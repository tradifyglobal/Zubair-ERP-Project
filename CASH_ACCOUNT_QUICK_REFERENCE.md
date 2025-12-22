# CASH ACCOUNT SETUP - QUICK REFERENCE CARD

## 🚀 ONE-LINE DEPLOYMENT

```bash
# SSH to app server, activate venv, and run setup
ssh zubair@192.168.2.69 "cd /home/zubair/tradifyerp && source venv/bin/activate && python manage.py setup_cash_account"
```

---

## 📋 WHAT WAS CREATED

| File | Purpose | Location |
|------|---------|----------|
| `setup_cash_account.py` | Django management command | `TradifyERP/accounting/management/commands/` |
| `setup_cash_account.sql` | SQL setup script | Project root |
| `deploy_cash_account_setup.sh` | Automated deployment | Project root |
| `CASH_ACCOUNT_IMPLEMENTATION_GUIDE.md` | Complete documentation | Project root |
| `CASH_ACCOUNT_DEPLOYMENT_CHECKLIST.md` | Deployment steps | Project root |
| `CASH_ACCOUNT_COMPLETE_SUMMARY.md` | Full summary | Project root |

---

## ✅ ACCOUNTS CONFIGURED

### Cash Account (NEW)
```
Account #: 100001
Name: Cash
Type: ASSET
Purpose: Receive cash from shareholders and other sources
```

### Capital Accounts (EXISTING)
```
Account #: 3000 (Main Capital)
Account #: 3100 (Shareholder Investment)
Account #: 3100-01, 3100-02, etc. (Individual shareholders)
```

---

## 🔄 WORKFLOW SUMMARY

```
USER CREATES RECEIPT → APPROVER APPROVES → FINANCE POSTS → GL UPDATED
     (DRAFT)              (APPROVED)        (AUTHORIZED)   (POSTED)
```

**GL Entries Created**:
- DEBIT: Capital Account (3100-01) 
- CREDIT: Cash Account (100001)

---

## 📱 USER URLS

| Action | URL |
|--------|-----|
| Create Cash Receipt | `/accounting/cash-receipts/create/` |
| List Receipts | `/accounting/cash-receipts/` |
| View General Ledger | `/accounting/general-ledger/` |
| Dashboard | `/accounting/dashboard/` |

---

## 🔐 SERVER CREDENTIALS

| Server | IP | User | Password |
|--------|-----|------|----------|
| App | 192.168.2.69 | zubair | erp |
| Database | 192.168.2.59 | zubair | sql |

---

## 📊 DATABASE CHECKS

### Is Cash Account Created?
```sql
SELECT * FROM accounting_account WHERE account_number='100001';
```

### Recent Cash Receipts
```sql
SELECT id, debit_amount, status FROM accounting_cashreceiptline LIMIT 5;
```

### GL Entries for Cash Receipts
```sql
SELECT * FROM accounting_ledgerentry WHERE reference_number LIKE 'CASH-RECEIPT-%' LIMIT 10;
```

---

## 🛠️ TROUBLESHOOTING

| Problem | Fix |
|---------|-----|
| "Setup command not found" | Make sure `setup_cash_account.py` is in `accounting/management/commands/` |
| "Cash account not created" | Run: `python manage.py setup_cash_account` |
| "GL entries not showing" | Authorize the receipt first (click "Authorize & Post") |
| App won't load | Restart: `sudo systemctl restart gunicorn-tradifyerp` |

---

## ✨ FEATURES ENABLED

- ✅ Cash receipt creation with workflow
- ✅ Multi-level approval (approve → authorize)
- ✅ Automatic GL posting on authorization
- ✅ Shareholder capital tracking
- ✅ Full audit logging
- ✅ Entity-aware operations

---

## 📈 NEXT ACTIONS

1. **Deploy**: Run setup command on production
2. **Test**: Create test cash receipt
3. **Verify**: Check GL entries appear
4. **Train**: Teach users the workflow
5. **Monitor**: Watch for errors in logs

---

## 🎯 SUCCESS CRITERIA

- [ ] Cash Account (100001) exists
- [ ] Cash receipt form loads at `/accounting/cash-receipts/create/`
- [ ] Can create receipt and approve it
- [ ] GL entries appear when receipt is authorized
- [ ] Both debit (3100-01) and credit (100001) entries visible
- [ ] Shareholder is linked to receipt

---

## 📞 SUPPORT

**Documentation**: See `CASH_ACCOUNT_IMPLEMENTATION_GUIDE.md`
**Deployment**: See `CASH_ACCOUNT_DEPLOYMENT_CHECKLIST.md`
**Full Summary**: See `CASH_ACCOUNT_COMPLETE_SUMMARY.md`

---

**Status**: ✅ READY FOR DEPLOYMENT  
**Date**: December 15, 2025  
**Version**: 1.0
