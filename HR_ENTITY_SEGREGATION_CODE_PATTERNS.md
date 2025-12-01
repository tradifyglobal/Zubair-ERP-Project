# HR Module Entity Segregation - Code Patterns Reference

## Overview
This document provides quick reference code patterns used in the HR module for entity segregation.

## Pattern 1: List View with Direct Entity Field

**Models affected:** Department, Position, Employee, Payroll, Benefit, Leave

```python
from django.views.generic import ListView
from accounting.mixins import SessionEntityMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class DepartmentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all departments."""
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20
    
    def get_queryset(self):
        # SessionEntityMixin automatically filters by entity_id
        queryset = super().get_queryset()
        
        # Add additional filtering (search, filters, etc.)
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset
```

**Why this works:**
- SessionEntityMixin.get_queryset() automatically adds `.filter(entity_id=entity_id)`
- Works only for models with direct entity field
- Reduces code duplication

---

## Pattern 2: List View with Entity Through Relationship

**Models affected:** Attendance, PayrollRecord, SalaryHistory, EmployeeBenefit, LeaveBalance, LeaveRequest, Disciplinary, Performance

```python
from django.views.generic import ListView
from accounting.mixins import SessionEntityMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class AttendanceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all attendance records."""
    model = Attendance
    template_name = 'hr/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 20
    
    def get_queryset(self):
        # Must manually filter for models without direct entity field
        entity_id = self.request.session.get('selected_entity_id')
        queryset = Attendance.objects.filter(
            employee__entity_id=entity_id
        ).order_by('-attendance_date') if entity_id else Attendance.objects.none()
        
        # Add additional filtering
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return queryset
```

**Why this pattern:**
- SessionEntityMixin can't automatically filter these (no direct entity field)
- Must use `employee__entity_id` to access entity through relationship
- SessionEntityMixin still handles dispatch() validation and context

---

## Pattern 3: Detail View with Entity Filtering

**For any DetailView needing entity validation:**

```python
from django.views.generic import DetailView
from accounting.mixins import SessionEntityMixin
from django.contrib.auth.mixins import LoginRequiredMixin

class PayrollDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View payroll details and records."""
    model = Payroll
    template_name = 'hr/payroll_detail.html'
    context_object_name = 'payroll'
    
    def get_queryset(self):
        # Filter to only show objects from selected entity
        entity_id = self.request.session.get('selected_entity_id')
        return Payroll.objects.filter(
            entity_id=entity_id
        ) if entity_id else Payroll.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add entity-specific data
        payroll = self.get_object()
        context['payroll_records'] = payroll.payroll_records.all()
        return context
```

**Why this matters:**
- Prevents users from guessing URLs to view other entities' records
- get_object_or_404() uses get_queryset() internally
- Returns 404 for non-existent or cross-entity records

---

## Pattern 4: Create View with Entity Pre-population

**For CreateView with direct entity field:**

```python
from django.views.generic import CreateView
from accounting.mixins import SessionEntityMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class DepartmentCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new department."""
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass request to form so it can pre-populate entity
        kwargs['request'] = self.request
        return kwargs
```

**Form handling:**

```python
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['entity', 'name', 'code', 'description', ...]
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate entity from session
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id
```

**Why this approach:**
- Entity field automatically populated from session
- User can't change to different entity (if form is read-only)
- Prevents accidental data assignment to wrong entity

---

## Pattern 5: Function-Based View with Entity Validation

**For function views that modify data:**

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def create_position(request):
    """AJAX endpoint to create a new position."""
    if request.method == 'POST':
        from .forms import PositionForm
        
        # Create form instance
        form = PositionForm(request.POST, request=request)
        
        if form.is_valid():
            # Set entity from session
            position = form.save(commit=False)
            entity_id = request.session.get('selected_entity_id')
            
            if not entity_id:
                return JsonResponse({
                    'success': False,
                    'error': 'No entity selected'
                }, status=400)
            
            position.entity_id = entity_id
            position.save()
            
            return JsonResponse({
                'success': True,
                'id': position.id,
                'title': position.title,
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    }, status=400)

@login_required
def approve_leave_request(request, pk):
    """Approve leave request."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Verify ownership before allowing modification
    entity_id = request.session.get('selected_entity_id')
    if leave_request.employee.entity_id != entity_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        leave_request.status = 'APPROVED'
        leave_request.save()
        return redirect('hr:leave-request-detail', pk=leave_request.id)
    
    return render(request, 'hr/leave_request_approve.html', 
                  {'leave_request': leave_request})
```

**Security checks:**
- Validates entity_id exists before creating objects
- Returns 403 for cross-entity modification attempts
- Uses session entity as authoritative source

---

## Pattern 6: Filtering Related Objects by Entity

**For foreign key dropdowns/filters:**

```python
from django import forms

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['entity', 'department', 'position', 'manager', ...]
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate entity from session
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id
                
                # Filter related fields by entity
                self.fields['department'].queryset = Department.objects.filter(
                    entity_id=entity_id
                )
                self.fields['position'].queryset = Position.objects.filter(
                    entity_id=entity_id
                )
                self.fields['manager'].queryset = Employee.objects.filter(
                    entity_id=entity_id
                )
```

**Why this matters:**
- Users only see dropdowns for their entity's data
- Prevents invalid foreign key assignments
- Improves UX with relevant choices

---

## Session Entity Context

All views that inherit from SessionEntityMixin get access to:

```python
# In the view:
entity_id = self.request.session.get('selected_entity_id')
entity_code = self.request.session.get('selected_entity_code')
entity_name = self.request.session.get('selected_entity_name')
request.entity  # The Entity object (set by mixin dispatch)

# In templates (via context):
{{ entity }}  # Current entity object
{{ selected_entity_id }}  # Entity ID
{{ selected_entity_code }}  # Entity code
{{ selected_entity_name }}  # Entity name
{{ all_entities }}  # All active entities (for switcher)
```

---

## Common Mistakes to Avoid

❌ **WRONG - Using entity_id for models with Employee relationship:**
```python
# This will fail!
queryset = Attendance.objects.filter(entity_id=entity_id)
# Error: Cannot resolve keyword 'entity_id' into field
```

✓ **CORRECT - Using employee__entity_id:**
```python
queryset = Attendance.objects.filter(employee__entity_id=entity_id)
```

---

❌ **WRONG - Forgetting to pass request to form:**
```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    # Missing: kwargs['request'] = self.request
    return kwargs
```

✓ **CORRECT - Pass request for pre-population:**
```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['request'] = self.request
    return kwargs
```

---

❌ **WRONG - Not validating entity in function views:**
```python
@login_required
def modify_data(request, pk):
    obj = get_object_or_404(Model, pk=pk)
    # Missing entity validation!
    obj.field = request.POST.get('value')
    obj.save()
```

✓ **CORRECT - Always validate:**
```python
@login_required
def modify_data(request, pk):
    obj = get_object_or_404(Model, pk=pk)
    
    # Validate entity ownership
    entity_id = request.session.get('selected_entity_id')
    if obj.entity_id != entity_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    obj.field = request.POST.get('value')
    obj.save()
```

---

## Testing These Patterns

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounting.models import Entity
from hr.models import Department, Employee

class EntitySegregationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='pass')
        self.entity1 = Entity.objects.create(name='Entity 1', code='E1')
        self.entity2 = Entity.objects.create(name='Entity 2', code='E2')
    
    def test_list_view_filters_by_entity(self):
        """List view only shows selected entity's data."""
        # Create data in entity1
        dept1 = Department.objects.create(
            entity=self.entity1, name='Dept1', code='D1'
        )
        # Create data in entity2
        dept2 = Department.objects.create(
            entity=self.entity2, name='Dept2', code='D2'
        )
        
        # Login and set entity1
        self.client.login(username='testuser', password='pass')
        session = self.client.session
        session['selected_entity_id'] = self.entity1.id
        session.save()
        
        # Access list view
        response = self.client.get('/hr/departments/')
        
        # Should only see dept1
        self.assertContains(response, 'Dept1')
        self.assertNotContains(response, 'Dept2')
    
    def test_cross_entity_access_forbidden(self):
        """Can't access objects from different entity."""
        dept1 = Department.objects.create(
            entity=self.entity1, name='Dept1', code='D1'
        )
        dept2 = Department.objects.create(
            entity=self.entity2, name='Dept2', code='D2'
        )
        
        self.client.login(username='testuser', password='pass')
        session = self.client.session
        session['selected_entity_id'] = self.entity1.id
        session.save()
        
        # Try to access dept2's detail
        response = self.client.get(f'/hr/departments/{dept2.id}/')
        
        # Should get 404 (filtered out by get_queryset)
        self.assertEqual(response.status_code, 404)
```

---

## Migration from Old Code

If updating existing views without SessionEntityMixin:

**Old:**
```python
class MyListView(LoginRequiredMixin, ListView):
    model = MyModel
    
    def get_queryset(self):
        return MyModel.objects.filter(entity_id=request.session.get('selected_entity_id'))
```

**New:**
```python
class MyListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = MyModel
    
    def get_queryset(self):
        queryset = super().get_queryset()  # SessionEntityMixin handles entity filter
        return queryset
```

---

## References

- Full documentation: `HR_ENTITY_SEGREGATION_SUMMARY.md`
- Implementation: `TradifyERP/hr/views.py`, `TradifyERP/hr/forms.py`
- Core mixin: `TradifyERP/accounting/mixins.py`
