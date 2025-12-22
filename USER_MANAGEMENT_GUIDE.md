# User Management - Where to Add New Users

## ✅ RECOMMENDED: Use ERP User Management (NOT Django Admin)

### Why?
1. **Automatic Module Permissions** - Users get the right access automatically
2. **Entity Assignment** - Users are assigned to the correct business entity
3. **Synchronized** - Synced across the entire ERP system
4. **Better UI** - Purpose-built forms for ERP users
5. **Access Control** - RBAC (Role-Based Access Control) integrated

---

## How to Add New Users - Step by Step

### 1. Navigate to ERP User Management
**URL:** `/accounting/users/`
Or from menu: **ERP User Management → User List**

### 2. Click "Create New User"
**URL:** `/accounting/users/create/`

### 3. Fill in User Information
- **Username** - System login name
- **Email** - User's email address
- **First Name** - User's first name
- **Last Name** - User's last name
- **Password** - Set initial password
- **Confirm Password** - Re-enter password
- **Staff Status** - CHECK THIS (enables admin access)
- **Active** - CHECK THIS (activates account)

### 4. Assign Module Permissions
The system automatically shows checkboxes for each module:
- ✅ **View** - Can see the module
- ✅ **Add** - Can create new records
- ✅ **Edit** - Can modify records
- ✅ **Delete** - Can delete records
- ✅ **Review** - Can review/check records
- ✅ **Approve** - Can approve transactions
- ✅ **Export** - Can export data

**Available Modules:**
- Accounting
- Cash Management
- Shareholder Management
- Expenses
- HR Management
- Manufacturing
- Sales
- Inventory
- Accounts Payable
- Procurement
- CRM
- Projects
- Maintenance

### 5. Assign to Entity
- Select which business entity the user belongs to
- Can assign to multiple entities
- User can switch between assigned entities

### 6. Apply Quick Access Template (Optional)
Choose a pre-built template:
- **Admin** - Full access to all modules
- **Accounting Manager** - Accounting + Cash Management
- **Supervisor** - Reduced access
- **Employee** - Limited access

### 7. Click "Create User"

---

## What Gets Automatically Synced

When you create a user via ERP User Management:

### ✅ Django User Account
- Username
- Email
- Password (hashed)
- Staff status
- Active status

### ✅ User-to-Entity Mapping
- User assigned to selected entity
- UserEntity record created
- Can be multi-entity

### ✅ Module Permissions
- Stored in ModulePermission model
- Can_view, Can_add, Can_edit, Can_delete
- Can_approve, Can_review, Can_export
- Access levels configured

### ✅ Admin Permissions
- All Django admin permissions granted
- Module permission filters applied on top
- Proper RBAC hierarchy

### ✅ Audit Trail
- User creation logged
- All permission changes tracked
- UserModuleAccessLog maintained

---

## DO NOT USE Django Admin to Create Users

### ❌ Why NOT Django Admin?

1. **Missing Module Permissions** - No permissions assigned
2. **No Entity Assignment** - User won't be assigned to entity
3. **Access Control Issues** - User can see all data unfiltered
4. **No Audit Trail** - ERP logging bypassed
5. **Broken Forms** - Module-specific fields missing
6. **Sync Issues** - User won't have proper access to ERP

### ⚠️ If You Already Added Users via Admin:

You MUST go to `/accounting/users/` and edit each user to:
1. Assign to correct entity
2. Set proper module permissions
3. Configure access levels

---

## User Management Features in ERP

### User List (`/accounting/users/`)
- View all users for current entity
- Filter by name, email, username
- See permission count for each user
- See active status
- Statistics: Total users, Active users

### Create New User (`/accounting/users/create/`)
- Full form with validation
- Module permission grid
- Entity assignment
- Quick access templates
- Immediate permission grant

### Edit User (`/accounting/users/<id>/edit/`)
- Update user info
- Modify module permissions
- Change entity assignments
- Apply templates
- Toggle user status (active/inactive)

### User Detail (`/accounting/users/<id>/`)
- View user information
- See all assigned permissions
- See entity assignments
- View access history

### Apply Templates (`/accounting/users/<id>/apply-template/`)
- Quick permission setup
- Pre-defined role templates
- Bulk permission assignment

### Toggle User Status
- Activate/deactivate without deleting
- Maintains audit trail
- Preserves permissions

---

## Permission Levels Explained

### View Only
- User can see data but not modify

### Add/Edit
- User can create and modify records
- Status remains DRAFT until approved

### Delete
- User can delete records
- Deleted items remain in audit trail

### Review
- User can review submissions
- Flag items for correction

### Approve
- User can approve Draft records
- Changes status to APPROVED

### Export
- User can export data to CSV/Excel

---

## Quick Reference

| Task | Location | Impact |
|------|----------|--------|
| Create User | `/accounting/users/create/` | Full sync ✅ |
| Edit User | `/accounting/users/<id>/edit/` | Full sync ✅ |
| Change Permissions | `/accounting/users/<id>/edit/` | Full sync ✅ |
| Change Entity | `/accounting/users/<id>/edit/` | Full sync ✅ |
| Add via Admin | `/admin/auth/user/` | Broken ❌ |
| Deactivate User | `/accounting/users/<id>/edit/` | Full sync ✅ |

---

## Troubleshooting

### User Can't Access a Module?
1. Go to `/accounting/users/<id>/edit/`
2. Check "View" permission is enabled
3. Check user is assigned to correct entity
4. Ensure user is active (is_active=True)

### User Sees Wrong Data?
1. Check entity assignment
2. Verify module permissions
3. Clear browser cache
4. User may need to log out and back in

### User Created in Admin Can't Access ERP?
1. Go to `/accounting/users/`
2. Find the user (created via admin)
3. Click Edit
4. Assign to entity
5. Set module permissions
6. Click Save

---

## Summary

**✅ ALWAYS USE:** `/accounting/users/create/` 
**❌ NEVER USE:** Django Admin for user creation

The ERP User Management system automatically handles:
- User creation
- Entity assignment
- Module permissions
- Access control
- Audit logging
- RBAC synchronization

All in one integrated form!

---

*Best Practice: Use ERP User Management for ALL user operations*
