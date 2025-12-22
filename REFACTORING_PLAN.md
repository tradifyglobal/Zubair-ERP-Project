# Shareholder Capital Contribution Workflow Refactoring
# Strategy & Implementation Plan

## Overview
Move the approval workflow from CapitalContribution model to Cash/Bank Receipt transactions.
This aligns with real-world accounting practice where transactions are approved before posting.

## Architecture Change

### BEFORE (Current - Incorrect)
```
CapitalContribution
  ├─ DRAFT
  ├─ SUBMITTED
  ├─ FIRST_REVIEW_COMPLETED
  ├─ REVIEWED
  ├─ APPROVED ← Journal entries created here
  └─ REJECTED
```

### AFTER (Target - Correct)
```
CashReceiptLine / BankReceiptLine
  ├─ DRAFT
  ├─ PENDING_APPROVAL
  ├─ APPROVED ← Auto-triggers capital contribution posting
  ├─ AUTHORIZED
  ├─ POSTED ← Journal entries created
  └─ REJECTED

CapitalContribution
  └─ SIMPLE RECORD ← Links to source transaction
      ├─ source_cash_receipt or source_bank_receipt FK
      ├─ is_auto_posted = True (set when source transaction approved)
      └─ No workflow, no submit/review/approve buttons
```

## Files Affected

### 1. Models (accounting/models.py)
- ADD: source_cash_receipt, source_bank_receipt, is_auto_posted fields
- DEPRECATE: workflow_status, submitted_by, reviewed_by, approved_by, etc. (keep for migration safety)
- UPDATE: save() method to prevent manual workflow changes

### 2. Views (shareholder/views.py)
- REMOVE: CapitalContributionSubmitView
- REMOVE: CapitalContributionReviewView
- REMOVE: CapitalContributionApproveView
- REMOVE: CapitalContributionRejectView
- KEEP: CapitalContributionListView, DetailView (read-only), CreateView (for manual entry)

### 3. URLs (shareholder/urls.py)
- REMOVE: capital-contribution-submit
- REMOVE: capital-contribution-review
- REMOVE: capital-contribution-approve
- REMOVE: capital-contribution-reject

### 4. Forms (shareholder_forms.py / accounting/stakeholder_forms.py)
- REMOVE: CapitalContributionSubmitForm
- REMOVE: CapitalContributionReviewForm
- REMOVE: CapitalContributionApprovalForm
- UPDATE: CapitalContributionForm (remove workflow fields)

### 5. Templates
- UPDATE: capital_contribution_detail.html (remove workflow buttons & status)
- UPDATE: capital_contribution_list.html (remove workflow status column)
- REMOVE: capital_contribution_submit.html
- REMOVE: capital_contribution_review.html
- REMOVE: capital_contribution_approve.html

### 6. Cash/Bank Receipt Views (cash_views.py)
- UPDATE: Approval logic to auto-create capital contribution & GL entries
- ADD: Method to link capital contribution to receipt

## Implementation Steps

### Phase 1: Database & Models
1. Create migration 0020_capital_contribution_simplification.py
2. Add source_cash_receipt, source_bank_receipt, is_auto_posted fields
3. Keep workflow fields (don't delete) for backward compatibility

### Phase 2: Views & Forms
1. Disable workflow views by marking them as deprecated
2. Remove workflow forms
3. Update CapitalContributionForm to exclude workflow fields

### Phase 3: Templates
1. Remove workflow UI from capital contribution pages
2. Show linked source transaction instead
3. Show "Auto-posted on [date]" instead of "Approved on [date]"

### Phase 4: Cash/Bank Receipt Integration
1. When receipt is APPROVED: auto-create capital contribution with source_cash_receipt/source_bank_receipt
2. Auto-post GL entries at approval time
3. Set is_auto_posted=True

### Phase 5: Testing & Validation
1. Test capital contribution creation from bank receipt approval
2. Verify GL entries created automatically
3. Verify capital account updated
4. Verify shareholder ledger reflects contribution

## SQL Migration Pattern
```sql
-- Add new fields
ALTER TABLE accounting_capitalcontribution 
ADD COLUMN source_cash_receipt_id INTEGER REFERENCES accounting_cashreceiptline(id),
ADD COLUMN source_bank_receipt_id INTEGER REFERENCES accounting_bankreceiptline(id),
ADD COLUMN is_auto_posted BOOLEAN DEFAULT FALSE;

-- Keep existing workflow fields for safety (can be deprecated in future)
```

## Backward Compatibility
- Existing workflow fields remain in DB
- Set read-only in forms
- UI hidden but data preserved
- Future: Can clean up in next major version

## Success Criteria
✓ CapitalContribution is simple read-only record
✓ Approval workflow only at transaction level
✓ Capital contributions auto-created from approved receipts
✓ GL entries auto-posted on receipt approval
✓ Shareholder ledger updates automatically
✓ No manual submission/review/approval for contributions
✓ Audit trail shows transaction approval → contribution posting
