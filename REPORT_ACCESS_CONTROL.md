# Report-Level Access Control System

## Overview

This system provides granular control over which users can view specific reports. Users can be assigned different access levels (view-only, edit, full access) for each report, optionally limited to specific entities.

**Key Features:**
- ✓ Restrict access to sensitive reports (Shareholder Investment, Accounts, etc.)
- ✓ Multiple access levels: View Only, Edit, Full Access
- ✓ Entity-specific or organization-wide access
- ✓ Time-limited access with expiration dates
- ✓ Superusers always have full access
- ✓ Backward compatible (unrestricted reports accessible by default)
- ✓ Audit trail of access grants

---

## For Administrators

### Assigning Report Access

#### Using Django Admin

1. Go to `/admin/`
2. Find "Report Access" section
3. Click "Add Report Access"
4. Select user, report type, and access level
5. Optionally set entity and expiry date
6. Save

#### Using Management Command

```bash
# Grant view-only access to shareholder investment report
python manage.py assign_report_access \
  --username=xyz \
  --report=shareholder_investment \
  --access_level=view_only

# Grant edit access to specific entity
python manage.py assign_report_access \
  --username=xyz \
  --report=accounts \
  --access_level=edit \
  --entity=Pristine-planet-01

# Grant access that expires in 30 days
python manage.py assign_report_access \
  --username=xyz \
  --report=profit_loss \
  --access_level=view_only \
  --expiry_days=30

# Revoke access
python manage.py assign_report_access \
  --username=xyz \
  --report=shareholder_investment \
  --remove

# List available reports
python manage.py assign_report_access --list_reports

# List all users
python manage.py assign_report_access --list_users
```

### Available Reports

| Report Code | Report Name | Default Access |
|---|---|---|
| `accounts` | Accounts Report | Restricted |
| `trial_balance` | Trial Balance Report | Restricted |
| `profit_loss` | Profit & Loss Report | Restricted |
| `balance_sheet` | Balance Sheet Report | Restricted |
| `cash_flow` | Cash Flow Report | Restricted |
| `shareholder_investment` | Shareholder Investment Report | Restricted |
| `capital_contributions` | Capital Contributions Report | Restricted |
| `ledger_analysis` | Ledger Analysis Report | Restricted |
| `cash_transactions` | Cash Transactions Report | Unrestricted |
| `bank_transactions` | Bank Transactions Report | Unrestricted |
| `journal_voucher` | Journal Voucher Report | Unrestricted |
| `stakeholder_report` | Stakeholder Report | Unrestricted |
| `accounting_dashboard` | Accounting Dashboard | Restricted |
| `shareholder_dashboard` | Shareholder Dashboard | Restricted |

### Access Levels

| Level | Permissions | Use Case |
|---|---|---|
| **view_only** | Read data only | Stakeholders viewing their own data |
| **edit** | Read and modify data | Team members managing reports |
| **full_access** | Read, modify, export | Managers with complete authority |

---

## For Developers

### Adding Report Access to New Views

To add access control to a new report view:

```python
from accounting.mixins import ReportAccessMixin
from django.views.generic import TemplateView

class MyNewReportView(ReportAccessMixin, SessionEntityMixin, LoginRequiredMixin, TemplateView):
    template_name = 'my_report.html'
    report_type = 'my_new_report'  # Must match a code in ReportAccess.REPORT_CHOICES
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Your code here
        # report_access_level is automatically in context
        return context
```

### Template Usage

Show conditional UI elements based on access level:

```html
{% if can_edit %}
    <button>Edit Report</button>
{% endif %}

{% if can_export %}
    <button>Export Data</button>
{% endif %}

{% if report_access_level == 'view_only' %}
    <div class="alert alert-info">Read-only access</div>
{% endif %}
```

Or include the pre-built notice:

```html
{% include 'partials/report_access_notice.html' %}
```

### How It Works

1. **Request arrives** at view
2. **ReportAccessMixin.dispatch()** checks:
   - Is user a superuser? → Allow (full_access)
   - Is report unrestricted? → Allow (full_access)
   - Does user have ReportAccess record? 
     - Yes: Check expiry date → Allow/Deny
     - No: Deny (403 Forbidden)
3. **Access level is passed** to template via context
4. **Template renders** based on `report_access_level`

### Model Structure

```python
class ReportAccess(models.Model):
    user = ForeignKey(User)
    report_type = CharField(choices=REPORT_CHOICES)
    access_level = CharField(choices=ACCESS_LEVEL_CHOICES)
    entity = ForeignKey(Entity, null=True)  # null = all entities
    is_active = Boolean()
    expiry_date = Date(null=True)  # null = no expiry
    granted_by = ForeignKey(User)
    granted_at = DateTime(auto_now_add=True)
```

---

## Examples

### Example 1: Restrict Shareholder Report

**Scenario:** Only finance managers can view the shareholder investment report.

```bash
# Grant access to finance manager
python manage.py assign_report_access \
  --username=finance_manager \
  --report=shareholder_investment \
  --access_level=view_only

# User 'xyz' cannot access this report (will see 403 Forbidden)
```

### Example 2: Entity-Specific Access

**Scenario:** User 'rajesh' should see accounts only for "Pristine-planet-01" entity.

```bash
python manage.py assign_report_access \
  --username=rajesh \
  --report=accounts \
  --access_level=view_only \
  --entity=Pristine-planet-01
```

### Example 3: Temporary Access

**Scenario:** Grant auditor temporary access for 3 months.

```bash
python manage.py assign_report_access \
  --username=auditor \
  --report=profit_loss \
  --access_level=full_access \
  --expiry_days=90
```

### Example 4: Multiple Reports

**Scenario:** Grant CFO access to all financial reports.

```bash
python manage.py assign_report_access --username=cfo --report=accounts --access_level=full_access
python manage.py assign_report_access --username=cfo --report=trial_balance --access_level=full_access
python manage.py assign_report_access --username=cfo --report=profit_loss --access_level=full_access
python manage.py assign_report_access --username=cfo --report=balance_sheet --access_level=full_access
```

---

## Troubleshooting

### User Sees "Access Denied"

1. Check if report has restrictions: `ReportAccess` record exists
2. Verify `is_active=True` and access hasn't expired
3. Check entity matches current entity OR is null (all entities)
4. Check user is not trying to access from wrong entity

### Grant Access But Still Denied

```bash
# Debug what access the user has
python manage.py shell

>>> from accounting.models import ReportAccess
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='xyz')
>>> ReportAccess.objects.filter(user=user)
# Check records here
```

### Restrict New Report

1. Add to `ReportAccess.REPORT_CHOICES`
2. Update view with `ReportAccessMixin`
3. Create `ReportAccess` record to activate restriction

---

## Security Notes

- **Superusers:** Always have access (cannot be restricted)
- **Session Entity:** Access can be limited to specific entity
- **Expiry:** Automatically enforced at request time
- **Audit Trail:** `granted_by` and `granted_at` track who granted access
- **No SQL Injection:** Uses Django ORM with parameterized queries

---

## Backward Compatibility

- If no `ReportAccess` records exist for a report, **everyone can access it** (unrestricted)
- This allows gradual rollout of access control
- Once first `ReportAccess` record created for a report, report becomes restricted

---

## Performance

- Caching: No additional caching (Django ORM handles queries efficiently)
- Database Hits: 1-2 queries per request (ReportAccess lookup)
- Optimization: Use `select_related()` in ReportAccessMixin for entity lookups

---

## Future Enhancements

- [ ] Group-based access (assign permissions to groups)
- [ ] Role-based access (Finance Role, Admin Role, etc.)
- [ ] API permissions (REST endpoints)
- [ ] Report-level field masking (hide sensitive columns)
- [ ] Data-level access (only see entity's data)
- [ ] Audit dashboard (view all access grants and changes)
- [ ] Notification on access grant/revoke
- [ ] Integration with LDAP/AD for auto-provisioning
