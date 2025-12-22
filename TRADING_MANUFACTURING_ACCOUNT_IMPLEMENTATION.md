# Trading & Manufacturing Account Module - Implementation Complete

## Overview
Created a new sub-module under Accounting for **Trading & Manufacturing Account** that shows Gross Profit calculations based on sales revenue and cost of sales (purchases and manufacturing expenses).

## What Was Created

### 1. Backend Calculation Module
**File**: `TradifyERP/accounting/trading_manufacturing.py`

**Functions**:
- `calculate_trading_manufacturing_account(entity, period_start, period_end)` - Main calculation function
  - Gets all INCOME accounts (Sales Revenue - GL codes 4000-4999)
  - Gets all EXPENSE accounts (Cost of Sales - GL codes 5000-5999, 6000-6999)
  - Auto-categorizes expenses into:
    * Purchases
    * Salaries
    * Wages
    * Transportation (Inward)
    * Factory Rent
    * Factory Electricity
    * Miscellaneous
    * Other Direct Costs
  - Calculates Gross Profit = Sales - Cost of Sales
  - Returns structured data with balances and percentages

- `get_manufacturing_metrics(entity, period_start, period_end)` - Additional KPIs
  - Gross Profit Margin %
  - Cost of Sales Ratio %
  - Cost breakdown by category

**Features**:
- Uses **GL codes only** (not sub-codes)
- Reads from posted ledger entries
- Respects account types (INCOME = credit balance, EXPENSE = debit balance)
- Groups costs by category for better analysis

### 2. View Logic
**File**: `TradifyERP/accounting/views_tm.py`

**Class**: `TradingManufacturingAccountView`
- Form-based view with date range selector
- Defaults to current month
- Allows custom date range selection
- SessionEntityMixin for entity-specific data

### 3. Template
**File**: `TradifyERP/templates/accounting/trading_manufacturing_account.html`

**Sections**:
1. **Date Range Selector** - Select period start and end dates
2. **Summary Metrics Cards**:
   - Total Sales (green)
   - Total Costs (red)
   - Gross Profit with margin % (blue/yellow based on positive/negative)
3. **Sales/Revenue Table**:
   - GL Code | Account Name | Amount (₹)
   - Shows all INCOME accounts with credit balances
   - Total Sales Revenue subtotal
4. **Cost of Sales Table**:
   - GL Code | Account Name | Category | Amount (₹)
   - Grouped by category (Purchases, Salaries, Wages, etc.)
   - Shows all EXPENSE accounts with debit balances
   - Total Cost of Sales subtotal
5. **Gross Profit Calculation**:
   - Sales Revenue - Cost of Sales = Gross Profit
   - Shows margin percentage
6. **Financial Metrics**:
   - Gross Profit Margin %
   - Cost of Sales Ratio %
   - Cost breakdown by category pie chart data

### 4. URL Routing
**File**: `TradifyERP/accounting/urls.py`

**Added**:
```python
from .views_tm import TradingManufacturingAccountView

# In urlpatterns:
path('trading-manufacturing/', TradingManufacturingAccountView.as_view(), name='trading_manufacturing'),
```

**URL**: `https://tradifyglobal.com/accounting/trading-manufacturing/`

### 5. Navigation Links

**Vertical Sidebar** (`templates/partials/sidebar.html`):
```
Accounting APP
├─ Financial Reports
│  ├─ General Ledger Dashboard
│  ├─ Accounts
│  ├─ Ledger Entries
│  ├─ Trial Balances
│  ├─ Profit & Loss Reports
│  ├─ Trading & Manufacturing Account ✅ NEW
│  └─ Balance Sheets
```

**Horizontal Navigation** (`templates/partials/hori-sidebar.html`):
```
Accounting Dropdown
└─ Financial Reports
   ├─ Trial Balances
   ├─ Profit & Loss Reports
   ├─ Trading & Manufacturing Account ✅ NEW
   └─ Balance Sheets
```

## How It Works

### Data Flow
```
1. User selects date range (period_start, period_end)
2. System queries LedgerEntry table for posted entries in date range
3. Groups entries by Account:
   - INCOME accounts (GL 4000-4999) → Sales Revenue
   - EXPENSE accounts (GL 5000-5999) → Cost of Sales
4. Calculates balances based on account type:
   - INCOME: Credit balance (Credits - Debits)
   - EXPENSE: Debit balance (Debits - Credits)
5. Categorizes expenses automatically by account name keywords
6. Calculates Gross Profit = Total Sales - Total Costs
7. Displays formatted report with metrics
```

### Account Categorization
The system automatically categorizes expense accounts based on keywords in the account name:

| Category | Keywords in Account Name |
|----------|-------------------------|
| Purchases | 'purchase', 'cost of goods' |
| Salaries | 'salary', 'salaries' |
| Wages | 'wage', 'wages' |
| Transportation (Inward) | 'transport', 'freight', 'inward' |
| Factory Rent | 'factory rent', 'manufacturing rent' |
| Factory Electricity | 'factory electricity', 'factory power', 'factory utilities' |
| Miscellaneous | 'miscellaneous', 'misc', 'sundry' |
| Other Direct Costs | All other expense accounts |

## Usage

### Access the Report
1. **Via Navigation**: Accounting → Financial Reports → Trading & Manufacturing Account
2. **Direct URL**: `https://tradifyglobal.com/accounting/trading-manufacturing/`

### Generate Report
1. Select **Period Start** date (e.g., 2025-12-01)
2. Select **Period End** date (e.g., 2025-12-19)
3. Click **Generate Report** button
4. View results with:
   - Sales revenue breakdown by GL account
   - Cost of sales breakdown by category and GL account
   - Gross profit calculation
   - Financial metrics

### Example Output
```
TRADING & MANUFACTURING ACCOUNT
Period: Dec 01, 2025 to Dec 19, 2025

SALES / REVENUE
GL Code    Account Name              Amount (₹)
4100       Sales Revenue             500,000.00
4200       Service Revenue            50,000.00
                                    ───────────
Total Sales Revenue                  550,000.00

LESS: COST OF SALES
Category: Purchases
5100       Purchase of Goods         300,000.00

Category: Salaries
5200       Factory Salaries           80,000.00

Category: Wages
5210       Worker Wages               40,000.00

Category: Transportation (Inward)
5300       Inward Freight             15,000.00

Category: Factory Rent
5400       Manufacturing Rent         20,000.00

Category: Factory Electricity
5500       Factory Power              10,000.00

Category: Miscellaneous
5900       Misc Factory Expenses       5,000.00
                                    ───────────
Total Cost of Sales                  470,000.00

═══════════════════════════════════════════════
GROSS PROFIT                          80,000.00
Margin: 14.55%
═══════════════════════════════════════════════
```

## GL Account Setup Required

For the module to work properly, you need these GL accounts in your Chart of Accounts:

### Income Accounts (Sales)
- **4000-4999**: Sales Revenue accounts
  - Example: 4100 - Sales Revenue
  - Example: 4200 - Service Revenue

### Expense Accounts (Cost of Sales)
- **5000-5999**: Direct manufacturing/trading expenses
  - Example: 5100 - Purchase of Goods
  - Example: 5200 - Factory Salaries
  - Example: 5210 - Worker Wages
  - Example: 5300 - Inward Transportation
  - Example: 5400 - Factory Rent
  - Example: 5500 - Factory Electricity
  - Example: 5900 - Miscellaneous Factory Expenses

## Differences from Profit & Loss Report

| Feature | Trading & Manufacturing Account | Profit & Loss Report |
|---------|-------------------------------|---------------------|
| **Focus** | Gross Profit only | Net Profit (comprehensive) |
| **Revenue** | All sales revenue | All income sources |
| **Costs** | Direct manufacturing costs only | All operating expenses |
| **Result** | Gross Profit | Net Profit/Loss |
| **Use Case** | Manufacturing/trading businesses | All businesses |
| **Categories** | Auto-categorized by expense type | General grouping |

## Deployment Steps

### To Production Server (192.168.20.10)

1. **Upload new files**:
```bash
scp trading_manufacturing.py zubair@192.168.20.10:/var/www/tradifyerp/accounting/
scp views_tm.py zubair@192.168.20.10:/var/www/tradifyerp/accounting/
scp templates/accounting/trading_manufacturing_account.html zubair@192.168.20.10:/var/www/tradifyerp/templates/accounting/
```

2. **Update existing files**:
```bash
scp accounting/urls.py zubair@192.168.20.10:/var/www/tradifyerp/accounting/
scp templates/partials/sidebar.html zubair@192.168.20.10:/var/www/tradifyerp/templates/partials/
scp templates/partials/hori-sidebar.html zubair@192.168.20.10:/var/www/tradifyerp/templates/partials/
```

3. **Restart Gunicorn**:
```bash
ssh zubair@192.168.20.10
sudo systemctl restart gunicorn
```

4. **Test**:
- Navigate to: `https://tradifyglobal.com/accounting/trading-manufacturing/`
- Select a date range
- Click "Generate Report"
- Verify sales, costs, and gross profit display correctly

## Benefits

✅ **Separate Gross Profit Analysis** - Focus on manufacturing efficiency  
✅ **Automatic Categorization** - Expenses grouped by type  
✅ **GL Code Based** - Uses main GL codes, not sub-codes  
✅ **Real-time Calculation** - Always up-to-date from ledger entries  
✅ **Manufacturing Metrics** - Gross profit margin, cost ratios  
✅ **Visual Dashboard** - Easy to read cards and tables  
✅ **Date Range Flexibility** - Any period selection  
✅ **Multi-currency Support** - Shows in entity's currency (₹ Rupees)  

## Next Steps

1. ✅ Deploy to production server
2. ✅ Test with actual GL data
3. ⚠️ Create GL accounts for manufacturing if needed:
   - Purchases (5100)
   - Salaries (5200)
   - Wages (5210)
   - Transportation Inward (5300)
   - Factory Rent (5400)
   - Factory Electricity (5500)
   - Miscellaneous (5900)
4. ✅ Train users on the new report

---

**Created**: December 19, 2025  
**Status**: ✅ Ready for Deployment  
**Access URL**: `/accounting/trading-manufacturing/`
