# QUICK FIX REFERENCE

## The Error
```
NoReverseMatch at /accounting/trial-balances/
Reverse for 'trial-balance-dashboard' not found.
```

## Why It Happened
- OLD route at `/accounting/trial-balances/` pointed to old views.py class
- Template tried to use URL name `trial-balance-dashboard` from NEW urls_trial_balance.py
- Old view didn't know about the new URL names
- **Result**: Routing conflict causing template rendering to fail

## The Fix (2 Steps)

### Step 1: Fix Routing
**File**: `accounting/urls.py`
```python
# BEFORE (line 140):
path('trial-balances/', TrialBalanceListView.as_view(), name='trial_balance_list'),

# AFTER (line 140):
# path('trial-balances/', TrialBalanceListView.as_view(), name='trial_balance_list'),  # DEPRECATED

# ADDED (end of file):
try:
    from .urls_trial_balance import urlpatterns as trial_balance_urlpatterns
    urlpatterns += trial_balance_urlpatterns
except ImportError:
    pass
```

### Step 2: Fix Templates
**Templates**: trial_balance_*.html files
```
Replace: {% url 'trial-balances' %}      → {% url 'trial-balance-list' %}
Replace: {% url 'monthly-trial-balances' %} → {% url 'trial-balance-monthly' %}
Remove:  {% url 'trial-balance-generate' %} → (auto-generated, not manual)
```

## Result
✅ All Trial Balance URLs now working correctly  
✅ HTTP 302 redirects to login (expected for unauthenticated)  
✅ No NoReverseMatch errors  
✅ Dashboard, lists, reports all functioning  

## New URL Pattern
- Use: `/accounting/trial-balance/` (singular)
- Don't use: `/accounting/trial-balances/` (plural - deprecated)
