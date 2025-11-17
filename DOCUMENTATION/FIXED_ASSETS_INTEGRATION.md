# Fixed Asset Integration with Ledger Entries

## Overview
Fixed Assets are now fully integrated with the General Ledger system. When you create a fixed asset, journal entries are automatically created to record the transaction.

## How It Works

### 1. Purchase Transaction (Automatic)
When a fixed asset is created:
- **Debit**: Fixed Assets Account (Asset)
- **Credit**: Cash/Bank Account (Asset)
- Status: Auto-posted to ledger

Example: Purchase of Equipment for $10,000
```
Debit:  Fixed Assets    $10,000
Credit: Cash           $10,000
```

### 2. Monthly Depreciation (Manual)
Run the depreciation command at the end of each month:

```bash
# Generate depreciation for current month
python manage.py generate_depreciation

# Generate for specific year-month
python manage.py generate_depreciation --year-month 2025-11

# Generate for specific entity
python manage.py generate_depreciation --entity-id 1
```

This creates entries:
- **Debit**: Depreciation Expense
- **Credit**: Accumulated Depreciation (Contra-Asset)

Example: Monthly depreciation of $167 (5-year equipment, $10,000 cost)
```
Debit:  Depreciation Expense          $167
Credit: Accumulated Depreciation     $167
```

## Features

### In Fixed Assets Module
- ✅ Asset details (code, name, category, dates, costs)
- ✅ Depreciation tracking (annual rate, accumulated amount, book value)
- ✅ Ledger entry links (click to view original purchase journal entry)
- ✅ Disposal tracking (disposal date, salvage value, disposed status)
- ✅ Last depreciation date shown

### In Ledger Entries
- ✅ All purchase transactions appear with reference `FA-[ASSET-CODE]`
- ✅ All depreciation transactions appear with reference `DEP-[ASSET-CODE]-[YYYY-MM]`
- ✅ Fully searchable and filterable

### In Financial Reports
- ✅ Balance Sheet shows net Fixed Assets (gross - accumulated depreciation)
- ✅ Profit & Loss shows Depreciation Expense
- ✅ Trial Balance includes all related accounts

## Chart of Accounts Setup

The system will automatically create necessary accounts if they don't exist:
- **Account 1500** - Fixed Assets (ASSET type)
- **Account 1510** - Accumulated Depreciation (ASSET type, contra-asset)
- **Account 5100** - Depreciation Expense (EXPENSE type)

## Model Fields

### FixedAsset Model
```python
purchase_ledger_entry    # OneToOne link to the purchase journal entry
last_depreciation_date   # Date of last depreciation posting
disposal_date           # When asset was disposed
disposal_amount         # Salvage/proceeds value
is_disposed             # Boolean flag for disposal status
```

## Example Workflow

### Month 1: Purchase Equipment
1. Create Fixed Asset record:
   - Code: EQUIP-001
   - Name: Office Computer
   - Cost: $5,000
   - Life: 5 years
   - Annual Depreciation: $1,000

2. System automatically creates:
   - Purchase journal entry (Dr. Equipment / Cr. Cash)
   - Entries visible in Ledger Entries module

### Month 2: Record Depreciation
1. Run: `python manage.py generate_depreciation`
2. System creates:
   - Depreciation entry (Dr. Depreciation Expense / Cr. Accumulated Depreciation)
   - Amount: $83.33 (monthly = $1,000 / 12)
   - Last depreciation date updated to current month

### View in Reports
- **Balance Sheet**: Shows Equipment $5,000, less Accumulated Depreciation ($83.33) = Net $4,916.67
- **P&L**: Shows Depreciation Expense of $83.33

## Key Accounting Relationships

```
Fixed Assets (GL Account 1500)
├── Accumulated Depreciation (Contra - GL Account 1510)
│   └── Updated each month by depreciation command
└── Purchase Ledger Entry (OneToOne)
    └── Links asset to original purchase transaction

Profit & Loss
└── Depreciation Expense (GL Account 5100)
    └── Created each month by depreciation command
```

## FAQ

**Q: Do I have to manually post depreciation?**
A: Yes, run the management command monthly. You can automate this with cron jobs or Django Q.

**Q: Can I dispose of an asset?**
A: Yes, edit the asset and set `is_disposed = True` and fill in `disposal_date` and `disposal_amount`.

**Q: What if I delete a fixed asset?**
A: The linked journal entries remain in the ledger for audit trail.

**Q: How do I see the purchase journal entry?**
A: Click the "📊 Journal Entry" link in the Fixed Assets list, or click the asset code link.

**Q: Can I adjust accumulated depreciation manually?**
A: Yes, through the accounting module, create manual depreciation adjustments as needed.

**Q: What's the difference between book value and disposal amount?**
A: Book value = Cost - Accumulated Depreciation. Disposal amount is what you actually sell it for.
