# Employee Expense Workflow - Quick Start Guide

**December 7, 2025** | Production Deployment Complete

## What's New ✨

### ✅ Auto-Population
- Employee name **automatically filled in** when creating expense reports
- No need to manually select employee from dropdown
- Based on the logged-in user's profile

### ✅ Two-Step Approval Workflow
```
Employee Submits → Manager Reviews → Finance Approves → GL Posted
```

1. **Employee submits** expense report with receipts
2. **Manager reviews** and approves (or rejects)
3. **Finance Manager** approves and posts to GL
4. **System creates** reimbursement record automatically

### ✅ Comprehensive Attachments
- Upload **receipts, invoices, bills, proofs of payment**
- Attach to entire report **or individual expenses**
- **Download anytime** for review
- **Multiple formats** supported (PDF, JPG, PNG, DOC, DOCX)

### ✅ Complete Approval Visibility
- See **who approved and when**
- View **approval notes** from managers and finance
- Track **workflow status** with color-coded badges
- Full **audit trail** of all decisions

---

## User Workflows by Role

### 👨‍💼 For Employees

**Step 1: Create Report**
```
Menu → Expenses → Create New Expense Report
├─ Period dates auto-filled to current month
├─ Add description (optional)
└─ Click "Create Report"
```

**Step 2: Add Expenses**
```
Click "Add Expense"
├─ Select category
├─ Enter date
├─ Enter amount
├─ Upload receipt (if required)
└─ Click "Add Expense"
```

**Repeat** for each expense item

**Step 3: Upload Supporting Documents** (optional)
```
Click "Upload Document"
├─ Select document type
├─ Upload file
├─ Add description
└─ Click "Upload"
```

**Step 4: Submit for Review**
```
Click "Submit for Review"
├─ System validates:
│  ├─ Has expenses
│  └─ All required receipts attached
├─ Report status → "Pending Manager Review"
└─ Manager gets notification
```

**Step 5: Monitor Status**
```
Go to Reports list
├─ See current status
├─ View approval timeline
└─ Receive notifications of changes
```

**If Rejected by Manager:**
- Status returns to "Draft"
- Review manager's reason
- Make corrections
- Submit again

---

### 👔 For Managers

**Step 1: View Pending Reports**
```
Menu → Expenses → Reports
├─ Filter: "Pending Manager Review"
└─ Click report to review
```

**Step 2: Review Expenses**
```
Examine:
├─ All expense items and amounts
├─ Categories used
├─ Employee descriptions
└─ Download and review attachments
```

**Step 3: Decide**
```
Click "Review & Approve" button
├─ Approve → Moves to Finance Manager
├─ Reject  → Returns to employee with reason
└─ Add optional manager notes
```

**After Approval:**
- Report moves to "Pending Finance Approval"
- Finance Manager receives notification
- Manager can see workflow progress

---

### 💰 For Finance Managers

**Step 1: View Pending Approvals**
```
Menu → Expenses → Reports
├─ Filter: "Pending Finance Approval"
└─ Click report
```

**Step 2: Final Review**
```
Verify:
├─ Manager's approval notes
├─ GL account mappings
├─ Total approved amounts
└─ Budget availability (if tracking)
```

**Step 3: Post to GL**
```
Click "Approve & Post" button
├─ Add optional finance notes
└─ System automatically:
   ├─ Creates GL entries
   ├─ Posts expenses to ledger
   ├─ Creates reimbursement record
   └─ Sets status to "Posted"
```

**Step 4: Schedule Payment**
```
Menu → Expenses → Reimbursements
├─ Find newly created reimbursement
├─ Set payment date
└─ Arrange transfer/check
```

---

## Key Status Badges

| Status | Color | Meaning |
|--------|-------|---------|
| **Draft** | Gray | Employee still editing |
| **Pending Manager Review** | Yellow | Waiting for manager approval |
| **Pending Finance Approval** | Blue | Manager approved, awaiting finance |
| **Approved** | Green | Finance approved & ready |
| **Posted** | Purple | GL entries created |
| **Rejected** | Red | Sent back for correction |

---

## Important Rules

### ✓ Must Follow
- **Receipts**: If category requires receipt, must attach before submitting
- **Amounts**: Must be greater than 0
- **Dates**: Expense date must be within report period
- **Categories**: Expense must have valid category selected

### ✓ Approval Rules
1. **Manager must approve first** before finance can review
2. **Finance cannot post** if manager rejected
3. **Employee can resubmit** after rejection
4. **Both can add notes** to their approval

### ✓ GL Posting
- **Automatic** when finance approves
- Uses **category's GL account** mapping
- Creates **debit entries** to expense accounts
- Creates **reference** number for tracking

---

## Attachment Types

| Type | Usage |
|------|-------|
| **Receipt** | Store receipt for purchases |
| **Invoice** | Vendor invoices |
| **Bill** | Bills and statements |
| **Proof of Payment** | Bank statements, payment confirmations |
| **Other** | Any other supporting document |

**Supported Formats**: PDF, JPG, PNG, DOC, DOCX, XLSX

---

## Common Scenarios

### Scenario 1: Employee Submits, Manager Approves, Finance Approves
```
✓ Employee creates report with $1,500 expenses
✓ Uploads 3 receipts
✓ Submits → Status: Pending Manager Review
✓ Manager reviews → Approves → Status: Pending Finance Approval
✓ Finance reviews → Approves & Posts → Status: Posted
✓ GL entries created automatically
✓ Reimbursement record created
→ Ready for payment
```

### Scenario 2: Manager Rejects, Employee Corrects
```
✓ Employee submits report
✓ Manager reviews → Rejects (missing receipt)
✓ Status returns to Draft
✓ Employee adds receipt
✓ Employee resubmits
✓ Manager approves this time
✓ Continues to Finance
```

### Scenario 3: Finance Rejects for GL Issue
```
✓ Manager approves
✓ Finance reviews → Rejects (GL account issue)
✓ Status returns to Draft
✓ Manager corrects GL mapping
✓ Employee resubmits
✓ Finance approves & posts
```

---

## Troubleshooting

**"Employee field not auto-populating?"**
- User must have Employee record in HR module
- Contact admin to create employee profile linked to your account

**"Can't submit - says receipt required?"**
- Some categories require attachments
- Click "Upload Document" to attach receipts before submitting

**"Can't see approve button?"**
- Only managers can approve at manager stage
- Only finance staff can approve at finance stage
- Check your user role/group permissions

**"GL entries not created?"**
- Finance must click "Approve & Post" (not just approve)
- Approval must be at finance stage (after manager approved)
- GL account must be mapped in category

**"Can't download attachment?"**
- Check file still exists in system
- Try refreshing the page
- Contact admin if file is missing

---

## Key Improvements Over Previous System

| Feature | Before | Now |
|---------|--------|-----|
| Employee Selection | Manual dropdown | Auto-populated ✓ |
| Approval Process | Single stage | Two-stage ✓ |
| Attachment Support | Limited (1 per item) | Multiple files ✓ |
| Workflow Visibility | Hidden | Full timeline display ✓ |
| Rejection Handling | Lost data | Can resubmit ✓ |
| GL Posting | Manual | Automatic ✓ |
| Audit Trail | Basic | Comprehensive ✓ |
| Manager Review | None | Required ✓ |
| Finance Control | Limited | Full ✓ |

---

## Contact & Support

**For Technical Issues**:
- Check EXPENSE_WORKFLOW_DOCUMENTATION.md for detailed guide
- Contact system administrator

**For Process Questions**:
- Ask your manager about approval requirements
- Finance team handles GL and payment questions

---

## Quick Links

- **Create Expense Report**: `/expenses/reports/create/`
- **View Reports**: `/expenses/reports/`
- **Reimbursements**: `/expenses/reimbursements/`
- **Full Documentation**: See `EXPENSE_WORKFLOW_DOCUMENTATION.md`

---

**Last Updated**: December 7, 2025
**Status**: ✅ Live in Production
**Database**: Migration 0002_add_expense_attachment applied
