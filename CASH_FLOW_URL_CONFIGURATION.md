# URL Configuration Template for Cash Flow Module

Add this to your `TradifyERP/cash_management/urls.py`

```python
"""
Cash Management URL Configuration
Includes both Cash Position Dashboard and Cash Flow Statement URLs
"""

from django.urls import path
from . import views
from .cash_flow_views import (
    CashFlowStatementListView,
    CashFlowStatementDetailView,
    CashFlowStatementGenerateView,
    CashFlowVarianceAnalysisView,
    CashFlowComparisonView,
)

app_name = 'cash_management'

urlpatterns = [
    # ======== CASH POSITION DASHBOARD ========
    # These views already exist
    
    path(
        'positions/',
        views.CashPositionListView.as_view(),
        name='cash_position_list'
    ),
    
    
    # ======== CASH FLOW STATEMENTS ========
    # New views for period-based cash flow reporting
    
    # Browse all statements
    path(
        'statements/',
        CashFlowStatementListView.as_view(),
        name='cash_flow_list'
    ),
    
    # View single statement in detail
    path(
        'statements/<int:pk>/',
        CashFlowStatementDetailView.as_view(),
        name='cash_flow_detail'
    ),
    
    # Generate new statement from GL
    path(
        'statements/generate/',
        CashFlowStatementGenerateView.as_view(),
        name='cash_flow_generate'
    ),
    
    # Analyze variance for a statement
    path(
        'statements/<int:pk>/variance/',
        CashFlowVarianceAnalysisView.as_view(),
        name='cash_flow_variance'
    ),
    
    # Compare multiple periods
    path(
        'statements/compare/',
        CashFlowComparisonView.as_view(),
        name='cash_flow_comparison'
    ),
]
```

---

## Navigation URLs in Templates

### Links for Cash Position Dashboard Template

Add these navigation items to your cash position dashboard template:

```html
<!-- In cash_management/cash_position_dashboard.html -->

<!-- Primary Navigation -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="{% url 'cash_management:cash_position_list' %}">
            💰 Cash Management
        </a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link" href="{% url 'cash_management:cash_position_list' %}">
                📊 Dashboard
            </a>
            <a class="nav-link" href="{% url 'cash_management:cash_flow_list' %}">
                📋 Statements
            </a>
        </div>
    </div>
</nav>

<!-- Quick Links in Dashboard -->
<div class="card">
    <div class="card-header">
        <h5>🔄 Related Reports</h5>
    </div>
    <div class="card-body">
        <p class="mb-2">
            <a href="{% url 'cash_management:cash_flow_list' %}" class="btn btn-sm btn-outline-primary">
                <i class="bi bi-arrow-right"></i> View Cash Flow Statements
            </a>
        </p>
        <p class="mb-0">
            <a href="{% url 'cash_management:cash_flow_generate' %}" class="btn btn-sm btn-outline-success">
                <i class="bi bi-plus-circle"></i> Generate Monthly Statement
            </a>
        </p>
    </div>
</div>
```

### Links for Cash Flow Statements Template

```html
<!-- In cash_management/cash_flow_statements_list.html -->

<div class="row">
    <div class="col">
        <h1>📊 Cash Flow Statements</h1>
    </div>
    <div class="col-auto">
        <!-- Back to Dashboard Button -->
        <a href="{% url 'cash_management:cash_position_list' %}" class="btn btn-outline-secondary me-2">
            <i class="bi bi-arrow-left"></i> Back to Dashboard
        </a>
        
        <!-- Generate Statement Button -->
        <a href="{% url 'cash_management:cash_flow_generate' %}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Generate Statement
        </a>
    </div>
</div>
```

---

## Testing URLs

After adding the URLs and views, test each endpoint:

### Manual Browser Testing

```
1. List all statements:
   http://192.168.20.10/cash/statements/

2. Generate new statement:
   http://192.168.20.10/cash/statements/generate/

3. View specific statement (ID=1):
   http://192.168.20.10/cash/statements/1/

4. Variance analysis for statement (ID=1):
   http://192.168.20.10/cash/statements/1/variance/

5. Compare multiple periods:
   http://192.168.20.10/cash/statements/compare/

6. Back to dashboard:
   http://192.168.20.10/cash/positions/
```

### Automated URL Testing

```python
# test_cash_flow_urls.py
from django.test import TestCase, Client
from django.urls import reverse
from accounting.models import Entity

class CashFlowURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        self.entity = Entity.objects.create(
            name='Test Company',
            code='TEST001'
        )
        self.client.session['entity_id'] = self.entity.id
        self.client.save()
    
    def test_cash_flow_list_url(self):
        response = self.client.get(reverse('cash_management:cash_flow_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_cash_flow_generate_url(self):
        response = self.client.get(reverse('cash_management:cash_flow_generate'))
        self.assertEqual(response.status_code, 200)
    
    def test_cash_flow_comparison_url(self):
        response = self.client.get(reverse('cash_management:cash_flow_comparison'))
        self.assertEqual(response.status_code, 200)
```

Run tests:
```bash
python manage.py test cash_management.tests.CashFlowURLTests -v 2
```

---

## Main Project URLs Configuration

If you need to include cash_management URLs from your main `urls.py`:

```python
# In TradifyERP/urls.py or your main urls file

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... other apps ...
    
    # Cash Management URLs
    path('cash/', include('cash_management.urls', namespace='cash_management')),
]
```

This allows all cash_management URLs to be accessed under `/cash/` prefix:
- `/cash/positions/` - Dashboard
- `/cash/statements/` - Statement list
- `/cash/statements/generate/` - Generate new
- `/cash/statements/<id>/` - View detail
- `/cash/statements/<id>/variance/` - Variance analysis
- `/cash/statements/compare/` - Period comparison

---

## URL Namespace Best Practices

### Using Named URLs with Namespaces

```html
<!-- In templates, use the 'cash_management:' namespace -->

<!-- ✓ Correct -->
<a href="{% url 'cash_management:cash_flow_list' %}">Statements</a>

<!-- ✗ Incorrect (will fail if not namespaced) -->
<a href="{% url 'cash_flow_list' %}">Statements</a>
```

### In Views

```python
# In a view, redirect to named URL
from django.shortcuts import redirect
from django.urls import reverse

def my_view(request):
    # ... do something ...
    return redirect('cash_management:cash_flow_list')
```

### In Forms

```python
# If you create forms, use action attribute
class CashFlowForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_action = reverse('cash_management:cash_flow_generate')
```

---

## API Endpoints (Optional - Future Enhancement)

For mobile app or JavaScript frontend, you could add REST API endpoints:

```python
# Optional future additions to urls.py

from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'statements', api_views.CashFlowStatementViewSet)
router.register(r'categories', api_views.CashFlowCategoryViewSet)

urlpatterns = [
    # ... existing patterns ...
    
    # REST API for mobile
    path('api/', include(router.urls)),
]
```

This would provide REST endpoints:
- `GET /cash/api/statements/` - List statements (JSON)
- `POST /cash/api/statements/` - Create statement
- `GET /cash/api/statements/1/` - Get specific statement
- `GET /cash/api/categories/` - List categories

---

## Deployment to Production

### Step 1: Apply URL Changes

```bash
# On your local development machine
# Edit urls.py with the configuration above
# Commit to git

git add TradifyERP/cash_management/urls.py
git commit -m "feat(urls): Add cash flow statement URLs"
git push origin master
```

### Step 2: Deploy to Production Server

```bash
# SSH to production server
ssh root@192.168.20.10

# Navigate to project
cd /var/www/tradifyerp

# Pull latest changes
git pull origin master

# Restart web server to reload URLs
systemctl restart gunicorn

# Verify URLs are accessible
curl http://localhost/cash/statements/
```

### Step 3: Test All Routes

```bash
# Test from production server
curl -I http://192.168.20.10/cash/positions/       # Should return 302 (redirect to login)
curl -I http://192.168.20.10/cash/statements/      # Should return 302 (redirect to login)
curl -I http://192.168.20.10/cash/statements/generate/  # Should return 302

# All 302 responses are expected if not authenticated in curl
# Browser access with proper authentication should return 200
```

---

## Troubleshooting URL Issues

### Issue: 404 Page Not Found

```
Error: Page not found (404)
The path /cash/statements/ matched no URL patterns.
```

**Solution**:
1. Verify urls.py includes the new paths
2. Check namespace is correct: `app_name = 'cash_management'`
3. Restart Django server: `systemctl restart gunicorn`
4. Clear browser cache: Ctrl+Shift+Delete

```bash
# Verify URL patterns are registered
python manage.py show_urls | grep cash
```

### Issue: "Reverse for 'cash_flow_list' not found"

```
Error: Reverse for 'cash_flow_list' not found
```

**Solution**:
1. Make sure namespace is included in template: `{% url 'cash_management:cash_flow_list' %}`
2. Verify `app_name = 'cash_management'` in urls.py
3. Check URL name matches exactly: `name='cash_flow_list'`

### Issue: Views Return 403 Forbidden

```
Error: 403 Client Error: FORBIDDEN for url...
```

**Solution**:
1. Ensure you're logged in
2. Check LoginRequiredMixin is present in views
3. Verify SessionEntityMixin is setting entity correctly

```python
# In view
print(f"User: {request.user}")  # Should be logged-in user, not AnonymousUser
print(f"Entity: {request.entity}")  # Should be set from session
```

---

**End of URL Configuration Guide**

Next step: Run `python manage.py makemigrations` and `migrate` to create the database tables for the Cash Flow models.
