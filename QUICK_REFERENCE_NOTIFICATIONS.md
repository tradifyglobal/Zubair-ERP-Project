# Quick Reference - Expense Notifications

## 🎯 What Was Built

A notification system that shows pending expense reviews and approvals on the bell icon, exactly like shareholder contributions.

## 📍 Files Changed

| File | Change | Purpose |
|------|--------|---------|
| `TradifyERP/expenses/notifications.py` | NEW | Detection functions for pending reports |
| `TradifyERP/expenses/context_processors.py` | NEW | Makes notification data available in templates |
| `TradifyERP/TradifyERP/settings.py` | +1 line | Register context processor |
| `TradifyERP/templates/partials/hori-header.html` | +110 lines | Display notifications in bell icon |

## 🔧 How It Works

```
User Logs In
    ↓ Context Processor Runs
    ↓ Checks ModulePermissions
    ↓ Queries Pending Reports
    ↓ Returns Counts & QuerySets
    ↓ Template Displays Notifications
    ↓ Bell Icon Shows Badge
```

## 📋 Template Variables

Use these in any template:

```django
{{ expense_pending_reviews_count }}      # Number of reviews needed
{{ expense_pending_approvals_count }}    # Number of approvals needed
{{ expense_pending_final_approvals_count }} # Finance approvals needed
{{ expense_total_pending }}               # Total of all three

{% for report in expense_pending_reviews %}
    {{ report.report_number }}
    {{ report.total_amount }}
{% endfor %}
```

## ✅ Who Sees What

| User Type | Sees |
|-----------|------|
| Reviewer (module='reviewer') | Pending Reviews section |
| Approver (module='expenses', can_approve=True) | Pending Approvals section |
| Finance Approver (assigned in workflow) | Finance Approval section |
| Regular User | No expense sections |

## 🚀 Deployment

**Copy these files to server:**
```bash
/var/www/tradifyerp/TradifyERP/expenses/notifications.py
/var/www/tradifyerp/TradifyERP/expenses/context_processors.py
/var/www/tradifyerp/TradifyERP/TradifyERP/settings.py
/var/www/tradifyerp/TradifyERP/templates/partials/hori-header.html
```

**Restart Gunicorn:**
```bash
systemctl restart gunicorn
```

## 🔍 Verify It's Working

1. Login as reviewer/approver
2. Create a test expense report
3. Submit it to put in PENDING_REVIEW
4. Check bell icon - should show notification
5. Click link - should go to report detail

## 📞 Issues?

**No notifications showing?**
- Check `settings.py` has context processor registered
- Verify user has proper ModulePermission
- Check database for pending reports

**Counts wrong?**
- Check ModulePermission records in admin
- Verify report status is PENDING_REVIEW or PENDING_APPROVAL

**Links broken?**
- Verify URL pattern: `path('report/<int:pk>/', EmployeeExpenseReportDetailView.as_view(), name='report-detail')`

## 📚 Full Documentation

See `EXPENSE_NOTIFICATION_IMPLEMENTATION.md` and `NOTIFICATION_SESSION_COMPLETION.md`

## 🎉 Latest Commits

```
af69706 - fix: Update context processor to return querysets
2a30313 - feat: Add expense notifications to bell icon
```

**All code is on GitHub:** `tradifyglobal/Zubair-ERP-Project` (branch: changes)
