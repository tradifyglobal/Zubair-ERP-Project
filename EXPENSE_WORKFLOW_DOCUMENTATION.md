# Employee Expense Approval Workflow

**Updated: December 7, 2025**

## Overview

The Employee Expense Module now includes a complete 2-stage approval workflow with comprehensive attachment support for receipts, invoices, and supporting documents.

## Features Implemented

### 1. **Auto-Population of Employee Field**
- When an employee creates an expense report, their name is automatically populated from the logged-in user
- Employees can only submit their own expenses
- Form no longer requires manual employee selection

### 2. **Comprehensive Attachment Management**
- **ExpenseAttachment Model**: Stores all supporting documents separately
- Supports multiple attachment types:
  - Receipt
  - Invoice
  - Bill
  - Proof of Payment
  - Other Supporting Documents
- File metadata tracked: name, size, type, upload date, uploader
- Multiple files can be attached to both report-level and individual expense items
- Download capability for reviewing documents

### 3. **Two-Stage Approval Workflow**

#### Stage 1: Manager Review (PENDING_REVIEW)
```
Employee submits report
        ↓
Manager receives notification
        ↓
Manager reviews expenses and attachments
        ↓
Manager either:
  - Approves → Moves to Finance stage
  - Rejects → Back to employee with reason
```

**Manager Responsibilities:**
- Review completeness of expense report
- Verify all required receipts are attached
- Validate expense categories and descriptions
- Add review notes
- Forward to Finance or reject with reason

#### Stage 2: Finance Approval (PENDING_APPROVAL)
```
Manager-approved report received
        ↓
Finance Manager reviews for GL posting
        ↓
Finance Manager either:
  - Approves & Posts → Creates GL entries + Reimbursement record
  - Rejects → Back to requestor
```

**Finance Manager Responsibilities:**
- Final approval and budget verification
- Post expenses to General Ledger
- Create reimbursement record
- Verify GL account mappings
- Track for payment processing

### 4. **Report Status Lifecycle**

```
DRAFT
  ├─ Employee adds expenses
  ├─ Uploads supporting documents
  └─ Submits when ready
    ↓
PENDING_REVIEW
  ├─ Manager receives
  ├─ Reviews attachments
  └─ Approves or Rejects
    ├─ REJECTED → Employee corrects
    │   └─ Back to DRAFT
    └─ Approved
      ↓
PENDING_APPROVAL
  ├─ Finance Manager receives
  ├─ Posts to GL
  └─ Approves or Rejects
    ├─ REJECTED → Employee corrects
    │   └─ Back to DRAFT
    └─ Approved
      ↓
POSTED
  └─ GL entries created
    ├─ Reimbursement scheduled
    └─ Payment processed
```

## New Models

### ExpenseAttachment
```python
Fields:
  - attachment_type: Receipt, Invoice, Bill, Proof of Payment, Other
  - file: FileField with automatic metadata extraction
  - file_name: Automatically populated from file
  - file_size: Bytes, tracked for audit
  - file_type: Extension from filename (pdf, jpg, doc, etc.)
  - description: Optional context for the attachment
  - report: FK to EmployeeExpenseReport (optional)
  - expense_item: FK to EmployeeExpense (optional)
  - uploaded_by: User who uploaded
  - created_at, updated_at: Timestamps
```

## Views Updated

### New Views Added

1. **EmployeeExpenseApproveView**
   - Manager reviews and approves reports
   - GET: Shows approval form with all details
   - POST: Processes approval or rejection
   - Checks: User is staff/manager
   - Moves report to PENDING_APPROVAL

2. **EmployeeExpenseFinanceApprovalView**
   - Finance manager final approval
   - GET: Shows finance approval form
   - POST: Approves, posts to GL, creates reimbursement
   - Checks: User is staff/finance
   - Creates GL entries for all approved items

3. **ExpenseAttachmentUploadView**
   - Upload documents at report or item level
   - Tracks file metadata automatically
   - Supports PDF, JPG, PNG, DOC, DOCX, XLSX
   - Enforces maximum file size

4. **ExpenseAttachmentDeleteView**
   - Delete attachments
   - Permission checks: owner or staff only
   - Removes from storage

### Enhanced Views

1. **EmployeeExpenseReportCreateView**
   - Auto-populates employee from request.user
   - Creates approval workflow automatically
   - Validates employee exists
   - Creates audit log entry

2. **EmployeeExpenseSubmitView**
   - Enhanced validation: Checks for required receipts
   - Verifies category requirements (receipt_required flag)
   - Only allows employee or staff to submit
   - Creates attachment audit trail

## Forms Updated

### EmployeeExpenseReportForm
- Removed manual employee selection
- Added user parameter for auto-population
- Maintains period dates and description

### ExpenseAttachmentForm
- New form for attachment uploads
- Selectable attachment type
- File input with type restrictions
- Optional description field

## Templates Enhanced

### report_detail.html
Comprehensive redesign with:

**Header Section:**
- Report ID and employee name
- Current status with color-coded badges
- Period information
- Total expense amount

**Main Content:**
- Employee information
- Expense items table with attachment counts
- Supporting documents gallery
  - File preview cards
  - Download buttons
  - Upload dates and descriptions

**Approval Workflow Panel:**
- Manager review status
- Finance approval status
- Approval dates and notes
- Visual indicators (icons, colors, badges)

**Action Buttons:**
- Submit for Review (DRAFT)
- Approve/Reject (PENDING_REVIEW - managers only)
- Approve & Post/Reject (PENDING_APPROVAL - finance only)

**Information Panel:**
- Creation date
- Review dates
- Approval dates
- Timeline of events

## Database Changes

### Migration 0002_add_expense_attachment.py
```sql
-- Creates expense_attachmentexpenseattachment table
-- Columns: id, attachment_type, file, file_name, file_size, file_type, 
--          description, created_at, updated_at, 
--          expense_item_id, report_id, uploaded_by_id
```

## Workflow Rules

### Receipt Requirements
- Categories with `requires_receipt=True` must have attachments
- System validates before allowing submission
- Can attach to report or individual items

### Approval Rules
- Manager must approve before finance can review
- Finance cannot approve until manager approves
- Both can add notes to their approval
- Both can reject (sends back to employee)

### GL Posting
- Only happens after finance approval
- Individual expense items posted as debit entries
- Uses category's GL account mapping
- Creates reference number: EXP-{report_id}-{item_id}
- Sets is_posted=True and posted_at timestamp

### Reimbursement
- Automatically created after finance approval
- Amount = sum of approved item amounts
- Method defaults to BANK_TRANSFER
- Can be scheduled for payment

## Permission Checks

### Employee
- Can create own expense reports
- Can submit own reports
- Can upload attachments
- Cannot approve or edit others' reports
- Cannot see approvals panel

### Manager
- Can review all pending reports
- Can approve or reject at manager stage
- Can add review notes
- Cannot post to GL (finance only)
- Can see approval workflow

### Finance Manager
- Can review manager-approved reports
- Can approve and post to GL
- Can create reimbursement records
- Can reject if needed
- Has access to GL posting functionality

### Admin/Staff
- Can perform all actions
- Can override approvals
- Access to all reports and attachments

## Audit Trail

All approval actions are logged:
- Manager approval/rejection
- Finance approval/rejection
- Attachment uploads
- GL posting
- Reimbursement creation

Each audit entry includes:
- Action type
- User who performed it
- Timestamp
- Old values (before)
- New values (after)
- Description

## File Upload Handling

### Supported Formats
- **Images**: JPG, JPEG, PNG
- **Documents**: PDF, DOC, DOCX
- **Spreadsheets**: XLSX, XLS
- **Total size**: Tracked in database

### Storage
- Upload path: `expense_attachments/{year}/{month}/`
- Files retained after report approval
- File metadata automatically extracted
- Download URLs generated on access

## User Experience Flow

### For Employees

1. **Create Report**
   - Go to Expenses → Create New Report
   - Period dates auto-populated to current month
   - Add description if needed
   - Click "Create Report"

2. **Add Expenses**
   - Click "Add Expense" button
   - Select category
   - Enter date and amount
   - Upload receipt (required for some categories)
   - Click "Add Expense"

3. **Upload Additional Documents**
   - Click "Upload Document" button
   - Select document type
   - Upload file
   - Add description (optional)
   - Click "Upload"

4. **Submit for Review**
   - System validates:
     - At least one expense item
     - All required receipts attached
   - Click "Submit for Review"
   - Report moves to PENDING_REVIEW status
   - Manager is notified

5. **Monitor Status**
   - Reports page shows status
   - Report detail shows approval timeline
   - Notifications when approved/rejected

### For Managers

1. **Review Pending Reports**
   - Go to Expenses → Reports
   - Filter by "Pending Manager Review"
   - Click on report to review

2. **Examine Details**
   - View all expenses
   - Download and review attachments
   - Check expense categories
   - Read employee notes

3. **Approve or Reject**
   - Click "Review & Approve" button
   - Enter manager notes (optional)
   - Select action:
     - "Approve" → Moves to finance
     - "Reject" → Returns to employee with reason
   - Click action button

4. **Track Progress**
   - Once approved, report moves to finance
   - Can see history in workflow panel

### For Finance Managers

1. **Approve Finance Reports**
   - Go to Expenses → Reports
   - Filter by "Pending Finance Approval"
   - Click on report to finalize

2. **Final Review**
   - Verify manager notes
   - Check GL account mappings
   - Review total approved amounts
   - Validate budget if applicable

3. **Post and Approve**
   - Click "Approve & Post" button
   - Enter finance notes (optional)
   - System will:
     - Post expenses to GL
     - Create GL entries
     - Create reimbursement record
     - Update report status to POSTED

4. **Schedule Payment**
   - Go to Reimbursements
   - Set scheduled payment date
   - Arrange fund transfer or check

## Testing Checklist

### Employee Submission
- [ ] Employee field auto-populates from login
- [ ] Can create report without employee selection
- [ ] Can add multiple expenses
- [ ] Can upload attachments
- [ ] Receipt validation works
- [ ] Submission validation works
- [ ] Status changes to PENDING_REVIEW

### Manager Approval
- [ ] Manager sees pending reports
- [ ] Can download attachments
- [ ] Can approve report
- [ ] Can reject with reason
- [ ] Notes saved correctly
- [ ] Workflow updates correctly
- [ ] Status moves to PENDING_APPROVAL (if approved)

### Finance Approval
- [ ] Finance sees manager-approved reports
- [ ] Can approve and post to GL
- [ ] GL entries created correctly
- [ ] Reimbursement record created
- [ ] Report status becomes POSTED
- [ ] Can reject if needed

### Attachment Handling
- [ ] Multiple file upload works
- [ ] File metadata extracted
- [ ] Download links work
- [ ] Deletion works
- [ ] File deleted from storage

### Audit Trail
- [ ] All actions logged
- [ ] Timestamps correct
- [ ] User attribution correct
- [ ] Old/new values tracked

## API Endpoints (URLs)

```
# Reports
/expenses/reports/ - List all reports
/expenses/reports/create/ - Create new report (auto-employee)
/expenses/reports/<id>/ - View report detail with workflow
/expenses/reports/<id>/submit/ - Submit for review
/expenses/reports/<id>/approve/ - Manager approve
/expenses/reports/<id>/finance-approve/ - Finance approve & post

# Attachments
/expenses/reports/<id>/attachment/upload/ - Upload document
/expenses/attachments/<id>/delete/ - Delete attachment

# Other
/expenses/expenses/<id>/create/ - Add expense item
```

## Notifications (Future Enhancement)

Consider implementing:
- Email to manager when report submitted
- Email to employee when approved/rejected
- Email to finance when ready for approval
- SMS alerts for pending approvals
- In-app notifications dashboard

## Troubleshooting

### Error: "Your user account is not linked to an employee record"
**Solution**: Create an Employee record in HR module linked to this user

### Error: "Receipt required for this category"
**Solution**: Upload a receipt before submitting. Either:
- Add file when creating expense, or
- Upload document to report later

### Error: "Permission denied" on approval
**Solution**: Only staff/managers can approve. Check user roles.

### GL entries not created
**Solution**: Finance manager must click "Approve & Post", not just approve

### Files not downloading
**Solution**: Check file permissions on server, ensure storage path exists

## Performance Notes

- Attachment queries should be optimized with select_related/prefetch_related
- File uploads larger than 10MB may timeout
- Consider CDN for file serving in production
- Archive old attachments after 90 days for storage optimization
