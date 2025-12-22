# Implementation Guide: Capital Contribution Workflow Refactoring

## ✅ COMPLETED STEPS

### 1. URL Changes
- **File**: `shareholder/urls.py`
- **Status**: ✅ DONE
- **Changes**: Removed workflow URLs (submit, review, approve, reject)
- **Result**: Capital contribution URLs now only show: list, detail, create, edit, export, import

### 2. Migration Created
- **File**: `accounting/migrations/0020_capital_contribution_simplification.py`
- **Status**: ✅ CREATED
- **Changes**: Adds fields for source transaction tracking
  - `source_cash_receipt` (FK to CashReceiptLine)
  - `source_bank_receipt` (FK to BankReceiptLine)
  - `is_auto_posted` (Boolean flag)

## 🔄 NEXT STEPS (Manual Implementation)

### Step 1: Apply Migration to Database
```bash
python manage.py migrate accounting 0020_capital_contribution_simplification
```

### Step 2: Update Models (accounting/models.py)

Add these fields to CapitalContribution class:

```python
class CapitalContribution(models.Model):
    # ... existing fields ...
    
    # Source Transaction Tracking (NEW - replaces workflow)
    source_cash_receipt = models.ForeignKey(
        'accounting.CashReceiptLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_contributions',
        help_text='Source cash receipt that triggered this contribution'
    )
    
    source_bank_receipt = models.ForeignKey(
        'accounting.BankReceiptLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_contributions',
        help_text='Source bank receipt that triggered this contribution'
    )
    
    is_auto_posted = models.BooleanField(
        default=False,
        help_text='True if GL entries were auto-created from approved transaction'
    )
    
    # Add helper method
    def get_source_transaction(self):
        """Returns the source cash/bank receipt if available."""
        return self.source_cash_receipt or self.source_bank_receipt
    
    def mark_as_auto_posted(self):
        """Mark this contribution as automatically posted from transaction approval."""
        self.is_auto_posted = True
        self.save()
```

### Step 3: Update Views (shareholder/views.py)

**COMMENT OUT OR REMOVE** these view classes:
- `CapitalContributionSubmitView`
- `CapitalContributionReviewView`
- `CapitalContributionApproveView`
- `CapitalContributionRejectView`

Replace with a note:
```python
# ==================== Capital Contribution Workflow Views ====================
# DEPRECATED: Workflow moved to transaction level (CashReceiptLine/BankReceiptLine)
# Capital contributions are now auto-created and posted when source transaction is approved
# No manual submission/review/approval needed at contribution level
#
# CapitalContributionSubmitView - REMOVED
# CapitalContributionReviewView - REMOVED
# CapitalContributionApproveView - REMOVED
# CapitalContributionRejectView - REMOVED
```

### Step 4: Update Templates

**capital_contribution_detail.html**
- REMOVE all workflow buttons (Submit, Review, Approve, Reject)
- REMOVE workflow progress visualization  
- ADD: Show "Source Transaction" section if linked
- ADD: Show "Auto-posted on [date]" instead of approval status

Replace the workflow section with:
```html
<!-- Source Transaction Info -->
{% if contribution.source_cash_receipt %}
    <div class="alert alert-info">
        <strong><i class="mdi mdi-information"></i> Auto-Posted Transaction:</strong>
        This contribution was automatically created and posted from 
        <a href="{% url 'accounting:cash_receipt_detail' contribution.source_cash_receipt.id %}">
            Cash Receipt #{{ contribution.source_cash_receipt.id }}
        </a>
        on {{ contribution.source_cash_receipt.date }}.
    </div>
{% elif contribution.source_bank_receipt %}
    <div class="alert alert-info">
        <strong><i class="mdi mdi-information"></i> Auto-Posted Transaction:</strong>
        This contribution was automatically created and posted from 
        <a href="{% url 'accounting:bank_receipt_detail' contribution.source_bank_receipt.id %}">
            Bank Receipt #{{ contribution.source_bank_receipt.id }}
        </a>
        on {{ contribution.source_bank_receipt.date }}.
    </div>
{% else %}
    <div class="alert alert-warning">
        <strong><i class="mdi mdi-alert"></i> Manual Entry:</strong>
        This contribution was manually created. No auto-posting from transaction.
    </div>
{% endif %}
```

REMOVE these sections:
- "Workflow Status"
- "Workflow Progress" (the visual timeline)
- "Submit" button
- "Review" buttons
- "Approve" button
- "Reject" button

**capital_contribution_list.html**
- REMOVE "Workflow Status" column from table
- REMOVE "Actions" with submit/review/approve buttons
- KEEP: View, Edit, Delete actions only

### Step 5: Update Cash/Bank Receipt Approval Logic

**In cash_views.py**, update approval methods:

```python
def create_capital_contribution_from_receipt(receipt, stakeholder, amount, currency):
    """
    Auto-create a capital contribution when bank/cash receipt is approved.
    Links the contribution to the source transaction.
    """
    from accounting.models import CapitalContribution
    from django.utils import timezone
    
    contribution = CapitalContribution.objects.create(
        entity=receipt.entity,
        stakeholder=stakeholder,
        contribution_date=receipt.date,
        amount=amount,
        currency=currency,
        currency_destination=receipt.entity.default_currency,
        status='COMPLETED',  # Mark as completed since it's from approved transaction
        # NEW: Link to source transaction
        source_bank_receipt=receipt if isinstance(receipt, BankReceiptLine) else None,
        source_cash_receipt=receipt if isinstance(receipt, CashReceiptLine) else None,
        is_auto_posted=True
    )
    
    # Auto-create GL entries
    create_gl_entries_for_contribution(contribution)
    
    return contribution
```

### Step 6: Update Forms (accounting/stakeholder_forms.py)

**Remove these form classes:**
- `CapitalContributionSubmitForm`
- `CapitalContributionReviewForm`
- `CapitalContributionApprovalForm`

**Update CapitalContributionForm:**
```python
class CapitalContributionForm(forms.ModelForm):
    """Form for recording capital contributions."""
    
    class Meta:
        model = CapitalContribution
        # REMOVE: workflow_status, submitted_by, reviewed_by, approved_by, etc.
        fields = [
            'stakeholder',
            'contribution_date',
            'amount',
            'currency',
            'currency_destination',
            'exchange_rate',
            'payment_mode',
            'status',
            'description',
        ]
        widgets = {
            'contribution_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
```

## 📊 WORKFLOW COMPARISON

### OLD WORKFLOW (Remove)
```
User creates Capital Contribution
    ↓
DRAFT (in CapitalContribution)
    ↓
User submits → SUBMITTED
    ↓
Reviewer 1 reviews → FIRST_REVIEW_COMPLETED
    ↓
Reviewer 2 reviews → REVIEWED
    ↓
Approver approves → APPROVED
    ↓
GL entries created
```

### NEW WORKFLOW (Implement)
```
User receives shareholder investment
    ↓
Creates Bank/Cash Receipt (CashReceiptLine/BankReceiptLine)
    ↓
Receipt is DRAFT
    ↓
Receipt submitted for approval
    ↓
Receipt approved
    ↓
AUTOMATIC: CapitalContribution created
AUTOMATIC: GL entries created
AUTOMATIC: is_auto_posted = True
```

## 🧪 TESTING CHECKLIST

- [ ] Migration runs without error: `python manage.py migrate`
- [ ] Capital contribution list page loads
- [ ] Capital contribution detail page loads
- [ ] Create new contribution form works
- [ ] Edit contribution form works
- [ ] NO "Submit" button visible
- [ ] NO "Review" button visible
- [ ] NO "Approve" button visible
- [ ] NO workflow progress display visible
- [ ] Bank receipt approval auto-creates contribution
- [ ] GL entries created when receipt approved
- [ ] Shareholder ledger updated
- [ ] Capital position on balance sheet updated

## 🔗 Related Files to Monitor

- `accounting/models.py` - CapitalContribution model
- `accounting/stakeholder_forms.py` - Forms
- `shareholder/views.py` - Views
- `shareholder/urls.py` - URLs ✅ DONE
- `shareholder/templates/shareholder/capital_contribution_*.html` - Templates
- `accounting/cash_views.py` - Receipt approval logic
- Tests for capital contribution creation and GL posting

## 📝 NOTES

- Workflow fields (submitted_by, reviewed_by, approved_by) are kept in DB for backward compatibility
- These fields will be NULL for new contributions
- Can be deprecated/removed in v2.0 if needed
- Ensure all foreign key relationships are updated
- Update audit logs to track auto-posting
- Consider sending notifications when contribution auto-posted

## 🚀 DEPLOYMENT

1. Create backup of database
2. Apply migration
3. Deploy updated code
4. Test in staging
5. Deploy to production
6. Monitor logs for any issues
