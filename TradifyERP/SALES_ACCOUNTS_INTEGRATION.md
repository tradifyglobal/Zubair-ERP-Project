# Sales-Accounts Integration Implementation Guide

**Version:** 1.0  
**Date:** December 6, 2025  
**Status:** ✅ Implementation Complete  
**Module:** Sales & Accounts Integration

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Key Linkages](#key-linkages)
4. [Data Models](#data-models)
5. [Integration Workflows](#integration-workflows)
6. [Account Mappings](#account-mappings)
7. [Integration Functions](#integration-functions)
8. [Usage Examples](#usage-examples)
9. [Reports & Analytics](#reports--analytics)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Sales-Accounts Integration establishes real-time financial visibility across sales activities and the general ledger, ensuring:

- ✅ **Automatic GL Posting**: Sales orders → Invoices → GL entries
- ✅ **Real-time Receivables Tracking**: AR aging, collection forecasting
- ✅ **Payment Reconciliation**: Automatic cash/bank account updates
- ✅ **Tax Compliance**: Automatic tax liability postings
- ✅ **Financial Reporting**: Consolidated revenue and profitability metrics
- ✅ **Adjustment Handling**: Discounts, returns, and write-offs posted to GL

---

## Architecture

### Integration Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    SALES MODULE                             │
├─────────────────────────────────────────────────────────────┤
│  • Quotations    • Pricing Rules    • Customer Segments     │
│  • Sales Orders  • Discounts        • Adjustments           │
│  • Invoices      • Payments         • Financial Reports     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─→ GL Posting Manager
                     ├─→ AR Manager
                     ├─→ Payment Processor
                     ├─→ Adjustment Processor
                     └─→ Report Generator
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  ACCOUNTS MODULE                            │
├─────────────────────────────────────────────────────────────┤
│  • Chart of Accounts        • General Ledger Entries       │
│  • GL Postings              • Trial Balance                │
│  • Tax Transactions         • Financial Reports            │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

| Component | From Sales | To Accounts | Trigger |
|-----------|-----------|------------|---------|
| **Revenue** | Invoice | GL (Debit: AR, Credit: Revenue) | Invoice status → ISSUED |
| **Tax** | Invoice | GL (Debit: AR, Credit: Tax Payable) | Invoice status → ISSUED |
| **Payment** | SalesPayment | GL (Debit: Cash, Credit: AR) | Payment recorded |
| **Adjustments** | SalesAdjustment | GL (various accounts) | Adjustment approved |
| **Report** | SalesFinancialReport | GL Report linking | Report generated |

---

## Key Linkages

### 1. Sales Order → Invoice → GL Entry

**Workflow:**
```
SalesOrder (CONFIRMED)
    ↓
Invoice (DRAFT)
    ├─ Issue Invoice
    ├─ Status: ISSUED
    ├─ create_ar_from_invoice()
    ├─ post_invoice_revenue_to_gl()
    └─ post_invoice_tax_to_gl()
    ↓
GL Entries (AUTHORIZED)
    ├─ DR: AR / CR: Revenue (INCOME account)
    ├─ DR: AR / CR: Tax Payable (LIABILITY account)
    └─ AccountsReceivable record (OUTSTANDING)
```

**GL Accounts Involved:**
- **1200 Series**: Accounts Receivable (ASSET)
- **2100 Series**: Tax Payable (LIABILITY)
- **4000 Series**: Revenue/Sales Income (INCOME)

---

### 2. Customer Payment → Cash Account Update → AR Settlement

**Workflow:**
```
Customer Payment Received
    ↓
process_payment()
    ├─ Create SalesPayment record
    ├─ Post cash receipt to GL
    ├─ Update AR record
    ├─ Update Invoice (amount_paid)
    └─ Reconcile payment
    ↓
GL Entries (AUTHORIZED)
    ├─ DR: Cash / CR: AR
    └─ AR Status: PARTIAL → PAID
    ↓
Bank Account Updated
    └─ Cash balance increases
```

**GL Accounts Involved:**
- **1000 Series**: Cash/Bank Accounts (ASSET)
- **1200 Series**: Accounts Receivable (ASSET)

---

### 3. Adjustments → GL Postings

**Adjustment Types & GL Impact:**

| Adjustment Type | GL Debit | GL Credit | AR Impact |
|----------------|----------|-----------|-----------|
| **DISCOUNT** | Discount Expense | AR | Reduces AR |
| **RETURN** | Sales Return | AR | Reduces AR |
| **CREDIT_NOTE** | Sales Return | AR | Reduces AR |
| **WRITE_OFF** | Bad Debt Expense | AR | Clears AR |
| **PRICE_CORRECTION** | Price Adj. | AR | Increases/Decreases AR |

**Workflow:**
```
SalesAdjustment (DRAFT)
    ├─ Await approval (if required)
    ├─ Status: APPROVED
    ├─ post_adjustment_to_gl()
    └─ Status: POSTED
    ↓
GL Entry + AR Update
    ├─ Invoice amount reduced
    ├─ AR amount reduced
    └─ Customer balance adjusted
```

---

### 4. Tax Flow

**Tax Posting Workflow:**
```
Invoice Created (subtotal: 100, tax_rate: 10%)
    ├─ tax_amount = 100 × 0.10 = 10
    ├─ total_amount = 100 + 10 = 110
    ↓
Invoice ISSUED
    ├─ Create GL entry: DR: AR, CR: Tax Payable (10)
    ├─ Create TaxTransaction record
    └─ Tax liability tracked
    ↓
Tax Payment Made
    └─ GL: DR: Tax Payable, CR: Cash
```

---

### 5. Financial Visibility

**Real-time Metrics Available:**

1. **Revenue Dashboard**
   - Gross revenue (all invoices)
   - Net revenue (after discounts/returns)
   - Tax collected

2. **AR Dashboard**
   - Outstanding balance
   - Aging buckets (Current, 30-60, 60-90, 90+)
   - Overdue amounts
   - Collection forecast

3. **Profitability**
   - Gross profit (revenue - COGS)
   - Net margin
   - Trend analysis

4. **Customer Metrics**
   - Active customers count
   - New customers (period)
   - Repeat customers

---

## Data Models

### 1. AccountsReceivable

Tracks outstanding customer receivables linked to invoices.

**Fields:**
- `invoice` (FK): Link to Invoice
- `customer` (FK): Customer reference
- `invoice_amount`: Total invoice amount
- `amount_received`: Cumulative payments
- `amount_outstanding`: Remaining balance
- `status`: OUTSTANDING / PARTIAL / PAID / OVERDUE / WRITTEN_OFF / DISPUTED
- `aging_bucket`: CURRENT / 30_60 / 60_90 / OVER_90
- `invoice_date`, `due_date`, `last_payment_date`: Date tracking
- `ar_gl_posting_id` (FK): Link to GL entry for revenue

**Key Methods:**
```python
ar_record.update_aging_bucket()      # Update aging based on due date
ar_record.calculate_days_overdue()    # Days past due date
```

---

### 2. GeneralLedgerPosting

Tracks all GL postings generated from sales transactions.

**Fields:**
- `invoice` (FK): Source invoice
- `sales_order` (FK): Source sales order
- `posting_type`: REVENUE / TAX / DISCOUNT / RETURN / WRITE_OFF
- `debit_account`, `credit_account`: GL accounts
- `debit_amount`, `credit_amount`: Amounts
- `gl_ledger_entry` (FK): Link to actual LedgerEntry
- `status`: PENDING / POSTED / REVERSED / FAILED
- `posted_at`: Timestamp

**Posting Types:**
- **REVENUE**: Invoice revenue recognition
- **TAX**: Sales tax liability
- **DISCOUNT**: Additional discounts applied
- **RETURN**: Sales returns
- **WRITE_OFF**: Bad debt write-offs

---

### 3. SalesPayment

Records customer payments against invoices.

**Fields:**
- `invoice` (FK): Invoice being paid
- `customer` (FK): Customer making payment
- `payment_date`: Date received
- `amount`: Payment amount (with validation: > 0)
- `payment_method`: CASH / CHECK / BANK_TRANSFER / CREDIT_CARD / ONLINE / OTHER
- `reference_number`: Check #, transaction ID, etc.
- `cash_gl_posting_id` (FK): Link to GL entry for cash receipt
- `status`: PENDING / RECONCILED / BOUNCED / REVERSED

**Usage:**
```python
from sales.integration import PaymentProcessor

payment = PaymentProcessor.process_payment(
    invoice=invoice,
    amount=Decimal('1000.00'),
    payment_date=timezone.now().date(),
    payment_method='BANK_TRANSFER',
    reference_number='TRANS-123456',
    user=request.user
)
```

---

### 4. SalesAdjustment

Tracks sales adjustments with optional approval workflow.

**Fields:**
- `invoice` (FK): Related invoice
- `adjustment_type`: DISCOUNT / RETURN / WRITE_OFF / CREDIT_NOTE / PRICE_CORRECTION
- `adjustment_date`: Date of adjustment
- `amount`: Adjustment amount (with validation: > 0)
- `reason`: Business reason
- `adjustment_gl_posting_id` (FK): Link to GL entry
- `status`: DRAFT / APPROVED / POSTED / REVERSED
- `requires_approval`: Boolean flag
- `approved_by`, `approved_at`: Approval tracking

**Usage:**
```python
from sales.integration import AdjustmentProcessor

adjustment = SalesAdjustment.objects.create(
    entity=entity,
    invoice=invoice,
    adjustment_type='DISCOUNT',
    adjustment_date=timezone.now().date(),
    amount=Decimal('50.00'),
    reason='Customer retention discount',
    status='DRAFT',
    requires_approval=True
)

# After approval...
AdjustmentProcessor.post_adjustment_to_gl(adjustment)
```

---

### 5. SalesFinancialReport

Consolidated sales financial metrics linked to accounting.

**Fields:**
- `report_type`: DAILY / WEEKLY / MONTHLY / QUARTERLY / ANNUAL
- `period_start`, `period_end`: Reporting period
- `gross_revenue`: Total invoice amounts
- `total_discounts`: All discounts in period
- `total_returns`: All returns in period
- `net_revenue`: Gross - discounts - returns
- `total_tax_collected`: Tax amounts
- `total_invoiced`: All invoices issued
- `total_received`: All payments received
- `total_outstanding`: Unpaid amounts
- `overdue_amount`: Past due amounts
- `total_cost_of_goods`: COGS (from manufacturing)
- `gross_profit`: Net revenue - COGS
- `gross_profit_margin`: Percentage
- `total_active_customers`: Count
- `new_customers`: Count in period
- `repeat_customers`: Count
- `is_posted_to_gl`: Reconciliation flag
- `gl_report_id`: GL report reference

---

## Integration Workflows

### Workflow 1: Complete Invoice-to-Payment Cycle

```
1. CREATE QUOTATION
   ├─ Quotation (DRAFT)
   └─ Customer agrees → Status: ACCEPTED

2. CREATE SALES ORDER
   ├─ SO created from quotation
   └─ SO status: CONFIRMED

3. GENERATE INVOICE
   ├─ Invoice (DRAFT) from SO
   ├─ Subtotal: 10,000
   ├─ Tax (10%): 1,000
   ├─ Total: 11,000
   └─ Status: ISSUED
   
4. POST TO GL
   ├─ GL Entry 1: DR: AR (11,000), CR: Revenue (10,000)
   ├─ GL Entry 2: DR: AR (1,000), CR: Tax Payable (1,000)
   ├─ Create AR record: Outstanding = 11,000
   ├─ Invoice.gl_posting_id = LedgerEntry_1
   ├─ Invoice.tax_gl_posting_id = LedgerEntry_2
   └─ Invoice.is_posted_to_gl = True

5. CUSTOMER PAYS 5,000 (partial)
   ├─ Create SalesPayment (5,000)
   ├─ GL Entry: DR: Cash (5,000), CR: AR (5,000)
   ├─ Update AR: received = 5,000, outstanding = 6,000
   ├─ Update Invoice: amount_paid = 5,000, status = PARTIAL
   └─ Mark payment RECONCILED

6. CUSTOMER PAYS REMAINDER 6,000
   ├─ Create SalesPayment (6,000)
   ├─ GL Entry: DR: Cash (6,000), CR: AR (6,000)
   ├─ Update AR: received = 11,000, outstanding = 0
   ├─ Update Invoice: amount_paid = 11,000, status = PAID
   └─ AR status: PAID

7. RECONCILIATION
   ├─ Invoice total_amount = 11,000
   ├─ Invoice amount_paid = 11,000
   ├─ Match complete ✓
```

---

### Workflow 2: Sales Adjustment (Early Payment Discount)

```
1. CUSTOMER PAYS EARLY
   ├─ Amount: 10,500 (for 11,000 invoice)
   ├─ Early payment discount: 500
   └─ Request: "Early payment discount"

2. CREATE ADJUSTMENT
   ├─ SalesAdjustment (DRAFT)
   ├─ Type: DISCOUNT
   ├─ Amount: 500
   ├─ Status: DRAFT
   └─ Requires_approval: True (configurable)

3. APPROVAL WORKFLOW
   ├─ Manager reviews
   ├─ Status: APPROVED
   └─ Approved_by: Manager user

4. POST TO GL
   ├─ GL Entry: DR: Discount Expense (500), CR: AR (500)
   ├─ Invoice.total_amount: 11,000 → 10,500
   ├─ AR.amount_outstanding: 11,000 → 10,500
   └─ Adjustment.status: POSTED

5. RECORD PAYMENT
   ├─ SalesPayment (10,500)
   ├─ GL Entry: DR: Cash (10,500), CR: AR (10,500)
   ├─ AR.amount_received: 10,500
   ├─ AR.amount_outstanding: 0
   ├─ Invoice.status: PAID
   └─ Payment.status: RECONCILED
```

---

### Workflow 3: Sales Return (Full)

```
1. CUSTOMER RETURNS ALL GOODS
   ├─ Original invoice: 11,000 (10,000 + 1,000 tax)
   └─ Return date: Today

2. CREATE ADJUSTMENT
   ├─ SalesAdjustment (DRAFT)
   ├─ Type: RETURN (or CREDIT_NOTE)
   ├─ Amount: 11,000
   ├─ Status: DRAFT
   └─ Reason: "Full product return - defective"

3. APPROVAL
   ├─ Manager approves
   └─ Status: APPROVED

4. POST TO GL
   ├─ GL Entry: DR: Sales Return (11,000), CR: AR (11,000)
   ├─ Invoice.total_amount: 11,000 → 0
   ├─ AR.amount_outstanding: 11,000 → 0
   ├─ AR.status: PAID (credit note issued)
   └─ Adjustment.status: POSTED

5. RESOLUTION
   ├─ Payment: 0 (credit applied)
   └─ Account reconciled
```

---

### Workflow 4: Bad Debt Write-off

```
1. CUSTOMER UNABLE TO PAY
   ├─ Invoice: 5,000 (100 days overdue)
   ├─ No further recovery expected
   └─ Decision: Write off

2. CREATE ADJUSTMENT
   ├─ SalesAdjustment (DRAFT)
   ├─ Type: WRITE_OFF
   ├─ Amount: 5,000
   ├─ Reason: "Uncollectible - company liquidated"
   └─ Requires_approval: True (mandatory for write-offs)

3. APPROVAL CHAIN
   ├─ Finance manager reviews
   ├─ Director approves
   └─ Status: APPROVED

4. POST TO GL
   ├─ GL Entry: DR: Bad Debt Expense (5,000), CR: AR (5,000)
   ├─ AR.amount_outstanding: 5,000 → 0
   ├─ AR.status: WRITTEN_OFF
   ├─ Invoice.status: Unchanged (for audit trail)
   └─ Adjustment.status: POSTED

5. ACCOUNTING IMPACT
   ├─ Income statement: Bad Debt Expense increases
   ├─ Balance sheet: AR decreases
   └─ Allowance for Doubtful Accounts: May be used (separate process)
```

---

## Account Mappings

### Standard Chart of Accounts Setup

**Asset Accounts (1000 Series)**
```
1000-1099: Cash & Bank Accounts
  ├─ 1010: Cash on Hand
  ├─ 1020: Bank Account - Primary
  ├─ 1030: Bank Account - Secondary
  └─ 1050: Petty Cash

1100-1199: Other Current Assets
  ├─ 1100: Short-term Investments
  └─ 1150: Prepaid Expenses

1200-1299: Accounts Receivable
  ├─ 1200: Accounts Receivable (Control)
  ├─ 1210: AR - Domestic
  ├─ 1220: AR - Export
  ├─ 1290: Allowance for Doubtful Accounts (Contra)
```

**Liability Accounts (2000 Series)**
```
2000-2099: Current Liabilities
  ├─ 2000: Accounts Payable (Control)
  ├─ 2100: Sales Tax Payable
  ├─ 2110: VAT Payable
  ├─ 2120: Income Tax Payable
  ├─ 2200: Short-term Notes Payable
  └─ 2300: Current Portion - Long-term Debt

2100-2199: Tax Accounts
  ├─ 2110: GST Payable
  ├─ 2111: GST Recoverable (Contra)
  ├─ 2120: Sales Tax Payable
  └─ 2130: Withholding Tax Payable
```

**Income Accounts (4000 Series)**
```
4000-4099: Sales Revenue
  ├─ 4000: Sales - Domestic
  ├─ 4010: Sales - Export
  ├─ 4050: Service Revenue
  └─ 4090: Other Revenue

4100-4199: Sales Adjustments
  ├─ 4100: Sales Discounts
  ├─ 4110: Sales Returns
  ├─ 4120: Sales Allowances
  └─ 4200: Cost of Goods Sold (COGS)
```

**Expense Accounts (5000 Series)**
```
5000-5099: Sales-Related Expenses
  ├─ 5010: Sales Commission
  ├─ 5020: Freight & Shipping
  ├─ 5030: Bad Debt Expense
  └─ 5040: Warranty Expense

5100-5199: Administrative Expenses
  ├─ 5100: Office Salaries
  ├─ 5110: Office Rent
  ├─ 5120: Utilities
  └─ 5200: Depreciation
```

### Configuring Accounts in Integration

```python
# In your accounting module setup:

SALES_GL_ACCOUNTS = {
    'AR': '1200',              # Accounts Receivable
    'CASH': '1010',            # Cash on Hand
    'BANK': '1020',            # Bank Account
    'REVENUE': '4000',         # Sales Revenue
    'TAX_PAYABLE': '2110',     # Tax Payable
    'SALES_DISCOUNT': '4100',  # Sales Discounts
    'SALES_RETURN': '4110',    # Sales Returns
    'BAD_DEBT': '5030',        # Bad Debt Expense
    'EARLY_PAY_DISCOUNT': '4120',  # Early Payment Discounts
}

# Map by entity for multi-company support
def get_gl_account(entity, account_type):
    mapping = entity.entity_chart_of_accounts.get(account_type)
    return Account.objects.get(account_number=mapping)
```

---

## Integration Functions

### GLPostingManager

**Class:** `sales.integration.GLPostingManager`

#### post_invoice_revenue_to_gl(invoice)

Posts invoice revenue to GL when invoice is issued.

**Parameters:**
- `invoice`: Invoice object (must be status='ISSUED')

**GL Entries Created:**
1. DR: Accounts Receivable
2. CR: Revenue (Income)

**Returns:** GeneralLedgerPosting object

**Example:**
```python
from sales.integration import GLPostingManager
from sales.models import Invoice

invoice = Invoice.objects.get(invoice_number='INV-001')
invoice.status = 'ISSUED'
invoice.save()

gl_posting = GLPostingManager.post_invoice_revenue_to_gl(invoice)
# GL Entry created with:
# - invoice.gl_posting_id = gl_posting.gl_ledger_entry
# - invoice.is_posted_to_gl = True
# - invoice.gl_posted_at = now()
```

#### post_invoice_tax_to_gl(invoice)

Posts invoice tax liability to GL.

**Parameters:**
- `invoice`: Invoice object (must have tax_amount > 0)

**GL Entries Created:**
1. DR: Accounts Receivable
2. CR: Tax Payable (Liability)

**Returns:** GeneralLedgerPosting object or None

**Example:**
```python
gl_tax_posting = GLPostingManager.post_invoice_tax_to_gl(invoice)
if gl_tax_posting:
    print(f"Tax posted: {gl_tax_posting.credit_amount}")
```

---

### AccountsReceivableManager

**Class:** `sales.integration.AccountsReceivableManager`

#### create_ar_from_invoice(invoice)

Creates AR record when invoice is issued.

**Parameters:**
- `invoice`: Invoice object (must be status='ISSUED')

**AR Record:**
- Status: OUTSTANDING
- Amount Outstanding: Invoice total_amount
- Aging Bucket: CURRENT

**Returns:** AccountsReceivable object

**Example:**
```python
from sales.integration import AccountsReceivableManager

ar_record = AccountsReceivableManager.create_ar_from_invoice(invoice)
# AR created with:
# - status: OUTSTANDING
# - amount_outstanding: invoice.total_amount
# - amount_received: 0
```

#### get_ar_aging_summary(entity, as_of_date=None)

Returns AR aging summary by bucket.

**Parameters:**
- `entity`: Entity object
- `as_of_date`: Optional date (default: today)

**Returns:** Dictionary with aging buckets

**Example:**
```python
aging = AccountsReceivableManager.get_ar_aging_summary(entity)
print(f"Current: {aging['current']['amount']}")
print(f"30-60 days: {aging['30_60']['amount']}")
print(f"60-90 days: {aging['60_90']['amount']}")
print(f"Over 90 days: {aging['over_90']['amount']}")

# Output:
# {
#     'current': {'count': 5, 'amount': Decimal('50000.00')},
#     '30_60': {'count': 2, 'amount': Decimal('10000.00')},
#     '60_90': {'count': 1, 'amount': Decimal('5000.00')},
#     'over_90': {'count': 1, 'amount': Decimal('2000.00')},
# }
```

#### get_collection_forecast(entity, days_ahead=30)

Returns expected collections for next N days.

**Parameters:**
- `entity`: Entity object
- `days_ahead`: Number of days to forecast (default: 30)

**Returns:** Dictionary with daily forecast

**Example:**
```python
forecast = AccountsReceivableManager.get_collection_forecast(entity, days_ahead=30)
# {
#     '2025-12-07': Decimal('5000.00'),
#     '2025-12-08': Decimal('0.00'),
#     '2025-12-09': Decimal('3000.00'),
#     ...
# }
```

---

### PaymentProcessor

**Class:** `sales.integration.PaymentProcessor`

#### process_payment(invoice, amount, payment_date, payment_method, reference_number, user)

Processes customer payment for invoice.

**Parameters:**
- `invoice`: Invoice object
- `amount`: Decimal payment amount (> 0)
- `payment_date`: Date of payment
- `payment_method`: One of CASH, CHECK, BANK_TRANSFER, CREDIT_CARD, ONLINE, OTHER
- `reference_number`: Check #, transaction ID, etc.
- `user`: User recording payment

**Operations:**
1. Create SalesPayment record
2. Post GL entries (Cash DR / AR CR)
3. Update AR record (received, outstanding, status)
4. Update Invoice (amount_paid, status)
5. Mark payment as RECONCILED

**Returns:** SalesPayment object

**Example:**
```python
from sales.integration import PaymentProcessor
from decimal import Decimal

payment = PaymentProcessor.process_payment(
    invoice=invoice,
    amount=Decimal('5000.00'),
    payment_date=timezone.now().date(),
    payment_method='BANK_TRANSFER',
    reference_number='TXN-2025-12345',
    user=request.user
)

# Updates:
# - SalesPayment created (status: RECONCILED)
# - GL entries posted
# - AR.amount_received: 5000
# - AR.amount_outstanding: 6000
# - Invoice.amount_paid: 5000
# - Invoice.status: PARTIAL
```

---

### AdjustmentProcessor

**Class:** `sales.integration.AdjustmentProcessor`

#### post_adjustment_to_gl(adjustment)

Posts sales adjustment to GL.

**Parameters:**
- `adjustment`: SalesAdjustment object (must be status='APPROVED')

**GL Entries Created (by type):**
- **DISCOUNT**: DR: Discount Expense / CR: AR
- **RETURN**: DR: Sales Return / CR: AR
- **WRITE_OFF**: DR: Bad Debt Expense / CR: AR

**Operations:**
1. Create GL entry
2. Update Invoice amounts
3. Update AR amounts
4. Mark adjustment POSTED

**Returns:** LedgerEntry object

**Example:**
```python
from sales.integration import AdjustmentProcessor

adjustment = SalesAdjustment.objects.get(pk=1)
adjustment.status = 'APPROVED'
adjustment.save()

ledger_entry = AdjustmentProcessor.post_adjustment_to_gl(adjustment)

# Updates:
# - GL entry created
# - Invoice.total_amount reduced
# - AR.amount_outstanding reduced
# - Adjustment.status: POSTED
```

---

### FinancialReportGenerator

**Class:** `sales.integration.FinancialReportGenerator`

#### generate_report(entity, report_type, period_start, period_end, user)

Generates consolidated sales financial report.

**Parameters:**
- `entity`: Entity object
- `report_type`: One of DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUAL
- `period_start`: Report period start date
- `period_end`: Report period end date
- `user`: User generating report

**Metrics Calculated:**
- Gross revenue, net revenue, discounts, returns
- Tax collected and payable
- AR totals, collections, overdue amounts
- Gross profit, profit margin
- Customer counts (active, new, repeat)

**Returns:** SalesFinancialReport object

**Example:**
```python
from sales.integration import FinancialReportGenerator
from datetime import date

report = FinancialReportGenerator.generate_report(
    entity=entity,
    report_type='MONTHLY',
    period_start=date(2025, 12, 1),
    period_end=date(2025, 12, 31),
    user=request.user
)

# Report contains:
print(f"Gross Revenue: {report.gross_revenue}")
print(f"Net Revenue: {report.net_revenue}")
print(f"Tax Collected: {report.total_tax_collected}")
print(f"Total Outstanding: {report.total_outstanding}")
print(f"Gross Profit: {report.gross_profit}")
print(f"Profit Margin: {report.gross_profit_margin}%")
```

---

## Usage Examples

### Example 1: Complete Invoice Workflow

```python
from sales.models import Invoice, Customer, SalesOrder
from sales.integration import (
    GLPostingManager,
    AccountsReceivableManager,
    PaymentProcessor,
    AdjustmentProcessor,
    FinancialReportGenerator
)
from decimal import Decimal
from django.utils import timezone

# Assume: SalesOrder already exists and is CONFIRMED

# 1. CREATE INVOICE FROM SALES ORDER
invoice = Invoice.objects.create(
    entity=entity,
    invoice_number='INV-2025-001',
    sales_order=sales_order,
    customer=customer,
    invoice_date=timezone.now().date(),
    due_date=timezone.now().date() + timedelta(days=30),
    subtotal=Decimal('10000.00'),
    tax_amount=Decimal('1000.00'),
    total_amount=Decimal('11000.00'),
    status='DRAFT',
    issued_by=request.user
)

# 2. ISSUE INVOICE (POST TO GL)
invoice.status = 'ISSUED'
invoice.save()

# Post revenue to GL
gl_posting_revenue = GLPostingManager.post_invoice_revenue_to_gl(invoice)
print(f"Revenue posted: {gl_posting_revenue.debit_amount}")

# Post tax to GL
gl_posting_tax = GLPostingManager.post_invoice_tax_to_gl(invoice)
print(f"Tax posted: {gl_posting_tax.debit_amount}")

# Create AR record
ar_record = AccountsReceivableManager.create_ar_from_invoice(invoice)
print(f"AR Status: {ar_record.status}, Outstanding: {ar_record.amount_outstanding}")

# 3. CHECK AR AGING
aging_summary = AccountsReceivableManager.get_ar_aging_summary(entity)
print(f"AR by aging: {aging_summary}")

# 4. CUSTOMER PAYS PARTIAL PAYMENT
payment = PaymentProcessor.process_payment(
    invoice=invoice,
    amount=Decimal('5000.00'),
    payment_date=timezone.now().date(),
    payment_method='BANK_TRANSFER',
    reference_number='TXN-001',
    user=request.user
)
print(f"Payment recorded: {payment.amount}, Status: {payment.status}")

# Verify AR updated
ar_record.refresh_from_db()
print(f"AR Updated - Received: {ar_record.amount_received}, Outstanding: {ar_record.amount_outstanding}")

# 5. APPLY EARLY PAYMENT DISCOUNT
adjustment = SalesAdjustment.objects.create(
    entity=entity,
    invoice=invoice,
    adjustment_type='DISCOUNT',
    adjustment_date=timezone.now().date(),
    amount=Decimal('500.00'),
    reason='Early payment discount',
    status='DRAFT',
    requires_approval=False
)

# Approve and post
adjustment.status = 'APPROVED'
adjustment.save()
AdjustmentProcessor.post_adjustment_to_gl(adjustment)
print(f"Adjustment posted: {adjustment.adjustment_type}")

# 6. FINAL PAYMENT
final_payment = PaymentProcessor.process_payment(
    invoice=invoice,
    amount=Decimal('5500.00'),  # Remaining after discount
    payment_date=timezone.now().date() + timedelta(days=1),
    payment_method='CHECK',
    reference_number='CHK-5001',
    user=request.user
)

# Verify invoice is paid
invoice.refresh_from_db()
ar_record.refresh_from_db()
print(f"Invoice Status: {invoice.status}")
print(f"AR Status: {ar_record.status}")
print(f"Invoice Reconciliation - Total: {invoice.total_amount}, Paid: {invoice.amount_paid}")

# 7. GENERATE MONTHLY REPORT
from datetime import date
report = FinancialReportGenerator.generate_report(
    entity=entity,
    report_type='MONTHLY',
    period_start=date(2025, 12, 1),
    period_end=date(2025, 12, 31),
    user=request.user
)
print(f"Report - Revenue: {report.net_revenue}, Margin: {report.gross_profit_margin}%")
```

---

### Example 2: Customer Payment with Multiple AR Records

```python
# Scenario: Customer has multiple outstanding invoices
# Payment received: 15,000
# Invoice 1 outstanding: 5,000
# Invoice 2 outstanding: 8,000
# Invoice 3 outstanding: 6,000
# Total outstanding: 19,000

invoices = Invoice.objects.filter(customer=customer, status__in=['ISSUED', 'PARTIAL'])
ar_records = AccountsReceivable.objects.filter(customer=customer, status__in=['OUTSTANDING', 'PARTIAL'])

total_received = Decimal('15000.00')
remaining = total_received

# Allocate payment by due date (FIFO - oldest first)
for ar in ar_records.order_by('due_date'):
    if remaining <= 0:
        break
    
    payment_amount = min(remaining, ar.amount_outstanding)
    
    payment = PaymentProcessor.process_payment(
        invoice=ar.invoice,
        amount=payment_amount,
        payment_date=timezone.now().date(),
        payment_method='BANK_TRANSFER',
        reference_number='COMBINED-PAYMENT-123',
        user=request.user
    )
    
    remaining -= payment_amount
    print(f"Allocated {payment_amount} to {ar.invoice.invoice_number}")

print(f"Total allocated: {total_received - remaining}")
if remaining > 0:
    print(f"Unallocated payment: {remaining}")
```

---

### Example 3: Bad Debt Write-off Process

```python
from sales.models import SalesAdjustment
from sales.integration import AdjustmentProcessor

# Find overdue invoices (> 120 days)
from django.db.models import Q
from datetime import timedelta

cutoff_date = timezone.now().date() - timedelta(days=120)
ar_records = AccountsReceivable.objects.filter(
    due_date__lt=cutoff_date,
    status='OUTSTANDING',
    amount_outstanding__gt=0
)

for ar in ar_records:
    # Create write-off adjustment
    adjustment = SalesAdjustment.objects.create(
        entity=entity,
        invoice=ar.invoice,
        adjustment_type='WRITE_OFF',
        adjustment_date=timezone.now().date(),
        amount=ar.amount_outstanding,
        reason=f"Uncollectible debt - {ar.customer.customer_name}",
        status='DRAFT',
        requires_approval=True  # Require manager approval
    )
    
    print(f"Write-off created for {ar.invoice.invoice_number}")

# Manager approval workflow (in separate process/view)
pending_writeoffs = SalesAdjustment.objects.filter(
    adjustment_type='WRITE_OFF',
    status='DRAFT',
    requires_approval=True
)

for adj in pending_writeoffs:
    # After approval by manager:
    adj.status = 'APPROVED'
    adj.approved_by = manager_user
    adj.approved_at = timezone.now()
    adj.save()
    
    # Post to GL
    AdjustmentProcessor.post_adjustment_to_gl(adj)
    
    # Update AR status
    ar = adj.invoice.ar_record
    ar.status = 'WRITTEN_OFF'
    ar.save()
    
    print(f"Write-off posted: {adj.amount}")
```

---

## Reports & Analytics

### AR Aging Report

```python
# Get AR aging summary
from sales.integration import AccountsReceivableManager

aging = AccountsReceivableManager.get_ar_aging_summary(entity)

print("=" * 60)
print(f"AR AGING REPORT - {entity.name}")
print("=" * 60)

total_ar = Decimal('0.00')
for bucket_key in ['current', '30_60', '60_90', 'over_90']:
    bucket = aging[bucket_key]
    total_ar += bucket['amount']
    print(f"{bucket_key:15} {bucket['count']:3} invoices   ${bucket['amount']:>12,.2f}")

print("-" * 60)
print(f"{'TOTAL':15} {sum(a['count'] for a in aging.values()):3}         ${total_ar:>12,.2f}")
print("=" * 60)
```

### Collection Forecast Report

```python
# Get 30-day collection forecast
from sales.integration import AccountsReceivableManager
from datetime import date

forecast = AccountsReceivableManager.get_collection_forecast(entity, days_ahead=30)

print("=" * 60)
print(f"COLLECTION FORECAST - Next 30 Days")
print("=" * 60)

total_forecast = Decimal('0.00')
for date_str, amount in sorted(forecast.items()):
    if amount > 0:
        total_forecast += amount
        print(f"{date_str}   ${amount:>12,.2f}")

print("-" * 60)
print(f"{'TOTAL EXPECTED':30} ${total_forecast:>12,.2f}")
print("=" * 60)
```

### Sales Revenue Report

```python
# Generate comprehensive monthly report
from sales.integration import FinancialReportGenerator
from datetime import date

report = FinancialReportGenerator.generate_report(
    entity=entity,
    report_type='MONTHLY',
    period_start=date(2025, 12, 1),
    period_end=date(2025, 12, 31),
    user=request.user
)

print("=" * 60)
print(f"SALES FINANCIAL REPORT - {report.entity.name}")
print(f"Period: {report.period_start} to {report.period_end}")
print("=" * 60)
print("\nREVENUE SUMMARY:")
print(f"  Gross Revenue:        ${report.gross_revenue:>12,.2f}")
print(f"  Less: Discounts:      ${report.total_discounts:>12,.2f}")
print(f"  Less: Returns:        ${report.total_returns:>12,.2f}")
print(f"  Net Revenue:          ${report.net_revenue:>12,.2f}")
print(f"  Tax Collected:        ${report.total_tax_collected:>12,.2f}")

print("\nARCOUNTS RECEIVABLE:")
print(f"  Total Invoiced:       ${report.total_invoiced:>12,.2f}")
print(f"  Total Received:       ${report.total_received:>12,.2f}")
print(f"  Total Outstanding:    ${report.total_outstanding:>12,.2f}")
print(f"  Overdue Amount:       ${report.overdue_amount:>12,.2f}")

print("\nPROFITABILITY:")
print(f"  Gross Profit:         ${report.gross_profit:>12,.2f}")
print(f"  Profit Margin:        {report.gross_profit_margin:>12,.2f}%")

print("\nCUSTOMER METRICS:")
print(f"  Active Customers:     {report.total_active_customers:>12,}")
print(f"  New Customers:        {report.new_customers:>12,}")
print(f"  Repeat Customers:     {report.repeat_customers:>12,}")
print("=" * 60)
```

---

## Troubleshooting

### Issue 1: GL Entry Not Created When Invoice Issued

**Symptom:** Invoice status changed to ISSUED but GL entry not created

**Check:**
1. Verify GL accounts exist for entity
   ```python
   from accounting.models import Account
   revenue_account = Account.objects.filter(
       entity=entity,
       account_type='INCOME',
       is_active=True
   ).first()
   assert revenue_account, "Revenue account not found"
   ```

2. Check invoice amounts are positive
   ```python
   assert invoice.total_amount > 0, "Invoice total must be > 0"
   assert invoice.subtotal > 0, "Invoice subtotal must be > 0"
   ```

3. Verify GL posting was called
   ```python
   from sales.integration import GLPostingManager
   try:
       GLPostingManager.post_invoice_revenue_to_gl(invoice)
   except Exception as e:
       print(f"Error: {e}")
   ```

---

### Issue 2: AR Record Not Created

**Symptom:** Invoice marked ISSUED but no AR record created

**Check:**
1. Invoice must be ISSUED status
   ```python
   assert invoice.status == 'ISSUED', f"Invoice status is {invoice.status}"
   ```

2. Create AR manually if missing
   ```python
   from sales.integration import AccountsReceivableManager
   ar = AccountsReceivableManager.create_ar_from_invoice(invoice)
   print(f"AR created: {ar.pk}")
   ```

---

### Issue 3: Payment Not Reducing Outstanding Balance

**Symptom:** Payment recorded but AR still shows outstanding

**Check:**
1. Verify payment was marked RECONCILED
   ```python
   payment = SalesPayment.objects.get(pk=payment_id)
   assert payment.status == 'RECONCILED', f"Payment status: {payment.status}"
   ```

2. Check AR was updated
   ```python
   ar = AccountsReceivable.objects.get(invoice=invoice)
   print(f"AR received: {ar.amount_received}")
   print(f"AR outstanding: {ar.amount_outstanding}")
   ```

3. Recalculate if needed
   ```python
   ar.amount_received = ar.invoice.amount_paid
   ar.amount_outstanding = ar.invoice_amount - ar.amount_received
   ar.save()
   ```

---

### Issue 4: GL Entries Not Balanced

**Symptom:** Total debits ≠ total credits in GL

**Check:**
1. Verify all GL postings have matching debit/credit amounts
   ```python
   from sales.models import GeneralLedgerPosting
   postings = GeneralLedgerPosting.objects.filter(status='POSTED')
   for posting in postings:
       assert posting.debit_amount == posting.credit_amount, \
           f"Posting {posting.pk} unbalanced"
   ```

2. Check if adjustment amounts are correct
   ```python
   # Adjustments should reduce both DR and CR by same amount
   assert adjustment.amount <= invoice.total_amount
   ```

---

### Issue 5: Tax Posting Missing or Incorrect

**Symptom:** Invoice has tax but no tax GL entry

**Check:**
1. Verify tax amount > 0
   ```python
   assert invoice.tax_amount > 0, "No tax to post"
   ```

2. Manually post tax if missing
   ```python
   from sales.integration import GLPostingManager
   try:
       gl_posting_tax = GLPostingManager.post_invoice_tax_to_gl(invoice)
       print(f"Tax posted: {gl_posting_tax.credit_amount}")
   except Exception as e:
       print(f"Error posting tax: {e}")
   ```

---

## Integration Checklist

- [ ] Chart of Accounts configured with all required accounts
- [ ] GL accounts linked to sales module (Account numbers in settings)
- [ ] Entity setup with currency and default accounts
- [ ] Test invoice creation and GL posting
- [ ] Test customer payment processing
- [ ] Test adjustment workflow (discount, return, write-off)
- [ ] Test AR aging calculation
- [ ] Test collection forecast generation
- [ ] Test financial report generation
- [ ] Run reconciliation between Sales and GL totals
- [ ] Configure approval workflows for write-offs
- [ ] Set up email notifications for overdue invoices
- [ ] Configure tax rate updates for automatic tax posting
- [ ] Test multi-entity scenarios if applicable

---

## References

- `sales/models.py` - Data models
- `sales/integration.py` - Integration functions
- `accounting/models.py` - GL account definitions
- `sales/views.py` - Invoice and payment views

---

**Document Version:** 1.0  
**Last Updated:** December 6, 2025  
**Next Review:** December 13, 2025
