# Sales-Accounting Integration: Quick Reference

## The Real-World Connection

Your Sales module now works exactly like real-world accounting:

1. **When you CREATE an Invoice (Status: ISSUED)**
   - System automatically creates GL entry
   - Records: "Customer owes us money" (AR) and "We earned revenue"
   - Appears on P&L as revenue
   - Appears on Balance Sheet as AR (asset)

2. **When Customer PAYS (Amount Paid increases)**
   - System creates GL entry
   - Records: "We received cash" and "Customer's debt reduced"
   - AR decreases
   - Cash increases
   - Net effect on Balance Sheet: Assets unchanged but composition changed

3. **When you CANCEL an Invoice**
   - System reverses all GL entries
   - Records: "We undo the revenue" and "Remove the AR"
   - Opposite journal entry created
   - Audit trail maintained

## Key Accounting Concepts Applied

### Double-Entry Bookkeeping
Every transaction must have equal debits and credits:
```
Invoice Issued:
  DR Accounts Receivable (Asset)        $1,100
    CR Sales Revenue (Income)                    $1,000
    CR Sales Tax Payable (Liability)            $100
```

### The Accounting Equation
**Assets = Liabilities + Equity**

When you issue invoice for $1,100:
- Assets (AR): +$1,100
- Liabilities (Tax): +$100
- Equity (Revenue): +$1,000
- Equation balances: $1,100 = $100 + $1,000 ✓

### Accrual Accounting (Not Cash Basis)
Revenue recognized when INVOICE ISSUED, not when payment received.
- Allows proper matching of revenue and expenses
- More accurate income measurement
- Standard for businesses over $1M revenue

## GL Accounts Created

| # | Name | Type | Purpose |
|---|------|------|---------|
| 1000 | Cash | ASSET | Track money received |
| 1200 | Accounts Receivable | ASSET | Track customer debts |
| 2110 | Sales Tax Payable | LIABILITY | Track tax obligations |
| 4100 | Sales Revenue | INCOME | Track sales revenue |
| 4200 | Sales Discounts | INCOME | Track discounts given |
| 5100 | Cost of Goods Sold | EXPENSE | Track product costs |

## Viewing Results

### See Revenue Recognized
1. Go to Accounting > Ledger
2. Filter by Account: "Sales Revenue"
3. Filter by Date Range
4. See all revenue for the period

### See Outstanding AR
1. Go to Accounting > Ledger
2. Filter by Account: "Accounts Receivable"
3. View all unpaid invoices
4. Calculate balance (Debits - Credits)

### See on P&L
1. Go to Accounting > Reports > P&L
2. Sales Revenue section shows total recognized
3. Sales Discounts shows discounts given
4. COGS shows product costs

### See on Balance Sheet
1. Go to Accounting > Reports > Balance Sheet
2. Assets section: AR balance and Cash balance
3. Liabilities: Sales Tax Payable
4. Equity: Increased by net revenue

## Example Walkthrough

**Create Invoice INV-001 for $1,100 (includes $100 tax)**

```
GL Entry 1 (Revenue Recognition):
Date: 11/16/2025
Debit:  Accounts Receivable      $1,100
Credit: Sales Revenue                    $1,000
Credit: Sales Tax Payable               $100

Trial Balance: $1,100 = $1,100 ✓
```

**Customer Pays $500**

```
GL Entry 2 (Payment 1):
Date: 11/16/2025 (payment date)
Debit:  Cash                     $500
Credit: Accounts Receivable            $500

AR Balance now: $600 remaining
```

**Customer Pays Final $600**

```
GL Entry 3 (Payment 2):
Date: 11/17/2025 (payment date)
Debit:  Cash                     $600
Credit: Accounts Receivable            $600

AR Balance now: $0
Invoice Status: PAID
```

## Financial Statements After This Invoice

### P&L (Income Statement)
```
Sales Revenue                 $1,000
Sales Discounts                  $0
                             -------
Net Sales                     $1,000
COGS                             $0
                             -------
Gross Profit                  $1,000
Operating Expenses                $0
                             -------
Net Income                    $1,000

Sales Tax Liability:           $100 (on Balance Sheet, not P&L)
```

### Balance Sheet (Snapshot after final payment)
```
ASSETS
Cash                          $1,100
Accounts Receivable                $0
                             -------
Total Assets                  $1,100

LIABILITIES
Sales Tax Payable               $100
                             -------
Total Liabilities               $100

EQUITY
Retained Earnings             $1,000
                             -------
Total Equity                  $1,000

Total Liab + Equity           $1,100
```

Equation Balanced: Assets ($1,100) = Liabilities ($100) + Equity ($1,000) ✓

## Common Questions

**Q: Why create GL entry when invoice ISSUED, not when paid?**
A: Accrual accounting. Revenue recognized when earned (service/product delivered), not when cash received. More accurate financial picture.

**Q: What's the difference between DRAFT and ISSUED?**
- DRAFT: No GL entries. Use for quotes/internal prep
- ISSUED: GL entries created. Official business transaction

**Q: If customer doesn't pay, what happens to AR?**
A: AR stays on books as asset. Eventually written off if uncollectible (rare). Shows on AR Aging report as overdue.

**Q: How is sales tax handled?**
A: Separate GL account "Sales Tax Payable" is a liability. You collect it from customer but owe it to government. Pay periodically based on tax filing requirements.

**Q: Can I see how much cash I really have?**
A: Yes. Accounting > Ledger > Filter by "Cash" account. Shows all receipts and disbursements with running balance.

**Q: How does this connect to accounting profit?**
A: P&L is built from GL accounts. Net Income = Total Revenue - Total Expenses (all from GL). Matches to Balance Sheet Equity.

**Q: What if I make a mistake?**
A: Cancel the invoice. System creates reversal GL entries. Original entries still visible (audit trail), but net effect is zero.

## Troubleshooting

**GL entries not appearing?**
1. Check invoice status is "ISSUED"
2. Check GL accounts exist: Accounting > Chart of Accounts
3. If missing, run: `python manage.py setup_sales_gl_accounts`

**P&L not showing my sales?**
1. Check invoice date falls within report date range
2. Check invoice status is "ISSUED"
3. Check filter date range in report

**AR balance wrong?**
1. Filter Accounting > Ledger by "Accounts Receivable"
2. Check for DRAFT invoices (no GL entry)
3. Verify all payments recorded

**Tax amount wrong?**
1. Check Tax Amount in invoice form
2. Verify Sales Tax Payable account in GL

## Setup Checklist

- [ ] Run: `python manage.py setup_sales_gl_accounts`
- [ ] Verify GL accounts created in Accounting > Chart of Accounts
- [ ] Create test invoice with status "ISSUED"
- [ ] Check Accounting > Ledger for GL entries
- [ ] Record test payment
- [ ] Verify AR decreased
- [ ] Run P&L report - see revenue
- [ ] Run Balance Sheet - see AR and Cash
- [ ] Ready for production!

## Next Steps

1. **Daily**: Create invoices with status "ISSUED" as normal
2. **Weekly**: Review Accounting > Ledger for any anomalies
3. **Monthly**: 
   - Run P&L report (profit/loss)
   - Run Balance Sheet (what you own/owe)
   - Pay sales taxes if required
   - Reconcile AR to outstanding invoices
4. **Quarterly/Annually**: 
   - Full financial statement review
   - Tax preparation
   - AR aging analysis

---

**Key Takeaway**: Your Sales module is now connected to real accounting. Every invoice creates permanent financial records that flow into P&L and Balance Sheet. This is how real businesses operate.
