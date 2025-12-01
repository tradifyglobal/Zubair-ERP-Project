# Module Permission System - User Guide

## Overview
The TradifyERP Module Permission System allows administrators to control which modules each user can access and what actions they can perform (View, Add, Edit, Delete, Approve, Export).

## Features

### ✅ Granular Module Access Control
- **12 Modules**: Accounting, HR, Manufacturing, Sales, Inventory, Procurement, AP, AR, CRM, Projects, Cash Management, Shareholder, Maintenance
- **6 Permission Types**: View, Add, Edit, Delete, Approve, Export
- **User-Specific**: Different permissions for each user
- **Quick Templates**: Pre-configured permission sets for common roles

### ✅ Permission Templates

1. **Full Administrator** - Access to all modules with all permissions
2. **Accountant** - Full access to accounting modules, view only for others
3. **Accounting View Only** - Read-only access to accounting modules
4. **HR Manager** - Full HR access, view only for other modules
5. **Sales Manager** - Full sales & CRM, view inventory & accounting
6. **Inventory Manager** - Full inventory & procurement, view manufacturing & accounting
7. **Read Only All** - View-only access to all modules
8. **Custom** - Manually select permissions

## How to Use

### Accessing User Management

1. Navigate to **Dashboard** → **Users** (available in sidebar for admin users)
2. Or visit: `http://your-server/users/`

### Creating a New User

1. Click "**Add New User**" button
2. Fill in user information:
   - Username
   - First Name & Last Name
   - Email Address
   - Password (twice for confirmation)
   - Staff Status (can access admin site)
   - Active Status

3. **Choose Permission Method**:

   **Option A: Use Quick Template**
   - Select a template from dropdown
   - Click "Apply Template" (on save, permissions will be set)
   
   **Option B: Manual Selection**
   - Check boxes for each module and permission type
   - Select "View" to allow access to the module
   - Select "Add/Edit/Delete" for specific actions
   - Select "Approve" for approval rights
   - Select "Export" to allow data export

4. Click "**Create User**" to save

### Editing User Permissions

1. Go to **Users** list
2. Click the **Edit** (pencil icon) button for the user
3. Modify permissions by checking/unchecking boxes
4. Or apply a new template
5. Click "**Update User**" to save changes

### Viewing User Details

1. Go to **Users** list
2. Click the **View** (eye icon) button
3. See:
   - User information
   - All module permissions (checkmarks)
   - Recent activity logs

### Activating/Deactivating Users

1. Go to **Users** list
2. Click the **Toggle Status** (warning icon) button
3. Confirm the action
4. User status will be toggled (Active ↔ Inactive)

## Permission Types Explained

| Permission | Description | Example |
|------------|-------------|---------|
| **View** | Can see/read data in the module | View customer list, invoices |
| **Add** | Can create new records | Create new sales order, add employee |
| **Edit** | Can modify existing records | Update invoice, edit customer info |
| **Delete** | Can remove records | Delete draft orders, remove items |
| **Approve** | Can approve transactions | Approve purchase orders, sign off invoices |
| **Export** | Can export data to Excel/PDF | Export reports, download data |

## Navigation & Access Control

### Automatic Sidebar Filtering
- Users only see modules they have access to in the navigation sidebar
- If a user has no "View" permission for a module, it won't appear in their menu

### Action Button Visibility
- "Add New" buttons only appear if user has "Add" permission
- "Edit" buttons only appear if user has "Edit" permission
- "Delete" buttons only appear if user has "Delete" permission

### Permission Checks
- When user tries to access a page without permission:
  - They are redirected to dashboard
  - An error message is shown
  - Access attempt is logged

## Admin Features

### Access Logs
- All permission checks are logged
- View in user detail page
- Includes:
  - Timestamp
  - Module accessed
  - Action attempted
  - Result (Allowed/Denied)
  - IP address
  - Reason for denial

### Search Users
- Search by username, email, first name, or last name
- Real-time filtering

### User Statistics
- Total users count
- Active users count
- Inactive users count
- Module access summary

## Technical Details

### Models Created
1. **ModulePermission** - Stores user-to-module permissions
2. **UserModuleAccessLog** - Audit trail of access attempts

### Database Tables
- `accounting_modulepermission`
- `accounting_usermoduleaccesslog`

### URL Endpoints
```
/users/                          - List all users
/users/create/                   - Create new user
/users/<id>/                     - View user details
/users/<id>/edit/                - Edit user & permissions
/users/<id>/toggle-status/       - Activate/deactivate user
/users/<id>/apply-template/      - Apply permission template
```

### Permission Decorators (for Developers)
```python
# Function-based view
@module_permission_required('accounting', 'add')
def my_view(request):
    ...

# Class-based view
class MyView(ModulePermissionMixin, ListView):
    module_name = 'accounting'
    required_action = 'view'
    ...
```

### Template Context Variables
```django
{% if can_access_module 'accounting' %}
    <!-- Show accounting content -->
{% endif %}

{% if can_perform_action 'accounting' 'add' %}
    <a href="...">Add New</a>
{% endif %}
```

## Example Scenarios

### Scenario 1: Accountant User
**Permissions:**
- Accounting: ✅ View, Add, Edit, Delete, Approve, Export
- AP: ✅ View, Add, Edit, Delete, Approve
- AR: ✅ View, Add, Edit, Delete, Approve
- Cash Management: ✅ View, Add, Edit, Approve
- HR: ✅ View only
- Sales: ✅ View only
- Other modules: ❌ No access

**Result:** Can fully manage accounting, payables, receivables, and cash. Can view but not modify HR and sales data. Cannot access manufacturing, inventory, etc.

### Scenario 2: Sales Representative
**Permissions:**
- Sales: ✅ View, Add, Edit
- CRM: ✅ View, Add, Edit
- Inventory: ✅ View only
- Accounting: ✅ View only (invoices)
- Other modules: ❌ No access

**Result:** Can create and manage sales orders and CRM leads. Can check inventory levels. Can view invoices but cannot modify accounting data.

### Scenario 3: View-Only Auditor
**Permissions:**
- All modules: ✅ View, Export only

**Result:** Can see all data across all modules and export reports, but cannot create, modify, or delete anything.

## Best Practices

1. **Least Privilege Principle**: Give users only the permissions they need
2. **Use Templates**: Start with a template, then customize if needed
3. **Regular Reviews**: Periodically review and update user permissions
4. **Deactivate Instead of Delete**: Deactivate users who no longer need access (keeps audit trail)
5. **Document Roles**: Keep a record of which permissions each job role should have
6. **Test Permissions**: After creating a user, test by logging in as that user

## Security Notes

- ⚠️ **Superusers bypass all permission checks** - they have unrestricted access
- ⚠️ **Staff status** allows access to Django admin site
- ✅ All permission checks are logged for audit purposes
- ✅ Permission checks happen at both view level and template level
- ✅ Direct URL access is blocked if user lacks permissions

## Troubleshooting

### User Can't See a Module
- Check if "View" permission is enabled for that module
- Ensure user account is "Active"
- Check if user is logged in

### User Gets "Permission Denied" Error
- Verify the specific permission (Add/Edit/Delete) is enabled
- Check access logs to see what permission was missing
- Ensure module permission exists (not just system-wide permission)

### Template Dropdown Not Working
- Ensure JavaScript is enabled in browser
- Check browser console for errors
- Try manual permission selection instead

## Support

For issues or questions about the permission system:
1. Check this guide
2. Review user access logs
3. Contact system administrator
4. Check Django admin for raw permission data

---

**Version:** 1.0  
**Last Updated:** November 22, 2025  
**Module:** accounting.module_permissions
