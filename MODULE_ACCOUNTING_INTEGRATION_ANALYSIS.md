# TradifyERP - Module to Accounting Integration Analysis

## Overview
This document explains how all modules (Sales, Manufacturing, Procurement, Expenses, HR, Maintenance) connect to the Accounting module and reflect transactions in Trial Balance, Profit & Loss, and Trading & Manufacturing Account reports.

---

## 🎯 Integration Architecture

### Core Pattern: Double-Entry Accounting
All modules follow the same integration pattern:
1. **Transaction occurs** in operational module (Sales, Manufacturing, etc.)
2. **Signal/Method triggers** GL posting logic
3. **LedgerEntry records created** in accounting module (debit + credit)
4. **Financial reports pull** from LedgerEntry table
5. **Reports display** aggregated data

---

## 📊 Module-by-Module Integration

### 1. ✅ SALES MODULE → Accounting

**Integration File:** `TradifyERP/sales/integration.py`

**Key Models:**
- `Invoice` (sales/models.py)
- `GeneralLedgerPosting` (sales/models.py)
- `AccountsReceivable` (sales/models.py)
- `LedgerEntry` (accounting/models.py)

**Transaction Flow:**

```
Invoice Created (Status: ISSUED)
    ↓
GLPostingManager.post_invoice_revenue_to_gl()
    ├─ DR: Accounts Receivable (1200) = Total Amount
    └─ CR: Sales Revenue (4100) = Subtotal
    
GLPostingManager.post_invoice_tax_to_gl()
    ├─ DR: Accounts Receivable (1200) = Tax Amount
    └─ CR: Sales Tax Payable (2110) = Tax Amount

Payment Received
    ↓
PaymentProcessor.process_customer_payment()
    ├─ DR: Cash (1000) = Payment Amount
    └─ CR: Accounts Receivable (1200) = Payment Amount
```

**GL Posting Code:**
```python
# Location: sales/integration.py:146+
class GLPostingManager:
    @staticmethod
    def post_invoice_revenue_to_gl(invoice):
        # Creates LedgerEntry for AR (debit)
        # Creates LedgerEntry for Revenue (credit)
        # Links to GeneralLedgerPosting record
```

**Reflection in Reports:**

| Report | Account | Line Item | Amount Source |
|--------|---------|-----------|---------------|
| **P&L** | Sales Revenue (4100) | Revenue | invoice.subtotal (CREDIT) |
| **P&L** | Sales Tax Payable (2110) | Tax Expense | invoice.tax_amount (CREDIT) |
| **Trial Balance** | Accounts Receivable (1200) | Asset | Outstanding invoices (DEBIT) |
| **Trial Balance** | Sales Revenue (4100) | Income | Total sales (CREDIT) |
| **Trading & Manufacturing** | Sales | Total Sales | All sales revenue accounts |
| **Trading & Manufacturing** | Sales Returns | Returns | Sales return accounts |

**Verification Query:**
```python
# Check if sales are posting to GL
from accounting.models import LedgerEntry
sales_entries = LedgerEntry.objects.filter(
    reference_number__startswith='INV-',
    account__account_type='INCOME'
)
```

---

### 2. ✅ MANUFACTURING MODULE → Accounting

**Integration File:** `TradifyERP/manufacturing/signals.py`

**Key Models:**
- `ProductionOrder` (manufacturing/models.py)
- `JournalEntry` (accounting/models.py)
- `JournalEntryLine` (accounting/models.py)

**Transaction Flow:**

```
ProductionOrder (Status: COMPLETE)
    ↓
post_save signal → production_order_post_save()
    ├─ Calculate total_actual_cost
    │  (material_cost + labor_cost)
    ↓
JournalEntry Created:
    ├─ DEBIT: Finished Goods Inventory (1300)
    │         Amount: actual_material_cost + actual_labor_cost
    └─ CREDIT: Work-in-Process (1400)
               Amount: actual_material_cost + actual_labor_cost
```

**GL Posting Code:**
```python
# Location: manufacturing/signals.py:47+
@receiver(post_save, sender=ProductionOrder)
def production_order_post_save(sender, instance, created, **kwargs):
    if instance.status == 'COMPLETE':
        # Create JournalEntry with reference MFG-{po_number}
        # DEBIT: inventory_account (Finished Goods)
        # CREDIT: wip_account (Work in Process)
```

**Reflection in Reports:**

| Report | Account | Line Item | Amount Source |
|--------|---------|-----------|---------------|
| **P&L** | Cost of Goods Sold (5100) | Manufacturing Cost | When goods sold |
| **Trial Balance** | Finished Goods (1300) | Asset | Completed production (DEBIT) |
| **Trial Balance** | Work-in-Process (1400) | Asset | In-progress production (DEBIT) |
| **Trading & Manufacturing** | Manufacturing Costs | Direct Labor/Materials | Production costs |

**Verification Query:**
```python
# Check if manufacturing posts to GL
from accounting.models import JournalEntry
mfg_entries = JournalEntry.objects.filter(
    reference__startswith='MFG-'
)
```

---

### 3. ✅ PROCUREMENT MODULE → Accounting

**Integration File:** `TradifyERP/procurement/gl_integration.py`

**Key Models:**
- `PurchaseOrder` (procurement/models.py)
- `GoodsReceipt` (procurement/models.py)
- `LedgerEntry` (accounting/models.py)

**Transaction Flow:**

```
Goods Received (GR Created)
    ↓
create_gr_gl_entries(goods_receipt)
    ├─ DR: Inventory/Stock (1300) = GR Amount
    └─ CR: Accounts Payable (2000) = GR Amount

Vendor Payment Made
    ↓
create_po_payment_gl_entries(payment)
    ├─ DR: Accounts Payable (2000) = Payment Amount
    └─ CR: Cash/Bank (1000) = Payment Amount
```

**GL Posting Code:**
```python
# Location: procurement/gl_integration.py:52+
def create_po_gl_entries(purchase_order):
    # DR: Inventory account (ASSET)
    # CR: Accounts Payable (LIABILITY)
    # Reference: PO-{id}
```

**Reflection in Reports:**

| Report | Account | Line Item | Amount Source |
|--------|---------|-----------|---------------|
| **P&L** | Purchase Expense (5000) | Purchases | Non-inventory purchases |
| **Trial Balance** | Inventory (1300) | Asset | Goods received (DEBIT) |
| **Trial Balance** | Accounts Payable (2000) | Liability | Unpaid vendors (CREDIT) |
| **Trading & Manufacturing** | Purchases | Raw Materials | Purchase account debits |
| **Trading & Manufacturing** | Purchase Returns | Returns | Purchase return credits |

**Verification Query:**
```python
# Check if procurement posts to GL
from accounting.models import LedgerEntry
po_entries = LedgerEntry.objects.filter(
    reference_number__startswith='PO-'
)
```

---

### 4. ✅ EXPENSES MODULE → Accounting

**Integration File:** `TradifyERP/expenses/models.py` (post_to_gl method)

**Key Models:**
- `EmployeeExpense` (expenses/models.py)
- `EmployeeExpenseReport` (expenses/models.py)
- `ExpenseCategory` (expenses/models.py)

**Transaction Flow:**

```
Expense Approved (Status: APPROVED)
    ↓
EmployeeExpense.post_to_gl()
    ├─ DR: Expense Account (6000-6999) = Expense Amount
    │      (from ExpenseCategory.expense_account)
    └─ CR: Accounts Payable - Employee (2100) = Expense Amount

Reimbursement Paid
    ↓
Manual Entry:
    ├─ DR: Accounts Payable - Employee (2100) = Amount
    └─ CR: Cash/Bank (1000) = Amount
```

**GL Posting Code:**
```python
# Location: expenses/models.py:359+
def post_to_gl(self):
    # DEBIT: category.expense_account (EXPENSE)
    # CREDIT: AP - Employee Expenses (LIABILITY)
    # Reference: EXP-{report_id}-{item_id}
```

**Reflection in Reports:**

| Report | Account | Line Item | Amount Source |
|--------|---------|-----------|---------------|
| **P&L** | Travel Expense (6100) | Expenses | Category-specific expenses |
| **P&L** | Meals Expense (6200) | Expenses | Category-specific expenses |
| **Trial Balance** | AP - Employee (2100) | Liability | Unpaid reimbursements (CREDIT) |

**Verification Query:**
```python
# Check if expenses post to GL
from accounting.models import LedgerEntry
expense_entries = LedgerEntry.objects.filter(
    reference_number__startswith='EXP-'
)
```

---

### 5. ✅ HR MODULE → Accounting

**Integration File:** `TradifyERP/hr/views.py` (payroll_post_to_gl)

**Key Models:**
- `Payroll` (hr/models.py)
- `PayrollRecord` (hr/models.py)
- `Position` (hr/models.py)
- `LedgerEntry` (accounting/models.py)

**Transaction Flow:**

```
Payroll Approved (Status: APPROVED)
    ↓
payroll_post_to_gl(payroll)
    ├─ DR: Salary Expense (6000) = Total Gross
    │      (from Position.salary_expense_account)
    └─ CR: Salary Payable (2100) = Total Net
           (calculated automatically)

Payroll Paid
    ↓
Manual Entry:
    ├─ DR: Salary Payable (2100) = Net Amount
    └─ CR: Cash/Bank (1000) = Net Amount
```

**GL Posting Code:**
```python
# Location: hr/views.py (PayrollPostToGLView)
# For each PayrollRecord:
#   DEBIT: Position.salary_expense_account
#   CREDIT: Salary Payable account
#   Reference: PAY-{payroll_number}
```

**Reflection in Reports:**

| Report | Account | Line Item | Amount Source |
|--------|---------|-----------|---------------|
| **P&L** | Salary Expense (6000) | Operating Expenses | Payroll records |
| **P&L** | Benefits Expense (6050) | Operating Expenses | Employee benefits |
| **Trial Balance** | Salary Payable (2100) | Liability | Unpaid salaries (CREDIT) |

**Verification Query:**
```python
# Check if payroll posts to GL
from accounting.models import LedgerEntry
payroll_entries = LedgerEntry.objects.filter(
    reference_number__startswith='PAY-'
)
```

---

### 6. ⚠️ MAINTENANCE MODULE → Accounting

**Status:** NO DIRECT GL INTEGRATION CURRENTLY IMPLEMENTED

**Key Models:**
- `WorkOrder` (maintenance/models.py)
- `MaintenanceCost` (maintenance/models.py)
- `MaintenanceAsset` (maintenance/models.py)

**Current Situation:**
- Maintenance costs are tracked in `MaintenanceCost` model
- NO automatic GL posting when work orders are completed
- NO LedgerEntry creation
- Costs NOT appearing in Trial Balance or P&L automatically

**Recommended Integration:**

```python
# Proposed: maintenance/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounting.models import LedgerEntry, Account

@receiver(post_save, sender=WorkOrder)
def post_maintenance_to_gl(sender, instance, created, **kwargs):
    if instance.status == 'COMPLETED' and not instance.is_posted_to_gl:
        # Get maintenance expense account
        expense_account = Account.objects.get(
            entity=instance.entity,
            account_type='EXPENSE',
            name__icontains='Maintenance'
        )
        
        # Get AP or Cash account
        ap_account = Account.objects.get(
            entity=instance.entity,
            account_type='LIABILITY',
            name__icontains='Accounts Payable'
        )
        
        # Calculate total cost
        total_cost = instance.costs.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # DR: Maintenance Expense
        LedgerEntry.objects.create(
            account=expense_account,
            entity=instance.entity,
            entry_date=instance.completion_date,
            entry_type='DEBIT',
            amount=total_cost,
            description=f"Maintenance - {instance.work_order_number}",
            reference_number=f"WO-{instance.id}",
            is_posted=True
        )
        
        # CR: Accounts Payable or Cash
        LedgerEntry.objects.create(
            account=ap_account,
            entity=instance.entity,
            entry_date=instance.completion_date,
            entry_type='CREDIT',
            amount=total_cost,
            description=f"AP - Maintenance {instance.work_order_number}",
            reference_number=f"WO-{instance.id}",
            is_posted=True
        )
        
        instance.is_posted_to_gl = True
        instance.save()
```

**After Implementation Would Reflect:**

| Report | Account | Line Item | Amount Source |
|--------|---------|-----------|---------------|
| **P&L** | Maintenance Expense (6300) | Operating Expenses | Work order costs |
| **Trial Balance** | Maintenance Expense (6300) | Expense | Total maintenance (DEBIT) |
| **Trial Balance** | AP - Maintenance (2000) | Liability | Unpaid maintenance (CREDIT) |

---

## 📈 How Reports Pull Data

### Trial Balance
**Logic:** Aggregates all `LedgerEntry` records by `Account`

```python
# Location: accounting/trading_manufacturing.py or similar
accounts = Account.objects.filter(entity=entity, is_active=True)
for account in accounts:
    debits = LedgerEntry.objects.filter(
        account=account,
        entry_type='DEBIT',
        entry_date__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=account,
        entry_type='CREDIT',
        entry_date__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    balance = debits - credits  # Asset/Expense accounts
    # or credits - debits for Liability/Income/Equity accounts
```

**Data Source:** `accounting.models.LedgerEntry`

---

### Profit & Loss
**Logic:** Filters `LedgerEntry` by account types INCOME and EXPENSE

```python
# Location: accounting/profit_loss.py or views_profit_loss.py
income_accounts = Account.objects.filter(
    entity=entity,
    account_type='INCOME',
    is_active=True
)

expense_accounts = Account.objects.filter(
    entity=entity,
    account_type='EXPENSE',
    is_active=True
)

# Calculate total income
total_income = LedgerEntry.objects.filter(
    account__in=income_accounts,
    entry_date__range=[start_date, end_date],
    entry_type='CREDIT'
).aggregate(Sum('amount'))['amount__sum'] or 0

# Calculate total expenses
total_expenses = LedgerEntry.objects.filter(
    account__in=expense_accounts,
    entry_date__range=[start_date, end_date],
    entry_type='DEBIT'
).aggregate(Sum('amount'))['amount__sum'] or 0

net_profit = total_income - total_expenses
```

**Data Source:** `accounting.models.LedgerEntry` filtered by `account.account_type`

---

### Trading & Manufacturing Account
**Logic:** Further filters by account names/categories

```python
# Location: accounting/trading_manufacturing.py

# Sales Revenue (excludes returns)
sales_accounts = Account.objects.filter(
    entity=entity,
    account_type='INCOME',
    name__icontains='Sales'
).exclude(name__icontains='return')

total_sales = LedgerEntry.objects.filter(
    account__in=sales_accounts,
    entry_type='CREDIT',
    entry_date__range=[start_date, end_date]
).aggregate(Sum('amount'))['amount__sum'] or 0

# Sales Returns
sales_return_accounts = Account.objects.filter(
    entity=entity,
    account_type='INCOME',
    name__icontains='Sales',
    name__icontains='return'
)

sales_returns = LedgerEntry.objects.filter(
    account__in=sales_return_accounts,
    entry_type='CREDIT',
    entry_date__range=[start_date, end_date]
).aggregate(Sum('amount'))['amount__sum'] or 0

# Purchases (excludes returns)
purchase_accounts = Account.objects.filter(
    entity=entity,
    account_type='EXPENSE',
    name__icontains='Purchase'
).exclude(name__icontains='return')

total_purchases = LedgerEntry.objects.filter(
    account__in=purchase_accounts,
    entry_type='DEBIT',
    entry_date__range=[start_date, end_date]
).aggregate(Sum('amount'))['amount__sum'] or 0

# Purchase Returns
purchase_return_accounts = Account.objects.filter(
    entity=entity,
    account_type='EXPENSE',
    name__icontains='Purchase',
    name__icontains='return'
)

purchase_returns = LedgerEntry.objects.filter(
    account__in=purchase_return_accounts,
    entry_type='DEBIT',
    entry_date__range=[start_date, end_date]
).aggregate(Sum('amount'))['amount__sum'] or 0

# Net calculations
net_sales = total_sales - sales_returns
net_purchases = total_purchases - purchase_returns
gross_profit = net_sales - net_purchases
```

**Data Source:** `accounting.models.LedgerEntry` filtered by `account.name` patterns

---

## 🔍 Integration Verification Checklist

### For Each Module, Verify:

#### ✅ Sales Module
- [x] Invoice creation triggers GL posting
- [x] `reference_number` starts with 'INV-'
- [x] AR account debited
- [x] Revenue account credited
- [x] Tax account credited
- [x] Appears in P&L under Revenue
- [x] Appears in Trial Balance

**Test:**
```python
from sales.models import Invoice
from accounting.models import LedgerEntry

invoice = Invoice.objects.first()
entries = LedgerEntry.objects.filter(reference_number=f'INV-{invoice.id}')
print(f"Found {entries.count()} entries")  # Should be 2-3
```

#### ✅ Manufacturing Module
- [x] Production completion triggers GL posting
- [x] `reference` starts with 'MFG-'
- [x] Finished Goods debited
- [x] WIP credited
- [x] Costs appear in COGS (when sold)

**Test:**
```python
from manufacturing.models import ProductionOrder
from accounting.models import JournalEntry

po = ProductionOrder.objects.filter(status='COMPLETE').first()
entry = JournalEntry.objects.filter(reference=f'MFG-{po.po_number}').first()
print(f"Journal Entry: {entry}")  # Should exist
```

#### ✅ Procurement Module
- [x] Goods receipt triggers GL posting
- [x] `reference_number` starts with 'GR-' or 'PO-'
- [x] Inventory debited
- [x] AP credited
- [x] Appears in Trial Balance

**Test:**
```python
from procurement.models import GoodsReceipt
from accounting.models import LedgerEntry

gr = GoodsReceipt.objects.first()
entries = LedgerEntry.objects.filter(reference_number__startswith='GR-')
print(f"Found {entries.count()} entries")
```

#### ✅ Expenses Module
- [x] Expense approval triggers GL posting
- [x] `reference_number` starts with 'EXP-'
- [x] Expense account debited
- [x] AP - Employee credited
- [x] Appears in P&L under Expenses

**Test:**
```python
from expenses.models import EmployeeExpense
from accounting.models import LedgerEntry

expense = EmployeeExpense.objects.filter(is_posted=True).first()
entries = LedgerEntry.objects.filter(reference_number__startswith='EXP-')
print(f"Found {entries.count()} entries")
```

#### ✅ HR Module
- [x] Payroll approval can be posted to GL
- [x] `reference_number` starts with 'PAY-'
- [x] Salary Expense debited
- [x] Salary Payable credited
- [x] Appears in P&L under Operating Expenses

**Test:**
```python
from hr.models import Payroll
from accounting.models import LedgerEntry

payroll = Payroll.objects.filter(is_posted=True).first()
if payroll:
    entries = LedgerEntry.objects.filter(reference_number__startswith='PAY-')
    print(f"Found {entries.count()} entries")
```

#### ⚠️ Maintenance Module
- [ ] Work order completion does NOT trigger GL posting
- [ ] NO automatic LedgerEntry creation
- [ ] Costs NOT in P&L automatically
- **ACTION REQUIRED:** Implement GL integration

---

## 🛠️ Required GL Account Setup

For modules to post correctly, these accounts MUST exist:

### Assets (1000-1999)
- 1000: Cash/Bank
- 1200: Accounts Receivable
- 1300: Inventory/Stock/Finished Goods
- 1400: Work-in-Process

### Liabilities (2000-2999)
- 2000: Accounts Payable
- 2100: Accounts Payable - Employee Expenses
- 2110: Sales Tax Payable
- 2200: Salary Payable

### Income (4000-4999)
- 4100: Sales Revenue
- 4200: Sales Returns (negative income)
- 4300: Other Income

### Expenses (5000-6999)
- 5000: Cost of Goods Sold
- 5100: Purchase Expense
- 5200: Purchase Returns (negative expense)
- 6000: Salary Expense
- 6100: Travel Expense
- 6200: Meals Expense
- 6300: Maintenance Expense
- 6400: Other Operating Expenses

---

## 📋 Summary Table: Module Integration Status

| Module | Integration Status | GL Posting Method | Reference Prefix | Appears in P&L | Appears in TB | Appears in T&M |
|--------|-------------------|-------------------|------------------|----------------|---------------|----------------|
| **Sales** | ✅ Full | `sales/integration.py` | INV- | ✅ Revenue | ✅ AR/Revenue | ✅ Sales |
| **Manufacturing** | ✅ Full | `manufacturing/signals.py` | MFG- | ✅ COGS | ✅ Inventory | ✅ Manufacturing |
| **Procurement** | ✅ Full | `procurement/gl_integration.py` | PO-, GR- | ✅ Purchases | ✅ Inventory/AP | ✅ Purchases |
| **Expenses** | ✅ Full | `expenses/models.py` | EXP- | ✅ Expenses | ✅ AP/Expense | ❌ N/A |
| **HR** | ✅ Full | `hr/views.py` | PAY- | ✅ Salary Exp | ✅ Payable/Exp | ❌ N/A |
| **Maintenance** | ❌ Missing | None | N/A | ❌ No | ❌ No | ❌ No |

---

## 🎯 Action Items to Complete Integration

### 1. Implement Maintenance GL Integration
**File to create:** `TradifyERP/maintenance/signals.py`

**What it should do:**
- Listen for WorkOrder status change to 'COMPLETED'
- Sum all MaintenanceCost records for that work order
- Create debit to Maintenance Expense account (6300)
- Create credit to Accounts Payable or Cash account
- Set reference as 'WO-{work_order.id}'

### 2. Add Missing GL Accounts
Run this command or add via admin:
```bash
python manage.py shell
```

```python
from accounting.models import Account, Entity

entity = Entity.objects.first()

# Maintenance Expense
Account.objects.get_or_create(
    entity=entity,
    account_number='6300',
    defaults={
        'name': 'Maintenance Expense',
        'account_type': 'EXPENSE',
        'is_active': True,
        'currency': entity.company_currency
    }
)
```

### 3. Verify All Module Integrations
Run verification queries for each module to ensure transactions are posting.

---

## 📞 Support & Documentation

**For issues:**
1. Check `LedgerEntry` table for missing transactions
2. Verify GL accounts exist for each module
3. Check reference_number patterns
4. Review module integration files
5. Test with small transactions first

**Key Documentation Files:**
- `SALES_ACCOUNTS_INTEGRATION.md`
- `manufacturing/DOCUMENTATION.md`
- `procurement/README.md` (if exists)
- `expenses/README.md` (if exists)
- `hr/README.md`

---

**Generated:** December 19, 2024  
**System:** TradifyERP Production Analysis  
**Purpose:** Module-to-Accounting Integration Reference
