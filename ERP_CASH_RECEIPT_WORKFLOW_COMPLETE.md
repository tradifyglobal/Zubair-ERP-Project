# ERP Cash/Bank Receipt Workflow - Complete Implementation Guide

This document describes the complete 7-step ERP workflow for Cash and Bank Receipts with proper authorization hierarchy, GL posting, and financial reporting.

## 1. Transaction Initiation

**Business Scenario:**
- Shareholder deposits money (cash or bank transfer)
- Supporting documentation: Board resolution, investment agreement, approval memo

**System Entry Point:**
- User navigates to: **Accounting → Cash/Bank Management → New Cash Receipt**
- Fills in receipt details with shareholder information

**Key Fields:**
```
- Transaction Date
- Shareholder/Payer Name
- Mode (Cash/Bank Transfer)
- Amount (transaction currency)
- Purpose (Capital Contribution, etc.)
- Supporting Documents (attachments)
- Description/Notes
```

---

## 2. Receipt Entry in ERP

**Process:**
1. Finance team enters Cash Receipt Voucher (CRV) or Bank Receipt Voucher (BRV)
2. System auto-populates:
   - Stakeholder (linked from shareholder master)
   - Currency conversion (if applicable)
   - GL account mappings

**Status:** `DRAFT`

**Models Involved:**
- `CashReceiptLine` / `BankReceiptLine`
- `Stakeholder` (payer identification)
- `Currency` (exchange rates)
- `Account` (GL account selection)

**Form Validation:**
```python
- Amount > 0
- Shareholder selected
- Debit account selected (Share Capital account)
- Credit account defaulted (Cash/Bank account)
- All required fields populated
```

---

## 3. Authorization Workflow (Maker → Checker → Approver)

### 3A. Maker: Submit for Review

**Role:** Finance Clerk / Accountant
**Action:** Click "Submit for Approval"

**What Happens:**
```
Status: DRAFT → PENDING_APPROVAL
```

**Audit Trail:**
- User: {user.name}
- Timestamp: {action_time}
- Action: "submit_for_approval"

---

### 3B. Checker: Review & Approve

**Role:** Finance Manager / Assistant Manager
**Action:** Click "Approve"

**Validation Checks:**
```
- Amount vs. shareholder limit (configurable)
- Supporting documents attached
- Account details correct
- No duplicate entries for same shareholder/date
- Stakeholder information complete
```

**What Happens:**
```
Status: PENDING_APPROVAL → APPROVED
Fields Updated:
- approved_by: {current_user}
- approved_date: {now}
- approval_notes: {optional}
```

**Audit Trail:**
- User: {user.name}
- Timestamp: {action_time}
- Action: "approve_receipt"
- Notes: {approval_notes}

---

### 3C. Approver: Authorization & GL Posting

**Role:** CFO / Finance Head / Authorized Signatory
**Action:** Click "Authorize & Post"

**Pre-Authorization Checks:**
```
- Status is APPROVED
- All required fields complete
- No conflicting GL entries
- Entity has required GL accounts
```

**What Happens:**
1. Creates GL Entries:

```
Journal Entry: CASH-RECEIPT-{receipt_id}
Entry Date: {receipt_date}
Status: AUTHORIZED (Posted)

   Dr. Share Capital Account (3000-01)      Amount
   Cr. Cash Account (100001)                 Amount
```

2. Updates Receipt Status:
```
Status: APPROVED → AUTHORIZED (then POSTED)
Posted_by: {current_user}
Posted_date: {now}
GL_reference: CASH-RECEIPT-{receipt_id}
```

3. Auto-creates Capital Contribution Record:
```
Capital Contribution:
- Stakeholder: {linked_shareholder}
- Amount: {receipt_amount}
- Currency: {receipt_currency}
- Status: COMPLETED
- Source: CASH-RECEIPT-{receipt_id}
```

**Audit Trail:**
- User: {user.name}
- Timestamp: {action_time}
- Action: "authorize_and_post"
- GL Entries Created: [{ledger_entry_ids}]
- Capital Contribution: {contribution_id}

---

### 3D. Optional: Rejection Path

**Role:** Approver (at APPROVED stage)
**Action:** Click "Reject"

**What Happens:**
```
Status: APPROVED → REJECTED
Rejected_by: {current_user}
Rejected_date: {now}
Rejection_reason: {optional}
```

**Consequences:**
- No GL entries created
- No capital contribution recorded
- Stakeholder can resubmit if needed

**Audit Trail:**
- User: {user.name}
- Timestamp: {action_time}
- Action: "reject_receipt"
- Reason: {rejection_reason}

---

## 4. Posting to General Ledger (GL)

**Automatic GL Entry Creation (upon AUTHORIZATION):**

### Cash Receipt Example:
```
Date: 2025-12-17
Voucher: CASH-RECEIPT-1
Narration: Cash received from Sajaz Ahmed - Capital contribution

Dr. Share Capital - Sajaz Ahmed (3000-01)     INR 100,000.00
    Cr. Cash In Hand (100001)                             INR 100,000.00
```

### Bank Receipt Example:
```
Date: 2025-12-17
Voucher: BANK-RECEIPT-2
Narration: Bank transfer from Zubair Ahmed - Capital contribution

Dr. Bank Account - HDFC (1001)                  INR 50,000.00
    Cr. Share Capital - Zubair Ahmed (3000-02)                INR 50,000.00
```

**GL Entry Fields Captured:**
```
- Entry Type: DEBIT / CREDIT
- Account: GL account number
- Amount: Transaction amount
- Description: Auto-generated from receipt
- Entry Date: Receipt date
- Reference Number: CASH-RECEIPT-{id} / BANK-RECEIPT-{id}
- Is Posted: TRUE
- Workflow Status: AUTHORIZED
- Created By: {authorizing_user}
- Created Date: {authorization_date}
```

---

## 5. Ledger & Sub-Ledger Updates

### 5A. General Ledger Update

**Cash Account (100001):**
```
Opening Balance: 100,000.00
+ Credit Entry (Receipt)    50,000.00
= Closing Balance: 150,000.00
```

**Share Capital Account (3000-01):**
```
Opening Balance: 0.00
+ Debit Entry (Receipt)     50,000.00
= Closing Balance: 50,000.00
```

### 5B. Sub-Ledger: Shareholder Investment Register

**New Model: `ShareholderInvestmentRegister`**

```python
class ShareholderInvestmentRegister(models.Model):
    """
    Sub-ledger tracking shareholder contributions.
    
    Fields:
    - entity: ForeignKey(Entity)
    - stakeholder: ForeignKey(Stakeholder)
    - contribution_date: DateField
    - amount: DecimalField (company currency)
    - source_receipt: ForeignKey(CashReceiptLine / BankReceiptLine)
    - investment_type: ('CAPITAL', 'LOAN', 'DIVIDEND_REINVESTMENT')
    - currency: ForeignKey(Currency) - original currency
    - exchange_rate: DecimalField - conversion rate used
    - status: ('PENDING', 'COMPLETED', 'CANCELLED')
    - created_date: DateTimeField
    - created_by: ForeignKey(User)
    
    Indexed By: stakeholder, entity, contribution_date
```

**Sample Data:**
```
Shareholder: Sajaz Ahmed
Investment ID: SI-001-2025-12-17
Date: 2025-12-17
Amount (INR): 100,000.00
Type: CAPITAL CONTRIBUTION
Source: CASH-RECEIPT-1
Exchange Rate: 1.0 (INR to INR)
Status: COMPLETED
Created By: Finance Manager
```

---

## 6. Financial Reporting

### 6A. Balance Sheet Impact

**Equity Section:**
```
Share Capital:
  - Sajaz Ahmed (3000-01)        INR 100,000.00
  - Zubair Ahmed (3000-02)       INR 50,000.00
                                  ─────────────
  Total Share Capital:            INR 150,000.00
```

### 6B. Cash Flow Statement

**Operating Activities:**
```
Shareholder Contributions (Capital)     INR 150,000.00
```

### 6C. Shareholder Investment Report

**View: `ShareholderInvestmentReportView`**

```python
class ShareholderInvestmentReportView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """
    Report showing all shareholder contributions.
    
    Columns:
    - Shareholder Name
    - Investment Count
    - Total Invested (Company Currency)
    - First Investment Date
    - Last Investment Date
    - Average Investment Size
    - Investment Status Count (Pending/Completed/Cancelled)
    """
```

**Sample Report:**
```
Shareholder Investment Summary - Testing Entity (2025-12-17)

Shareholder         | Contributions | Total Amount | First Date | Last Date  | Status
─────────────────────────────────────────────────────────────────────────────────────
Sajaz Ahmed         | 2             | 150,000.00   | 2025-11-01 | 2025-12-17 | Active
Zubair Ahmed        | 1             | 50,000.00    | 2025-12-10 | 2025-12-10 | Active
Fatima Khan         | 1             | 25,000.00    | 2025-12-15 | 2025-12-15 | Pending
─────────────────────────────────────────────────────────────────────────────────────
TOTAL               | 4             | 225,000.00   |            |            |
```

### 6D. GL Dashboard Cash Position

**Updated CashPositionView:**

```
Cash Position Summary
──────────────────────

Cash Accounts:
  - Cash In Hand (100001)         INR 150,000.00
  - Bank - HDFC (1001)            INR 75,000.00
  ─────────────────────────────────────────────
  Total Cash & Bank:              INR 225,000.00

Capital Contributions:
  - Completed                      INR 225,000.00
  - Pending                        INR 25,000.00
  - Rejected/Cancelled             INR 0.00
```

---

## 7. Audit Trail & Compliance

### Audit Log Entries

**All Actions Logged:**

```python
AuditLog.objects.create(
    user=request.user,
    action='{action_type}',
    model_name='CashReceiptLine',
    object_id=receipt_id,
    entity=request.entity,
    timestamp=now(),
    description='{detailed_description}',
    changes={
        'before': {...},
        'after': {...}
    },
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT')
)
```

**Action Types Tracked:**
```
- create_receipt
- submit_for_approval
- approve_receipt
- authorize_and_post
- reject_receipt
- gl_entries_created
- capital_contribution_created
```

**Audit Report:**

```
Timeline of Cash Receipt CR-001 (Sajaz Ahmed - 100,000 INR)
─────────────────────────────────────────────────────────

2025-12-17 09:30 AM | Accounting Clerk (Ahmed) | CREATE_RECEIPT
                    | Saved as DRAFT
                    | Amount: 100,000 INR

2025-12-17 10:15 AM | Finance Manager (Fatima) | SUBMIT_FOR_APPROVAL
                    | Status: DRAFT → PENDING_APPROVAL
                    | Notes: "Document verified"

2025-12-17 02:30 PM | Finance Manager (Fatima) | APPROVE_RECEIPT
                    | Status: PENDING_APPROVAL → APPROVED
                    | Notes: "Approved subject to CFO authorization"

2025-12-17 04:45 PM | CFO (Ali Khan) | AUTHORIZE_AND_POST
                    | Status: APPROVED → AUTHORIZED
                    | GL Entries Created: 2 (Dr/Cr)
                    | Capital Contribution ID: CAP-001-2025
                    | Posted to GL

2025-12-18 09:00 AM | Auditor (Ravi) | VIEW_AUDIT_TRAIL
                    | Verified all approvals and GL entries
```

---

## Implementation Checklist

### Models & Database
- [x] CashReceiptLine / BankReceiptLine with workflow_status
- [x] LedgerEntry with GL posting
- [x] CapitalContribution tracking
- [ ] **NEW:** ShareholderInvestmentRegister (sub-ledger)
- [x] AuditLog for compliance
- [x] Stakeholder (shareholder master)

### Views & Workflows
- [x] CashReceiptApprovalView (Submit)
- [x] CashReceiptAuthorizationView (Approve)
- [x] CashReceiptAuthorizationView (Authorize)
- [x] CashReceiptRejectView (Reject)
- [x] Similar for BankReceiptLine, CashPaymentLine, BankPaymentLine
- [ ] **ENHANCE:** Add multi-level approval permissions
- [ ] **NEW:** ShareholderInvestmentReportView

### Templates
- [x] Cash Receipt list with workflow buttons
- [x] Approval view with document preview
- [ ] **ENHANCE:** Add approval comments/notes field
- [ ] **NEW:** Shareholder investment register report

### Reports
- [ ] **NEW:** Shareholder Investment Summary
- [ ] **NEW:** Cash/Bank Receipt Audit Trail Report
- [ ] **ENHANCE:** Balance Sheet - Equity section
- [ ] **ENHANCE:** Cash Flow Statement

### Permissions & Security
- [ ] **NEW:** Finance Manager can APPROVE only
- [ ] **NEW:** CFO/Finance Head can AUTHORIZE only
- [ ] **NEW:** Audit view access control
- [ ] **NEW:** Signature/approval workflows with digital signatures

### Testing
- [ ] End-to-end workflow (Submit → Approve → Authorize)
- [ ] GL entry verification
- [ ] Capital contribution auto-creation
- [ ] Audit trail completeness
- [ ] Financial reporting accuracy
- [ ] Multi-currency handling
- [ ] Permission boundaries

---

## SQL Views for Reporting

### Capital Contributions by Stakeholder
```sql
SELECT 
    s.name AS shareholder_name,
    COUNT(cc.id) AS contribution_count,
    SUM(cc.amount_company_currency) AS total_amount,
    MIN(cc.contribution_date) AS first_contribution,
    MAX(cc.contribution_date) AS last_contribution,
    STRING_AGG(cc.status, ', ') AS contribution_statuses
FROM accounting_stakeholder s
LEFT JOIN accounting_capitalcontribution cc ON s.id = cc.stakeholder_id
WHERE cc.entity_id = {entity_id}
GROUP BY s.id, s.name
ORDER BY total_amount DESC;
```

### Cash Receipt Authorization Timeline
```sql
SELECT 
    crl.id,
    crl.reference_number,
    s.name AS shareholder,
    crl.debit_amount,
    crl.workflow_status,
    al.user_id,
    al.timestamp,
    al.action,
    al.description
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
LEFT JOIN accounting_auditlog al ON al.object_id = crl.id 
    AND al.model_name = 'CashReceiptLine'
WHERE crl.entity_id = {entity_id}
ORDER BY crl.date DESC, al.timestamp ASC;
```

---

## Next Steps for Implementation

1. **Create ShareholderInvestmentRegister model** (sub-ledger)
2. **Enhance CashReceiptLine/BankReceiptLine** with approval notes field
3. **Create ShareholderInvestmentReportView** for reporting
4. **Implement permission-based approval hierarchy** (Maker/Checker/Approver roles)
5. **Add approval workflow status tracking** (who approved, when, with comments)
6. **Generate financial reports** automatically from GL and sub-ledgers
7. **Create audit trail dashboard** for compliance
8. **Add digital signature support** (optional, for regulatory compliance)
