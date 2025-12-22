# TradifyERP User Guide
## Complete Guide to Accounting, Chart of Accounts, Shareholders & Expenses

**Version:** 1.0  
**Last Updated:** December 19, 2025  
**System URL:** https://tradifyglobal.com

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Accounting Module Overview](#accounting-module-overview)
3. [Chart of Accounts Setup](#chart-of-accounts-setup)
4. [Shareholder Management](#shareholder-management)
5. [Employee Expense Management](#employee-expense-management)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Login to TradifyERP

1. Navigate to: **https://tradifyglobal.com**
2. Enter your username and password
3. Click **"Login"**

**📸 Screenshot Needed:** Login page showing username/password fields

### Dashboard Overview

After login, you'll see the main dashboard with quick links to:
- **Accounting** - Financial management
- **Shareholders** - Capital contributions and distributions
- **Expenses** - Employee expense tracking
- **Reports** - Financial statements and analytics

**📸 Screenshot Needed:** Main dashboard showing module tiles

---

## Accounting Module Overview

The Accounting module is the core of TradifyERP, managing all financial transactions.

### Accessing Accounting Module

**Path:** Dashboard → **Accounting**

**📸 Screenshot Needed:** Accounting module homepage

### Sub-Modules

| Module | Purpose | Common Use Cases |
|--------|---------|------------------|
| **Chart of Accounts** | Manage account structure | Add new accounts, organize finances |
| **General Ledger** | View all transactions | Audit trail, balance verification |
| **Journal Entries** | Manual transactions | Adjustments, accruals, corrections |
| **Trial Balance** | Account balances summary | Month-end reconciliation |
| **Cash Payments** | Record cash outflows | Vendor payments, expenses |
| **Bank Payments** | Record bank transactions | Wire transfers, checks |
| **Cash Receipts** | Record cash inflows | Customer payments, sales |
| **Bank Receipts** | Record bank deposits | Customer deposits, transfers |

---

## Chart of Accounts Setup

### Understanding Account Structure

TradifyERP uses a **4-digit account numbering system**:

```
1000-1999: ASSETS (what you own)
2000-2999: LIABILITIES (what you owe)
3000-3999: EQUITY (owner's investment)
4000-4999: INCOME (revenue earned)
5000-5999: EXPENSES (costs incurred)
```

### Standard Chart of Accounts

#### **1. ASSET ACCOUNTS (1000-1999)**

| Account # | Account Name | Type | Usage |
|-----------|--------------|------|-------|
| 1000 | Cash in Hand | ASSET | Physical cash, petty cash |
| 1100 | Cash and Bank | ASSET | Bank account balances |
| 1200 | Accounts Receivable | ASSET | Money owed by customers |
| 1500 | Fixed Assets | ASSET | Equipment, vehicles, buildings |
| 1510 | Accumulated Depreciation | ASSET (contra) | Depreciation of fixed assets |

**📸 Screenshot Needed:** Asset accounts list in Chart of Accounts

#### **2. LIABILITY ACCOUNTS (2000-2999)**

| Account # | Account Name | Type | Usage |
|-----------|--------------|------|-------|
| 2000 | Accounts Payable | LIABILITY | Money owed to vendors |
| 2100 | Accounts Payable - Employee Expenses | LIABILITY | Approved expenses pending reimbursement |
| 2110 | Salaries Payable | LIABILITY | Unpaid employee salaries |

**📸 Screenshot Needed:** Liability accounts list

#### **3. EQUITY ACCOUNTS (3000-3999)**

| Account # | Account Name | Type | Usage |
|-----------|--------------|------|-------|
| 3000 | Owner's Capital | EQUITY | Initial investment |
| 3100-XX | Shareholder Capital - [Name] | EQUITY | Individual shareholder investments |
| 3200-XX | Drawings/Distributions - [Name] | EQUITY (contra) | Profit distributions to shareholders |

**Example:**
- 3100-01: Shareholder Capital - John Smith
- 3200-01: Drawings/Distributions - John Smith

**📸 Screenshot Needed:** Equity accounts showing shareholder structure

#### **4. INCOME ACCOUNTS (4000-4999)**

| Account # | Account Name | Type | Usage |
|-----------|--------------|------|-------|
| 4000 | Sales Revenue | INCOME | Product/service sales |
| 4100 | Service Revenue | INCOME | Service income |
| 4900 | Other Income | INCOME | Miscellaneous income |

**📸 Screenshot Needed:** Income accounts list

#### **5. EXPENSE ACCOUNTS (5000-5999)**

| Account # | Account Name | Type | Usage |
|-----------|--------------|------|-------|
| 5100 | Travel Expense | EXPENSE | Business travel costs |
| 5200 | Office Supplies Expense | EXPENSE | Stationery, supplies |
| 5300 | Meals & Entertainment Expense | EXPENSE | Business meals |
| 5400 | Utilities Expense | EXPENSE | Electricity, water, internet |
| 5500 | Maintenance & Repairs Expense | EXPENSE | Equipment repairs |
| 5600 | Professional Services Expense | EXPENSE | Consulting, legal fees |
| 5700 | Training & Development Expense | EXPENSE | Employee training |
| 5800 | Communications Expense | EXPENSE | Phone, internet |

**📸 Screenshot Needed:** Expense accounts list

### How to Add a New Account

**Path:** Accounting → **Chart of Accounts** → **Add Account**

#### Step-by-Step:

1. Click **"Add Account"** button
2. Fill in required fields:

   **Field Descriptions:**
   
   | Field | Description | Example |
   |-------|-------------|---------|
   | **Account Number** | 4-digit unique code | 5900 |
   | **Account Name** | Descriptive name | "Marketing Expense" |
   | **Account Type** | Select from dropdown | EXPENSE |
   | **Currency** | Account currency | USD |
   | **Description** | Optional details | "Advertising and promotions" |
   | **Is Active** | Check to enable | ✓ |

3. Click **"Save"**

**📸 Screenshot Needed:** Add Account form with all fields labeled

### Account Type Guidelines

**When creating accounts, choose the correct type:**

- **ASSET** - Resources owned (cash, inventory, receivables)
- **LIABILITY** - Obligations owed (payables, loans)
- **EQUITY** - Owner's stake (capital, retained earnings)
- **INCOME** - Revenue earned (sales, services)
- **EXPENSE** - Costs incurred (salaries, rent, supplies)

---

## Shareholder Management

### Overview

The Shareholder module tracks:
- Capital contributions (investments)
- Profit distributions (dividends)
- Drawings/withdrawals
- Individual shareholder balances

### Setting Up Stakeholders

**Path:** Accounting → **Stakeholders** → **Add Stakeholder**

#### Step 1: Create Stakeholder Record

**📸 Screenshot Needed:** Stakeholder creation form

**Required Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| **Entity** | Your company | "Main Company" |
| **Name** | Stakeholder full name | "John Smith" |
| **Type** | SHAREHOLDER or PARTNER | SHAREHOLDER |
| **Email** | Contact email | john.smith@email.com |
| **Phone** | Contact number | +1-555-0123 |
| **ID Number** | National ID/Passport | 123-45-6789 |
| **Ownership %** | Share percentage | 25.00 |

**Optional Fields:**
- Address
- Bank details (for distributions)
- Notes

#### Step 2: GL Accounts Auto-Creation

✅ **Automatic:** When you create a stakeholder, the system automatically creates:
- **Capital Account** (3100-XX): Tracks investments
- **Drawings Account** (3200-XX): Tracks distributions

**You don't need to manually create these accounts!**

**📸 Screenshot Needed:** Chart of Accounts showing auto-created shareholder accounts

### Recording Capital Contributions

**Path:** Shareholders → **Capital Contributions** → **Add Contribution**

#### Scenario: Shareholder invests $10,000 cash

**📸 Screenshot Needed:** Capital Contribution form

**Form Fields:**

| Field | What to Enter | Example |
|-------|---------------|---------|
| **Stakeholder** | Select from dropdown | John Smith |
| **Entity** | Your company | Main Company |
| **Contribution Type** | CASH or BANK | CASH |
| **Amount** | Investment amount | 10,000.00 |
| **Date** | Transaction date | 2025-12-19 |
| **Description** | Purpose/notes | "Initial capital investment" |

**Approval Workflow:**

1. **Draft** → Create contribution
2. **Submit** → Submit for approval
3. **Review** → Manager reviews
4. **Approve** → Finance approves
5. **Authorized** → GL posting automatic

**📸 Screenshot Needed:** Contribution approval workflow buttons

**GL Posting (Automatic):**
```
DEBIT:  1000 - Cash in Hand          $10,000
CREDIT: 3100-01 - Capital - John Smith  $10,000
```

### Recording Profit Distributions

**Path:** Cash/Bank Payments → **Create Payment** (Purpose: Profit Distribution)

#### Scenario: Distribute $5,000 profit to shareholder

**📸 Screenshot Needed:** Cash Payment form with Profit Distribution selected

**Form Fields:**

| Field | What to Enter | Example |
|-------|---------------|---------|
| **Payment Type** | CASH_PAYMENT | Cash Payment |
| **Payment Purpose** | PROFIT_DISTRIBUTION | Profit Distribution |
| **Stakeholder** | Select shareholder | John Smith |
| **Amount** | Distribution amount | 5,000.00 |
| **Payment Date** | Transaction date | 2025-12-19 |
| **Description** | Purpose | "Q4 2025 profit distribution" |

**Approval Workflow:**

1. **Draft** → Create payment
2. **Pending Approval** → Submit
3. **Approved** → Manager approves
4. **Authorized** → Finance authorizes → **GL posting happens here**

**📸 Screenshot Needed:** Payment workflow status progression

**GL Posting (Automatic):**
```
DEBIT:  3200-01 - Drawings - John Smith  $5,000
CREDIT: 1000 - Cash in Hand                $5,000
```

### Viewing Shareholder Balances

**Path:** Shareholders → **Capital Contributions** → Filter by Stakeholder

**📸 Screenshot Needed:** Capital Contributions list filtered by stakeholder

**How to Check Balance:**

1. Go to **Shareholders** → **Capital Contributions**
2. Filter by stakeholder name
3. View summary:
   - Total Contributions
   - Total Withdrawals
   - Current Balance

**Alternative:** Run **Trial Balance** report and look at 3100/3200 accounts

---

## Employee Expense Management

### Overview

The Expense module tracks:
- Employee expense reports
- Receipt management
- Approval workflows
- Reimbursement processing
- GL posting

### Setting Up Expense Categories

**Path:** Admin → **Expenses** → **Expense Categories**

**📸 Screenshot Needed:** Expense Categories list

#### Default Categories (Already Set Up):

| Category | GL Account | Receipt Required | Manager Approval |
|----------|-----------|------------------|------------------|
| Travel Expenses | 5100 | ✓ Yes | ✓ Yes |
| Office Supplies | 5200 | ✓ Yes | ✗ No |
| Meals & Entertainment | 5300 | ✓ Yes | ✓ Yes |
| Utilities | 5400 | ✓ Yes | ✓ Yes |
| Maintenance & Repairs | 5500 | ✓ Yes | ✓ Yes |
| Professional Services | 5600 | ✓ Yes | ✓ Yes |
| Training & Development | 5700 | ✓ Yes | ✓ Yes |
| Communications | 5800 | ✓ Yes | ✗ No |

**Each category is linked to a GL account - this is already configured!**

### Employee Expense Workflow

#### **Step 1: Employee Creates Expense Report**

**Path:** Expenses → **Reports** → **Create Report**

**📸 Screenshot Needed:** Create Expense Report form

**Form Fields:**

| Field | What to Enter | Example |
|-------|---------------|---------|
| **Period Start** | Start date of expenses | 2025-12-01 |
| **Period End** | End date of expenses | 2025-12-07 |
| **Description** | Purpose of expenses | "Business trip to NYC" |

Click **"Save"**

#### **Step 2: Add Expense Items**

**Path:** Open the report → **Add Expense Item**

**📸 Screenshot Needed:** Add Expense Item form

**Form Fields:**

| Field | What to Enter | Example |
|-------|---------------|---------|
| **Category** | Select from dropdown | Travel Expenses |
| **Expense Date** | Date expense occurred | 2025-12-02 |
| **Amount** | Expense amount | 250.00 |
| **Description** | What was purchased | "Flight ticket to NYC" |
| **Receipt** | Upload file | flight_receipt.pdf |
| **Receipt Number** | Invoice/receipt # | INV-12345 |

Click **"Save"**

**You can add multiple expense items to one report.**

**📸 Screenshot Needed:** Expense report showing multiple line items

#### **Step 3: Submit for Approval**

1. Review all expense items
2. Click **"Submit for Approval"**
3. Report status changes to **"Submitted"**

**📸 Screenshot Needed:** Submit button and status change

#### **Step 4: Manager Approval**

**Path:** Expenses → **Reports** → Filter: Pending Review

**📸 Screenshot Needed:** Manager view of pending reports

**Manager Actions:**
1. Click on report to review
2. Check all expense items and receipts
3. Click **"Approve"** or **"Reject"**
4. Add notes (optional)

**Upon Approval:**
- Report status → **"Approved"**
- **GL posting happens automatically**

**GL Entries Created (Automatic):**
```
For each expense item:
DEBIT:  5XXX - Expense Account (e.g., 5100 Travel)  $250.00
CREDIT: 2100 - Accounts Payable - Employee Expenses  $250.00
```

**📸 Screenshot Needed:** Approved report showing GL entry confirmation

#### **Step 5: Finance Creates Reimbursement**

**Path:** Expenses → **Reimbursements** → **Create Reimbursement**

**📸 Screenshot Needed:** Create Reimbursement form

**Form Fields:**

| Field | What to Enter | Example |
|-------|---------------|---------|
| **Report** | Select approved report | Report #123 - John Doe |
| **Amount** | Reimbursement amount | 250.00 |
| **Method** | Payment method | Bank Transfer |
| **Scheduled Date** | When to pay | 2025-12-20 |

Click **"Save"**

#### **Step 6: Process Payment**

**Path:** Expenses → **Reimbursements** → Open reimbursement → **Process Payment**

**📸 Screenshot Needed:** Process Payment button

**Form Fields:**

| Field | What to Enter | Example |
|-------|---------------|---------|
| **Transaction ID** | Bank reference | TXN-ABC123 |

Click **"Process Payment"**

**Upon Payment:**
- Reimbursement status → **"Completed"**
- **GL posting happens automatically**

**GL Entries Created (Automatic):**
```
DEBIT:  2100 - Accounts Payable - Employee Expenses  $250.00
CREDIT: 1100 - Cash and Bank                         $250.00
```

**📸 Screenshot Needed:** Completed reimbursement with GL confirmation

### Viewing Expense Reports

**Path:** Expenses → **Reports**

**Available Filters:**
- Status (Draft, Submitted, Approved, Rejected)
- Employee
- Date Range
- Category

**📸 Screenshot Needed:** Reports list with filter options

---

## Common Workflows

### Workflow 1: Recording a Sale

**Scenario:** Customer pays $1,000 cash for products

**Path:** Accounting → **Cash Receipts** → **Create Receipt**

**📸 Screenshot Needed:** Cash Receipt form

**Steps:**
1. Select **Receipt Type**: Cash Receipt
2. Enter **Amount**: 1,000.00
3. Enter **Date**: Today's date
4. Select **Account**: 4000 - Sales Revenue
5. Enter **Description**: "Product sale - Invoice #123"
6. Click **"Save"**
7. Submit for approval
8. Manager approves → GL posting automatic

**GL Posting:**
```
DEBIT:  1000 - Cash in Hand      $1,000
CREDIT: 4000 - Sales Revenue     $1,000
```

### Workflow 2: Paying a Vendor Bill

**Scenario:** Pay $500 for office supplies via bank

**Path:** Accounting → **Bank Payments** → **Create Payment**

**Steps:**
1. Select **Payment Type**: Bank Payment
2. Enter **Amount**: 500.00
3. Enter **Date**: Payment date
4. Select **Account**: 5200 - Office Supplies Expense
5. Enter **Description**: "Office supplies - Invoice #ABC"
6. Click **"Save"**
7. Submit → Approve → Authorize

**GL Posting:**
```
DEBIT:  5200 - Office Supplies Expense  $500
CREDIT: 1100 - Cash and Bank            $500
```

### Workflow 3: Month-End Closing

**Steps:**
1. **Review Trial Balance**
   - Path: Accounting → **Trial Balance**
   - Verify all accounts balance
   - Check for unusual balances

2. **Review Ledger Entries**
   - Path: Accounting → **General Ledger**
   - Filter by date range (current month)
   - Verify all postings

3. **Generate Financial Statements**
   - **Profit & Loss**: Accounting → **P&L Report**
   - **Balance Sheet**: Accounting → **Balance Sheet**

**📸 Screenshot Needed:** Trial Balance report
**📸 Screenshot Needed:** P&L Statement
**📸 Screenshot Needed:** Balance Sheet

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "GL account not configured for expense category"

**Problem:** Expense approval fails with this error

**Solution:**
1. Go to **Admin** → **Expenses** → **Expense Categories**
2. Find the category
3. Click **"Edit"**
4. Select **"Expense Account"** from dropdown (e.g., 5100)
5. Click **"Save"**

**📸 Screenshot Needed:** Edit Category form highlighting Expense Account field

---

#### Issue 2: "Cannot find Cash/Bank account"

**Problem:** Reimbursement payment fails

**Solution:**
Ensure you have these accounts:
- **1000** - Cash in Hand (for cash payments)
- **1100** - Cash and Bank (for bank payments)

Create if missing:
1. Accounting → **Chart of Accounts** → **Add Account**
2. Create account 1000 or 1100 as ASSET type

---

#### Issue 3: "Shareholder accounts not created"

**Problem:** Capital contribution fails

**Solution:**
Shareholder accounts auto-create when:
1. Stakeholder is created
2. First capital contribution is made

Check: Accounting → **Chart of Accounts** → Look for 3100-XX and 3200-XX

If missing, contact system administrator.

---

#### Issue 4: "Reimbursement amount exceeds approved expenses"

**Problem:** Payment processing fails

**Solution:**
This is a validation error. Check:
1. Total approved expense items
2. Reimbursement amount
3. Ensure reimbursement ≤ approved total

You may need to split into multiple reimbursements.

---

## Viewing Financial Reports

### Trial Balance

**Path:** Accounting → **Trial Balance**

**Purpose:** Shows all account balances at a point in time

**How to Generate:**
1. Select **Date** (end date for balances)
2. Click **"Generate"**

**What to Check:**
- Total Debits = Total Credits (must balance)
- Account balances make sense
- No negative balances in wrong places

**📸 Screenshot Needed:** Trial Balance report with totals highlighted

---

### Profit & Loss Statement

**Path:** Accounting → **P&L Report**

**Purpose:** Shows income vs expenses for a period

**How to Generate:**
1. Select **Start Date** (e.g., Jan 1, 2025)
2. Select **End Date** (e.g., Dec 31, 2025)
3. Click **"Generate"**

**Report Shows:**
- **Revenue** (4000-series accounts)
- **Expenses** (5000-series accounts)
- **Net Profit** = Revenue - Expenses

**📸 Screenshot Needed:** P&L report showing revenue, expenses, and net profit

---

### Balance Sheet

**Path:** Accounting → **Balance Sheet**

**Purpose:** Shows what you own (assets) vs what you owe (liabilities) + equity

**How to Generate:**
1. Select **As of Date** (e.g., Dec 31, 2025)
2. Click **"Generate"**

**Report Shows:**
- **Assets** (1000-series)
- **Liabilities** (2000-series)
- **Equity** (3000-series)
- **Must Balance:** Assets = Liabilities + Equity

**📸 Screenshot Needed:** Balance Sheet report

---

## General Ledger

**Path:** Accounting → **General Ledger**

**Purpose:** Complete transaction log

**How to Use:**
1. Select filters:
   - Date range
   - Account (optional)
   - Entry status (Posted/All)
2. Click **"Filter"**

**Shows:**
- Date
- Account
- Description
- Debit amount
- Credit amount
- Reference number
- Status

**Use Cases:**
- Audit trail
- Finding specific transactions
- Reconciling accounts

**📸 Screenshot Needed:** General Ledger report with transactions

---

## Best Practices

### 1. Account Naming
✅ **Do:**
- Use clear, descriptive names
- Follow standard numbering
- Be consistent

❌ **Don't:**
- Use vague names ("Misc Account")
- Skip account numbers
- Duplicate names

### 2. Transaction Descriptions
✅ **Do:**
- Include invoice/reference numbers
- Describe the transaction clearly
- Note the counterparty

❌ **Don't:**
- Leave blank
- Use only "Payment" or "Receipt"
- Forget dates

### 3. Approvals
✅ **Do:**
- Review all supporting documents
- Check amounts match receipts
- Verify account selections

❌ **Don't:**
- Auto-approve without review
- Skip receipt verification
- Ignore policy limits

### 4. Month-End
✅ **Do:**
- Run trial balance
- Review unusual balances
- Reconcile bank accounts
- Generate financial statements

❌ **Don't:**
- Skip reconciliations
- Ignore imbalances
- Close books with errors

---

## Quick Reference Cards

### Account Selection Guide

**When recording a transaction, ask yourself:**

| Transaction Type | Account to Use |
|------------------|----------------|
| Received cash from sale | DR: 1000 (Cash), CR: 4000 (Revenue) |
| Paid cash for supplies | DR: 5200 (Supplies), CR: 1000 (Cash) |
| Bank transfer received | DR: 1100 (Bank), CR: 4000 (Revenue) |
| Bank payment for utilities | DR: 5400 (Utilities), CR: 1100 (Bank) |
| Shareholder invests cash | DR: 1000 (Cash), CR: 3100-XX (Capital) |
| Distribute profit | DR: 3200-XX (Drawings), CR: 1000 (Cash) |
| Employee expense approved | DR: 5XXX (Expense), CR: 2100 (AP) |
| Reimburse employee | DR: 2100 (AP), CR: 1100 (Bank) |

---

### Status Meanings

| Status | Meaning | Action Needed |
|--------|---------|---------------|
| **Draft** | Not yet submitted | Complete and submit |
| **Pending Approval** | Awaiting manager review | Manager to approve/reject |
| **Approved** | Manager approved | Finance to authorize |
| **Authorized** | Finance approved | GL posting automatic |
| **Posted** | In general ledger | Complete - no action |
| **Rejected** | Not approved | Review and resubmit |

---

## Contact & Support

### Getting Help

**For system issues:**
- Email: support@tradifyglobal.com
- Phone: +1-XXX-XXX-XXXX

**For accounting questions:**
- Contact your Finance Manager
- Refer to this user guide

**For training requests:**
- Contact HR or your supervisor

---

## Appendix: Complete Account List

### Assets (1000-1999)

```
1000 - Cash in Hand
1100 - Cash and Bank
1200 - Accounts Receivable
1500 - Fixed Assets
1510 - Accumulated Depreciation
```

### Liabilities (2000-2999)

```
2000 - Accounts Payable
2100 - Accounts Payable - Employee Expenses
2110 - Salaries Payable
```

### Equity (3000-3999)

```
3000 - Owner's Capital
3100-01 - Shareholder Capital - [Name 1]
3100-02 - Shareholder Capital - [Name 2]
3200-01 - Drawings/Distributions - [Name 1]
3200-02 - Drawings/Distributions - [Name 2]
```

### Income (4000-4999)

```
4000 - Sales Revenue
4100 - Service Revenue
4900 - Other Income
```

### Expenses (5000-5999)

```
5100 - Travel Expense
5200 - Office Supplies Expense
5300 - Meals & Entertainment Expense
5400 - Utilities Expense
5500 - Maintenance & Repairs Expense
5600 - Professional Services Expense
5700 - Training & Development Expense
5800 - Communications Expense
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-19 | Initial release - Complete user guide |

---

**End of User Guide**

For the latest version of this guide, visit: **https://tradifyglobal.com/docs**
