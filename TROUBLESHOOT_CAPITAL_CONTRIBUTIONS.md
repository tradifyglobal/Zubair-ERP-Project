# Troubleshooting Capital Contributions Display

If you're still not seeing the capital contributions on your dashboard after the records were created, use this guide.

## 1. Verify Records Exist in Database

Run this command via Django shell:
```python
from accounting.models import CapitalContribution, Entity
entity = Entity.objects.get(id=7)  # Testing entity
contribs = CapitalContribution.objects.filter(entity=entity, workflow_status='APPROVED')
print(f"Found {contribs.count()} approved contributions")
for cc in contribs:
    print(f"  #{cc.id}: {cc.stakeholder} - {cc.amount}")
```

Expected output: Should show 2 records (#18 and #19)

## 2. Check Your Session Entity

The dashboard filters by `session.selected_entity_id`. Make sure you have the **Testing entity** selected:

```python
# In Django view or shell:
print(request.session.get('selected_entity_id'))
# Should print: 7 (Testing entity)
```

If it's different, go to the entity switcher and select "Testing" entity.

## 3. Clear Browser Cache/Session

1. Log out completely
2. Clear browser cookies and cache
3. Log back in
4. Navigate to shareholder dashboard

## 4. Verify Dashboard View Query

Check the actual dashboard view query by adding debug output:

**File**: `TradifyERP/accounting/dashboard_views.py` (around line 261 where CapitalContribution is filtered)

Add debug print:
```python
entity_id = request.session.get('selected_entity_id')
print(f"Dashboard Query - Entity ID: {entity_id}")

contributions = CapitalContribution.objects.filter(
    entity_id=entity_id,
    workflow_status='APPROVED'
)
print(f"Found {contributions.count()} contributions")  # Add this debug line
```

Then check Gunicorn logs to see the output.

## 5. Check Gunicorn Logs

```bash
ssh zubair@192.168.20.10
sudo journalctl -u gunicorn -f  # Follow logs as they appear
```

Or for recent logs:
```bash
sudo journalctl -u gunicorn -n 50  # Last 50 lines
```

## 6. Verify Database Records Directly

Connect to PostgreSQL and query:
```sql
ssh zubair@192.168.20.10
psql -U tradifyerp_user -d tradifyerp_db -h localhost

SELECT id, stakeholder_id, amount, currency_id, workflow_status, created_at
FROM accounting_capitalcontribution
WHERE entity_id = 7
ORDER BY created_at DESC;
```

Expected output:
```
id | stakeholder_id | amount  | currency_id | workflow_status | created_at
19 |              1 | 5000.00 |           1 | APPROVED        | 2025-12-15...
18 |              2 | 4000.00 |           1 | APPROVED        | 2025-12-15...
```

## 7. Force Django Cache Clear

If caching is enabled, clear it:

```bash
ssh zubair@192.168.20.10
source /var/www/tradifyerp/venv/bin/activate
cd /var/www/tradifyerp
python manage.py shell

from django.core.cache import cache
cache.clear()
```

## 8. Restart Gunicorn

If nothing else works, restart the application:

```bash
ssh zubair@192.168.20.10
sudo systemctl restart gunicorn
# Check status
sudo systemctl status gunicorn
```

## 9. Check Permission Issues

Verify the current user has view permissions:

```python
from django.contrib.auth.models import User
user = User.objects.get(username='current_user')
print(f"User permissions: {user.get_all_permissions()}")
# Should include: 'accounting.view_capitalcontribution'
```

## 10. Review Entity Setup

Confirm Testing entity is properly configured:

```python
from accounting.models import Entity
test_entity = Entity.objects.get(id=7)
print(f"Entity: {test_entity.name}")
print(f"Status: {test_entity.is_active}")
print(f"Stakeholders: {test_entity.stakeholders.count()}")
```

## Still Not Working?

Contact support with:
1. Your selected entity ID (from session)
2. Output from #1 (database query results)
3. Gunicorn log entries from #5
4. Browser console errors (F12 -> Console tab)
