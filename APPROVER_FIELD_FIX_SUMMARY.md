# Capital Contribution Review Form - Approver Field Fix

## Problem
The `CapitalContributionReviewForm` was displaying the `approver` field to both first and second reviewers. The approver field should only appear for the second reviewer since:
- **First reviewer**: Reviews the contribution but does NOT assign an approver
- **Second reviewer**: Reviews the contribution AND assigns an approver for the approval stage

## Solution
Modified the form to conditionally include the `approver` field based on the review stage.

### Changes Made

#### 1. **Updated `CapitalContributionReviewForm` in `accounting/stakeholder_forms.py`**
   - Added `is_second_review` parameter to `__init__` method
   - Changed `approver` field from `required=True` to `required=False`
   - Dynamically delete `approver` field for first review (`if not is_second_review: del self.fields['approver']`)
   - Updated clean method to validate approver only for second review
   - Changed Meta fields from `['review_notes_2', 'approval_notes']` to `['review_notes', 'approval_notes']`
   - Form's `save()` method only sets `assigned_approver` if `is_second_review=True`

#### 2. **Updated `CapitalContributionSecondReviewView` in `accounting/stakeholder_workflow_views.py`**
   - Added `get_form_kwargs()` method to pass `is_second_review=True` to the form
   - No changes to `form_valid()` - the form's save method handles setting `assigned_approver`

#### 3. **Updated `CapitalContributionReviewView` in `shareholder/views.py`**
   - Added `get_form_kwargs()` method to dynamically pass `is_second_review` based on workflow_status
   - Updated `get_form()` to check if 'approver' field exists before filtering approvers
   - Fixed `form_valid()` to:
     - Use `form.cleaned_data.get('approver')` instead of `request.POST.get()`
     - Save review notes to appropriate field (`review_notes` for first, `review_notes_2` for second)
     - Set `assigned_approver` instead of `approved_by`
     - Save review notes before saving the instance

## Workflow

### First Review
- Form displays: `verified_receipts`, `review_notes`, `approval_notes`
- Form does NOT display: `approver`
- On save: Sets `reviewed_by`, `reviewed_at`, `review_notes`, moves to `FIRST_REVIEW_COMPLETED`

### Second Review
- Form displays: `verified_receipts`, `review_notes`, `approval_notes`, `approver`
- `approver` field is required
- On save: Sets `reviewed_by_2`, `reviewed_at_2`, `review_notes_2`, `assigned_approver`, moves to `REVIEWED`

## Benefits
✅ Cleaner user interface - first reviewers don't see irrelevant approver field
✅ Proper separation of concerns - assignment only happens in second review
✅ Consistent with workflow logic
✅ Form validation ensures approver is selected for second review

## Field Mapping
- `CapitalContribution.assigned_approver` - Set by second reviewer to assign for approval
- `CapitalContribution.approved_by` - Set by approver when approving
- These are separate fields allowing for delegation of approval responsibility
