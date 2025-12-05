# Sales Module - Accounting Integration Guide

## Overview
The Sales module is fully integrated with the Accounting module to automatically create General Ledger (GL) entries for all sales transactions. This ensures that:
- Revenue is recognized when invoices are issued
- Accounts Receivable (AR) is tracked automatically
- Sales taxes are recorded as liabilities
- Payments reduce AR when received
- All transactions have audit trails

## Real-World Accounting Flow

### 1. Invoice Creation (Draft Status)
- **GL Action**: No entries created
- **Reason**: Revenue not yet recognized (prudent accounting principle)
- **Used For**: Work-in-progress, quotations

### 2. Invoice Issued
- **GL Action**: Creates double-entry for revenue recognition
```
DR Accounts Receivable (ASSET)     = Total Amount
    CR Sales Revenue (INCOME)      = Subtotal
    CR Sales Tax Payable (LIABILITY) = Tax Amount
```
- **Impact on Financial Statements**:
  - Balance Sheet: AR increases (asset) → Equity increases through Income
  - P&L: Revenue recognized in period

### 3. Payment Received
- **GL Action**: Updates AR and Cash accounts
```
DR Cash/Bank (ASSET)               = Amount Paid
    CR Accounts Receivable (ASSET) = Amount Paid
```
- **Impact on Financial Statements**:
  - Balance Sheet: Cash increases, AR decreases (net effect on assets depends on payment amount)
  - P&L: No impact (revenue already recognized)

### 4. Invoice Cancelled
- **GL Action**: Reverses all revenue recognition entries
```
CR Accounts Receivable (ASSET)     = Total Amount
    DR Sales Revenue (INCOME)      = Subtotal
    DR Sales Tax Payable (LIABILITY) = Tax Amount
```
- **Impact on Financial Statements**:
  - Balance Sheet: AR decreases, Equity decreases through Income
  - P&L: Revenue reduced (correction entry)

## Setup Instructions

### Step 1: Create GL Accounts
Run the management command to create required GL accounts:

```bash
# For a specific entity
python manage.py setup_sales_gl_accounts ENTITY_CODE

# For all entities
python manage.py setup_sales_gl_accounts
```

This creates:
- **1200**: Accounts Receivable (Asset)
- **1000**: Cash (Asset)
- **2110**: Sales Tax Payable (Liability)
- **4100**: Sales Revenue (Income)
- **4200**: Sales Discounts (Income)
- **5100**: Cost of Goods Sold (Expense)

### Step 2: Verify Account Setup
1. Go to Accounting > Chart of Accounts
2. Verify the GL accounts created above exist for your entity
3. Ensure currency is set correctly (USD by default)

### Step 3: Start Creating Invoices
1. Go to Sales > Invoices > Create New
2. Fill in invoice details
3. Set status to **ISSUED** to trigger GL entries
4. Save

GL entries are created automatically when you save.

## How It Works in Practice

### Example Transaction
**Customer: Yashoda**
**Invoice: INV-001**
- Subtotal: $1,000
- Tax (10%): $100
- Total: $1,100

### Step 1: Create and Issue Invoice
When you create an invoice with status "ISSUED":

**GL Entry Created:**
```
Date: Invoice Date
Reference: INV-001

Debit:  Accounts Receivable     $1,100
  Credit: Sales Revenue                $1,000
  Credit: Sales Tax Payable             $100
```

**Impact on Trial Balance:**
- Accounts Receivable: +$1,100 (Debit balance)
- Sales Revenue: +$1,000 (Credit balance - increases income)
- Sales Tax Payable: +$100 (Credit balance - liability)

### Step 2: Customer Pays $500
When you record payment of $500:

**GL Entry Created:**
```
Date: Payment Date
Reference: PAY-INV-001

Debit:  Cash                    $500
  Credit: Accounts Receivable         $500
```

**Impact on Trial Balance:**
- Cash: +$500 (Debit balance)
- Accounts Receivable: -$500 (now $600 remaining)
- Net Asset effect: $0 (one asset increases, another decreases)

### Step 3: Customer Pays Remaining $600
**GL Entry Created:**
```
Date: Payment Date
Reference: PAY-INV-001

Debit:  Cash                    $600
  Credit: Accounts Receivable         $600
```

**Impact:**
- Accounts Receivable: $0 (fully paid)
- Cash: +$600
- Invoice marked as "PAID"

## Viewing GL Entries

### 1. Individual Ledger Entries
- Go to **Accounting > Ledger**
- Filter by:
  - Account: "Accounts Receivable" or "Sales Revenue"
  - Reference: "INV-001" (invoice number)
  - Date Range

### 2. Trial Balance
- Go to **Accounting > Trial Balance**
- View all GL account balances as of a date
- Verify totals balance (Debits = Credits)

### 3. Profit & Loss Report
- Go to **Accounting > Reports > P&L**
- Sales Revenue shows all recognized revenue for period
- Sales Tax Payable shows total tax obligations
- Shows net income/loss

### 4. Balance Sheet
- Go to **Accounting > Reports > Balance Sheet**
- Assets section shows:
  - Accounts Receivable balance (total outstanding invoices)
  - Cash balance (from payment receipts)
- Liabilities section shows:
  - Sales Tax Payable balance (total tax collected not yet paid)
- Equity shows accumulated profit

### 5. Accounts Receivable Aging Report
- Go to **Accounting > Reports > AR Aging**
- Shows which invoices are:
  - Current (not yet due)
  - 30+ days overdue
  - 60+ days overdue
  - 90+ days overdue

## Invoice Status Tracking

| Status | GL Impact | Customer Facing | Accounting View |
|--------|-----------|-----------------|-----------------|
| **DRAFT** | None | Quotation/draft | Not recognized |
| **ISSUED** | Revenue recognized, AR created | Invoice sent | GL entries created |
| **PAID** | AR fully reduced | Payment received | AR = $0 |
| **PARTIAL** | AR partially reduced | Partial payment received | AR reduced by payment |
| **OVERDUE** | AR remains (aging increases) | Payment not received | AR aging > terms |
| **CANCELLED** | GL entries reversed | Invoice voided | GL corrected |

## Accounting Principles Applied

### 1. Accrual Accounting
- Revenue recognized when earned (invoice issued), not when cash received
- Allows proper P&L matching of revenue and expenses

### 2. Double-Entry Bookkeeping
- Every transaction has equal debits and credits
- Ensures Trial Balance always balances
- Provides audit trail

### 3. Asset = Liability + Equity
- Accounts Receivable is an asset
- Revenue increases equity
- Payments convert AR to Cash (both assets)

### 4. Revenue Recognition
- Revenue recognized when invoice is ISSUED
- Not recognized for DRAFT invoices
- Reversed if invoice is CANCELLED

### 5. Audit Trail
- Every GL entry has:
  - Reference number (INV-001, PAY-INV-001, REV-INV-001)
  - Description with context
  - Date and user
  - Transaction type (debit/credit)

## Troubleshooting

### GL Accounts Not Found
**Problem**: When creating an invoice, GL entries are not created.

**Cause**: GL accounts not configured for the entity.

**Solution**: 
```bash
python manage.py setup_sales_gl_accounts ENTITY_CODE
```

### Invoice Revenue Not Appearing in P&L
**Problem**: Invoice issued but doesn't show in P&L report.

**Cause**: Invoice status is not ISSUED.

**Solution**: Update invoice status to ISSUED and save.

### AR Balance Doesn't Match Invoice Total
**Problem**: Accounts Receivable balance differs from outstanding invoices.

**Cause**: 
1. Invoice was DRAFT when created (no GL entry)
2. Invoice was CANCELLED but GL not reversed
3. Multiple payments were recorded

**Solution**: Check individual GL entries in Accounting > Ledger filtered by reference number.

## Advanced Features

### 1. Multi-Currency Support
- GL entries in invoice currency
- Exchange rates apply for consolidation
- Supports realistic global businesses

### 2. Tax Tracking
- Sales Tax Payable tracks all taxes collected
- Can be filtered by date for tax filing
- Separate from revenue (proper liability)

### 3. Discount Handling
- Discounts reduce revenue recognized
- Shown as separate GL account for analysis
- Can track customer profitability

### 4. Partial Payments
- Creates separate GL entry for each payment
- Allows precise AR aging
- Tracks payment history

### 5. Write-offs
- Uncollectible invoices can be written off
- Creates allowance account
- Proper financial statement presentation

## Integration with Other Modules

### Manufacturing Module
- COGS (Cost of Goods Sold) tracked separately
- Inventory valuation reflected in GL
- Product profitability analysis

### HR Module
- Sales commissions post to expense accounts
- Payroll integrated with GL
- Labor cost allocation to sales

### Accounting Module
- All GL entries visible in main ledger
- Financial statements include sales activity
- Comprehensive P&L and Balance Sheet

## Best Practices

1. **Always Issue Invoices**: Don't leave invoices in DRAFT status
2. **Timely Recording**: Record payments as received
3. **Regular Reconciliation**: Match AR in GL to outstanding invoices
4. **Tax Compliance**: Track Sales Tax Payable for filing
5. **Audit Trail**: All entries have reference numbers for audit
6. **Period Closing**: Close periods to lock GL entries before reviewing
7. **Backup**: Regular database backups of GL entries

## FAQ

**Q: When are GL entries created?**
A: When invoice status is changed to ISSUED.

**Q: Can I reverse a GL entry?**
A: No, but you can mark invoice as CANCELLED which creates reversal entries.

**Q: Do draft invoices create GL entries?**
A: No, only ISSUED invoices create GL entries.

**Q: What if customer doesn't pay?**
A: AR remains until payment received or invoice written off. AR aging shows overdue.

**Q: How do refunds work?**
A: Create a negative invoice (credit note) which reverses the GL entries.

**Q: Can I modify GL entries directly?**
A: Not recommended. Instead, cancel and recreate the invoice.

**Q: How is sales tax reported?**
A: Sales Tax Payable account tracks all taxes. Filter GL for tax payment period.

**Q: Does inventory get affected?**
A: Only if manufacturing module is integrated (COGS recorded).

## Support

For issues or questions about Sales-Accounting integration:
1. Check this guide's troubleshooting section
2. Review GL entries in Accounting > Ledger
3. Verify account setup with setup_sales_gl_accounts command
4. Check invoice status is correct (must be ISSUED for GL)
