# Leave Balance - Quick Reference Card

## Problem & Solution

| Issue | Solution |
|-------|----------|
| ❌ "Leave balance not found" error | ✅ Create leave balance via HR → Leave Balances → Add |
| Employee can't submit leave request | ✅ Create matching leave balance first |
| No leave balances visible | ✅ Ensure employee and leave type from same entity |

---

## 30-Second Setup

```
1. HR Menu → Leave Balances
2. Click "Add Leave Balance" (blue button)
3. Select: Employee, Leave Type, Year
4. Enter: Opening Balance, Allocated, Taken
5. Click "Save"
6. Done! ✓
```

---

## Form Fields Explained

```
Employee          → John Smith (who has leave)
Leave Type        → Annual Leave (type of leave)
Year              → 2025 (which year)
Opening Balance   → 5 (carried from last year)
Allocated         → 20 (given this year)
Taken             → 3 (already used)
─────────────────────────────
Available         → 22 (auto-calculated)
```

---

## Example Scenarios

### Scenario A: New Employee
```
Employee: Alice Johnson (hired Jan 2025)
Leave Type: Annual Leave
Year: 2025
Opening: 0 (new, no carryover)
Allocated: 15 (prorated from 20)
Taken: 0
→ Available: 15 days
```

### Scenario B: Existing Employee
```
Employee: Bob Smith
Leave Type: Annual Leave
Year: 2025
Opening: 5 (carried from 2024)
Allocated: 20 (annual)
Taken: 8 (used Jan-Nov)
→ Available: 17 days
```

### Scenario C: Special Leave
```
Employee: Carol White
Leave Type: Sick Leave
Year: 2025
Opening: 2 (rollover allowed)
Allocated: 10 (annual)
Taken: 1
→ Available: 11 days
```

---

## Links & Navigation

| Page | URL | Purpose |
|------|-----|---------|
| Leave Balances List | `/hr/leave-balances/` | View all balances |
| Add Leave Balance | `/hr/leave-balances/create/` | Create new balance |
| Leave Balance Detail | `/hr/leave-balances/{id}/` | View one balance |
| Edit Balance | `/hr/leave-balances/{id}/update/` | Edit existing |
| Leave Requests | `/hr/leave-requests/` | Submit/manage requests |
| Leave Types | `/hr/leaves/` | View all leave types |
| Employees | `/hr/employees/` | Manage employees |

---

## What Happens When...

### ...Employee Submits Leave Request?
```
System checks:
  ✓ Employee exists
  ✓ Leave type approved
  ✓ Leave balance exists
  ✓ Available days ≥ requested days
→ Request APPROVED and "Taken" auto-updates
```

### ...Leave Balance is Missing?
```
System cannot find:
  ✗ Balance for this employee
  ✗ Balance for this leave type
  ✗ Balance for this year
→ Request REJECTED with error message
```

### ...You Edit "Taken"?
```
1. Find balance
2. Click Edit
3. Change "Taken" field
4. Save
5. "Available" recalculates automatically
→ Balance updated instantly
```

---

## Common Operations

### Add Leave Balance for 1 Employee
**Time: 2 minutes**
1. Go to Leave Balances
2. Click "Add Leave Balance"
3. Fill form (5 fields)
4. Save

### Create for All Employees in Department
**Approach:** Repeat above for each employee, or use Django admin bulk import

### Adjust Existing Balance
**Time: 1 minute**
1. Find balance in list (use search)
2. Click "Edit"
3. Modify "Taken" field
4. Save

### Verify Balance Before Request
**Time: 30 seconds**
1. Go to Leave Balances
2. Search employee name
3. Check "Available" column

---

## Validation Rules

✅ **Allowed:**
- Multiple balances for same employee (different leave types)
- Multiple balances for same leave type (different employees)
- Zero opening balance (new employees)
- Negative available (if taken > allocated)

❌ **NOT Allowed:**
- Duplicate balance (same employee + leave type + year)
- Employee from different entity
- Leave type from different entity
- Text in numeric fields

---

## Real-World Workflow

```
November 2025: Prepare for 2026
  → Create leave balances for all employees for year 2026
  
January 1, 2026: Year starts
  → Employees can now submit leave requests
  
Throughout 2026: Employees submit requests
  → Each approved request updates "Taken" field
  
November 2026: Year ending
  → Review unused leave for carryover
  
December 2026: Prepare for 2027
  → Create new balances with carried-over opening balance
  → Set new annual allocation
```

---

## Troubleshooting Checklist

| Problem | Check | Solution |
|---------|-------|----------|
| Can't find employee | Entity match | Select correct entity dropdown |
| Can't find leave type | Entity match | Ensure leave type from same entity |
| Duplicate error | Year collision | Edit existing instead of creating new |
| Form won't save | Required fields | Fill all marked with * |
| Available is wrong | Math error | Check: opening + allocated - taken |
| Employee still gets error | Balance missing | Verify saved in system |

---

## Key Takeaways

✨ **Remember:**
- **1 Balance = 1 Employee + 1 Leave Type + 1 Year**
- **Available = Opening + Allocated - Taken**
- **Without Balance → Leave Request Rejected**
- **Create Before Year Starts**
- **Keep Entities Matched**

📍 **Location:** HR Menu → Leave Management → Leave Balances

⏱️ **Time to Setup:** ~2 minutes per employee

✅ **Status:** Ready to use immediately after creation

---

## Support

**Still getting "Leave balance not found"?**

1. ✅ Did you create the leave balance? → Go add it
2. ✅ Is employee from same entity? → Check entity selection
3. ✅ Is leave type from same entity? → Check leave type entity
4. ✅ Is year correct? → Should match current/target year
5. ✅ Does balance show in list? → Use search to verify

If still stuck → Contact HR Admin

