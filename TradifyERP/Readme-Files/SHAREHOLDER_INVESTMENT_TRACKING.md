# Shareholder Investment Tracking System

## Overview
This system allows you to set and track investment commitments for each shareholder, with a target of 10 lacs (1,000,000 in base currency) per shareholder. It provides real-time tracking of:

- **Investment Target**: Limit set for each shareholder (default: 10 lacs)
- **Invested Amount**: Total amount already contributed by shareholder
- **Balance to Invest**: Remaining amount needed to meet target
- **Investment Progress**: Visual progress indicator as percentage
- **Payment Commitments**: Promised payment dates and amounts
- **Overdue Tracking**: Automatically identifies overdue payments

---

## Features

### 1. Investment Limits
- Set individual investment targets for each shareholder
- Default: 10 lacs (₹10,00,000) per shareholder
- Configurable by currency and entity
- Automatically calculates from completed capital contributions

### 2. Payment Commitments
- Record promised payment dates from shareholders
- Track committed amounts and payment status
- Automatic overdue detection
- Status tracking: Pending, Paid, Overdue, Rescheduled, Cancelled

### 3. Investment Report Dashboard
- View all shareholders with investment status at a glance
- See invested vs. target amounts
- Track progress with visual progress bars
- View next payment due dates
- Identify overdue commitments

---

## How to Use

### Setting Up Investment Limits

1. **Navigate to Investment Report**
   - Go to: `Shareholder > Investment Report`
   - URL: `/shareholder/investment-report/`

2. **Click "Set Investment Limit"**
   - Select the shareholder
   - Select currency
   - Enter target investment amount (default: 1,000,000 for 10 lacs)
   - Click Save

3. **System Automatically Calculates:**
   - Total invested (from completed capital contributions)
   - Balance to invest
   - Investment percentage

### Adding Payment Commitments

1. **From Investment Report**
   - Click "Add Payment Commitment"
   - Select shareholder
   - Enter committed amount
   - Select currency
   - Enter promised payment date
   - Add notes if needed
   - Click Save

2. **Tracking Commitment**
   - System tracks promised vs actual payment date
   - Automatically marks as Overdue if payment date passes
   - Shows in Investment Report for easy visibility

### Viewing Investment Report

The Investment Report provides a complete overview:

| Column | Description |
|--------|-------------|
| Shareholder | Name of the shareholder |
| Target Investment | Set investment limit (e.g., 10 lacs) |
| Invested Amount | Amount already contributed |
| Balance to Invest | Remaining amount to meet target |
| Progress | Visual progress bar (0-100%) |
| Next Payment | Next promised payment date and amount |
| Status | Completed/Pending/Overdue |
| Action | View shareholder details |

---

## Data Models

### ShareholderInvestmentLimit
```python
- entity: Foreign Key (Entity)
- stakeholder: One-to-One Key (Stakeholder)
- currency: Foreign Key (Currency)
- target_investment_amount: Decimal (default: 1,000,000)
- total_invested: Decimal (auto-calculated)
- balance_to_invest: Decimal (auto-calculated)
- is_active: Boolean
```

**Methods:**
- `update_totals()`: Recalculates invested and balance amounts
- `invested_percentage`: Property that returns investment progress %

### ShareholderPaymentCommitment
```python
- entity: Foreign Key (Entity)
- stakeholder: Foreign Key (Stakeholder)
- committed_amount: Decimal
- currency: Foreign Key (Currency)
- promised_payment_date: Date
- status: Choice (Pending/Paid/Overdue/Rescheduled/Cancelled)
- actual_payment_date: Date (nullable)
- notes: Text
- reference_number: Char (nullable)
```

**Properties:**
- `is_overdue`: Boolean indicating if payment is past due date

---

## URLs and Views

### URLs
- `/shareholder/investment-report/` - Investment Report Dashboard
- `/shareholder/investment-limits/create/` - Create Investment Limit
- `/shareholder/investment-limits/<id>/edit/` - Edit Investment Limit
- `/shareholder/payment-commitments/create/` - Create Payment Commitment
- `/shareholder/payment-commitments/<id>/edit/` - Edit Payment Commitment

### Views
1. **ShareholderInvestmentReportView** - Displays investment dashboard
2. **ShareholderInvestmentLimitCreateView** - Create investment limit
3. **ShareholderInvestmentLimitUpdateView** - Edit investment limit
4. **ShareholderPaymentCommitmentCreateView** - Create commitment
5. **ShareholderPaymentCommitmentUpdateView** - Edit commitment

---

## Integration with Capital Contributions

The system automatically integrates with existing capital contributions:

1. When a capital contribution is **marked as COMPLETED**:
   - `ShareholderInvestmentLimit.update_totals()` should be called
   - Total invested updates automatically
   - Balance to invest recalculates
   - Progress percentage updates

2. Completed contributions include:
   - Bank transfers
   - Cash deposits
   - Cheque deposits
   - Wire transfers
   - Other payment modes

---

## Sample Workflow

### Scenario: ABC Limited - Shareholder Investment Setup

**Step 1: Set Investment Targets**
- Shareholder: Rajesh Kumar
- Target: ₹10,00,000 (10 lacs)
- Currency: INR

**Step 2: Record Investment**
- Rajesh invests ₹5,00,000 via bank transfer (marked as Completed)
- System shows:
  - Invested: ₹5,00,000
  - Balance: ₹5,00,000
  - Progress: 50%

**Step 3: Add Payment Commitment**
- Promised: ₹3,00,000 by 31-Dec-2025
- System shows in report with promised date

**Step 4: Process Remaining Payment**
- When final ₹2,00,000 received and confirmed
- Total invested becomes ₹10,00,000
- Status shows: "Completed"
- Progress reaches 100%

---

## Report Features

### Dashboard Statistics
- **Total Shareholders**: Count of active shareholders with limits
- **Fully Invested**: Count of shareholders who met target
- **Overdue Payments**: Count of commitments past due date
- **Average Progress**: Average investment percentage

### Visual Indicators
- **Progress Bars**: Color-coded (Red < 50%, Yellow 50-100%, Green ≥ 100%)
- **Status Badges**:
  - Green "Completed" - Target met
  - Yellow "Pending" - In progress
  - Red "Overdue" - Payment past due

### Filtering and Sorting
- Sort by invested amount
- Sort by balance remaining
- Sort by due date
- Filter by status

---

## Configuration

### Default Investment Amount
Currently set to **1,000,000** (10 lacs in INR)

To change globally:
1. Edit `accounting/models.py`
2. Modify `ShareholderInvestmentLimit.target_investment_amount` default
3. Run migrations

To change per-shareholder:
1. Edit the specific investment limit
2. Update target amount
3. System recalculates automatically

### Currency Management
- Each limit can use different currency
- Payments tracked by commitment currency
- Reports show symbol and amount per currency

---

## Best Practices

1. **Set Limits Early**: Establish targets when onboarding shareholders
2. **Record Commitments**: Document promised payment dates in writing
3. **Regular Review**: Check investment report weekly for overdue items
4. **Follow Up**: Contact shareholders with overdue payments
5. **Update Status**: Mark commitments as Paid when received
6. **Document Changes**: Add notes when rescheduling commitments

---

## Permissions

Required permissions to use:
- `accounting.view_stakeholder` - View investment report
- `accounting.add_shareholderinvestmentlimit` - Create limits
- `accounting.change_shareholderinvestmentlimit` - Edit limits
- `accounting.add_shareholderpaymentcommitment` - Create commitments
- `accounting.change_shareholderpaymentcommitment` - Edit commitments

---

## Troubleshooting

### Issue: Balance not updating after capital contribution
- **Solution**: Run `ShareholderInvestmentLimit.update_totals()` manually or ensure contribution is marked as COMPLETED

### Issue: Overdue payments not showing
- **Solution**: Check that promised_payment_date is in the past and status is PENDING

### Issue: Progress bar showing 0%
- **Solution**: Ensure capital contributions are marked as COMPLETED, not PENDING

---

## Future Enhancements

1. **Email Notifications**: Auto-send reminders for upcoming/overdue payments
2. **Payment Plans**: Support installment plans with multiple commitments
3. **Dividend Calculations**: Link investments to shareholder dividend payments
4. **Certificate Generation**: Create investment certificate upon completion
5. **Export Reports**: Export to PDF/Excel for stakeholder reports
6. **SMS Alerts**: Send SMS reminders for payment due dates

---

## Technical Implementation

### Database Schema
```
ShareholderInvestmentLimit
├── entity (FK)
├── stakeholder (1-1)
├── currency (FK)
├── target_investment_amount
├── total_invested (calculated)
├── balance_to_invest (calculated)
└── is_active

ShareholderPaymentCommitment
├── entity (FK)
├── stakeholder (FK)
├── committed_amount
├── currency (FK)
├── promised_payment_date
├── status
├── actual_payment_date
├── notes
└── reference_number
```

### Key Calculations

```python
# Investment percentage
invested_percentage = (total_invested / target_investment_amount) * 100

# Is overdue?
is_overdue = (status == 'PENDING' AND promised_payment_date < today())

# Balance to invest
balance = target_investment_amount - total_invested
```

---

## Support

For issues or questions:
1. Check the Investment Report for data accuracy
2. Verify shareholder and currency selections
3. Ensure capital contributions are marked as COMPLETED
4. Review promised payment dates are entered correctly

---

**Version**: 1.0  
**Last Updated**: December 1, 2025  
**System**: TradifyERP
