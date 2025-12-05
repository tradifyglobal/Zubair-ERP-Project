# Workflow Permission Checkbox Fix

## Problem
When adding or updating "Workflow Reviewer" and "Workflow Approver" permissions for a user and then editing the user again, the checkboxes would appear unchecked even though the permissions were saved in the database.

## Root Cause
The issue was in the user edit form template (`user_edit.html`). The template was using nested loops to find and render form fields:

```html
<td class="text-center">
    {% for field in permission_form %}
        {% if field.name == module_code|add:"_can_view" %}
            {{ field }}
        {% endif %}
    {% endfor %}
</td>
```

### Why This Was Problematic

1. **Inefficient**: The template iterates through ALL form fields multiple times (7 times per module) to find matching fields
2. **Fragile**: String matching between `field.name` and dynamically generated field names is error-prone
3. **Template Duplication Bug**: There was actually a duplicate `<td>` opening tag that was breaking the table structure
4. **Rendering Issues**: The nested loops could cause the BoundField rendering to behave unexpectedly

## Solution

### Changes Made

#### 1. Enhanced User View Context (`accounting/user_views.py`)
Added an organized `form_fields` context variable that pre-organizes form BoundFields by module and permission type:

```python
form_fields_by_module = {}
for module_code, module_name in ModulePermission.MODULE_CHOICES:
    form_fields_by_module[module_code] = {
        'view': permission_form[f'{module_code}_can_view'],
        'add': permission_form[f'{module_code}_can_add'],
        # ... etc for all permission types
    }
context['form_fields'] = form_fields_by_module
```

#### 2. Simplified Template (`accounting/templates/accounting/user_management/user_edit.html`)
Changed from nested loops to direct dictionary access:

```html
<td class="text-center">{{ form_fields|get_item:module_code|get_item:"view" }}</td>
<td class="text-center">{{ form_fields|get_item:module_code|get_item:"add" }}</td>
<!-- ... etc -->
```

#### 3. Added Template Filter (`accounting/templatetags/permission_tags.py`)
Added `get_item` filter for dictionary/form access in templates:

```python
@register.filter
def get_item(form, key):
    """Get an item from a form by key (for use with context-provided keys)."""
    if form and hasattr(form, '__getitem__'):
        try:
            return form[key]
        except (KeyError, TypeError):
            return None
    return None
```

#### 4. Added Include Template (`accounting/templates/includes/form_checkbox_field.html`)
Simple fallback include for field rendering if needed.

## How It Works Now

1. **Context Generation**: When viewing/editing a user, the view generates a `form_fields` dictionary with all permission checkboxes pre-organized
2. **Template Access**: The template simply looks up the form field from the organized structure
3. **Proper Rendering**: Django's form BoundField is properly rendered with the correct `checked` attribute based on initial values
4. **Simplified Submission**: All form fields are rendered as proper form inputs with correct names, ensuring they're submitted with form data

## Testing

The fix has been tested to ensure:
- ✅ Form fields render with correct HTML attributes
- ✅ Checkboxes show as `checked` when permissions are already saved
- ✅ Form submission properly captures checkbox states
- ✅ All modules (accounting, hr, manufacturing, sales, inventory, procurement, ap, ar, crm, projects, cash_management, shareholder, maintenance, reviewer, approver) work correctly
- ✅ After save and reload, permissions persist correctly

## Files Modified

1. `accounting/user_views.py` - Enhanced context data
2. `accounting/templates/accounting/user_management/user_edit.html` - Simplified template
3. `accounting/templatetags/permission_tags.py` - Added get_item filter
4. `accounting/templates/includes/form_checkbox_field.html` - Added include template

## Impact

This fix ensures that:
- Workflow Reviewer and Approver permissions are properly preserved across user edit sessions
- The user interface is more responsive (fewer template loops)
- The code is more maintainable (cleaner template logic)
- Other permission types (View, Add, Edit, Delete, Export) also render correctly

## Migration Notes

No database migrations needed. This is a pure template/view fix that doesn't change the data model or existing data.
