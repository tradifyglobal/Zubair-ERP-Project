# Employee Leave Balance Management Guide

## Problem Solved

**Error:** "Leave balance not found for this employee and leave type. Please contact HR."

**Root Cause:** When employees try to submit leave requests, the system checks for an existing leave balance record. Without this record, the leave request cannot be created.

---

## Solution: How to Add Employee Leave Balances

### Method 1: Using the Web Interface (Recommended)

#### Step 1: Navigate to Leave Balances
1. Go to **HR Menu → Leave Management → Leave Balances**
2. Or visit: `http://localhost:8000/hr/leave-balances/`

#### Step 2: Add New Leave Balance
1. Click the **"Add Leave Balance"** button (blue button with + icon)
2. You'll be taken to the Leave Balance Creation Form

#### Step 3: Fill in the Form

**Left Column (Main Information):**

| Field | Description | Example |
|-------|-------------|---------|
| **Employee** | Select the employee | John Smith |
| **Leave Type** | Select the leave type | Annual Leave |
| **Year** | The year for this balance | 2025 |
| **Opening Balance** | Days carried over from previous year | 5 days |
| **Allocated** | Days allocated for this year | 20 days |
| **Taken** | Days already used this year | 3 days |

**Calculation Shown:**
```
Available Balance = Opening + Allocated - Taken
Available Balance = 5 + 20 - 3 = 22 days
```

#### Step 4: Save
- Click **"Save Leave Balance"** button
- The system will validate:
  - Employee exists in selected entity
  - Leave type is from same entity
  - No duplicate balance exists (same employee, leave type, year)

### Method 2: Using Django Admin

1. Go to **Admin Panel** → **HR** → **Leave Balances**
2. Click **"Add Leave Balance"** button
3. Fill in all required fields
4. Save

---

## Understanding Leave Balances

### What is a Leave Balance?

A leave balance tracks how many days of leave an employee has available for each leave type in a given year.

### Components

```
┌─────────────────────────────────────┐
│      LEAVE BALANCE STRUCTURE         │
├─────────────────────────────────────┤
│ Employee: John Smith                │
│ Leave Type: Annual Leave            │
│ Year: 2025                          │
│                                      │
│ Opening Balance:    5 days          │
│ + Allocated:       20 days          │
│ - Taken:            3 days          │
│ ────────────────────────────        │
│ = Available:       22 days          │
└─────────────────────────────────────┘
```

### Field Explanations

**Opening Balance**
- Days carried over from last year
- Typically from unused leave from 2024
- Can be 0 if no carryover allowed

**Allocated**
- New days given for this year
- Usually matches the leave type's annual allocation
- Can be different based on hire date or special policies

**Taken**
- Days already used this year
- Automatically updated when leave requests are approved
- You can manually adjust if needed

**Available (Auto-calculated)**
- Days remaining for employee to take
- Used for validation when submitting leave requests
- Must be > 0 to approve a leave request

---

## Scenario Example

### Scenario: New Employee Onboarded in 2025

**John Smith** was hired on January 15, 2025

**Step 1: Create Leave Balance**
- Employee: John Smith
- Leave Type: Annual Leave
- Year: 2025
- Opening Balance: 0 (new employee)
- Allocated: 15 days (prorated from 20 annual days)
- Taken: 0 (just started)
- **Available: 15 days**

**Step 2: Employee Requests Leave**
- John submits a leave request for Jan 20-22, 2025 (3 days)
- System checks: Available balance = 15 days ✓ (Enough)
- Leave request approved

**Step 3: Balance After Approval**
- Taken is updated automatically to 3 days
- Available = 0 + 15 - 3 = **12 days remaining**

**Step 4: Next Request**
- John submits another request (5 days)
- System checks: Available = 12 days ✓ (Enough)
- Leave request approved
- New available = 0 + 15 - 8 = **7 days**

---

## Bulk Import Leave Balances

If you have many employees, you can use the Django admin bulk import feature:

### Using Django Admin Bulk Actions

1. Go to HR Admin → Leave Balances
2. Select multiple balances
3. Use the "Action" dropdown to perform bulk operations

### Using Management Command (Advanced)

If you need to create balances for all employees in an entity:

```bash
# Command structure (to be implemented if needed)
python manage.py create_leave_balances --entity=<entity_id> --year=<year> --leave-type=<leave_type_id>
```

---

## Viewing Leave Balances

### List View
1. Go to **HR → Leave Management → Leave Balances**
2. Search by employee name
3. See all balances with available days at a glance

### Detail View
1. Click on any leave balance row
2. View complete information
3. See employee and leave type details
4. Edit button available

---

## Common Tasks

### Task 1: Adjust Used Leave Manually

**Scenario:** An employee's approved leave request was canceled but system didn't update.

**Solution:**
1. Go to Leave Balances
2. Find the balance
3. Click Edit
4. Reduce the "Taken" field
5. Save
6. System recalculates available balance

### Task 2: Add Mid-Year Bonus Leave

**Scenario:** High performers get 5 bonus days in July.

**Solution:**
1. Find John Smith's Annual Leave balance for 2025
2. Click Edit
3. Change Allocated from 20 to 25
4. Save
5. John now has 5 additional days available

### Task 3: Carry Over Unused Leave

**Scenario:** Year ends and John has 10 unused days; carry over to next year.

**Solution for 2025 (end of year):**
1. Find John's balance for 2025
2. Note the available days: 10
3. Create new balance for 2026:
   - Employee: John Smith
   - Leave Type: Annual Leave
   - Year: 2026
   - Opening Balance: 10 (carried over)
   - Allocated: 20 (new annual)
   - Taken: 0 (starting fresh)

---

## Integration with Leave Requests

### When Leave Request is Submitted

```
Employee John Smith
    ↓
Submits leave request (Jan 20-22, 3 days)
    ↓
System searches for:
  - Employee: John Smith ✓
  - Leave Type: Annual Leave ✓
  - Year: 2025 ✓
    ↓
[FOUND] Leave Balance exists
    ↓
Check available balance: 15 days > 3 days ✓
    ↓
[APPROVED] Leave request saved
    ↓
Leave Balance updated:
  - Taken: 0 → 3
  - Available: 15 → 12
```

### When Leave Balance is Missing

```
Employee John Smith
    ↓
Submits leave request (Jan 20-22, 3 days)
    ↓
System searches for:
  - Employee: John Smith ✓
  - Leave Type: Annual Leave ✓
  - Year: 2025 ✓
    ↓
[NOT FOUND] Leave Balance doesn't exist
    ↓
❌ ERROR: "Leave balance not found for this 
        employee and leave type. Please contact HR."
```

---

## Troubleshooting

### Issue: Cannot Find Employee in Leave Balance Form

**Cause:** Employee is from a different entity
**Solution:** Make sure you've selected the correct entity in the top-right dropdown before creating the balance

### Issue: Cannot Find Leave Type in Form

**Cause:** Leave type is from a different entity
**Solution:** Verify leave type belongs to the same entity as the employee

### Issue: Duplicate Leave Balance Error

**Cause:** Balance already exists for this employee + leave type + year
**Solution:** Click "Edit" on the existing balance to modify it, or delete old record first

### Issue: Available Balance is Negative

**Cause:** More leave taken than allocated
**Solution:** This can happen if balances are manually adjusted. Review and correct the "Taken" field

---

## Best Practices

### 1. Create Balances Before Leave Year Starts
- Create all balances in December for next year
- Ensures employees can submit requests on Jan 1st

### 2. Keep Allocations Consistent
- Use the same allocated value for all employees unless special circumstances
- Reference: Leave type's annual_allocation field

### 3. Monitor Available Balances
- Review quarterly to catch over-usage
- Alert employees when balance is low

### 4. Document Adjustments
- When manually editing, note reason in system
- Prevents disputes later

### 5. Handle Leavers Properly
- Keep historical balances for terminated employees
- Don't delete records

---

## FAQs

### Q: What if employee doesn't have allocated leave yet?
**A:** Set Allocated to 0. They can update later when leave is approved.

### Q: Can same balance be used for multiple leave types?
**A:** No. Each leave type needs its own balance record.

### Q: What happens if balance goes negative?
**A:** System still allows, but you should investigate and correct it.

### Q: How do we handle part-time employees?
**A:** Allocate proportional days. E.g., 50% part-time = 10 days instead of 20.

### Q: Can we have negative opening balance?
**A:** Technically yes, but not recommended. It means employee owed leave from previous year.

---

## Summary

**To resolve "Leave balance not found" error:**

1. ✅ Navigate to HR → Leave Balances
2. ✅ Click "Add Leave Balance"
3. ✅ Select Employee and Leave Type
4. ✅ Enter year and allocations
5. ✅ Save
6. ✅ Employee can now submit leave requests

**Key Points:**
- One balance per employee per leave type per year
- Available = Opening + Allocated - Taken
- Without balance, leave requests are rejected
- Update "Taken" when leave is approved
- Balances integrate directly with leave request system

**Related Pages:**
- Leave Balances List: `/hr/leave-balances/`
- Leave Requests: `/hr/leave-requests/`
- Leave Types: `/hr/leaves/`
- Employees: `/hr/employees/`

