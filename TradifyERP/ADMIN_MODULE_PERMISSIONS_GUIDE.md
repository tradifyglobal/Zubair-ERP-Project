# Module Permissions Admin Interface

## Overview
Enhanced Django admin interface for managing module permissions with all checkboxes for granular access control.

## Features

### 1. ModulePermissionAdmin
Standalone admin interface for managing module permissions globally.

**Location**: Django Admin → Accounting → Module Permissions

**Features**:
- ✅ View all module permissions by user and module
- ✅ Filter by: Module, Active status, Permission types, Date granted
- ✅ Search by username, email, or name
- ✅ Show permission summary (View, Add, Edit, Delete, Approve, Export)
- ✅ Display audit information (who granted, when, date created/updated)
- ✅ Manage all permission types:
  - ✅ View - Can view/read records
  - ✅ Add - Can create new records
  - ✅ Edit - Can modify existing records
  - ✅ Delete - Can delete records
  - ✅ Approve - Can approve transactions
  - ✅ Export - Can export data

### 2. CustomUserAdmin with ModulePermissionInline
Extended Django User admin with inline permission editing.

**Location**: Django Admin → Auth → Users → [Edit User]

**Features**:
- ✅ Edit user information (username, email, first/last name, password)
- ✅ Manage user status (active, staff, superuser)
- ✅ Edit group memberships
- ✅ **New**: Inline Module Permissions section
  - Add multiple module permissions without leaving the user page
  - Edit all permission checkboxes for each module
  - Activate/deactivate permissions
  - Shows all 15 available modules

## Accessing the Admin Interface

### View/Edit Module Permissions Directly
```
http://localhost:8000/admin/accounting/modulepermission/
```

### Edit User with Inline Permissions
```
http://localhost:8000/admin/auth/user/[user_id]/change/
```

Example:
```
http://localhost:8000/admin/auth/user/2/change/
```

## How to Grant Permissions

### Method 1: From Module Permissions Admin Page
1. Go to **Django Admin → Accounting → Module Permissions**
2. Click **"Add Module Permission"** button
3. Select the user
4. Select the module (Accounting, HR, Manufacturing, etc.)
5. Check the desired permissions:
   - View
   - Add
   - Edit
   - Delete
   - Approve
   - Export
6. Set "Active" status (checked by default)
7. Add notes if needed
8. Click **Save**

### Method 2: From User Edit Page (Recommended)
1. Go to **Django Admin → Auth → Users**
2. Click on the user to edit
3. Scroll down to **"Module Permissions"** section
4. Click **"Add another Module Permission"** to add a new permission row
5. Fill in:
   - Module: Select from dropdown
   - Checkboxes: View, Add, Edit, Delete, Approve, Export
   - Active: Check to enable permission
6. Click **Save** at bottom of page

## Available Modules

1. **accounting** - Accounting & Finance
2. **hr** - Human Resources
3. **manufacturing** - Manufacturing
4. **sales** - Sales Management
5. **inventory** - Inventory Management
6. **procurement** - Procurement
7. **ap** - Accounts Payable
8. **ar** - Accounts Receivable
9. **crm** - Customer Relationship Management
10. **projects** - Project Management
11. **cash_management** - Cash Management
12. **shareholder** - Shareholder Management
13. **maintenance** - Site Maintenance
14. **reviewer** - Workflow Reviewer
15. **approver** - Workflow Approver

## Permission Types

| Permission | Description |
|-----------|-------------|
| **View** | Can view/read records in this module |
| **Add** | Can create new records in this module |
| **Edit** | Can modify existing records in this module |
| **Delete** | Can delete records in this module |
| **Approve** | Can approve transactions in this module |
| **Export** | Can export data from this module |

## Common Scenarios

### Grant Full Access to a Module
1. Go to user's edit page
2. In Module Permissions, select the module
3. Check: View, Add, Edit, Delete, Approve, Export
4. Save

### Grant Read-Only Access
1. Go to user's edit page
2. In Module Permissions, select the module
3. Check only: **View**
4. Save

### Grant Approval-Only Access
1. Go to user's edit page
2. In Module Permissions, select the module
3. Check: **View** and **Approve**
4. Save

### Revoke Access
1. Go to Module Permissions admin page
2. Find the permission record
3. Uncheck "Active" checkbox
4. Save

## Admin Features

### List View
- **Columns**: User, Module, Permission Summary, Active Status, Date Granted
- **Filters**: Module, Active Status, Permission Types, Date Range
- **Search**: Find by username, email, first/last name
- **Date Hierarchy**: Navigate by granted date

### Detail View
- **User & Module**: Select user and module (read-only on edit)
- **Permissions**: All 6 checkboxes for granular control
- **Additional Info**: Access level description, activation status, notes
- **Audit Information**: Who granted it, date granted, created/updated dates

## Audit Trail

Each permission record tracks:
- ✅ **User**: Who the permission is for
- ✅ **Module**: Which module
- ✅ **Granted By**: Who granted the permission (auto-set to current admin user)
- ✅ **Granted Date**: When the permission was granted
- ✅ **Created At**: When the record was created
- ✅ **Updated At**: Last modification timestamp

## Technical Details

### Model
```python
class ModulePermission(models.Model):
    user = ForeignKey(User)  # User the permission is for
    module = CharField(choices=MODULE_CHOICES)  # Module code
    can_view = BooleanField()
    can_add = BooleanField()
    can_edit = BooleanField()
    can_delete = BooleanField()
    can_approve = BooleanField()
    can_export = BooleanField()
    is_active = BooleanField()
    granted_by = ForeignKey(User)  # Admin who granted it
    granted_date = DateTimeField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Admin Configuration
- **ModulePermissionInline**: Tabular inline for inline editing in User admin
- **ModulePermissionAdmin**: Standalone admin with advanced filtering and search
- **CustomUserAdmin**: Extended User admin with ModulePermissionInline

## Best Practices

1. ✅ **Use the User edit page** for managing permissions for specific users (Method 2)
2. ✅ **Use Module Permissions admin** for viewing all permissions globally
3. ✅ **Grant minimum necessary access** - only check needed permissions
4. ✅ **Document special access** - use notes field for temporary or special permissions
5. ✅ **Review regularly** - audit who has what access periodically
6. ✅ **Deactivate instead of delete** - use "Active" toggle to revoke access while preserving history

## Troubleshooting

### Permission Not Showing
- Check if "Active" checkbox is checked
- Verify the permission was saved (look for created_at date)
- Refresh the page

### Can't See Module Permissions in User Admin
- Ensure you're viewing the edit page (change), not the add page
- The inline section appears after the user is saved

### Changes Not Taking Effect
- Clear browser cache or do a hard refresh (Ctrl+Shift+R)
- Clear Django cache: `python manage.py cache_clear`
- Restart the server

## Files Modified

1. `accounting/admin.py` - Added:
   - `ModulePermissionInline` class
   - `ModulePermissionAdmin` class  
   - `CustomUserAdmin` class
   - Unregistered default User admin and registered custom one

## Integration

These admin changes integrate with:
- **Frontend User Management**: `/accounting/users/` page
- **Permission System**: `accounting.module_permissions.ModulePermission`
- **Permission Checking**: `permission_utils.py` decorators
- **Context Processors**: Global permission context in templates

## Related Documentation

- See `WORKFLOW_PERMISSION_FIX.md` for checkbox rendering fixes
- See `Readme-Files/PERMISSION_SYSTEM_IMPLEMENTATION.md` for system overview
- See `Readme-Files/ADMIN_403_FIX.md` for Django admin access configuration
