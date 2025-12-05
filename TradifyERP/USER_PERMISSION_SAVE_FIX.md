# User Permission Save Fix

## Problem

The user edit page (`/accounting/users/12/edit/`) was **not saving module permissions** when the user attempted to update them.

## Root Cause

The issue was a **cascading form validation error** in the `UserEditView.form_valid()` method:

1. **Entity Form was Required**: `UserEntityAssignmentForm.entities` field was `required=True` by default
2. **Transaction Atomicity**: The entire `form_valid()` method was wrapped in `@transaction.atomic`, which means ALL database changes are rolled back if ANY error occurs
3. **Validation Cascade**: When the entity form had validation errors (e.g., no entities selected), the database transaction was completely rolled back, INCLUDING the successfully-processed module permission changes

### Flow That Caused the Bug:

```
1. User fills out module permissions checkboxes
2. User submits form
3. UserEditForm validates successfully ✓
4. BulkModulePermissionForm validates successfully ✓
5. Permissions are prepared to save ✓
6. UserEntityAssignmentForm validates...
7. Entity form FAILS (entities field is required but none selected) ✗
8. @transaction.atomic rolls back EVERYTHING
9. Nothing gets saved - both permissions and entities are rolled back
10. User sees warning: "Entity assignments had validation errors"
11. User thinks permissions weren't saved (and they weren't!)
```

## Solution

### Change 1: Make Entity Form Optional

**File**: `accounting/user_permission_forms.py`

```python
entities = forms.ModelMultipleChoiceField(
    queryset=Entity.objects.filter(is_active=True),
    widget=forms.CheckboxSelectMultiple(attrs={
        'class': 'form-check-input entity-checkbox',
    }),
    label="Assigned Entities",
    help_text="Select which entities this user can access",
    required=False  # <-- CHANGED: Was required=True (default)
)
```

This allows the entity form to remain valid even when no entities are selected, preventing the cascade failure.

### Change 2: Better Error Handling

**File**: `accounting/user_views.py`

Modified `UserEditView.form_valid()` to:
- Separate permission save from entity assignment errors
- Show informative messages when entity form has errors
- Always allow permissions to save independently

```python
# Get entity assignment form
entity_form = UserEntityAssignmentForm(self.request.POST, user=user)
if entity_form.is_valid():
    entity_form.save(user=user, granted_by=self.request.user)
    messages.success(self.request, f'Entity assignments updated for "{user.username}".')
else:
    # Log but don't prevent saving
    logger.warning(f"Entity form had validation errors (non-blocking): {entity_form.errors}")
    messages.info(self.request, 'Note: Entity assignments were not changed...')
```

## Testing

The fix was tested with:
- Permission changes with no entity form data
- Form validation passes independently
- Database saves correctly
- User sees appropriate success messages

## Impact

- ✅ Users can now update module permissions successfully
- ✅ Entity assignments can still be managed independently
- ✅ Better error messaging
- ✅ No unintended transaction rollbacks

## Files Changed

1. `accounting/user_permission_forms.py` - Made entities field optional
2. `accounting/user_views.py` - Improved error handling and logging

## Deployment

No migrations required. This is a form and view logic change only.

