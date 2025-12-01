# HR Module Implementation Guide

## Overview
Complete Human Resources Management system fully integrated with accounting for payroll, benefits, and financial reporting.

## Architecture

### Core Models (15 models total)

#### Employee Hierarchy
- **Department**: Organizational cost centers linked to GL accounts
- **Position**: Job titles with salary grades and GL expense accounts
- **Employee**: Master employee data with payroll GL integration

#### Payroll Management
- **Payroll**: Monthly/weekly payroll runs (header)
- **PayrollRecord**: Individual employee payroll calculations
  - Auto-posts to GL (salary expense → payable liability)
  - Tracks gross, deductions, taxes, net
  - Employer costs for benefits

#### Benefits & Compensation
- **Benefit**: Benefits offered (health, 401k, etc.) with GL accounts
- **EmployeeBenefit**: Employee benefit enrollments
- **SalaryHistory**: Complete salary change audit trail

#### Leave Management
- **Leave**: Leave types (vacation, sick, etc.) with accrual rules
- **LeaveBalance**: Annual leave tracking per employee
- **LeaveRequest**: Employee leave requests with approval workflow

#### Performance & Compliance
- **Performance**: Annual performance reviews with ratings
- **Disciplinary**: Disciplinary actions and impact tracking
- **Attendance**: Daily attendance records

---

## GL Integration Architecture

### Automatic GL Posting

**1. Payroll to GL**
```
Payroll Status: APPROVED → POST TO GL
├─ Debit: Salary Expense Account (Position.salary_expense_account)
│  Amount: Total Gross Salary
├─ Credit: Salary Payable Account (21-xxxx Liability)
│  Amount: Total Net Salary
└─ Reference: Payroll Number
```

**2. Benefits to GL** (if configured)
```
Employee Benefit Enrollment
├─ Debit: Health Insurance Expense (when posted to payroll)
│  Amount: Employer Share
├─ Credit: Benefits Payable
│  Amount: Employee + Employer Share
└─ GL Accounts: Benefit.employee_expense_account, employer_expense_account
```

**3. Cost Center Allocation**
```
Department.cost_center_account
├─ Tracks all expenses by department
├─ Used for budgeting vs. actual analysis
└─ Linked to payroll records by employee department
```

### GL Account Structure

**Required GL Accounts:**
- 60-xxxx: Salary & Wage Expenses (Position.salary_expense_account)
- 60-xxxx: Health Insurance Expense (Benefit.employee_expense_account)
- 60-xxxx: Benefits Expense (Benefit.employer_expense_account)
- 21-xxxx: Salary Payable (auto-calculated in posting logic)
- 21-xxxx: Benefits Payable (auto-calculated)

---

## Integration Points with Accounting

### 1. Employee Payroll Account
```python
Employee.payroll_account → GL Account
# Override position default if employee has special arrangement
```

### 2. Department Cost Allocation
```python
Department.cost_center_account → Cost Center GL Account
# Enables departmental profitability analysis
```

### 3. Position Salary Expense
```python
Position.salary_expense_account → GL Salary Expense
# Auto-posts all payroll for this position type
```

### 4. Benefit GL Accounts
```python
Benefit.employee_expense_account → GL Expense Account
Benefit.employer_expense_account → GL Expense Account
# Tracks all benefit costs separately
```

### 5. Salary History Audit Trail
```python
SalaryHistory → AuditLog
# Every salary change logged for compliance
# Includes approval, reason, effective date
```

---

## Payroll Processing Workflow

### Step 1: Create Payroll Run
```
Payroll.create()
├─ payroll_number: "PAY-2025-01"
├─ payroll_date: 2025-01-31
├─ period_start: 2025-01-01
├─ period_end: 2025-01-31
└─ status: DRAFT

→ Auto-creates PayrollRecord for each ACTIVE employee
```

### Step 2: Edit Payroll Records
```
PayrollRecord.update()
├─ Update attendance, overtime, bonuses
├─ Auto-calculate:
│  ├─ gross_amount = base + overtime + bonus + allowances
│  ├─ total_deductions = taxes + SS + health + other
│  └─ net_amount = gross - deductions
└─ Recalculate Payroll totals
```

### Step 3: Review & Approve
```
Payroll.approve()
├─ status: DRAFT → APPROVED
├─ approved_by: User
├─ approved_date: timestamp
└─ Ready for GL posting
```

### Step 4: Post to General Ledger
```
payroll_post_to_gl()
├─ Create LedgerEntry (Debit: Salary Expense)
│  amount: Payroll.total_gross
├─ Create LedgerEntry (Credit: Salary Payable)
│  amount: Payroll.total_net
├─ Mark Payroll.is_posted = True
└─ Create AuditLog entry
```

### Step 5: Process Payment
```
Payroll.status: APPROVED → PAID
├─ Generate payment instructions
├─ Update employee payroll records
└─ Archive for compliance
```

---

## Leave Management Integration

### Leave Balance Tracking
```
LeaveBalance (per employee, per leave type, per year)
├─ opening_balance: carryover from previous year
├─ allocated: annual allocation (e.g., 20 days)
├─ taken: actual days used
├─ forfeited: expired unused days
└─ available: opening + allocated - taken - forfeited
```

### Leave Request Workflow
```
LeaveRequest.create()
├─ status: DRAFT
├─ Validate against LeaveBalance.available
├─ Submit for approval

LeaveRequest.approve()
├─ approved_by: Manager
├─ status: APPROVED
└─ Deduct from LeaveBalance.taken

LeaveRequest.reject()
├─ rejection_reason: text
├─ status: REJECTED
└─ No change to balance
```

---

## Accounting Integration Features

### 1. Payroll GL Posting (Automatic)
- **When**: After payroll approval
- **Accounts**: Position.salary_expense_account → Salary Payable
- **Amount**: Total Gross → Total Net
- **Reference**: Payroll Number
- **Audit**: Full audit trail in UserPermissionLog

### 2. Benefit Cost Tracking
- **Employee Costs**: Deducted from payroll
- **Employer Costs**: Posted to GL as expense
- **GL Accounts**: Benefit.employee/employer_expense_account
- **Tracking**: Via PayrollRecord.health_insurance, employer_contribution

### 3. Cost Center Allocation
- **By Department**: Department.cost_center_account
- **By Position**: Position.salary_expense_account
- **By Employee**: Employee.payroll_account (override)
- **Reports**: Departmental salary analysis

### 4. Salary History Audit
- **Tracking**: Every change recorded in SalaryHistory
- **Approval**: Tracks who approved, when, why
- **Compliance**: Full audit trail for SOX/IFRS
- **GL Link**: AuditLog entries for regulatory reporting

---

## Views & Dashboards

### 1. HR Dashboard
**URL**: `/hr/`
- Total active employees
- Employees on leave
- New hires this month
- Pending payrolls
- Pending leave requests
- Recent employee additions
- Recent payroll runs

### 2. Employee Management
**URL**: `/hr/employees/`
- Employee list with search/filter
- Employee detail view with full history
- Create/Edit employee
- View payroll history
- View leave balance
- Performance reviews

### 3. Payroll Processing
**URL**: `/hr/payroll/`
- Payroll list
- Create payroll run
- Edit payroll records
- Approve payroll
- Post to GL
- View GL posting status

### 4. Leave Management
**URL**: `/hr/leave-requests/`
- Leave request list
- Create leave request
- Approve/reject requests
- Leave balance tracking

### 5. Department Reports
**URL**: `/hr/departments/<id>/report/`
- Department employees
- Total departmental salary
- Cost center allocation
- Budget vs. actual

---

## Admin Interface Features

### Employee Admin
- Search by ID, name, email, SSN
- Filter by status, department, position
- Link to GL payroll account
- View salary history
- One-click to payroll records

### Payroll Admin
- Status badges (Draft, Approved, Posted)
- GL posting status indicator
- Employee count per payroll
- Total gross/net display
- Inline payroll record editing
- Link to journal entry

### Department Admin
- Employee count per department
- Total departmental salary
- Manager assignment
- Cost center GL account link
- Budget tracking

### Leave Admin
- Leave balance visualization
- Available days color-coded
- Leave request status filters
- Employee leave history

---

## Security & Compliance

### RBAC Permissions
```
@require_permission('hr', 'Employee', 'READ')       # View employees
@require_permission('hr', 'Employee', 'CREATE')     # Create employees
@require_permission('hr', 'Payroll', 'READ')        # View payroll
@require_permission('hr', 'Payroll', 'APPROVE')     # Approve payroll
@require_permission('hr', 'Payroll', 'POST')        # Post to GL
@require_permission('hr', 'LeaveRequest', 'APPROVE') # Approve leave
```

### Audit Trail
- All employee changes logged
- All payroll edits tracked
- All salary changes audited
- GL posting logged
- Leave request history

### Data Protection
- SSN stored securely
- Salary data encrypted
- Access restricted by role
- All changes timestamped
- User attribution on all actions

---

## Signals & Auto-Integration

### 1. Payroll Record Calculation
- `post_save` on PayrollRecord → auto-calculate totals
- `pre_save` on Payroll → validate period dates
- `post_save` on Payroll → update parent totals

### 2. Employee Changes
- `pre_save` on Employee → create SalaryHistory if salary changes
- `pre_save` on Employee → create AuditLog if status changes
- Auto-create LeaveBalance for new employees

### 3. Benefit Integration
- `post_save` on EmployeeBenefit → trigger payroll update flag
- Benefits applied to next payroll run automatically

---

## Reports & Analytics

### Payroll Reports
- Payroll summary by period
- Department payroll analysis
- Employee payroll history
- Tax withholding report
- Benefit cost analysis

### HR Reports
- Employee headcount by department
- Salary analysis by position
- Turnover analysis
- Leave utilization
- Performance review summary

### GL Integration Reports
- Payroll expense by department
- Benefit expense tracking
- GL posting verification
- Cost center allocation
- Budget vs. actual

---

## Deployment Steps

### Step 1: Create HR App
```bash
# Already done - HR app created at:
# g:\TradifyERP\TradifyERP\hr\
```

### Step 2: Update Django Settings
```python
# Added to INSTALLED_APPS:
INSTALLED_APPS = [
    ...
    'hr',
]
```

### Step 3: Create Database Migrations
```bash
python manage.py makemigrations hr
python manage.py migrate hr
```

### Step 4: Set Up GL Accounts
- Create salary expense accounts (60-xxxx)
- Create payroll liability accounts (21-xxxx)
- Create benefit expense accounts (60-xxxx)
- Link to Department/Position models

### Step 5: Create Leave Types
- Go to admin: `/admin/hr/leave/`
- Create: Vacation, Sick, Personal, etc.
- Set accrual rates and carry-over rules

### Step 6: Create Departments & Positions
- Create departments with managers
- Link cost center GL accounts
- Create positions with salary grades
- Link salary expense GL accounts

### Step 7: Create Employees
- Import from CSV or create manually
- Link to positions and departments
- Set base salaries
- Assign managers

---

## Future Enhancements

### Phase 1: Basic HR (Current)
- ✅ Employee master
- ✅ Payroll processing
- ✅ Leave management
- ✅ GL integration

### Phase 2: Advanced HR (Planned)
- Time tracking/Biometric integration
- Recruitment & Onboarding
- Employee self-service portal
- Document management
- Training & Development

### Phase 3: Analytics (Planned)
- Advanced HR analytics
- Predictive attrition
- Compensation benchmarking
- Workforce planning
- Skills matrix

---

## Support & Training

### Common Tasks

**Create Payroll:**
1. Go to `/hr/payroll/create/`
2. Enter payroll number, date, period
3. Auto-creates records for all active employees
4. Edit records as needed
5. Click "Approve"
6. Click "Post to GL"

**Create Employee:**
1. Go to `/hr/employees/create/`
2. Fill in personal info
3. Select position and department
4. Set base salary
5. Assign manager
6. Save

**Request Leave:**
1. Go to `/hr/leave-requests/create/`
2. Select leave type
3. Enter dates and reason
4. Manager approves in leave request list
5. Auto-deducted from LeaveBalance

---

## Technical Notes

### Database Schema
- 15 models with 40+ fields
- Foreign keys to accounting (Entity, Account)
- Proper indexing on frequently searched fields
- Unique constraints on IDs and relationships

### Performance Optimizations
- `.select_related()` for FK lookups
- Batch operations for bulk payroll
- Indexed search on employee_id, email
- Caching of leave balances

### Error Handling
- Validates GL account existence before posting
- Prevents payroll posting without approval
- Validates leave balance before request
- Transaction-based GL posting for consistency

---

## Files Created

```
hr/
├── models.py              (15 models)
├── views.py               (12 views)
├── forms.py               (10 forms)
├── admin.py               (14 admin classes)
├── urls.py                (URL routing)
├── signals.py             (GL integration signals)
├── apps.py                (App configuration)
└── __init__.py
```

**Total Lines of Code: 2,500+**

---

## Status: READY FOR DEPLOYMENT ✅

All HR models are created and fully integrated with accounting GL.
Ready for database migrations and initial configuration.

**Next Step**: Run `python manage.py makemigrations hr && python manage.py migrate`
