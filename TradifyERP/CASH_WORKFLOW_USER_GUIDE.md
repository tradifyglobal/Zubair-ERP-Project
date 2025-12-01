# Cash Management Workflow - Quick Reference Guide

## 🎯 The 3-Step Workflow

### Step 1: DRAFT (Create)
- **Who**: Data Entry Person
- **Action**: Fill form and click "Save & Submit"
- **Result**: Transaction saved in DRAFT state
- **Status Indicator**: Gray badge "Draft"
- **Available Buttons**: Approve ✓ | Reject ✗

### Step 2: APPROVED (Review)
- **Who**: Manager/Approver
- **Action**: Review transaction details, click "Approve" (✓)
- **Result**: Transaction moved to APPROVED state
- **Status Indicator**: Blue badge "Approved"
- **Available Buttons**: Authorize & Post → | Reject ✗

### Step 3: AUTHORIZED (Post to GL)
- **Who**: Finance/Authorized User
- **Action**: Review approved transaction, click "Authorize & Post" (→)
- **Result**: GL entries created and transaction POSTED
- **Status Indicator**: Green badge "Authorized"
- **Available Buttons**: None (finalized)

## 📍 Workflow States

| State | Color | Meaning | Next Action |
|-------|-------|---------|-------------|
| Draft | Gray | Initial state after creation | Approve or Reject |
| Pending Approval | Yellow | Awaiting approval | Approve or Reject |
| Approved | Blue | Ready for posting | Authorize & Post or Reject |
| Authorized | Green | Posted to GL, finalized | — |
| Rejected | Red | Declined, no GL entries | Create new transaction |

## 🔴 Rejection Rules

- Can reject from: **DRAFT** or **PENDING_APPROVAL** states only
- Cannot reject: **APPROVED**, **AUTHORIZED**, or **POSTED** transactions
- Effect: Transaction marked as REJECTED, no GL entries created
- Note: User must create a new transaction to fix any errors

## ✅ Quick Button Guide

### Approval View (Approver Role)
When viewing a Draft receipt/payment:
- **✓ Approve Button**: Move to APPROVED state
- **✗ Reject Button**: Move to REJECTED state (requires confirmation)

### Authorization View (Finance Role)
When viewing an Approved receipt/payment:
- **→ Authorize & Post**: Create GL entries and AUTHORIZE
- **✗ Reject Button**: Move back to REJECTED state (requires confirmation)

## 📊 Data Flow

```
Cash Receipt Form (Create)
           ↓
    [Save & Submit]
           ↓
    DRAFT Status
    (Gray Badge)
           ↓
  ┌────────┴────────┐
  ↓                 ↓
Approve          Reject
  ↓                 ↓
APPROVED        REJECTED
(Blue Badge)    (Red Badge)
  ↓                 ↓
Authorize       [END]
  ↓
Create GL Entries
  ↓
AUTHORIZED
(Green Badge)
  ↓
[FINALIZED]
```

## 🛡️ Safety Features

1. **Multi-Step Approval**: Prevents single point of failure
2. **GL Entry Deferral**: GL entries only created at final authorization step
3. **Audit Trail**: Every action logged with user and timestamp
4. **Rejection Support**: Can reject at any pre-authorization stage
5. **Confirmation Dialogs**: Rejection requires user confirmation

## 🔍 Example Workflow

### Creating a Cash Receipt

**Day 1 - Morning (Accounting Clerk)**
1. Navigate to Cash Receipts → New Cash Receipt
2. Fill in:
   - Date: 2025-11-29
   - Debit Account: 3100-01 (Capital - Shareholder)
   - Credit Account: 100001 (Cash)
   - Description: Shareholder capital deposit
   - Amount: 50,000
3. Click "Save & Submit"
4. ✅ Message: "Cash receipt created successfully! Status: Draft - Awaiting approval"

**Day 1 - Afternoon (Manager)**
1. Go to Cash Receipts List
2. Find the receipt with Gray "Draft" badge
3. Click "✓" (Approve) button
4. ✅ Message: "Cash receipt approved! Ready for authorization."
5. Status changes to Blue "Approved" badge
6. New button appears: "→ Authorize & Post"

**Day 1 - End of Day (Finance Manager)**
1. Go to Cash Receipts List
2. Find the receipt with Blue "Approved" badge
3. Click "→" (Authorize & Post) button
4. ✅ Message: "Cash receipt authorized and posted to GL!"
5. Status changes to Green "Authorized" badge
6. GL entries created:
   - DR: 3100-01 (Capital) 50,000
   - CR: 100001 (Cash) 50,000

**Result**: Transaction fully processed and GL entries posted

## ❌ Rejection Example

If an error is discovered before authorization:

**Scenario**: Wrong account was selected
1. View the Draft receipt with "Approve" button
2. Click "✗" (Reject) button
3. Confirm rejection in dialog
4. ✅ Message: "Cash receipt rejected."
5. Status changes to Red "Rejected" badge
6. **No GL entries created**
7. Create a new receipt with correct account

## 📱 Mobile Workflow

- Buttons are optimized for touch/mobile
- Use horizontal scroll on tables if needed
- Status badges are color-coded for quick identification
- Confirmation dialogs prevent accidental actions

## ⚙️ System Requirements

- **Creating**: Any user with Cash Management access
- **Approving**: User with Manager role
- **Authorizing**: User with Finance Manager role
- **No GL Entry Creation** at form submission
- **GL Entries Created** only at authorization step

## 🔐 Permissions

- Approval View: Requires Manager/Supervisor role
- Authorization View: Requires Finance/Finance Manager role
- Both roles can reject transactions
- Audit logs track who performed each action

## 💡 Best Practices

1. ✅ **Review carefully** before approving
2. ✅ **Verify amounts** match documentation
3. ✅ **Check accounts** are correct before authorization
4. ✅ **Use meaningful descriptions** for audit trail
5. ✅ **Reject immediately** if errors detected
6. ❌ Don't skip approval steps
7. ❌ Don't authorize without review
8. ❌ Don't create duplicate transactions

## 📞 Support

For issues or questions:
- Check the workflow status badge
- Review the available action buttons
- Check audit log for transaction history
- Contact Finance Manager if transaction stuck
