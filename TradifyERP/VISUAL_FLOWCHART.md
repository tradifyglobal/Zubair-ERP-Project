# Sales-Accounting Integration: Visual Flowchart

## Invoice Lifecycle with GL Impact

```
┌─────────────────────────────────────────────────────────────────┐
│              INVOICE LIFECYCLE & GL INTEGRATION                  │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ CREATE INVOICE  │
    │  (Form Input)   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────┐
    │  Set Status:            │
    │  - DRAFT                │ ◀── No GL entries
    │  - ISSUED ◀─────────────┼─── GL entries created!
    │  - PAID                 │
    │  - PARTIAL              │
    │  - CANCELLED            │
    │  - OVERDUE              │
    └────────┬────────────────┘
             │
             ▼
    ┌────────────────────────────────────────────┐
    │ IF STATUS = ISSUED                         │
    │ ────────────────────────────────────────── │
    │ GL Entry Created:                          │
    │                                            │
    │ DR Accounts Receivable      $Total         │
    │   CR Sales Revenue                $Sub    │
    │   CR Sales Tax Payable           $Tax    │
    │                                            │
    │ Reference: INV-{invoice_id}               │
    └────────┬───────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │  FINANCIAL STATEMENTS:       │
    │  ────────────────────────    │
    │  P&L:                        │
    │    Revenue: +$Subtotal       │
    │                              │
    │  Balance Sheet:              │
    │    Assets: AR +$Total        │
    │    Liabilities: Tax +$Tax    │
    │    Equity: +$Subtotal        │
    └──────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────┐
    │  UPDATE AMOUNT PAID          │
    │  (Record Customer Payment)   │
    └────────┬────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────────┐
    │ IF AMOUNT_PAID > Previous Amount Paid      │
    │ ─────────────────────────────────────────  │
    │ GL Entry Created (Payment):                │
    │                                            │
    │ DR Cash                     $Payment       │
    │   CR Accounts Receivable          $Payment │
    │                                            │
    │ Reference: PAY-INV-{id}-{timestamp}       │
    └────────┬───────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │  AR BALANCE UPDATED:         │
    │  ─────────────────────       │
    │  AR = Total - Amount_Paid    │
    │                              │
    │  If AR = 0:                  │
    │    Status → PAID             │
    │  If 0 < AR < Total:          │
    │    Status → PARTIAL          │
    └──────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │  IF STATUS CHANGED TO CANCELLED        │
    │  ──────────────────────────────────── │
    │  GL Reversal Entry Created:            │
    │                                        │
    │  CR Accounts Receivable     $Total     │
    │    DR Sales Revenue              $Sub  │
    │    DR Sales Tax Payable          $Tax  │
    │                                        │
    │  Reference: REV-INV-{invoice_id}      │
    │                                        │
    │  Net GL Effect: ZERO                  │
    │  (Invoice cancelled, no impact)       │
    └────────────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ INVOICE COMPLETE OR DELETED  │
    │                              │
    │ GL Entries:                  │
    │ - Visible in Ledger          │
    │ - Included in P&L            │
    │ - Included in Balance Sheet  │
    │ - Audit trail maintained     │
    └──────────────────────────────┘
```

---

## GL Account Flows

```
┌─────────────────────────────────────────────────────────────────┐
│          HOW MONEY AND LIABILITY FLOW THROUGH GL                 │
└─────────────────────────────────────────────────────────────────┘

INVOICE ISSUED:

    Sales Revenue (INCOME)           Sales Tax Payable (LIABILITY)
    └─ Credit: +$1,000              └─ Credit: +$100
                │                              │
                │                              │
                └──────┬───────────────────────┘
                       │
                       │ Both created when
                       │ invoice status = ISSUED
                       │
                       ▼
    ┌──────────────────────────────┐
    │ Accounts Receivable (ASSET)  │
    │ Debit: +$1,100               │
    │                              │
    │ Customer Owes: $1,100        │
    └──────────────────────────────┘


PAYMENT RECEIVED - $500:

    Cash (ASSET)                    Accounts Receivable (ASSET)
    ├─ Debit: +$500               └─ Credit: -$500
    │
    └─ Customer paid $500
       AR reduces to $600


PAYMENT RECEIVED - $600:

    Cash (ASSET)                    Accounts Receivable (ASSET)
    ├─ Debit: +$600               └─ Credit: -$600
    │
    └─ Customer paid final $600
       AR reduces to $0
       Invoice marked PAID
```

---

## Trial Balance Reconciliation

```
┌─────────────────────────────────────────────────────────────────┐
│              TRIAL BALANCE EXAMPLE                               │
│         (Must Balance: Debits = Credits)                         │
└─────────────────────────────────────────────────────────────────┘

Account                  | Debit    | Credit
─────────────────────────┼──────────┼──────────
Cash                     | $1,100   |
Accounts Receivable      |    $0    |
Sales Revenue            |          | $1,000
Sales Tax Payable        |          |   $100
─────────────────────────┼──────────┼──────────
TOTALS                   | $1,100   | $1,100
                         |    ✓ BALANCED ✓
                         
Key Points:
- Debits = Credits (accounting equation)
- Cash increased by $1,100 (from payments)
- AR decreased to $0 (fully paid)
- Revenue recognized: $1,000
- Tax liability: $100 (to be paid to government)
```

---

## Financial Statements Impact

```
┌─────────────────────────────────────────────────────────────────┐
│          PROFIT & LOSS STATEMENT (P&L)                           │
└─────────────────────────────────────────────────────────────────┘

Sales Revenue            $1,000 ◀── From GL (CREDIT entries)
Sales Discounts           ($0)
                        ────────
Net Sales                $1,000
                        
COGS                        $0   ◀── From GL (would be from inventory)
Gross Profit             $1,000
                        
Operating Expenses          $0
Net Operating Income     $1,000
                        
Net Income               $1,000  ◀── Bottom line profit


┌─────────────────────────────────────────────────────────────────┐
│          BALANCE SHEET                                            │
│         (Snapshot at point in time)                              │
└─────────────────────────────────────────────────────────────────┘

ASSETS                           LIABILITIES
─────────────────                ─────────────────
Cash              $1,100         Sales Tax        $100
                                  Payable
Accounts Rec.        $0
                                 Total Liab       $100
Total Assets     $1,100
                                 EQUITY
                                 ─────────────────
                                 Retained         $1,000
                                 Earnings
                                 (from P&L net income)

                                 Total Equity    $1,000

Total Assets           $1,100    |
                                 |
Liabilities + Equity: $100 + $1,000 = $1,100 ✓
                  ────────────────────────────
                    BALANCED!

Equation: Assets = Liabilities + Equity
          $1,100 =      $100     +   $1,000
          ✓ CORRECT
```

---

## GL Entry Reference Numbers

```
┌─────────────────────────────────────────────────────────────────┐
│        GL ENTRY REFERENCE NUMBER SCHEME                          │
│     (For tracking and audit trail)                               │
└─────────────────────────────────────────────────────────────────┘

Format              | Example           | Meaning
────────────────────┼───────────────────┼──────────────────────────
INV-{id}            | INV-001           | Invoice revenue recognition
                    |                   | 3 entries (AR, Revenue, Tax)

PAY-INV-{id}-{ts}   | PAY-INV-001-123   | Payment received on invoice
                    |                   | 2 entries (Cash, AR)

REV-INV-{id}        | REV-INV-001       | Invoice reversed/cancelled
                    |                   | 3 entries (opposite of INV)


LOOKUP EXAMPLES:
───────────────

To find all GL entries for Invoice INV-001:
├─ Filter Accounting > Ledger
├─ Reference = INV-001
└─ Returns 3 entries: AR, Revenue, Tax

To find all payments received:
├─ Filter Accounting > Ledger
├─ Reference starts with PAY-
└─ Returns all payment entries

To find reversals (cancelled invoices):
├─ Filter Accounting > Ledger
├─ Reference starts with REV-
└─ Returns all reversal entries
```

---

## Status Transitions and GL Impact

```
┌─────────────────────────────────────────────────────────────────┐
│           INVOICE STATUS STATE MACHINE                           │
│        (What triggers GL entries)                                │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────┐
                    │  DRAFT   │ ◀─────── No GL entries
                    │ (Invoice)│         (Internal only)
                    └────┬─────┘
                         │ Set status to ISSUED
                         ▼
    ┌─────────────────────────────────────┐
    │  ISSUED                             │
    │  (Official invoice)                 │
    │  ✓ GL entries created:              │
    │    - Revenue recognized             │
    │    - AR created                     │
    │    - Tax recorded                   │
    └─────────────────┬───────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌─────────────┐
    │ PAID   │  │PARTIAL │  │   OVERDUE   │
    │(GL)    │  │ (GL)   │  │  (Status)   │
    │Amt Paid│  │Amt Paid│  │  No GL      │
    │= Total │  │< Total │  │  (tracking) │
    └────────┘  └────────┘  └─────────────┘
         │            │
         │     Can transition between
         │     PARTIAL ↔ PAID
         │
         └─────────────┬──────────────────┐
                       │                  │
                       ▼                  ▼
                 ┌──────────┐      ┌───────────────┐
                 │CANCELLED │      │     (or)      │
                 │(GL)      │      │    BACK TO    │
                 │Entries   │      │    PARTIAL    │
                 │Reversed  │      │    (GL)       │
                 └──────────┘      └───────────────┘

GL Events:
  ISSUED      → Create GL (Revenue + AR + Tax)
  PAY $X      → Create GL (Cash + reduce AR)
  CANCELLED   → Reverse GL (all opposite entries)
  DELETED     → Reverse GL before deletion
```

---

## Real Transaction Example Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│          COMPLETE INVOICE LIFECYCLE WITH GL                     │
│          (Daily example from real business)                      │
└─────────────────────────────────────────────────────────────────┘

DAY 1 - SALES REP CREATES QUOTE
────────────────────────────────
  Invoice: INV-001
  Status: DRAFT
  Amount: $1,100
  
  GL Impact: NONE (not official yet)
  
  P&L: Not recognized
  Balance Sheet: Nothing shown


DAY 2 - CUSTOMER APPROVES, MARKED ISSUED
──────────────────────────────────────────
  Invoice: INV-001
  Status: DRAFT → ISSUED
  
  GL Entry 1 (Reference: INV-001)
  ├─ DR Accounts Receivable        $1,100
  ├─ CR Sales Revenue              $1,000
  └─ CR Sales Tax Payable          $100
  
  GL Impact: Revenue recognized!
  
  P&L: Revenue = $1,000
  Balance Sheet: 
  ├─ Assets: AR = $1,100
  └─ Liabilities: Tax = $100


DAY 5 - CUSTOMER PAYS PARTIAL AMOUNT
──────────────────────────────────────
  Invoice: INV-001
  Status: ISSUED → PARTIAL
  Amount Paid: $0 → $500
  
  GL Entry 2 (Reference: PAY-INV-001-{ts})
  ├─ DR Cash                       $500
  └─ CR Accounts Receivable        $500
  
  GL Impact: Cash received!
  
  P&L: No change (revenue already recorded)
  Balance Sheet:
  ├─ Assets: Cash = $500, AR = $600
  └─ Liabilities: Tax = $100


DAY 10 - CUSTOMER PAYS FINAL AMOUNT
────────────────────────────────────
  Invoice: INV-001
  Status: PARTIAL → PAID
  Amount Paid: $500 → $1,100
  
  GL Entry 3 (Reference: PAY-INV-001-{ts2})
  ├─ DR Cash                       $600
  └─ CR Accounts Receivable        $600
  
  GL Impact: Remaining payment received!
  
  P&L: No change (revenue already recorded)
  Balance Sheet:
  ├─ Assets: Cash = $1,100, AR = $0
  └─ Liabilities: Tax = $100


END OF MONTH FINANCIAL REPORT
──────────────────────────────

P&L for Month:
  Sales Revenue        $1,000
  COGS                    $0
  Gross Profit         $1,000
  Expenses                $0
  Net Income           $1,000  ◀── Profit from this sale

Balance Sheet (End of Month):
  Assets:
    Cash               $1,100  ◀── All payment received
    AR                    $0   ◀── Fully paid
  Liabilities:
    Sales Tax          $100    ◀── To be paid to government
  Equity:
    Retained Earnings  $1,000  ◀── From net income
  
  Verification:
    Assets ($1,100) = Liabilities ($100) + Equity ($1,000) ✓


TAX FILING (Quarterly)
──────────────────────

Sales Tax Calculation:
  Filter GL account: Sales Tax Payable
  Date Range: Jan 1 - Mar 31
  Total Tax Collected: $1,100
  
  Action: Pay $1,100 to government
  
  GL Entry: (Tax Payment)
  ├─ DR Sales Tax Payable       $1,100
  └─ CR Cash                    $1,100
  
  Result: Sales Tax Payable = $0 (paid)


AUDIT TRAIL - 12 MONTHS LATER
───────────────────────────────

External auditor requests:
  "Show me all GL entries for sales revenue"
  
Response (from GL system):
  Reference: INV-001
  ├─ Entry 1: DR AR $1,100 (revenue recognition)
  ├─ Entry 2: CR Revenue $1,000
  ├─ Entry 3: CR Tax $100
  ├─ Entry 4: DR Cash $500 (payment 1)
  ├─ Entry 5: CR AR $500
  ├─ Entry 6: DR Cash $600 (payment 2)
  └─ Entry 7: CR AR $600
  
  All entries visible, traceable, verified ✓
```

---

This is how real-world accounting works. Your system now operates exactly this way. Every transaction creates a permanent GL record that flows into financial statements.
