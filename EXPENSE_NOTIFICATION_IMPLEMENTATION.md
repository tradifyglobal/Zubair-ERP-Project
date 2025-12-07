# Expense Notification System Implementation

**Date:** December 7, 2025  
**Status:** ✅ COMPLETED  
**Commit:** `2a30313`

## Overview

Implemented a comprehensive notification system for expense module approvals and reviews that displays on the bell icon notification system, matching the shareholder contributions notification pattern.

## Features Implemented

### 1. Notification Detection Functions (`expenses/notifications.py`)

Three main detection functions with counts and querysets:

```python
get_pending_reviews_for_user(user, entity=None)
- Detects reports in PENDING_REVIEW status
- Returns reports for users with 'reviewer' module permission
- Count: expense_pending_reviews_count

get_pending_approvals_for_user(user, entity=None)
- Detects reports in PENDING_APPROVAL status
- Returns reports for users with 'expenses' + 'can_approve' permission
- Count: expense_pending_approvals_count

get_pending_final_approvals_for_user(user, entity=None)
- Detects reports assigned to user as finance_approver
- Returns reports where finance_approved=False
- Count: expense_pending_final_approvals_count

get_all_pending_for_user(user, entity=None)
- Aggregates all three types
- Returns dict with counts and querysets
- Count: expense_total_pending (sum of all three)
```

### 2. Context Processor (`expenses/context_processors.py`)

Makes notification data available in all templates:

```python
pending_expense_notifications(request)
```

**Template Variables Available:**
- `expense_notifications` - Full dict with all data
- `expense_pending_reviews_count` - Number of pending reviews
- `expense_pending_approvals_count` - Number of pending approvals
- `expense_pending_final_approvals_count` - Number of pending final approvals
- `expense_total_pending` - Total across all types
- `expense_pending_reviews` - QuerySet of reports requiring review
- `expense_pending_approvals` - QuerySet of reports requiring approval
- `expense_pending_final_approvals` - QuerySet of reports requiring final approval

### 3. Settings Registration (`TradifyERP/settings.py`)

Added context processor to TEMPLATES configuration:

```python
'expenses.context_processors.pending_expense_notifications'
```

Positioned after shareholder context processor for consistent notification handling.

### 4. Bell Icon Integration (`templates/partials/hori-header.html`)

Enhanced notification system to display expense notifications:

**Badge Display:**
- Combined count: `pending_notifications.total_pending + expense_total_pending`
- Shows total badge count for all notifications

**Notification Sections:**

1. **Shareholder Contributions** (Existing)
   - Awaiting Review (yellow)
   - Awaiting Approval (green)

2. **Expense Review** (NEW)
   - Label: "Expense Review Required"
   - Icon: Info blue (bx-file)
   - Shows report_number and total_amount
   - Links to report detail page

3. **Expense Approval** (NEW)
   - Label: "Expense Approval Required"
   - Icon: Success green (bx-check-circle)
   - Shows report_number and total_amount
   - Links to report detail page

4. **Finance Approval** (NEW)
   - Label: "Finance Approval Required"
   - Icon: Danger red (bx-check-double)
   - Shows report_number and total_amount
   - Links to report detail page

## Workflow Integration

### Permission-Based Display

**Expense Reviews** show only for users with:
- Module: 'reviewer'
- Active status (checked in notifications.py)

**Expense Approvals** show only for users with:
- Module: 'expenses'
- Permission: 'can_approve'

**Finance Approvals** show only for users assigned as:
- approval_workflow.finance_approver
- finance_approved = False (still pending)

## URL Routes

All notification links use:
```django
{% url 'expenses:report-detail' report.id %}
```

Ensure the following URL pattern exists in urls.py:
```python
path('report/<int:pk>/', EmployeeExpenseReportDetailView.as_view(), name='report-detail'),
```

## Template Context Variables

Example usage in templates:

```django
{% if expense_pending_reviews_count %}
    <p>You have {{ expense_pending_reviews_count }} expense reviews pending</p>
{% endif %}

{% for report in expense_pending_final_approvals %}
    <a href="{% url 'expenses:report-detail' report.id %}">
        {{ report.report_number }} - {{ report.total_amount }}
    </a>
{% endfor %}
```

## Notification Display Logic

1. **Authentication Check**: Only authenticated users receive notifications
2. **Entity Filter**: Notifications filtered by user's current entity
3. **Permission Validation**: QuerySets filtered by ModulePermission records
4. **Status Check**: Only reports in specific statuses displayed
5. **Assignment Check**: Finance approvals only for assigned users

## Testing Checklist

- [ ] Login as reviewer with 'reviewer' permission
  - [ ] See pending expense reviews in bell icon
  - [ ] Count is accurate
  - [ ] Links work correctly

- [ ] Login as manager with 'expenses' + 'can_approve'
  - [ ] See pending expense approvals in bell icon
  - [ ] Count is accurate
  - [ ] Links work correctly

- [ ] Login as finance approver (assigned in workflow)
  - [ ] See finance approval section
  - [ ] Count is accurate
  - [ ] Links work correctly

- [ ] Login as non-reviewer/approver
  - [ ] No expense sections display
  - [ ] Bell icon shows shareholder notifications only

- [ ] With mixed permissions
  - [ ] Shows all applicable sections
  - [ ] Counts sum correctly in badge

## Deployment Instructions

1. **Push to GitHub**: ✅ DONE (commit 2a30313)
2. **Copy Files to Server**:
   ```bash
   scp -r TradifyERP/expenses/notifications.py root@192.168.2.185:/var/www/tradifyerp/TradifyERP/expenses/
   scp -r TradifyERP/expenses/context_processors.py root@192.168.2.185:/var/www/tradifyerp/TradifyERP/expenses/
   scp TradifyERP/TradifyERP/settings.py root@192.168.2.185:/var/www/tradifyerp/TradifyERP/TradifyERP/
   scp TradifyERP/templates/partials/hori-header.html root@192.168.2.185:/var/www/tradifyerp/TradifyERP/templates/partials/
   ```

3. **Restart Gunicorn**:
   ```bash
   ssh root@192.168.2.185
   systemctl restart gunicorn
   ```

4. **Verify Deployment**:
   - Login to application
   - Check bell icon shows expense notifications
   - Test different user roles

## Files Modified

1. **TradifyERP/expenses/notifications.py** (NEW)
   - 70 lines
   - Functions for pending detection

2. **TradifyERP/expenses/context_processors.py** (NEW)
   - 35 lines
   - Context processor for template variables

3. **TradifyERP/TradifyERP/settings.py** (MODIFIED)
   - Added context processor to TEMPLATES config
   - 1 line addition

4. **TradifyERP/templates/partials/hori-header.html** (MODIFIED)
   - Added expense notification sections
   - Badge calculation updated
   - Multiple notification blocks added

## Key Design Decisions

1. **Mirrored Shareholder Pattern**: Exactly matches the notification system for capital contributions
2. **Three-Tier Expense Notifications**: Separate sections for review, approval, and final approval
3. **Permission Validation**: Notifications respect the module permission system
4. **Entity Awareness**: Filters by user's current entity
5. **Direct Links**: Each notification links directly to the report detail page
6. **Automatic Counts**: Badge updates automatically based on data
7. **Graceful Degradation**: Non-approvers see no expense sections

## Future Enhancements

- [ ] Real-time notification updates via WebSocket
- [ ] Notification preferences (opt-in/out)
- [ ] Email notifications for critical approvals
- [ ] Notification center page with detail view
- [ ] Mark notifications as read
- [ ] Notification history/audit trail
- [ ] Customizable notification intervals

## Related Features

- ✅ Two-stage finance approval workflow (commit 38fa0ae)
- ✅ Role-based approval buttons (commit 1ab929b)
- ✅ Permission-based workflow (commit 1845c32)
- ✅ Expense module with attachments (commits 10fd80c - 19f5db8)

## Summary

The expense notification system is now fully integrated with the bell icon notification center, providing approvers and reviewers with real-time visibility of pending expense actions. The implementation follows the established shareholder contribution notification pattern, ensuring consistency across the platform.

Users with appropriate permissions will now see:
- Pending expense reviews requiring their review
- Pending approvals requiring their approval
- Finance approvals requiring their final approval

All notifications link directly to the expense report detail page for quick access.
