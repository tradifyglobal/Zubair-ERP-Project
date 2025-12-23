# Password Change Feature - User Interface Guide

## Feature Overview
The user edit page (`/accounting/users/156/edit/`) now includes a password change option alongside the existing user information form.

## Visual Layout

### User Edit Page Structure (After Changes)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Edit User: [username]                           │
├─────────────────────────────────────────────────────────────────────────┤
│
│  LEFT COLUMN (col-lg-6)              RIGHT COLUMN (col-lg-6)
│  ┌──────────────────────┐            ┌──────────────────────┐
│  │ User Information     │            │ Entity Assignment    │
│  │ ─────────────────── │            │ ─────────────────── │
│  │ Username: [_______] │            │ ☐ Entity 1           │
│  │ First Name: [_____] │            │ ☐ Entity 2           │
│  │ Last Name: [______] │            │ ☐ Entity 3           │
│  │ Email: [_________]  │            │                      │
│  │ ☐ Staff Status      │            │ Default Entity: [...] │
│  │ ☐ Is Active         │            │ ☐ Can Switch Entities│
│  └──────────────────────┘            └──────────────────────┘
│
│  LEFT COLUMN (EXPANDED BELOW)
│  ┌──────────────────────┐      ← NEW: PASSWORD CHANGE CARD
│  │ Change Password      │         (ONLY FOR EXISTING USERS)
│  │ ─────────────────── │
│  │ New Password: [___] │
│  │ Confirm Password:[_] │
│  │                      │
│  │ ℹ Leave both fields  │
│  │ blank to keep the    │
│  │ current password     │
│  └──────────────────────┘
│
│  FULL WIDTH (col-12)
│  ┌──────────────────────────────────────────────────────────┐
│  │ Module Permissions                                       │
│  │ ────────────────────────────────────────────────────── │
│  │ [Permissions table with Module | View | Add | Edit ...] │
│  └──────────────────────────────────────────────────────────┘
│
│  BOTTOM ACTION BUTTONS
│  [Save User]  [Cancel]
│
└─────────────────────────────────────────────────────────────────────────┘
```

## Form Behavior

### When Creating a New User
```
Password Change Section: NOT VISIBLE
(Password fields only appear in "User Information" card)
```

### When Editing an Existing User (USER ID 156)
```
Password Change Section: VISIBLE

┌─────────────────────────────────┐
│ 🔐 Change Password              │ ← Yellow/Warning Header
├─────────────────────────────────┤
│ New Password: [________________]│
│ (Leave blank to skip changing   │
│  password. If provided,         │
│  minimum 8 characters)          │
│                                 │
│ Confirm New Password:           │
│ [________________]              │
│                                 │
│ ℹ️  Password Change:             │
│ Leave both fields blank to keep │
│ the current password. To change │
│ the password, fill in both      │
│ fields with the new password.   │
└─────────────────────────────────┘
```

## Interaction Examples

### Example 1: Update User Info Only (No Password Change)
1. User opens `/accounting/users/156/edit/`
2. Sees password change card
3. Updates username, email, permissions, entities
4. **LEAVES password fields EMPTY**
5. Clicks "Save User"
6. Result: ✅ User updated, password unchanged

### Example 2: Update User Info + Change Password
1. User opens `/accounting/users/156/edit/`
2. Sees password change card
3. Updates username, email, permissions, entities
4. **FILLS password fields with new password**
   - New Password: `SecurePass123!`
   - Confirm New Password: `SecurePass123!`
5. Clicks "Save User"
6. Result: ✅ User updated, password changed to `SecurePass123!`

### Example 3: Only Change Password (No Other Changes)
1. User opens `/accounting/users/156/edit/`
2. Sees password change card
3. **ONLY fills password fields**
   - New Password: `NewPassword456!`
   - Confirm New Password: `NewPassword456!`
4. Leaves all other fields unchanged
5. Clicks "Save User"
6. Result: ✅ Password changed, user info unchanged

### Example 4: Password Mismatch Error
1. User opens `/accounting/users/156/edit/`
2. Fills password fields with different values:
   - New Password: `SecurePass123!`
   - Confirm New Password: `SecurePass124!`
3. Clicks "Save User"
4. Result: ❌ Error message appears below password card:
   ```
   Passwords do not match.
   ```

### Example 5: Password Too Short Error
1. User opens `/accounting/users/156/edit/`
2. Fills password fields with short password:
   - New Password: `short`
   - Confirm New Password: `short`
3. Clicks "Save User"
4. Result: ❌ Error message appears:
   ```
   Password must be at least 8 characters long.
   ```

## Form Validation Messages

### Success Message
```
✅ Password updated for "john_doe".
✅ User "john_doe" updated successfully with module permissions and admin access.
```

### Error Messages

#### Mismatched Passwords
```
❌ Passwords do not match.
```

#### One Field Filled, Other Empty
```
❌ Both password fields must be filled if changing password.
```

#### Password Too Short
```
❌ Password must be at least 8 characters long.
```

#### General Error
```
❌ Error changing password: [error details]
```

## Comparison with Related Features

### This Feature vs "Reset Password" Button
| Aspect | Change Password (New) | Reset Password Button |
|--------|----------------------|----------------------|
| Location | User edit page | User detail page |
| When Used | While editing user info | Only changing password |
| Current Password Required | No | No |
| Password Entered By | Admin (entering new one) | Admin (entering new one) |
| Combined Update | ✅ Yes (with other fields) | ❌ No (password only) |
| Generate Random Password | ❌ No | ✅ Yes (optional) |
| Send Email Option | ❌ No | ✅ Yes (optional) |

### This Feature vs "Change Password" (User's Own)
| Aspect | Change Password (Admin/Edit) | Change Password (User's Own) |
|--------|-------------------------------|------------------------------|
| Who Can Use | Admin only | Any user |
| Requires Current Password | ❌ No | ✅ Yes |
| Combined with Other Updates | ✅ Yes | ❌ No |
| Page | User edit page | Separate page |
| URL | `/accounting/users/156/edit/` | `/accounting/change-password/` |

## Color Scheme and Icons

### Password Change Card Header
- **Background Color:** Yellow/Warning (`bg-warning`)
- **Text Color:** Dark (`text-dark`)
- **Icon:** Lock-Reset (`mdi mdi-lock-reset`)
- **Header Text:** "🔐 Change Password"

### Information Alert
- **Type:** Info alert (`alert alert-info`)
- **Icon:** Information circle (`mdi mdi-information`)
- **Usage:** Help text and guidelines

### Error Messages
- **Color:** Red/Danger
- **Display:** Below affected form field
- **Class:** `text-danger small`

## Responsive Behavior

### Desktop (lg and larger)
```
Two-column layout:
[User Info Card]      [Entity Card]
[Password Card]
[Full Width: Module Permissions]
```

### Tablet/Mobile (below lg)
```
Single column stacked:
[User Info Card]
[Password Card]
[Entity Card]
[Module Permissions]
```

## Technical Details

### Form Fields in Password Card

1. **new_password1**
   - Type: Password input
   - Class: `form-control`
   - Label: "New Password"
   - Help text: "Leave blank to skip changing password. If provided, password must be at least 8 characters long."
   - Required: False (optional)

2. **new_password2**
   - Type: Password input
   - Class: `form-control`
   - Label: "Confirm New Password"
   - Required: False (optional)

### Data Flow

```
User Input
    ↓
HTML Form (user_edit.html)
    ↓
POST Request to /accounting/users/156/edit/
    ↓
UserEditView.post() → form_valid()
    ↓
AdminPasswordChangeForm validation
    ↓
If valid: user.set_password() + user.save()
If invalid: Display error message
    ↓
Redirect to /accounting/users/ with success/error message
```

## Browser Console (Network)
```
POST /accounting/users/156/edit/ HTTP/1.1
Content-Type: application/x-www-form-urlencoded

csrfmiddlewaretoken=...
username=john_doe
email=john@example.com
first_name=John
last_name=Doe
new_password1=NewPassword123!
new_password2=NewPassword123!
is_staff=on
is_active=on
entities=1&entities=2
...
```

## Summary for End Users

**The password change option is now integrated into the user edit page, allowing administrators to:**

1. ✅ Update user information (username, email, name)
2. ✅ Manage permissions and entity assignments
3. ✅ **Optionally change password** in the same form
4. ✅ See clear validation messages for any errors
5. ✅ Leave password fields empty if no change needed

**No need to navigate to a separate page just to change a password!**
