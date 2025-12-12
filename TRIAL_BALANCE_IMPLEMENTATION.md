# Trial Balance Calculation Implementation

## Overview

Trial balance calculation has been fully implemented in your ERP system. A trial balance is an accounting report that verifies the fundamental equation of double-entry bookkeeping:

$$\text{Total Debits} = \text{Total Credits}$$

## System Architecture

### Core Components

#### 1. **Trial Balance Module** (`accounting/trial_balance.py`)
Contains three main functions:

**`calculate_trial_balance(entity, as_of_date)`**
- Calculates trial balance from GL entries as of a specific date
- Filters all posted LedgerEntry records up to the given date
- Groups entries by account and sums debits/credits
- Returns account balances with debit/credit totals
- Handles account-type-specific balance calculations

**Returns:**
```python
{
    'total_debits': Decimal,           # Sum of all debits
    'total_credits': Decimal,          # Sum of all credits
    'is_balanced': bool,               # True if debits == credits
    'account_balances': [
        {
            'account': Account,        # Account object
            'account_number': str,     # e.g., "1010"
            'account_name': str,       # e.g., "Cash"
            'account_type': str,       # ASSET, LIABILITY, EQUITY, INCOME, EXPENSE
            'debit_balance': Decimal,  # Total debits for account
            'credit_balance': Decimal, # Total credits for account
            'net_balance': Decimal,    # Absolute value of net position
            'balance_side': str,       # 'DEBIT' or 'CREDIT' (normal side)
        }
    ],
    'as_of_date': date,                # The calculation date
}
```

**`save_trial_balance(entity, as_of_date)`**
- Calculates and saves trial balance to TrialBalance model
- Updates existing record if already present
- Raises exception on calculation error

**Returns:** TrialBalance database object

**`verify_gl_balance(entity, as_of_date=None)`**
- Quick verification that GL is balanced
- Useful for auditing without saving
- Shows difference amount if unbalanced

**Returns:**
```python
{
    'balanced': bool,          # Is GL balanced?
    'total_debits': Decimal,
    'total_credits': Decimal,
    'difference': Decimal,     # Absolute difference if unbalanced
    'as_of_date': date,
}
```

### 2. **Updated Views** (`accounting/views.py`)

**`TrialBalanceListView`** - Enhanced to:
- Calculate trial balance for today automatically
- Save results to database
- Display account balances in context
- Handle calculation errors gracefully

### 3. **Management Command** (`accounting/management/commands/generate_trial_balance.py`)

Generate trial balance from command line:

```bash
# Generate for all entities (default: today)
python manage.py generate_trial_balance

# Generate for specific entity
python manage.py generate_trial_balance --entity=TRADIFY

# Generate for specific date
python manage.py generate_trial_balance --date=2025-12-10

# Combined
python manage.py generate_trial_balance --entity=TRADIFY --date=2025-12-10

# Verify only (don't save)
python manage.py generate_trial_balance --verify-only
```

## How Trial Balance is Calculated

### Step 1: Retrieve GL Entries
- Fetch all `LedgerEntry` records for the entity
- Filter by: `entry_date <= as_of_date` AND `is_posted = True`
- Select related: Account information

### Step 2: Group by Account
- Create dictionary: `account_id → {account, debit_total, credit_total}`
- Iterate through entries:
  - If `entry_type == 'DEBIT'`: Add amount to account's debit_total
  - If `entry_type == 'CREDIT'`: Add amount to account's credit_total
  - Track running totals of all debits and credits

### Step 3: Calculate Account Balances
For each account, determine "normal balance side":

```
ASSET accounts (e.g., Cash, Accounts Receivable):
  Normal Balance = DEBIT side
  Net Balance = Debits - Credits

LIABILITY accounts (e.g., Accounts Payable):
  Normal Balance = CREDIT side
  Net Balance = Credits - Debits

EQUITY accounts (e.g., Capital, Retained Earnings):
  Normal Balance = CREDIT side
  Net Balance = Credits - Debits

INCOME accounts (e.g., Sales Revenue):
  Normal Balance = CREDIT side
  Net Balance = Credits - Debits

EXPENSE accounts (e.g., Salaries, Rent):
  Normal Balance = DEBIT side
  Net Balance = Debits - Credits
```

### Step 4: Verify Balance
- Calculate: `is_balanced = (total_debits == total_credits)`
- In proper double-entry bookkeeping, this should ALWAYS be true
- If unbalanced, indicates data integrity issue or unposted entries

### Step 5: Save to Database
- Create/update `TrialBalance` record
- Store: total_debits, total_credits, is_balanced, as_of_date
- Enables historical trial balance tracking

## Key Concepts

### Double-Entry Bookkeeping Rule
Every transaction is recorded with:
- A DEBIT to one or more accounts
- A CREDIT to one or more accounts
- Total debits = Total credits (always balanced)

### Example Transaction
When you record "Employee paid $5,000 salary from Cash":

```
Debit:  5020 - Salary Expense          $5,000.00
Credit: 1010 - Cash                               $5,000.00
```

Trial Balance Contribution:
- 5020 Salary Expense: Debit balance = $5,000
- 1010 Cash: Credit balance = $5,000
- Total Debits = $5,000 | Total Credits = $5,000 ✓ BALANCED

### Account Type Classifications

| Type | Normal Balance | Examples | Use |
|------|---|---|---|
| ASSET | Debit | Cash, AR, Equipment | Resources owned |
| LIABILITY | Credit | AP, Loans Payable | Obligations |
| EQUITY | Credit | Capital, Retained Earnings | Ownership stake |
| INCOME | Credit | Sales Revenue, Interest | Increases equity |
| EXPENSE | Debit | Salaries, Rent, Utilities | Decreases equity |

## Usage Examples

### In Python/Views
```python
from accounting.trial_balance import calculate_trial_balance, save_trial_balance
from datetime import date
from accounting.models import Entity

entity = Entity.objects.get(code='TRADIFY')
as_of_date = date(2025, 12, 10)

# Calculate
tb_data = calculate_trial_balance(entity, as_of_date)
print(f"Total Debits: {tb_data['total_debits']}")
print(f"Is Balanced: {tb_data['is_balanced']}")

# Display accounts
for account in tb_data['account_balances']:
    print(f"{account['account_number']}: DR={account['debit_balance']} CR={account['credit_balance']}")

# Save
save_trial_balance(entity, as_of_date)
```

### Via Management Command
```bash
# Check current balance
python manage.py generate_trial_balance --entity=TRADIFY --verify-only

# Generate and save for all entities
python manage.py generate_trial_balance

# Generate for past date (period-end closing)
python manage.py generate_trial_balance --date=2025-11-30
```

## Integration with Other Modules

### LedgerEntry Model
- Source of truth for all GL entries
- Fields: account, entity, entry_date, entry_type (DEBIT/CREDIT), amount, is_posted

### Account Model
- Defines chart of accounts
- Fields: account_number, name, account_type, entity, is_active

### TrialBalance Model
- Stores trial balance snapshots
- Fields: entity, as_of_date, total_debits, total_credits, is_balanced
- Unique together: (entity, as_of_date) - one trial balance per date per entity

## Troubleshooting

### Trial Balance Out of Balance

**Symptom:** `total_debits ≠ total_credits`

**Diagnosis:**
```bash
# Verify GL entries
python manage.py generate_trial_balance --entity=TRADIFY --verify-only
```

**Common Causes:**
1. **Incomplete double-entry:** One side of transaction not recorded
   - Solution: Check JournalEntryPostingQueue for pending postings
   
2. **Data import error:** Unbalanced bulk import
   - Solution: Review import logs, reprocess unmatched entries

3. **Manual GL entry:** User created unbalanced debit-only entry
   - Solution: Require two-step entry (debit + credit together)

**Fix:**
```python
# Identify unbalanced accounts
from accounting.trial_balance import calculate_trial_balance
tb = calculate_trial_balance(entity, as_of_date)
# Look for accounts with only DR or only CR balance
```

### No GL Entries Found

**Symptom:** `total_debits = 0, total_credits = 0`

**Possible Causes:**
1. No GL entries have been posted yet
2. Entries exist but `is_posted=False` (pending)
3. All entries are dated after the `as_of_date`

**Verify:**
```python
from accounting.models import LedgerEntry
from datetime import date

entity_id = 1
as_of_date = date.today()

# Check posted entries
posted = LedgerEntry.objects.filter(
    entity_id=entity_id,
    entry_date__lte=as_of_date,
    is_posted=True
).count()
print(f"Posted entries: {posted}")

# Check pending entries
pending = LedgerEntry.objects.filter(
    entity_id=entity_id,
    is_posted=False
).count()
print(f"Pending entries: {pending}")
```

## Performance Considerations

### Query Optimization
- Uses `select_related('account')` to minimize database queries
- Filters at database level before processing in Python
- Single pass through entries (O(n) complexity)

### For Large GL (1000+ entries per date)
```python
from django.db.models import Q

# Faster calculation using database aggregation
from django.db.models import Sum, Case, When, DecimalField, F

totals = LedgerEntry.objects.filter(
    entity=entity,
    entry_date__lte=as_of_date,
    is_posted=True
).aggregate(
    total_debits=Sum(
        Case(
            When(entry_type='DEBIT', then=F('amount')),
            default=0,
            output_field=DecimalField()
        )
    ),
    total_credits=Sum(
        Case(
            When(entry_type='CREDIT', then=F('amount')),
            default=0,
            output_field=DecimalField()
        )
    ),
)
```

## Testing

### Unit Test Example
```python
from django.test import TestCase
from accounting.models import Entity, Account, LedgerEntry
from accounting.trial_balance import calculate_trial_balance
from datetime import date
from decimal import Decimal

class TrialBalanceTestCase(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(code='TEST', name='Test Entity')
        self.cash = Account.objects.create(
            entity=self.entity,
            account_number='1010',
            name='Cash',
            account_type='ASSET'
        )
        self.sales = Account.objects.create(
            entity=self.entity,
            account_number='4010',
            name='Sales Revenue',
            account_type='INCOME'
        )
    
    def test_simple_transaction_balanced(self):
        # Record: DR Cash 1000, CR Sales 1000
        LedgerEntry.objects.create(
            entity=self.entity,
            account=self.cash,
            entry_date=date.today(),
            entry_type='DEBIT',
            amount=Decimal('1000.00'),
            is_posted=True
        )
        LedgerEntry.objects.create(
            entity=self.entity,
            account=self.sales,
            entry_date=date.today(),
            entry_type='CREDIT',
            amount=Decimal('1000.00'),
            is_posted=True
        )
        
        # Calculate
        tb = calculate_trial_balance(self.entity, date.today())
        
        # Verify
        self.assertEqual(tb['total_debits'], Decimal('1000.00'))
        self.assertEqual(tb['total_credits'], Decimal('1000.00'))
        self.assertTrue(tb['is_balanced'])
```

## Next Steps

1. **Generate trial balances** for historical periods using:
   ```bash
   python manage.py generate_trial_balance --date=2025-11-30
   ```

2. **Create trial balance template** to display accounts on the web interface

3. **Add period comparisons** (month-to-month, year-to-year)

4. **Integrate with financial statements**:
   - Balance Sheet (uses trial balance data)
   - Profit & Loss (uses trial balance data)

5. **Set up automated daily TB generation** via cron or Celery:
   ```bash
   0 1 * * * /usr/bin/python3 /var/www/tradifyerp/TradifyERP/manage.py generate_trial_balance
   ```

## Files Modified

- `accounting/trial_balance.py` - **NEW** - Core calculation module
- `accounting/views.py` - Updated `TrialBalanceListView` to use calculator
- `accounting/management/commands/generate_trial_balance.py` - **NEW** - CLI tool
- `accounting/models.py` - ✓ Already has TrialBalance model
- `accounting/admin.py` - ✓ Already has TrialBalanceAdmin

## Summary

Your trial balance system is now:
- ✅ **Fully implemented** with core calculation functions
- ✅ **Integrated with views** for web display
- ✅ **Command-line accessible** for batch processing
- ✅ **Database persistent** for historical tracking
- ✅ **Error-handled** with proper exception management
- ✅ **Ready for financial statements** (Balance Sheet, P&L)
