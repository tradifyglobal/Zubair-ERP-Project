# Cash Management Module - Quick Reference Guide

## 🚀 Getting Started

### Access Points
```
Dashboard → Accounting → Cash Management
  ├── Cash Receipts (100001)
  ├── Cash Payments (100001)
  ├── Bank Receipts (100002)
  └── Bank Payments (100002)
```

### URLs
| Action | URL |
|--------|-----|
| List Cash Receipts | `/accounting/cash-receipts/` |
| Create Cash Receipt | `/accounting/cash-receipts/create/` |
| List Cash Payments | `/accounting/cash-payments/` |
| Create Cash Payment | `/accounting/cash-payments/create/` |
| List Bank Receipts | `/accounting/bank-receipts/` |
| Create Bank Receipt | `/accounting/bank-receipts/create/` |
| List Bank Payments | `/accounting/bank-payments/` |
| Create Bank Payment | `/accounting/bank-payments/create/` |

## 📊 Transaction Types

### 1. Cash Receipt (Money In)
**When to use:** Shareholder capital contributions, cash deposits
**GL Impact:**
- **DR:** Shareholder Capital Account (e.g., 3100-01)
- **CR:** Cash (100001)

**Form Fields:**
- Date (auto-filled today)
- Account (shareholder capital account)
- Description
- Debit Amount & Credit Amount (must match)
- Reference # (optional)
- Notes (optional)

### 2. Cash Payment (Money Out)
**When to use:** Capital returns to shareholders, cash withdrawals
**GL Impact:**
- **DR:** Cash (100001)
- **CR:** Shareholder Capital Account (e.g., 3100-01)

**Form Fields:**
- Date (auto-filled today)
- Account (shareholder capital account)
- Description
- Debit Amount & Credit Amount (must match)
- Reference # (optional)
- Notes (optional)

### 3. Bank Receipt (Deposit to Bank)
**When to use:** Moving capital/funds to bank account
**GL Impact:**
- **DR:** Bank Account (100002)
- **CR:** Source Account (e.g., Capital 3100-01)

**Form Fields:**
- Date (auto-filled today)
- Bank Account (100002 or similar)
- Source Account (where money comes from)
- Description
- Amount
- Reference # (optional)
- Notes (optional)

### 4. Bank Payment (Withdraw from Bank)
**When to use:** Expenses, payments from bank account
**GL Impact:**
- **DR:** Target/Expense Account
- **CR:** Bank Account (100002)

**Form Fields:**
- Date (auto-filled today)
- Bank Account (100002 or similar)
- Target Account (where money goes - expense, etc.)
- Description
- Amount
- Reference # (optional)
- Notes (optional)

## ✅ Validation Rules

### Cash Receipt & Payment
- ❌ Debit and Credit amounts must be EQUAL
- ❌ Amounts must be > 0
- ✅ Both amounts required
- ✅ Account selection required
- ✅ Description required

### Bank Receipt & Payment
- ❌ Amount must be > 0
- ✅ Amount required
- ✅ Bank account required
- ✅ Source/Target account required
- ✅ Description required

## 📋 List View Features

### Columns Displayed
| Column | Details |
|--------|---------|
| Date | Format: "Nov 29, 2025" |
| Description | First 10 words, truncated |
| Reference | Shows reference number if exists |
| Account(s) | Account code + name (e.g., "3100-01 - Test - Capital") |
| Amounts | Debit/Credit in colored badges |
| Status | Draft (grey) or Posted (green) |
| Actions | View / Edit buttons |

### Filtering Options
- **Status:** All / Draft / Posted
- **Search:** By description or reference number
- **Reset:** Clear all filters

### Status Indicators
- **Draft** (grey badge): Not yet posted to GL
- **Posted** (green badge): Posted to GL as AUTHORIZED

## 🎯 Common Tasks

### Task: Record Shareholder Capital Contribution
1. Navigate to `/accounting/cash-receipts/create/`
2. Select Account: `3100-01 - Test - Capital`
3. Enter Description: `Initial capital contribution from Test`
4. Enter Debit Amount: `100,000.00`
5. Enter Credit Amount: `100,000.00` (must match!)
6. Click `Save & Post Receipt`
7. Success message shows ✓
8. 2 GL entries created automatically

### Task: Move Capital to Bank
1. Navigate to `/accounting/bank-receipts/create/`
2. Select Bank Account: `100002 - Bank Account`
3. Select Source Account: `3100-01 - Test - Capital`
4. Enter Description: `Transfer capital to bank`
5. Enter Amount: `50,000.00`
6. Click `Save & Post Receipt`
7. Success message shows ✓
8. 2 GL entries created automatically

### Task: Search for Specific Transaction
1. Go to relevant list view (e.g., `/accounting/cash-receipts/`)
2. Enter search term in search box
3. Click "Filter"
4. Results filtered by description or reference number

### Task: View Transaction Details
1. Go to list view
2. Locate transaction in table
3. Click eye icon (👁) in Actions column
4. View full transaction details (future)

### Task: Edit Draft Transaction
1. Go to list view
2. Look for transaction with "Draft" status
3. Click pencil icon (✏️) in Actions column
4. Update fields as needed
5. Save changes

## 🔍 Checking GL Integration

### Verify GL Entries Created

**Method 1: Direct Check**
1. Go to `/accounting/ledger-entries/`
2. Filter by status: `AUTHORIZED`
3. Should see 2 entries per cash transaction
4. Reference should show: `CASH-RECEIPT`, `CASH-PAYMENT`, `BANK-RECEIPT`, or `BANK-PAYMENT`
5. Amounts should match (debit on one, credit on other)

**Method 2: Account Balance Check**
1. Go to `/accounting/accounts/`
2. Click account (e.g., 100001 - Cash)
3. View account details with posting entries
4. Recent cash transactions should appear

**Method 3: Trial Balance Check**
1. Go to `/accounting/trial-balance/`
2. Total debits should equal total credits
3. Cash transaction balances should reflect

## 📈 Account Codes Reference

| Code | Account Name | Type |
|------|-------------|------|
| 100001 | Cash | Asset |
| 100002 | Bank Account | Asset |
| 3100 | Capital (Parent) | Equity |
| 3100-01 | Test - Capital | Equity |
| 3100-02 | Imteyazuddin S.M. - Capital | Equity |
| 3100-03 | Johnmac MacJohn - Capital | Equity |

## ⚙️ Admin Access

### Register Models
All cash models registered in Django Admin:
- Path: `/admin/accounting/cashreceiptline/`
- Path: `/admin/accounting/cashpaymentline/`
- Path: `/admin/accounting/bankreceiptline/`
- Path: `/admin/accounting/bankpaymentline/`

### Admin Features
- Create/Edit/Delete transactions
- Filter by entity, status, date
- Search by description/reference
- Bulk operations available

## 🐛 Troubleshooting

### Issue: "Cash account (100001) not found"
**Solution:** 
1. Go to `/admin/accounting/account/`
2. Search for account number "100001"
3. If not found, create it:
   - Account Number: 100001
   - Name: Cash
   - Type: Asset
   - Parent: (leave blank)

### Issue: Amounts don't match (Cash Receipt)
**Solution:**
- Debit Amount must exactly equal Credit Amount
- No rounding differences allowed
- If amounts are 100,000.00 and 100,000.01, they won't match

### Issue: Amount shows as 0
**Solution:**
- Ensure amount > 0
- Check decimal separator (. for decimals)
- Don't use currency symbols

### Issue: Form won't submit
**Solution:**
1. Check all required fields filled
2. Verify amount validation (> 0)
3. For cash receipt/payment: debit = credit
4. Look for error messages in red
5. Check browser console for JS errors

## 📊 Dashboard Integration

### Cash Position Card
- Shows total cash on hand (100001 balance)
- Shows bank total (100002 balance)
- Updated in real-time

### Recent Transactions
- Latest 5 cash transactions displayed
- Status indicator (draft/posted)
- Quick links to transaction details

## 🔐 Security & Permissions

### Data Segregation
- All transactions entity-specific
- Users only see their entity's data
- No cross-entity access

### Audit Trail
- Every transaction logged
- User who created it tracked
- Timestamp recorded
- Action type logged

### Workflow Status
- All cash transactions bypass approval workflow
- Automatically AUTHORIZED status
- Immediately posted to GL
- No pending approval state

## 📝 Form Tips

### Smart Defaults
- Date field auto-fills to today
- Account field shows all GL accounts
- Focus moves to next field after selection

### Validation Messages
- Messages appear in red under field
- Hover over error for details
- Form won't submit until errors fixed

### Account Selection
- Dropdown searchable (start typing)
- Shows account code and name
- Highlights matching accounts

## 🎨 UI Navigation

### List View Layout
```
[Breadcrumb]
[Page Title & Description] [New Transaction Button]
[Status Summary Cards]
[Search & Filter Bar]
[Data Table with Pagination]
```

### Create Form Layout
```
[Breadcrumb]
[Page Title]
[Form Fields in Groups]
[Validation Errors]
[Save & Cancel Buttons]
```

## 🚀 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Submit Form | `Tab` + `Enter` |
| Search Results | `Ctrl + F` (browser find) |
| New Transaction | Direct URL or menu |
| Go Back | Browser back button |

## 📞 Support

For issues or questions:
1. Check this quick reference
2. Review integration guide: `CASH_MANAGEMENT_INTEGRATION.md`
3. Check error message for details
4. Review transaction in GL for balance verification
5. Check audit log for transaction history

---

**Module Status:** ✅ Complete and Production Ready
**Last Updated:** November 29, 2025
**Version:** 1.0
