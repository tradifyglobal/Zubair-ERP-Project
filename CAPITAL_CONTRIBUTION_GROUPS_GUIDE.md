# Capital Contribution Group-Based Workflow - Implementation Guide

## Overview
Successfully implemented a group-based review and approval system for Capital Contributions. Instead of manually selecting individual reviewers and approvers from dropdown lists, the system now uses Django Groups where **any member** of the designated groups can perform the review or approval.

## What Changed

### 1. Django Groups Created
Two new groups have been automatically created:
- **Capital Contribution Reviewers** - Members can perform first and second reviews
- **Capital Contribution Approvers** - Members can approve contributions

### 2. New Workflow URLs
The following workflow actions are now available:

| Action | URL Pattern | Who Can Access |
|--------|-------------|----------------|
| Submit | `/accounting/capital-contributions/{id}/submit/` | Contribution creator |
| First Review | `/accounting/capital-contributions/{id}/review-1/` | Any member of Reviewers group |
| Second Review | `/accounting/capital-contributions/{id}/review-2/` | Any member of Reviewers group (must be different from first reviewer) |
| Approve | `/accounting/capital-contributions/{id}/approve/` | Any member of Approvers group |
| Reject | `/accounting/capital-contributions/{id}/reject/` | Any member of Reviewers or Approvers groups |

### 3. Simplified Forms
- **Submit Form**: No longer requires selecting reviewers 1 and 2 - just submit and any reviewer can handle it
- **Review Form**: No longer requires selecting an approver - any approver can handle it after both reviews are complete

## Setup Instructions

### Step 1: Add Users to Groups
You need to add users to the new groups via Django Admin:

1. Go to: `http://192.168.2.185/admin/auth/group/`
2. Click on **"Capital Contribution Reviewers"**
3. Select users from the "Available users" list and move them to "Chosen users"
4. Click **Save**
5. Repeat for **"Capital Contribution Approvers"**

### Step 2: Test the Workflow

#### Create a Test Contribution
1. Go to Capital Contributions list
2. Create a new contribution with status = DRAFT

#### Submit for Review
1. Open the contribution detail page
2. Click "Submit for Review" button
3. Add optional submission notes
4. Click Submit

#### First Review (Any Reviewer)
1. Login as any user in the **Reviewers** group
2. Go to the contribution detail page
3. Click "First Review" button
4. Add review notes (optional)
5. Click "Complete First Review"

#### Second Review (Different Reviewer)
1. Login as a **different** user in the Reviewers group
2. Go to the contribution detail page
3. Click "Second Review" button
4. Add review notes (optional)
5. Click "Complete Second Review"

#### Approve (Any Approver)
1. Login as any user in the **Approvers** group
2. Go to the contribution detail page
3. Click "Approve" button
4. Add approval notes (optional)
5. Click "Approve"
6. Contribution status automatically changes to COMPLETED

#### Reject (Any Reviewer or Approver)
- At any stage (after submission), any member of either group can reject
- Click "Reject" button
- Provide a mandatory rejection reason
- Contribution status changes to CANCELLED

## Workflow Status Flow

```
DRAFT → Submit → SUBMITTED
           ↓
    First Review → FIRST_REVIEW_COMPLETED
           ↓
   Second Review → REVIEWED
           ↓
      Approve → APPROVED (status = COMPLETED)
         
(Reject available at any stage) → REJECTED (status = CANCELLED)
```

## Key Features

### ✅ Benefits
1. **No Assignment Required**: No need to select specific users - any group member can act
2. **Flexibility**: If a reviewer is unavailable, another can step in
3. **Dual Review**: System enforces that second reviewer must be different from first
4. **Group Management**: Easy to add/remove users from groups via Django Admin
5. **Audit Trail**: All reviews, approvals, and rejections are logged with user and timestamp

### 🔒 Security
- Only group members can access workflow actions
- Non-members see permission denied messages
- Workflow status gates ensure proper sequence (can't approve before reviews)
- Second reviewer cannot be same as first reviewer

## Files Modified/Created

### New Files
1. `accounting/management/commands/setup_contribution_groups.py` - Management command
2. `accounting/stakeholder_workflow_views.py` - Workflow view classes
3. `accounting/templates/accounting/capital_contribution_submit.html`
4. `accounting/templates/accounting/capital_contribution_review.html`
5. `accounting/templates/accounting/capital_contribution_approve.html`
6. `accounting/templates/accounting/capital_contribution_reject.html`

### Modified Files
1. `accounting/stakeholder_forms.py` - Removed individual user selection fields
2. `accounting/urls.py` - Added workflow URL patterns

## Database Impact

### No Migration Required
- The CapitalContribution model already has all necessary fields:
  - `workflow_status` (tracks current stage)
  - `submitted_by`, `submitted_at`
  - `reviewed_by`, `reviewed_at`, `review_notes`
  - `reviewed_by_2`, `reviewed_at_2`, `review_notes_2`
  - `approved_by`, `approved_at`, `approval_notes`
  - `rejection_reason`

### Legacy Fields
The old assignment fields are still in the model for backward compatibility:
- `assigned_reviewer_1`
- `assigned_reviewer_2`
- `assigned_approver`

These are no longer used but kept to avoid database schema changes.

## Administration

### View Current Group Members
```sql
-- Via Django Shell
python manage.py shell

from django.contrib.auth.models import Group
reviewers = Group.objects.get(name='Capital Contribution Reviewers')
print(list(reviewers.user_set.all()))

approvers = Group.objects.get(name='Capital Contribution Approvers')
print(list(approvers.user_set.all()))
```

### Re-run Setup Command
If you need to recreate the groups:
```bash
cd /var/www/tradifyerp/TradifyERP
source ../venv/bin/activate
python manage.py setup_contribution_groups --reset
```

## Troubleshooting

### Issue: User cannot access workflow action
**Solution**: Ensure user is added to the correct group in Django Admin

### Issue: "You cannot perform the second review" message
**Solution**: Second reviewer must be a different user than first reviewer

### Issue: Workflow buttons not showing on detail page
**Solution**: Update the capital contribution detail template to include workflow action buttons based on workflow_status

## Next Steps

1. **Add Users to Groups**: Assign appropriate users to Reviewers and Approvers groups
2. **Update Detail Template**: Add workflow action buttons to `capitalcontribution_detail.html` 
3. **Test End-to-End**: Create a test contribution and walk through the entire workflow
4. **User Training**: Inform users about the new group-based system

## Support

If you need to:
- Add workflow buttons to the detail page
- Customize the workflow (add more stages)
- Change group permissions
- Add email notifications

Just let me know and I can help implement those features.
