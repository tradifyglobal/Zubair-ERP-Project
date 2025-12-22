# 💳 ERP Payment Workflows - Complete Specification

**Document Version**: 1.0  
**Date**: December 17, 2025  
**Status**: Ready for Implementation

---

## 📋 Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [Cash Payment Workflow](#cash-payment-workflow)
3. [Bank Payment Workflow](#bank-payment-workflow)
4. [GL Posting Logic](#gl-posting-logic)
5. [Ledger Updates](#ledger-updates)
6. [Data Models](#data-models)
7. [Receipt vs Payment Comparison](#receipt-vs-payment-comparison)
8. [Implementation Details](#implementation-details)

---

## 🎯 Workflow Overview

### Two Payment Types

**1. Cash Payment (CPV - Cash Payment Voucher)**
- For petty cash, out-of-pocket expenses
- Direct cash handed out to employees or for immediate expenses
- Immediate GL impact on authorization
- Cash account reduced, Expense account increased

**2. Bank Payment (BPV - Bank Payment Voucher)**
- For supplier payments, loan repayments, inter-account transfers
- Via bank transfer or cheque
- GL impact on authorization (advanced posting) or on bank confirmation (actual clearing)
- Bank account reduced, Expense/Payable account increased
- Optional: Bank reconciliation integration

---

## 💰 Cash Payment Workflow

### Phase 1: Initiation

**Trigger**: Finance request for payment
- Invoice from supplier
- Expense claim from employee
- Petty cash reimbursement request
- Other cash disbursement needs

**Input Documents**:
- Invoice/Bill
- Expense claim form
- Approval request email
- Supporting documentation

---

### Phase 2: Voucher Entry

**Actor**: Accountant / Finance Staff  
**System**: Cash Payment Voucher (CPV) Creation

**Data Captured**:

```json
{
  "CPV_Header": {
    "voucher_number": "CPV/2025/0001",
    "voucher_date": "2025-12-17",
    "entity": "Head Office",
    "payee_name": "Petty Cash / Employee Name",
    "payment_mode": "CASH",
    "total_amount": 5000,
    "description": "Office supplies and petty cash",
    "status": "DRAFT",
    "created_by": "accountant@company.com",
    "created_date": "2025-12-17 10:00:00"
  },
  
  "CPV_LineItems": [
    {
      "line_number": 1,
      "description": "Office stationery",
      "expense_account": "600-Office Supplies",
      "amount": 2000,
      "supporting_doc": "invoice_001.pdf",
      "tax_amount": 0,
      "tax_rate": 0
    },
    {
      "line_number": 2,
      "description": "Courier charges",
      "expense_account": "605-Freight & Logistics",
      "amount": 3000,
      "supporting_doc": "receipt_courier.pdf",
      "tax_amount": 0,
      "tax_rate": 0
    }
  ]
}
```

**Validation**:
- Payee information complete
- Expense accounts valid and active
- Amount > 0
- Supporting documents attached
- No duplicate payment (check against previous 7 days)

---

### Phase 3: Authorization Workflow

**Step 1: Maker (Accountant/Finance Staff)**
- Completes and reviews voucher
- Attaches supporting documents
- Performs initial validation
- Marks as "SUBMITTED_FOR_APPROVAL"
- Status: `DRAFT → SUBMITTED_FOR_APPROVAL`

**Step 2: Checker (Senior Accountant/Finance Manager)**
- Reviews voucher details and amounts
- Validates supporting documents
- Checks budget availability
- Verifies account codes and GL mappings
- **Actions**:
  - ✅ APPROVE: Moves to authorization
  - ❌ REJECT: Returns to maker with comments
  - 🔄 REQUEST_CHANGES: Specific issues to fix
- Status: `SUBMITTED_FOR_APPROVAL → CHECKED` or `REJECTED`

**Step 3: Approver (Finance Manager/CFO)**
- Final authorization authority
- Verifies payment authorization limits
- Checks cash availability
- **Actions**:
  - ✅ AUTHORIZE: Moves to GL posting (fires signal)
  - ❌ REJECT: Returns with authorization
- Status: `CHECKED → AUTHORIZED` or `REJECTED`

---

### Phase 4: GL Posting (On Authorization)

**Trigger**: Approver clicks "AUTHORIZE"  
**Signal**: Signal handler fires automatically

**GL Entries Created**:

```
Journal Entry: JE/CPV/2025/0001
Date: 2025-12-17
Narration: Cash Payment Voucher CPV/2025/0001

Line 1:
  Account: 600-Office Supplies
  Debit: 2000
  Credit: —
  
Line 2:
  Account: 605-Freight & Logistics
  Debit: 3000
  Credit: —

Line 3:
  Account: 100-Cash Account (Petty Cash)
  Debit: —
  Credit: 5000

Status: POSTED
Reference: CPV/2025/0001
```

**GL Impact**:
- Debit: Expense accounts (600, 605) = 5000
- Credit: Cash account (100) = 5000
- Net: Cash decreases, Expenses increase
- Balance Sheet: Assets decrease by 5000
- P&L: Expenses increase by 5000

**Audit Trail**:
- Created by: Maker
- Checked by: Checker
- Authorized by: Approver
- GL Posted by: System (auto)
- Timestamp: 2025-12-17 14:00:00

---

### Phase 5: Ledger Updates

**General Ledger**:
- Cash account (100) reduced by 5000
- Expense accounts (600, 605) increased accordingly
- Balance maintained (Dr = Cr)

**Sub-Ledgers**:
- **Cash Ledger**: Entry shows outflow, running balance decreases
- **Expense Ledger**: Each expense account updated with new balance
- **GL Summary**: Daily cash movement tracked

**Balance Calculations**:
```
Before: Cash Balance = 50,000
Less: Payment = 5,000
After: Cash Balance = 45,000

Expense Ledger:
  Before: Office Supplies = 15,000
  Add: Payment = 2,000
  After: Office Supplies = 17,000
```

---

## 🏦 Bank Payment Workflow

### Phase 1: Initiation

**Trigger**: Finance request for bank payment
- Supplier invoice for bulk order
- Loan installment payment
- Inter-account transfer
- Utility bills (electricity, water, etc.)
- Other bank-cleared payments

**Input Documents**:
- Invoice from vendor
- Loan statement
- Utility bill
- Bank transfer request
- Approval from initiator

---

### Phase 2: Voucher Entry

**Actor**: Accountant / Finance Staff  
**System**: Bank Payment Voucher (BPV) Creation

**Data Captured**:

```json
{
  "BPV_Header": {
    "voucher_number": "BPV/2025/0001",
    "voucher_date": "2025-12-17",
    "entity": "Head Office",
    "payee_name": "ABC Supplies Ltd",
    "payment_mode": "BANK_TRANSFER",
    "bank_account": "Current Account - Bank A",
    "beneficiary_bank_account": "123-456-789",
    "beneficiary_ifsc": "BANK0001",
    "total_amount": 100000,
    "description": "Payment for Purchase Order PO/2025/001",
    "status": "DRAFT",
    "created_by": "accountant@company.com",
    "created_date": "2025-12-17 10:30:00"
  },
  
  "BPV_LineItems": [
    {
      "line_number": 1,
      "description": "Raw materials purchase",
      "payable_account": "201-Accounts Payable",
      "expense_account": "400-Raw Materials",
      "po_reference": "PO/2025/001",
      "invoice_reference": "INV/2025/500",
      "amount": 100000,
      "supporting_doc": "invoice_500.pdf",
      "tax_amount": 18000,
      "tax_rate": 18,
      "net_amount": 82000
    }
  ]
}
```

**Validation**:
- Payee bank details complete
- Bank account active and has sufficient balance
- Payable/Expense accounts valid
- Amount > 0
- Invoice reconciled with PO
- No duplicate payment to same vendor (within 7 days)

---

### Phase 3: Authorization Workflow

**Step 1: Maker (Accountant/Finance Staff)**
- Completes voucher with bank details
- Verifies bank account ownership
- Attached supporting documents
- Status: `DRAFT → SUBMITTED_FOR_APPROVAL`

**Step 2: Checker (Senior Accountant/Finance Manager)**
- Reviews amount and vendor
- Validates invoice against PO
- Checks bank details
- Verifies reconciliation
- **Actions**:
  - ✅ APPROVE: Moves to authorization
  - ❌ REJECT: Returns to maker
- Status: `SUBMITTED_FOR_APPROVAL → CHECKED` or `REJECTED`

**Step 3: Authorizer (CFO/Finance Director)**
- Final payment authority
- Verifies bank balance and limits
- Checks authorization threshold
- May request additional verification for large amounts
- **Actions**:
  - ✅ AUTHORIZE: Queues for bank transfer
  - ❌ REJECT: Cancels payment
- Status: `CHECKED → AUTHORIZED` or `REJECTED`

---

### Phase 4: GL Posting (On Authorization)

**Trigger**: Approver clicks "AUTHORIZE"  
**Signal**: Signal handler fires automatically

**GL Entries Created**:

```
Journal Entry: JE/BPV/2025/0001
Date: 2025-12-17 (Advanced Posting)
Narration: Bank Payment Voucher BPV/2025/0001

Line 1:
  Account: 201-Accounts Payable
  Debit: 100000
  Credit: —

Line 2:
  Account: 110-Bank Account
  Debit: —
  Credit: 100000

Status: POSTED (Advanced)
Reference: BPV/2025/0001
Reconciliation Status: PENDING (awaiting bank confirmation)
```

**GL Impact** (Advanced Posting at Authorization):
- Debit: Payable account (201) = 100000
- Credit: Bank account (110) = 100000
- Net: Bank decreases, Payable decreases
- Balance Sheet: Assets decrease, Liabilities decrease

**Optional: Detailed Posting** (If tracking expense):
```
Line 1:
  Account: 400-Raw Materials / 201-Accounts Payable
  Debit: 100000 (to expense)
  Credit: —

Line 2:
  Account: 110-Bank Account
  Debit: —
  Credit: 100000
```

**Audit Trail**:
- Created by: Maker
- Checked by: Checker
- Authorized by: Approver
- GL Posted by: System (auto)
- Bank Status: INITIATED
- Timestamp: 2025-12-17 15:00:00

---

### Phase 5: Bank Reconciliation (Optional)

**Phase 5A: Bank Transfer Execution**
- System/Bank API transfers funds
- Bank confirmation received
- Status: `AUTHORIZED → IN_TRANSIT`

**Phase 5B: Bank Confirmation**
- Bank statement updated
- Payment marked as cleared
- Status: `IN_TRANSIT → CLEARED`
- Reconciliation GL entry created (if needed)

**Phase 5C: Ledger Updates**
- Bank account confirmed reduced
- Payable account marked as settled
- GL reconciliation validated
- Month-end bank reconciliation match verified

---

### Phase 6: Ledger Updates

**General Ledger**:
- Bank account (110) reduced by 100000
- Accounts Payable (201) reduced by 100000
- Balance maintained (Dr = Cr)

**Sub-Ledgers**:
- **Bank Ledger**: Entry shows outflow, running balance decreases
- **Payable Ledger**: Vendor balance reduced/settled
- **Bank Reconciliation**: Transaction tracked and matched

**Balance Calculations**:
```
Before: Bank Balance = 500,000
Less: Payment = 100,000
After: Bank Balance = 400,000

Payable Ledger (ABC Supplies Ltd):
  Before: Outstanding = 150,000
  Less: Payment = 100,000
  After: Outstanding = 50,000
```

---

## 📊 GL Posting Logic

### GL Posting Rules

#### For Cash Payments:

| Scenario | Debit Account | Credit Account | When Posted |
|----------|---|---|---|
| Expense Payment | Expense A/c | Cash A/c | On Authorization |
| Advance Adjustment | Advance Given A/c | Cash A/c | On Authorization |
| Refund/Return | Payable A/c | Cash A/c | On Authorization |
| Deposit Return | Bank A/c | Cash A/c | On Receipt |

#### For Bank Payments:

| Scenario | Debit Account | Credit Account | When Posted |
|----------|---|---|---|
| Supplier Payment (Advanced) | Accounts Payable | Bank A/c | On Authorization |
| Supplier Payment (Detailed) | Expense / Fixed Asset | Bank A/c | On Authorization |
| Loan Repayment | Loan Liability | Bank A/c | On Authorization |
| Inter-bank Transfer | Bank A/c (Recv) | Bank A/c (Pay) | On Authorization |
| Bank Charges | Bank Charges Exp | Bank A/c | On Bank Statement |

### Posting Timing

**Immediate (On Authorization)**: 
- Affects GL, sub-ledgers, and balance calculations
- Shows in reports immediately
- Reversible via reversal voucher if needed

**Delayed (On Bank Confirmation)**:
- Only for bank reconciliation entries
- Timing differences captured
- Month-end reconciliation handled separately

---

## 📑 Ledger Updates

### General Ledger (GL)

**Cash Ledger (Account 100)**:
```
Date       | Particulars              | Dr     | Cr     | Balance
2025-12-17 | Opening Balance          | —      | —      | 50,000
2025-12-17 | CPV/2025/0001           | —      | 5,000  | 45,000
2025-12-17 | BPV/2025/0001 (Bank Dep)| 15,000 | —      | 60,000
```

**Bank Ledger (Account 110)**:
```
Date       | Particulars              | Dr     | Cr     | Balance
2025-12-17 | Opening Balance          | —      | —      | 500,000
2025-12-17 | BPV/2025/0001           | —      | 100,000| 400,000
2025-12-17 | Interest Credited       | 2,000  | —      | 402,000
```

**Expense Ledger (Account 600)**:
```
Date       | Particulars              | Dr     | Cr     | Balance
2025-12-17 | Opening Balance          | —      | —      | 15,000
2025-12-17 | CPV/2025/0001           | 2,000  | —      | 17,000
```

**Accounts Payable (Account 201)**:
```
Date       | Particulars              | Dr     | Cr     | Balance
2025-12-17 | Invoice INV/2025/500    | —      | 100,000| 100,000
2025-12-17 | BPV/2025/0001           | 100,000| —      | 0
```

### Sub-Ledgers

**Cash Book** (Combined GL + Sub-ledger):
```
Date       | Description             | Receipt | Payment | Balance
2025-12-17 | Opening                 | —       | —       | 50,000
2025-12-17 | CPV/2025/0001          | —       | 5,000   | 45,000
2025-12-17 | Bank Deposit Received   | 15,000  | —       | 60,000
2025-12-17 | Closing                 | —       | —       | 60,000
```

**Supplier Ledger** (ABC Supplies Ltd):
```
Date       | Particulars              | Dr     | Cr     | Balance
2025-12-01 | Invoice INV/2025/500    | —      | 100,000| 100,000 Cr
2025-12-17 | BPV/2025/0001 Payment   | 100,000| —      | 0
```

### Report Updates

**Balance Sheet**:
- Assets: Cash/Bank accounts reduced
- Liabilities: Payables reduced (payments settle debts)
- Equity: Unchanged (unless dividend/capital return)

**Profit & Loss**:
- Expenses: Increased by CPV amounts
- Operating cash flow: Decreased by payments
- Expense category breakdowns: Updated

**Daily Bank Position**:
```
Opening Cash Balance:    50,000
Add: Receipts:          +15,000
Less: Payments:          -5,000
Closing Cash Balance:    60,000
```

**Monthly Trial Balance**:
```
Account | Debit   | Credit  | Balance
100     | —       | —       | 60,000 Dr
110     | —       | —       | 402,000 Dr
201     | —       | —       | 0
600     | 17,000  | —       | 17,000 Dr
701     | —       | 50,000  | 50,000 Cr
...     | —       | —       | ...
TOTAL   | X       | X       | (Balanced)
```

---

## 🗄️ Data Models

### Model: CashPaymentVoucher

```python
class CashPaymentVoucher(models.Model):
    # Identifiers
    voucher_number = CharField(unique=True)
    voucher_date = DateField()
    entity = ForeignKey(Entity)
    
    # Payee Information
    payee_name = CharField()
    payee_id = CharField(null=True)  # Link to stakeholder if employee
    
    # Amounts
    total_amount = DecimalField(10, 2)
    
    # Metadata
    description = TextField(blank=True)
    reference_document = CharField(blank=True)
    
    # Workflow Status
    status = CharField(choices=[
        ('DRAFT', 'Draft'),
        ('SUBMITTED_FOR_APPROVAL', 'Submitted for Approval'),
        ('CHECKED', 'Checked'),
        ('REJECTED', 'Rejected'),
        ('AUTHORIZED', 'Authorized'),
        ('GL_POSTED', 'GL Posted'),
        ('REVERSED', 'Reversed'),
        ('CANCELLED', 'Cancelled')
    ])
    
    # Approvals
    maker = ForeignKey(User, related_name='cash_payment_made_by')
    maker_date = DateTimeField(auto_now_add=True)
    
    checker = ForeignKey(User, related_name='cash_payment_checked_by', null=True)
    checker_date = DateTimeField(null=True)
    checker_comments = TextField(blank=True)
    
    approver = ForeignKey(User, related_name='cash_payment_approved_by', null=True)
    approver_date = DateTimeField(null=True)
    approver_comments = TextField(blank=True)
    
    # GL Posting
    journal_entry = ForeignKey(JournalEntry, null=True)
    gl_posting_date = DateTimeField(null=True)
    
    # Audit
    created_by = ForeignKey(User, related_name='cash_payment_created')
    created_date = DateTimeField(auto_now_add=True)
    updated_date = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-voucher_date', '-id']
        indexes = [
            Index(fields=['entity', 'voucher_date']),
            Index(fields=['status']),
            Index(fields=['voucher_number'])
        ]
```

### Model: CashPaymentLine

```python
class CashPaymentLine(models.Model):
    # Relationships
    voucher = ForeignKey(CashPaymentVoucher, on_delete=CASCADE)
    
    # Line Details
    line_number = PositiveIntegerField()
    description = CharField()
    amount = DecimalField(10, 2)
    
    # GL Accounts
    expense_account = ForeignKey(GLAccount, on_delete=PROTECT)
    
    # Supporting Documents
    supporting_document = FileField(upload_to='cash_payments/', null=True)
    document_reference = CharField(blank=True)
    
    # Tax
    tax_amount = DecimalField(10, 2, default=0)
    tax_rate = DecimalField(5, 2, default=0)
    
    # GL Entry Link
    gl_entry = ForeignKey(GLEntry, null=True)
    
    class Meta:
        ordering = ['voucher', 'line_number']
        unique_together = [['voucher', 'line_number']]
```

### Model: BankPaymentVoucher

```python
class BankPaymentVoucher(models.Model):
    # Identifiers
    voucher_number = CharField(unique=True)
    voucher_date = DateField()
    entity = ForeignKey(Entity)
    
    # Payee Information
    payee_name = CharField()
    payee_id = CharField(null=True)
    
    # Bank Details
    bank_account = ForeignKey(BankAccount)
    beneficiary_account_number = CharField()
    beneficiary_ifsc = CharField()
    beneficiary_bank = CharField()
    
    # Amounts
    total_amount = DecimalField(10, 2)
    
    # Metadata
    description = TextField(blank=True)
    payment_mode = CharField(choices=[
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
        ('DD', 'Demand Draft')
    ])
    
    # Workflow Status
    status = CharField(choices=[
        ('DRAFT', 'Draft'),
        ('SUBMITTED_FOR_APPROVAL', 'Submitted for Approval'),
        ('CHECKED', 'Checked'),
        ('REJECTED', 'Rejected'),
        ('AUTHORIZED', 'Authorized'),
        ('GL_POSTED', 'GL Posted'),
        ('IN_TRANSIT', 'In Transit'),
        ('CLEARED', 'Cleared'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
        ('CANCELLED', 'Cancelled')
    ])
    
    # Approvals
    maker = ForeignKey(User, related_name='bank_payment_made_by')
    maker_date = DateTimeField(auto_now_add=True)
    
    checker = ForeignKey(User, related_name='bank_payment_checked_by', null=True)
    checker_date = DateTimeField(null=True)
    checker_comments = TextField(blank=True)
    
    approver = ForeignKey(User, related_name='bank_payment_approved_by', null=True)
    approver_date = DateTimeField(null=True)
    approver_comments = TextField(blank=True)
    
    # GL Posting
    journal_entry = ForeignKey(JournalEntry, null=True)
    gl_posting_date = DateTimeField(null=True)
    
    # Bank Integration
    bank_reference = CharField(blank=True)
    bank_status = CharField(blank=True)
    bank_clearing_date = DateField(null=True)
    
    # Audit
    created_by = ForeignKey(User, related_name='bank_payment_created')
    created_date = DateTimeField(auto_now_add=True)
    updated_date = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-voucher_date', '-id']
        indexes = [
            Index(fields=['entity', 'voucher_date']),
            Index(fields=['status']),
            Index(fields=['voucher_number'])
        ]
```

### Model: BankPaymentLine

```python
class BankPaymentLine(models.Model):
    # Relationships
    voucher = ForeignKey(BankPaymentVoucher, on_delete=CASCADE)
    
    # Line Details
    line_number = PositiveIntegerField()
    description = CharField()
    amount = DecimalField(10, 2)
    
    # GL Accounts (can be either payable or expense)
    payable_account = ForeignKey(GLAccount, null=True, related_name='bank_payment_payable')
    expense_account = ForeignKey(GLAccount, null=True, related_name='bank_payment_expense')
    
    # References
    po_reference = CharField(blank=True)
    invoice_reference = CharField(blank=True)
    
    # Supporting Documents
    supporting_document = FileField(upload_to='bank_payments/', null=True)
    document_reference = CharField(blank=True)
    
    # Tax
    tax_amount = DecimalField(10, 2, default=0)
    tax_rate = DecimalField(5, 2, default=0)
    net_amount = DecimalField(10, 2)
    
    # GL Entry Link
    gl_entry = ForeignKey(GLEntry, null=True)
    
    class Meta:
        ordering = ['voucher', 'line_number']
        unique_together = [['voucher', 'line_number']]
```

---

## ⚖️ Receipt vs Payment Comparison

| Aspect | Cash/Bank Receipt | Cash/Bank Payment |
|--------|---|---|
| **Purpose** | Money coming into organization | Money going out from organization |
| **Voucher Type** | CRV / BRV | CPV / BPV |
| **Trigger** | Sale, capital contribution, loan received | Expense, supplier payment, loan repayment |
| **Voucher Entry** | Accountant records receipt | Accountant records payment request |
| **GL Debit** | Cash/Bank (Increases asset) | Expense/Payable (Increases expense/reduces liability) |
| **GL Credit** | Income/Capital/Receivable (Reduces receivable or increases equity/income) | Cash/Bank (Reduces asset) |
| **Balance Sheet Impact** | Increases assets, increases equity/income | Decreases assets, reduces liabilities/increases expenses |
| **Cash Flow** | Positive (inflow) | Negative (outflow) |
| **Audit Focus** | Validate source of funds, anti-fraud | Validate authorization, budget compliance |
| **Supporting Docs** | Deposit slip, invoice copy, receipt | Invoice, expense claim, authorization form |
| **Bank Integration** | Deposit confirmation | Transfer execution & confirmation |
| **Typical Accounts Used** | 100-Cash, 110-Bank, 600-Income | 600-Expenses, 201-Payables, 100-Cash, 110-Bank |
| **Status Workflow** | DRAFT → APPROVED → AUTHORIZED → POSTED | DRAFT → SUBMITTED → CHECKED → AUTHORIZED → POSTED |
| **GL Posting Trigger** | On AUTHORIZED | On AUTHORIZED (advanced) or ON CLEARED (reconciled) |
| **Reversibility** | Reversible via reversal receipt | Reversible via reversal payment |
| **Reconciliation** | Daily bank reconciliation | Bank reconciliation + clearing |

---

## 📝 Implementation Details

### Phase 1: Database Models (Done in Phase 2.1)
- 4 new models: CashPaymentVoucher, CashPaymentLine, BankPaymentVoucher, BankPaymentLine
- Migration: Create tables with proper indexes
- Relationships: Link to GLAccount, User, Entity, JournalEntry

### Phase 2: Views & Forms (Done in Phase 2.2)
- List views with filtering and pagination
- Create/edit forms with validation
- Approval views with comment capture
- Authorization views with GL preview
- Report dashboards (payment summary, payee summary)

### Phase 3: Signal Handlers (Done in Phase 2.3)
- Auto-create GL entries on authorization
- Update cash/bank balances
- Update ledger summaries
- Trigger bank reconciliation (if applicable)

### Phase 4: Templates (Done in Phase 2.4)
- Payment entry form
- Approval workflow UI
- Report dashboards
- Bank reconciliation UI

### Phase 5: URL Configuration (Done in Phase 2.5)
- Payment list endpoints
- Payment detail/edit endpoints
- Approval workflow endpoints
- Report endpoints

### Phase 6: Permissions & Security (Done in Phase 2.6)
- View payment permissions
- Create/edit permissions
- Approve/authorize permissions
- Delete/reverse permissions

### Phase 7: Testing & Deployment (Done in Phase 2.7)
- Unit tests for GL posting logic
- Integration tests for workflow
- End-to-end workflow tests
- Production deployment with verification

---

## 🎯 Success Criteria

✅ All models created with proper relationships  
✅ Migrations run successfully  
✅ GL posting logic verified with test cases  
✅ Approval workflow tested end-to-end  
✅ Reports showing correct balances  
✅ Bank reconciliation working (if integrated)  
✅ Production deployment verified  
✅ User training completed  

---

## 📞 Integration Points

**With Existing System**:
- Receipt vouchers (compare/reconcile)
- GL and sub-ledgers (post entries)
- Bank accounts (update balances)
- Approval workflow framework (reuse pattern)
- Reporting engine (query payment data)
- Audit logging (track changes)

**Future Integrations**:
- Bank APIs (auto-execution of transfers)
- Email notifications (approval alerts)
- Budget management (budget vs actual)
- Accounts payable aging (supplier aging reports)
- Expense management (employee reimbursements)

---

**Ready for Development** ✅
