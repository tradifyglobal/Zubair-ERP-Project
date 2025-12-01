# TradifyERP - Broken Buttons Fix Implementation Guide

**Date:** November 22, 2025  
**Purpose:** Step-by-step guide to fix all broken Add/Edit/Create buttons  

---

## Overview

This guide provides code examples and step-by-step instructions to fix all broken buttons identified in the audit report. The guide is organized by module and priority.

---

## PRIORITY 1: Cash Management Module

### Issue Summary
9+ broken buttons in cash management templates requiring Create and Update views.

### Affected Templates
1. `cash_management/templates/cash_management/paymentschedule_list.html`
2. `cash_management/templates/cash_management/cashposition_list.html`
3. `cash_management/templates/cash_management/liquidityforecast_list.html`
4. `cash_management/templates/cash_management/treasuryaccount_list.html`
5. `cash_management/templates/cash_management/fxexposure_list.html`
6. `cash_management/templates/cash_management/treasury_list.html`
7. `cash_management/templates/cash_management/payment_list.html`
8. `cash_management/templates/cash_management/forecast_list.html`

### Fix 1.1: Payment Schedule Create & Update Views

**File:** `cash_management/views.py`

Add after existing PaymentScheduleDetailView:

```python
class PaymentScheduleCreateView(LoginRequiredMixin, CreateView):
    """Create a new payment schedule."""
    model = PaymentSchedule
    form_class = PaymentScheduleForm  # Create this form in forms.py
    template_name = 'cash_management/paymentschedule_form.html'
    success_url = reverse_lazy('cash_management:payment_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Payment schedule created successfully.')
        return super().form_valid(form)


class PaymentScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing payment schedule."""
    model = PaymentSchedule
    form_class = PaymentScheduleForm
    template_name = 'cash_management/paymentschedule_form.html'
    success_url = reverse_lazy('cash_management:payment_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Payment schedule updated successfully.')
        return super().form_valid(form)
```

**File:** `cash_management/urls.py`

Add these URL patterns after existing payment_detail:

```python
path('payments/create/', views.PaymentScheduleCreateView.as_view(), name='paymentschedule_create'),
path('payments/<int:pk>/edit/', views.PaymentScheduleUpdateView.as_view(), name='paymentschedule_edit'),
```

**File:** `cash_management/templates/cash_management/paymentschedule_list.html`

Replace broken buttons (lines 17, 86-87):

```html
<!-- Line 17: Replace this -->
<!-- BEFORE: <a href="#" class="btn btn-primary btn-sm">Schedule Payment</a> -->
<!-- AFTER: -->
<a href="{% url 'cash_management:paymentschedule_create' %}" class="btn btn-primary btn-sm">Schedule Payment</a>

<!-- Line 86-87: Replace this -->
<!-- BEFORE: 
<a href="#" class="btn btn-sm btn-info">View</a>
<a href="#" class="btn btn-sm btn-warning">Edit</a>
-->
<!-- AFTER: -->
<a href="{% url 'cash_management:payment_detail' schedule.id %}" class="btn btn-sm btn-info">View</a>
<a href="{% url 'cash_management:paymentschedule_edit' schedule.id %}" class="btn btn-sm btn-warning">Edit</a>
```

### Fix 1.2: Cash Position Create View

**File:** `cash_management/views.py`

Add after existing CashPositionListView:

```python
class CashPositionCreateView(LoginRequiredMixin, CreateView):
    """Create a new cash position."""
    model = CashPosition
    form_class = CashPositionForm  # Create in forms.py
    template_name = 'cash_management/cashposition_form.html'
    success_url = reverse_lazy('cash_management:position_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Cash position created successfully.')
        return super().form_valid(form)
```

**File:** `cash_management/urls.py`

Add URL pattern:

```python
path('positions/create/', views.CashPositionCreateView.as_view(), name='cashposition_create'),
path('positions/<int:pk>/', views.CashPositionDetailView.as_view(), name='position_detail'),
```

**File:** `cash_management/templates/cash_management/cashposition_list.html`

Replace broken buttons (lines 17, 47):

```html
<!-- Line 17: -->
<a href="{% url 'cash_management:cashposition_create' %}" class="btn btn-primary btn-sm">Add Position</a>

<!-- Line 47: -->
<a href="{% url 'cash_management:position_detail' position.id %}" class="btn btn-sm btn-info">View</a>
```

### Fix 1.3: Liquidity Forecast Create & Update Views

**File:** `cash_management/views.py`

Add after existing LiquidityForecastDetailView:

```python
class LiquidityForecastCreateView(LoginRequiredMixin, CreateView):
    """Create a new liquidity forecast."""
    model = LiquidityForecast
    form_class = LiquidityForecastForm  # Create in forms.py
    template_name = 'cash_management/liquidityforecast_form.html'
    success_url = reverse_lazy('cash_management:forecast_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Liquidity forecast created successfully.')
        return super().form_valid(form)


class LiquidityForecastUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing liquidity forecast."""
    model = LiquidityForecast
    form_class = LiquidityForecastForm
    template_name = 'cash_management/liquidityforecast_form.html'
    success_url = reverse_lazy('cash_management:forecast_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Liquidity forecast updated successfully.')
        return super().form_valid(form)
```

**File:** `cash_management/urls.py`

Add URL patterns:

```python
path('forecasts/create/', views.LiquidityForecastCreateView.as_view(), name='forecast_create'),
path('forecasts/<int:pk>/edit/', views.LiquidityForecastUpdateView.as_view(), name='forecast_edit'),
```

**File:** `cash_management/templates/cash_management/liquidityforecast_list.html`

Replace broken buttons (lines 17, 61-62):

```html
<!-- Line 17: -->
<a href="{% url 'cash_management:forecast_create' %}" class="btn btn-primary btn-sm">Create Forecast</a>

<!-- Lines 61-62: -->
<a href="{% url 'cash_management:forecast_detail' forecast.id %}" class="btn btn-sm btn-info">View</a>
<a href="{% url 'cash_management:forecast_edit' forecast.id %}" class="btn btn-sm btn-warning">Edit</a>
```

### Fix 1.4: Treasury Account Create & Update Views

**File:** `cash_management/views.py`

Add after existing TreasuryAccountListView:

```python
class TreasuryAccountCreateView(LoginRequiredMixin, CreateView):
    """Create a new treasury account."""
    model = TreasuryAccount
    form_class = TreasuryAccountForm  # Create in forms.py
    template_name = 'cash_management/treasuryaccount_form.html'
    success_url = reverse_lazy('cash_management:treasury_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Treasury account created successfully.')
        return super().form_valid(form)


class TreasuryAccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing treasury account."""
    model = TreasuryAccount
    form_class = TreasuryAccountForm
    template_name = 'cash_management/treasuryaccount_form.html'
    success_url = reverse_lazy('cash_management:treasury_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Treasury account updated successfully.')
        return super().form_valid(form)
```

**File:** `cash_management/urls.py`

Add URL patterns:

```python
path('treasury/create/', views.TreasuryAccountCreateView.as_view(), name='treasuryaccount_create'),
path('treasury/<int:pk>/', views.TreasuryAccountDetailView.as_view(), name='treasury_detail'),
path('treasury/<int:pk>/edit/', views.TreasuryAccountUpdateView.as_view(), name='treasuryaccount_edit'),
```

**File:** `cash_management/templates/cash_management/treasuryaccount_list.html`

Replace broken buttons (lines 17, 63-64):

```html
<!-- Line 17: -->
<a href="{% url 'cash_management:treasuryaccount_create' %}" class="btn btn-primary btn-sm">Add Account</a>

<!-- Lines 63-64: -->
<a href="{% url 'cash_management:treasury_detail' account.id %}" class="btn btn-sm btn-info">View</a>
<a href="{% url 'cash_management:treasuryaccount_edit' account.id %}" class="btn btn-sm btn-warning">Edit</a>
```

### Fix 1.5: FX Exposure Create, Detail & Update Views

**File:** `cash_management/views.py`

Add after existing FXExposureListView:

```python
class FXExposureDetailView(LoginRequiredMixin, DetailView):
    """View FX exposure details."""
    model = FXExposure
    template_name = 'cash_management/fxexposure_detail.html'
    context_object_name = 'exposure'
    login_url = 'login'


class FXExposureCreateView(LoginRequiredMixin, CreateView):
    """Create a new FX exposure record."""
    model = FXExposure
    form_class = FXExposureForm  # Create in forms.py
    template_name = 'cash_management/fxexposure_form.html'
    success_url = reverse_lazy('cash_management:fx_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'FX exposure recorded successfully.')
        return super().form_valid(form)


class FXExposureUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing FX exposure record."""
    model = FXExposure
    form_class = FXExposureForm
    template_name = 'cash_management/fxexposure_form.html'
    success_url = reverse_lazy('cash_management:fx_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'FX exposure updated successfully.')
        return super().form_valid(form)
```

**File:** `cash_management/urls.py`

Add URL patterns:

```python
path('fx-exposure/create/', views.FXExposureCreateView.as_view(), name='fxexposure_create'),
path('fx-exposure/<int:pk>/', views.FXExposureDetailView.as_view(), name='fxexposure_detail'),
path('fx-exposure/<int:pk>/edit/', views.FXExposureUpdateView.as_view(), name='fxexposure_edit'),
```

**File:** `cash_management/templates/cash_management/fxexposure_list.html`

Replace broken buttons (lines 17, 79-80):

```html
<!-- Line 17: -->
<a href="{% url 'cash_management:fxexposure_create' %}" class="btn btn-primary btn-sm">Record Exposure</a>

<!-- Lines 79-80: -->
<a href="{% url 'cash_management:fxexposure_detail' exposure.id %}" class="btn btn-sm btn-info">View</a>
<a href="{% url 'cash_management:fxexposure_edit' exposure.id %}" class="btn btn-sm btn-warning">Edit</a>
```

### Fix 1.6: Fix Other Template References

**File:** `cash_management/templates/cash_management/treasury_list.html`

Replace line 17:

```html
<!-- BEFORE: <a href="#" class="btn btn-primary btn-sm">Add Account</a> -->
<!-- AFTER: -->
<a href="{% url 'cash_management:treasuryaccount_create' %}" class="btn btn-primary btn-sm">Add Account</a>
```

**File:** `cash_management/templates/cash_management/payment_list.html`

Replace line 17:

```html
<!-- BEFORE: <a href="#" class="btn btn-primary btn-sm">Schedule Payment</a> -->
<!-- AFTER: -->
<a href="{% url 'cash_management:paymentschedule_create' %}" class="btn btn-primary btn-sm">Schedule Payment</a>
```

**File:** `cash_management/templates/cash_management/forecast_list.html`

Replace line 17:

```html
<!-- BEFORE: <a href="#" class="btn btn-primary btn-sm">Create Forecast</a> -->
<!-- AFTER: -->
<a href="{% url 'cash_management:forecast_create' %}" class="btn btn-primary btn-sm">Create Forecast</a>
```

---

## PRIORITY 2: Projects Module

### Issue Summary
3 broken buttons: New Project, Create Task, Log Time

### Fix 2.1: Project Create View

**File:** `projects/views.py`

Add after existing ProjectDetailView:

```python
class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create a new project."""
    model = Project
    form_class = ProjectForm  # Create in forms.py
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Project created successfully.')
        return super().form_valid(form)
```

**File:** `projects/urls.py`

Add URL pattern:

```python
path('new/', views.ProjectCreateView.as_view(), name='project_create'),
```

**File:** `projects/templates/projects/project_list.html`

Replace line 17:

```html
<!-- BEFORE: <a href="#" class="btn btn-primary btn-sm">New Project</a> -->
<!-- AFTER: -->
<a href="{% url 'projects:project_create' %}" class="btn btn-primary btn-sm">New Project</a>
```

### Fix 2.2: Task Create View

**File:** `projects/views.py`

Add after existing TaskListView:

```python
class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create a new task."""
    model = Task
    form_class = TaskForm  # Create in forms.py
    template_name = 'projects/task_form.html'
    success_url = reverse_lazy('projects:task_list')
    login_url = 'login'
    
    def form_valid(self, form):
        # Associate task with a project if project_id is passed
        project_id = self.request.GET.get('project_id')
        if project_id:
            form.instance.project_id = project_id
        messages.success(self.request, 'Task created successfully.')
        return super().form_valid(form)
```

**File:** `projects/urls.py`

Add URL pattern:

```python
path('tasks/new/', views.TaskCreateView.as_view(), name='task_create'),
```

**File:** `projects/templates/projects/task_list.html`

Replace line 17:

```html
<!-- BEFORE: <a href="#" class="btn btn-primary btn-sm">Create Task</a> -->
<!-- AFTER: -->
<a href="{% url 'projects:task_create' %}" class="btn btn-primary btn-sm">Create Task</a>
```

### Fix 2.3: Time Entry Create View

**File:** `projects/views.py`

Add after existing TimeEntryListView:

```python
class TimeEntryCreateView(LoginRequiredMixin, CreateView):
    """Create a new time entry."""
    model = TimeEntry
    form_class = TimeEntryForm  # Create in forms.py
    template_name = 'projects/timeentry_form.html'
    success_url = reverse_lazy('projects:timeentry_list')
    login_url = 'login'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Time entry created successfully.')
        return super().form_valid(form)
```

**File:** `projects/urls.py`

Add URL pattern:

```python
path('time-entries/new/', views.TimeEntryCreateView.as_view(), name='timeentry_create'),
```

**File:** `projects/templates/projects/timeentry_list.html`

Replace line 17:

```html
<!-- BEFORE: <a href="#" class="btn btn-primary btn-sm">Log Time</a> -->
<!-- AFTER: -->
<a href="{% url 'projects:timeentry_create' %}" class="btn btn-primary btn-sm">Log Time</a>
```

---

## PRIORITY 3: HR Module

### Issue Summary
2 broken buttons in leave requests and performance

### Fix 3.1: Leave Request Detail View

**File:** `hr/views.py`

Add after existing LeaveRequestCreateView:

```python
class LeaveRequestDetailView(LoginRequiredMixin, DetailView):
    """View leave request details."""
    model = LeaveRequest
    template_name = 'hr/leave_request_detail.html'
    context_object_name = 'leave_request'
    login_url = 'login'
```

**File:** `hr/urls.py`

Add URL pattern:

```python
path('leave-requests/<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave-request-detail'),
```

**File:** `hr/templates/hr/leave_request_list.html`

Replace line 109:

```html
<!-- BEFORE: <a href="#" class="btn btn-sm btn-info" title="View"> -->
<!-- AFTER: -->
<a href="{% url 'hr:leave-request-detail' request.id %}" class="btn btn-sm btn-info" title="View">
```

### Fix 3.2: Performance Detail View

**File:** `hr/views.py`

Add after existing PerformanceCreateView:

```python
class PerformanceDetailView(LoginRequiredMixin, DetailView):
    """View performance review details."""
    model = Performance
    template_name = 'hr/performance_detail.html'
    context_object_name = 'performance'
    login_url = 'login'
```

**File:** `hr/urls.py`

Add URL pattern:

```python
path('performance/<int:pk>/', views.PerformanceDetailView.as_view(), name='performance-detail'),
```

**File:** `hr/templates/hr/performance_list.html`

Replace line 56:

```html
<!-- BEFORE: <a href="#" class="btn btn-sm btn-info" title="View"> -->
<!-- AFTER: -->
<a href="{% url 'hr:performance-detail' perf.id %}" class="btn btn-sm btn-info" title="View">
```

---

## PRIORITY 3: AR Module

### Issue Summary
1 broken button in customer payments edit

### Fix 4.1: Customer Payment Update View

**File:** `ar/views.py`

Add after existing CustomerPaymentDetailView:

```python
class CustomerPaymentUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing customer payment."""
    model = CustomerPayment
    form_class = CustomerPaymentForm
    template_name = 'ar/customerpayment_form.html'
    success_url = reverse_lazy('ar:payment_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Payment {form.instance.payment_number} updated successfully.')
        return super().form_valid(form)
```

**File:** `ar/urls.py`

Add URL pattern:

```python
path('payments/<int:pk>/edit/', views.CustomerPaymentUpdateView.as_view(), name='payment_edit'),
```

**File:** `ar/templates/ar/customerpayment_list.html`

Replace line 81:

```html
<!-- BEFORE: <a href="#" class="btn btn-sm btn-warning">Edit</a> -->
<!-- AFTER: -->
<a href="{% url 'ar:payment_edit' payment.id %}" class="btn btn-sm btn-warning">Edit</a>
```

---

## Forms.py Updates Required

Create or update the following forms in their respective modules:

### cash_management/forms.py

Add these forms:

```python
from django import forms
from .models import PaymentSchedule, CashPosition, LiquidityForecast, TreasuryAccount, FXExposure

class PaymentScheduleForm(forms.ModelForm):
    class Meta:
        model = PaymentSchedule
        fields = ['payment_date', 'amount', 'status', 'description']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CashPositionForm(forms.ModelForm):
    class Meta:
        model = CashPosition
        fields = ['account', 'position_date', 'amount', 'currency', 'notes']
        widgets = {
            'position_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class LiquidityForecastForm(forms.ModelForm):
    class Meta:
        model = LiquidityForecast
        fields = ['forecast_date', 'projected_inflows', 'projected_outflows', 'assumptions']
        widgets = {
            'forecast_date': forms.DateInput(attrs={'type': 'date'}),
            'assumptions': forms.Textarea(attrs={'rows': 3}),
        }

class TreasuryAccountForm(forms.ModelForm):
    class Meta:
        model = TreasuryAccount
        fields = ['account_name', 'account_type', 'currency', 'bank', 'account_number']

class FXExposureForm(forms.ModelForm):
    class Meta:
        model = FXExposure
        fields = ['transaction_currency', 'transaction_amount', 'functional_currency', 'value_date', 'exposure_type']
        widgets = {
            'value_date': forms.DateInput(attrs={'type': 'date'}),
        }
```

### projects/forms.py

Add these forms:

```python
from django import forms
from .models import Project, Task, TimeEntry

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'budget', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'assigned_to', 'due_date', 'priority', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['task', 'date', 'hours', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }
```

### hr/forms.py

Add/update these forms:

```python
from django import forms
from .models import LeaveRequest, Performance

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = ['employee', 'rating_period', 'rating', 'comments', 'goals_achieved']
        widgets = {
            'rating_period': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }
```

### ar/forms.py

Add/update:

```python
class CustomerPaymentForm(forms.ModelForm):
    class Meta:
        model = CustomerPayment
        fields = ['invoice', 'payment_amount', 'payment_date', 'payment_method', 'reference_number']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }
```

---

## Testing Checklist

### For Each Fix:

- [ ] View class exists and is properly defined
- [ ] URL pattern exists in urls.py with correct name
- [ ] Template link uses correct URL tag: `{% url 'app:name' param %}`
- [ ] Form class exists in forms.py (if needed)
- [ ] Test create button navigates to form
- [ ] Test form submission creates/updates object
- [ ] Test success message appears
- [ ] Test redirect to list view works
- [ ] Test with multiple users (permission testing)
- [ ] Test on different browsers/devices

### Integration Tests:

```python
# Example test for new view
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class CashManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.client.login(username='testuser', password='password')
    
    def test_payment_schedule_create_view(self):
        """Test payment schedule create view is accessible."""
        response = self.client.get(reverse('cash_management:paymentschedule_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cash_management/paymentschedule_form.html')
    
    def test_payment_schedule_create_form_submission(self):
        """Test payment schedule creation via form submission."""
        data = {
            'payment_date': '2025-12-01',
            'amount': 1000.00,
            'status': 'PENDING',
        }
        response = self.client.post(reverse('cash_management:paymentschedule_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        # Verify object was created
        self.assertTrue(PaymentSchedule.objects.filter(amount=1000.00).exists())
```

---

## Deployment Checklist

- [ ] All views created and tested
- [ ] All URL patterns added
- [ ] All templates updated with proper links
- [ ] All forms created
- [ ] Database migrations run (if model changes needed)
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual UI testing completed
- [ ] Code review completed
- [ ] Deployed to staging
- [ ] Staging testing completed
- [ ] Deployed to production
- [ ] Production monitoring active

---

## Troubleshooting

### Common Issues

**Issue 1: NoReverseMatch exception**
- Check URL name in template matches urls.py
- Verify parameters passed to URL tag match view's expected parameters

**Issue 2: ImportError for views/forms**
- Ensure view/form class is defined before it's imported in urls.py
- Check for circular imports

**Issue 3: 404 Not Found**
- Verify URL pattern path is correct
- Check view name in URL pattern matches view class

**Issue 4: Forms not rendering properly**
- Check form_class is properly referenced
- Ensure template_name is correct
- Verify form fields match model fields

---

## Estimated Timeline

- **Cash Management:** 3-4 hours
- **Projects:** 1-2 hours
- **HR:** 1 hour
- **AR:** 30 minutes
- **Testing:** 2-3 hours
- **Total:** 7-11 hours

---

**Implementation Date:** [To be scheduled]  
**Implemented By:** [To be assigned]  
**Reviewed By:** [To be assigned]  

