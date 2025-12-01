# HR Module Entity Segregation Implementation

## Overview
All HR module views and forms have been updated to ensure proper entity-based segregation using the `SessionEntityMixin`. This ensures that users can only see and interact with data belonging to their selected entity.

## Architecture

### Core Mixin: SessionEntityMixin
**Location:** `accounting/mixins.py`

The `SessionEntityMixin` provides automatic entity filtering by:
1. Checking for selected entity in session (`selected_entity_id`)
2. Filtering querysets by entity field where applicable
3. Adding entity context to templates
4. Redirecting to entity selection if no entity is selected

**Key Methods:**
- `dispatch()` - Validates entity selection before view processing
- `get_queryset()` - Filters by entity for models with direct entity field
- `get_context_data()` - Adds entity information to template context

## Entity Segregation Strategy

### 1. Models with Direct Entity Field

Models that directly own entity relationship (automatically filtered by SessionEntityMixin.get_queryset()):
- `Department` (ForeignKey to Entity)
- `Position` (ForeignKey to Entity)
- `Employee` (ForeignKey to Entity)
- `Payroll` (ForeignKey to Entity)
- `Benefit` (ForeignKey to Entity)
- `Leave` (ForeignKey to Entity)

**Implementation:** Views using these models call `super().get_queryset()` to leverage SessionEntityMixin filtering:
```python
def get_queryset(self):
    queryset = super().get_queryset()  # SessionEntityMixin handles entity filtering
    # Additional filtering (search, status, etc.)
    return queryset
```

### 2. Models with Entity Through Employee Relationship

Models that access entity through Employee (manual entity_id filtering required):
- `Attendance` (employee__entity_id)
- `PayrollRecord` (employee__entity_id)
- `SalaryHistory` (employee__entity_id)
- `EmployeeBenefit` (employee__entity_id)
- `LeaveBalance` (employee__entity_id)
- `LeaveRequest` (employee__entity_id)
- `Disciplinary` (employee__entity_id)
- `Performance` (employee__entity_id)

**Implementation:** Views manually filter using session entity:
```python
def get_queryset(self):
    entity_id = self.request.session.get('selected_entity_id')
    queryset = ModelName.objects.filter(employee__entity_id=entity_id) if entity_id else ModelName.objects.none()
    # Additional filtering
    return queryset
```

## Updated Views

### List Views (All with SessionEntityMixin)

| View | Model | Entity Filter | Implementation |
|------|-------|----------------|-----------------|
| EmployeeListView | Employee | Direct (entity_id) | super().get_queryset() + search |
| PositionListView | Position | Direct (entity_id) | super().get_queryset() + search |
| DepartmentListView | Department | Direct (entity_id) | super().get_queryset() + search |
| BenefitListView | Benefit | Direct (entity_id) | super().get_queryset() + search |
| LeaveListView | Leave | Direct (entity_id) | super().get_queryset() + search |
| PayrollListView | Payroll | Direct (entity_id) | Manual (session) + search + status filters |
| AttendanceListView | Attendance | Through Employee (employee__entity_id) | Manual (session) + search |
| PayrollRecordListView | PayrollRecord | Through Employee (employee__entity_id) | Manual (session) + search |
| SalaryHistoryListView | SalaryHistory | Through Employee (employee__entity_id) | Manual (session) + search |
| EmployeeBenefitListView | EmployeeBenefit | Through Employee (employee__entity_id) | Manual (session) + search |
| LeaveBalanceListView | LeaveBalance | Through Employee (employee__entity_id) | Manual (session) + search |
| DisciplinaryListView | Disciplinary | Through Employee (employee__entity_id) | Manual (session) + search |
| LeaveRequestListView | LeaveRequest | Through Employee (employee__entity_id) | Manual (session) + status filter |
| PerformanceListView | Performance | Through Employee (employee__entity_id) | Manual (session) |

### Detail/Update Views

| View | Entity Filter Implementation |
|------|------------------------------|
| EmployeeDetailView | Added get_queryset() for entity filtering |
| PayrollDetailView | Added get_queryset() for entity filtering |
| PayrollApproveView | Added get_queryset() for entity filtering |

### Create Views

| View | Entity Handling |
|------|-----------------|
| EmployeeCreateView | Entity set via form pre-population from session |
| PayrollCreateView | Entity set via form pre-population from session |
| LeaveRequestCreateView | Employee must belong to user's entity (validated by SessionEntityMixin) |
| PerformanceCreateView | Added form_valid() for consistency |

### Function-Based Views

| View | Entity Validation |
|------|-------------------|
| create_position() | UPDATED: Entity set from session, validates entity_id exists |
| approve_leave_request() | Entity validated against employee's entity |
| payroll_post_to_gl() | Entity validated against payroll's entity |
| employee_payroll_history() | Entity validated against employee's entity |
| hr_dashboard() | Filters all statistics by session entity |

## Updated Forms

### Forms with Entity Field Added/Updated

**Entity fields are now included in forms for consistency:**

1. **EmployeeForm** - Already had entity field with session pre-population
2. **DepartmentForm** - UPDATED: Added entity field with session pre-population
3. **PositionForm** - UPDATED: Added entity field with session pre-population
4. **PayrollForm** - Already had entity field with session pre-population
5. **BenefitForm** - UPDATED: Added entity field with session pre-population
6. **LeaveRequestForm** - Entity not needed (filtered via employee)
7. **PerformanceForm** - Entity not needed (filtered via employee)
8. **DisciplinaryForm** - Entity not needed (filtered via employee)

### Form Implementation Pattern

```python
def __init__(self, *args, **kwargs):
    request = kwargs.pop('request', None)
    super().__init__(*args, **kwargs)
    
    # Pre-populate entity from session
    if request and hasattr(request, 'session'):
        entity_id = request.session.get('selected_entity_id')
        if entity_id:
            self.fields['entity'].initial = entity_id
```

### View Form Integration

CreateView and UpdateView classes pass request to forms:
```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['request'] = self.request
    return kwargs
```

## Security Measures

### 1. SessionEntityMixin Dispatch
- Validates entity_id exists in session before allowing access
- Redirects to entity selection if no entity_id present
- Verifies entity exists and is active in database

### 2. Entity Validation in Function-Based Views
All function-based views that modify data validate:
```python
entity_id = request.session.get('selected_entity_id')
if object.entity_id != entity_id:
    return JsonResponse({'error': 'Unauthorized'}, status=403)
```

### 3. Queryset Filtering
- All list views automatically filter by session entity
- No cross-entity data visible to users
- Detail views verify ownership before displaying

## Testing Checklist

- [ ] Access each list view and verify only entity-specific data displays
- [ ] Verify search functionality works within entity scope
- [ ] Test create forms auto-populate entity from session
- [ ] Test update views only show editable objects from current entity
- [ ] Verify function-based views return 403 for cross-entity requests
- [ ] Test pagination works correctly on entity-filtered querysets
- [ ] Verify dashboard statistics only count entity-specific records
- [ ] Test that switching entities shows different data
- [ ] Verify session entity_id used consistently across all views

## Files Modified

### Views
- `hr/views.py` - Updated all views for entity segregation

### Forms
- `hr/forms.py` - Added entity field to DepartmentForm, PositionForm, BenefitForm

### Mixins
- `accounting/mixins.py` - SessionEntityMixin (no changes, already provided)

## Key Improvements

1. **Consistency** - All views use same SessionEntityMixin pattern
2. **Security** - Multi-layer validation of entity ownership
3. **Maintainability** - Centralized entity logic in mixin
4. **Scalability** - Easy to add new views following established pattern
5. **Performance** - Entity filtering at database query level
6. **User Experience** - Automatic entity pre-population in forms

## Implementation Notes

### For Creating New HR Views

Follow this pattern:

```python
class NewResourceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = ResourceModel
    paginate_by = 20
    
    def get_queryset(self):
        # If model has direct entity field:
        queryset = super().get_queryset()
        
        # If model accesses entity through relationship:
        entity_id = self.request.session.get('selected_entity_id')
        queryset = ResourceModel.objects.filter(employee__entity_id=entity_id)
        
        # Add search/filters
        return queryset

class NewResourceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = ResourceModel
    form_class = ResourceForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
```

### Form Creation Pattern

```python
class ResourceForm(forms.ModelForm):
    class Meta:
        model = ResourceModel
        fields = ['entity', ...]  # Include entity field
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id
```

## Troubleshooting

### View Returns No Results
- Verify session has `selected_entity_id`
- Check user has active UserRole for the entity
- Verify data exists for the selected entity

### Form Doesn't Pre-populate Entity
- Ensure `get_form_kwargs()` passes request to form
- Check form __init__ receives and processes request
- Verify selected_entity_id exists in session

### FieldError on Relationship Queries
- Models with Employee relationship use `employee__entity_id`
- Not `entity_id` directly
- Check model definition for actual relationship path

## Related Documentation

- See `accounting/mixins.py` for SessionEntityMixin full implementation
- See `accounting/models.py` for Entity model structure
- See `accounting/role_models.py` for UserRole access control
