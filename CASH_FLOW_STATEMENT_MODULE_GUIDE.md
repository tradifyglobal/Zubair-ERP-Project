# Cash Flow Statement Reporting Module

**Complete Implementation Guide**  
**TradifyERP | Cash Management Suite**  
**Version 1.0**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Models & Data Structure](#models--data-structure)
4. [Views & URL Routing](#views--url-routing)
5. [Installation & Setup](#installation--setup)
6. [Usage Guide](#usage-guide)
7. [Integration with Cash Position Dashboard](#integration-with-cash-position-dashboard)
8. [Advanced Features](#advanced-features)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **Cash Flow Statement Reporting Module** transforms raw accounting data from the General Ledger (GL) into standardized **cash flow statements** following the **Indirect Method** format.

### Key Capabilities

- **Automated Generation**: Creates monthly/quarterly/annual cash flow statements directly from GL entries
- **Multi-Period Comparison**: Compare cash flows across periods with trend analysis and YoY calculations
- **Variance Analysis**: Track actual vs. forecasted cash flows with detailed variance reporting
- **Bank Reconciliation**: Reconcile GL cash balances to bank statements
- **Categorization**: Intelligently categorizes GL transactions into Operating/Investing/Financing activities
- **Audit Trail**: Maintains source references to all GL entries (invoices, bills, transfers)

### Financial Value

This module completes your treasury intelligence suite:

```
Daily Operations
     ↓
Cash Position Dashboard (Real-time snapshot)
     ↓
General Ledger (Daily transactions)
     ↓
Cash Flow Statements (Period-based reporting)
     ↓
Financial Analysis & Forecasting
```

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Cash Flow Module                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │  Models Layer    │          │  Views Layer     │        │
│  ├──────────────────┤          ├──────────────────┤        │
│  │ • CashFlowStatement         │ • ListV (Browse) │        │
│  │ • CashFlowLineItem          │ • DetailView     │        │
│  │ • CashFlowCategory          │ • GenerateView   │        │
│  │ • CashFlowVarianceAnalysis  │ • VarianceView   │        │
│  │ • CashFlowComparison        │ • ComparisonView │        │
│  │ • CashFlowForecastDetail    └──────────────────┘        │
│  └──────────────────┘                                       │
│           ↓                                                  │
│  ┌──────────────────────────────────────┐                  │
│  │      General Ledger (Source)         │                  │
│  │  • LedgerEntry                       │                  │
│  │  • Invoice (AR)                      │                  │
│  │  • VendorBill (AP)                   │                  │
│  │  • Account (Chart of Accounts)       │                  │
│  │  • BankStatement (Reconciliation)    │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Statement Generation Process**:

```
1. User selects date range (e.g., Jan 1 - Jan 31, 2026)
                    ↓
2. System queries GL entries for period
                    ↓
3. Calculates opening balance (sum of prior GL entries)
                    ↓
4. Categorizes transactions by opposing account:
   - AR | Sales Account → Operating
   - AP | Expense Account → Operating  
   - Asset Account → Investing
   - Loan Account → Financing
                    ↓
5. Aggregates by category:
   - Operating Inflows (collections)
   - Operating Outflows (payments)
   - Investing Inflows (asset sales)
   - Investing Outflows (asset purchases)
   - Financing Inflows (loan proceeds)
   - Financing Outflows (loan repayments)
                    ↓
6. Creates CashFlowStatement record
                    ↓
7. Generates line items with source references
                    ↓
8. Calculates closing balance = Opening + Net Flow
                    ↓
9. Validates: GL balance matches expected closing
```

---

## Models & Data Structure

### 1. CashFlowStatement

**Primary Model** - Represents one period's cash flow statement

```python
CashFlowStatement
├── Entity foreign key (multi-company support)
├── Period Info:
│   ├── period_type (DAILY|WEEKLY|MONTHLY|QUARTERLY|ANNUAL)
│   ├── start_date
│   └── end_date
├── Balance Summary:
│   ├── opening_balance
│   ├── closing_balance
│   └── total_net_cash_flow
├── Activity Flows:
│   ├── Operating:
│   │   ├── operating_inflows
│   │   ├── operating_outflows
│   │   └── net_operating_cash_flow
│   ├── Investing:
│   │   ├── investing_inflows
│   │   ├── investing_outflows
│   │   └── net_investing_cash_flow
│   └── Financing:
│       ├── financing_inflows
│       ├── financing_outflows
│       └── net_financing_cash_flow
├── Reconciliation:
│   ├── bank_closing_balance
│   ├── reconciliation_difference
│   └── is_reconciled (boolean)
└── Metadata:
    ├── created_at
    ├── updated_or:
    ├── generated_by ('SYSTEM' or username)
    └── notes (optional)
```

**Key Properties**:
- `is_balanced`: Returns True if opening + net flow = closing balance
- Unique constraint on (entity, period_type, start_date, end_date)

---

### 2. CashFlowLineItem

**Detail Records** - Individual line items within a statement

```python
CashFlowLineItem
├── FK: cash_flow_statement
├── FK: category (CashFlowCategory)
├── Display:
│   ├── line_number (ordering)
│   ├── description (text)
│   ├── amount (Decimal)
│   └── is_inflow (boolean)
├── Source:
│   ├── source_type ('INVOICE'|'BILL'|'PAYMENT'|'TRANSFER')
│   ├── source_id (link to original document)
│   └── quantity_transactions (count of aggregated txns)
└── Notes:
    └── detail_notes
```

---

### 3. CashFlowCategory

**Classification** - Maps GL accounts to activity categories

```python
CashFlowCategory
├── name (e.g., "Collections from Customers")
├── activity_type (OPERATING|INVESTING|FINANCING)
├── description
├── account_patterns (comma-separated account #s)
├── is_inflow (default categorization)
└── (Example patterns: "200,201,202" → AR accounts)
```

**Pre-configured Categories**:

| Activity | Category | Type | Accounts |
|----------|----------|------|----------|
| Operating | Collections | Inflow | 200-210 (AR) |
| Operating | Service Revenue | Inflow | 400-410 |
| Operating | Supplier Payments | Outflow | 300-320 (AP) |
| Operating | Payroll Payments | Outflow | 500-510 |
| Investing | Asset Purchases | Outflow | 1000-1500 |
| Investing | Asset Sales | Inflow | 1000-1500 |
| Financing | Loan Proceeds | Inflow | 2100-2200 |
| Financing | Loan Repayments | Outflow | 2100-2200 |

---

### 4. CashFlowVarianceAnalysis

**Variance Tracking** - Actual vs. Forecasted comparison

```python
CashFlowVarianceAnalysis
├── FK: cash_flow_statement (one-to-one)
├── Operating:
│   ├── operating_forecast
│   ├── operating_variance (actual - forecast)
│   └── operating_variance_pct
├── Investing:
│   ├── investing_forecast
│   ├── investing_variance
│   └── investing_variance_pct
├── Financing:
│   ├── financing_forecast
│   ├── financing_variance
│   └── financing_variance_pct
├── Total:
│   ├── total_forecast
│   ├── total_variance
│   └── total_variance_pct
└── variance_explanation (notes from management)
```

**Usage**:
- Variance > +15%: Better than expected (favorable)
- Variance < -15%: Worse than expected (investigate)
- Variance ±5 to 15%: Monitor

---

### 5. CashFlowComparison  

**Period Comparison** - YoY or period-over-period analysis

```python
CashFlowComparison
├── FK: current_period_statement
├── FK: prior_period_statement
├── Operating:
│   ├── operating_current
│   ├── operating_prior
│   ├── operating_change
│   └── operating_change_pct
├── [Similar for Investing & Financing]
└── analysis_notes
```

---

### 6. CashFlowForecastDetail

**Forward-Looking** - Forecasted cash flows by category

```python
CashFlowForecastDetail
├── FK: entity
├── FK: category
├── forecast_date
├── forecasted_inflow
├── forecasted_outflow
├── source_documents (invoice/bill IDs)
├── confidence_level (HIGH|MEDIUM|LOW)
└── timestamps
```

---

## Views & URL Routing

### URL Patterns

```python
# In cash_management/urls.py

urlpatterns = [
    # Cash Flow Statements
    path('statements/', 
        CashFlowStatementListView.as_view(), 
        name='cash_flow_list'),
    
    path('statements/<int:pk>/', 
        CashFlowStatementDetailView.as_view(), 
        name='cash_flow_detail'),
    
    path('statements/generate/', 
        CashFlowStatementGenerateView.as_view(), 
        name='cash_flow_generate'),
    
    path('statements/<int:pk>/variance/', 
        CashFlowVarianceAnalysisView.as_view(), 
        name='cash_flow_variance'),
    
    path('statements/compare/', 
        CashFlowComparisonView.as_view(), 
        name='cash_flow_comparison'),
]
```

### View Classes

#### 1. CashFlowStatementListView
**Lists all statements for the entity**

- Template: `cash_flow_statements_list.html`
- Context variables:
  - `statements`: Paginated list of CashFlowStatements
  - `latest_statement`: Most recent statement
  - `total_recent_inflows`: Sum of last 12 months
  - `total_recent_outflows`: Sum of last 12 months
  - `avg_net_monthly_flow`: Average monthly net change

#### 2. CashFlowStatementDetailView  
**Single statement with line items grouped by activity**

- Template: `cash_flow_statement_detail.html`
- Context variables:
  - `statement`: The CashFlowStatement instance
  - `line_items_by_category`: Dict {activity_type: [items]}
  - `variance_analysis`: Associated variance record
  - `prior_comparison`: Comparison to previous period

#### 3. CashFlowStatementGenerateView
**Generate new statements from GL**

- Template: `cash_flow_generate.html`
- POST returns JSON: `{success: bool, statement_id: int, statement_url: str}`
- Supports date range presets: This Month, Last Month, YTD
- Options:
  - Include detailed line items
  - Calculate variance analysis
  - Overwrite existing statement

#### 4. CashFlowVarianceAnalysisView
**Analyze actual vs. forecast**

- Template: `cash_flow_variance_analysis.html`
- Context variables:
  - `statement`: The statement being analyzed
  - `forecast_summary`: Dict with operating/investing/financing variances
  - `variance_analysis`: Full variance record

#### 5. CashFlowComparisonView  
**Multi-period trend analysis**

- Template: `cash_flow_comparison.html`
- Context variables:
  - `statements`: Last 12 monthly statements
  - `yoy_comparison`: Year-over-year comparison data
  - `operating_trend`: List of monthly values
  - `investing_trend`: List of monthly values
  - `financing_trend`: List of monthly values

---

## Installation & Setup

### Step 1: Add Models to Django App

```bash
# 1. Copy cash_flow_models.py to your app
cp cash_flow_models.py TradifyERP/cash_management/

# 2. Import in __init__.py
# In TradifyERP/cash_management/__init__.py
from .cash_flow_models import (
    CashFlowStatement, CashFlowLineItem, CashFlowCategory,
    CashFlowVarianceAnalysis, CashFlowComparison, CashFlowForecastDetail
)
```

### Step 2: Create Database Migrations

```bash
python manage.py makemigrations cash_management
python manage.py migrate cash_management
```

### Step 3: Register in Admin

```python
# In TradifyERP/cash_management/admin.py

from django.contrib import admin
from .cash_flow_models import *

@admin.register(CashFlowStatement)
class CashFlowStatementAdmin(admin.ModelAdmin):
    list_display = ('entity', 'period_type', 'start_date', 'end_date', 
                    'net_operating_cash_flow', 'total_net_cash_flow', 'is_balanced')
    list_filter = ('period_type', 'entity', 'start_date')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('entity__name',)

@admin.register(CashFlowCategory)
class CashFlowCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type', 'is_inflow')
    list_filter = ('activity_type', 'is_inflow')
```

### Step 4: Load Views

```python
# In TradifyERP/cash_management/urls.py

from django.urls import path
from .cash_flow_views import (
    CashFlowStatementListView,
    CashFlowStatementDetailView,
    CashFlowStatementGenerateView,
    CashFlowVarianceAnalysisView,
    CashFlowComparisonView,
)

urlpatterns = [
    # ... existing patterns ...
    
    path('statements/', CashFlowStatementListView.as_view(), name='cash_flow_list'),
    path('statements/<int:pk>/', CashFlowStatementDetailView.as_view(), name='cash_flow_detail'),
    path('statements/generate/', CashFlowStatementGenerateView.as_view(), name='cash_flow_generate'),
    path('statements/<int:pk>/variance/', CashFlowVarianceAnalysisView.as_view(), name='cash_flow_variance'),
    path('statements/compare/', CashFlowComparisonView.as_view(), name='cash_flow_comparison'),
]
```

### Step 5: Pre-populate Categories

```python
# Run in Django shell: python manage.py shell

from cash_management.cash_flow_models import CashFlowCategory

# Operating Activity Categories
CashFlowCategory.objects.create(
    name="Collections from Customers",
    activity_type="OPERATING",
    description="Cash received from customer invoices",
    account_patterns="200,201,202,203",
    is_inflow=True
)

CashFlowCategory.objects.create(
    name="Payments to Suppliers",
    activity_type="OPERATING",
    description="Cash paid to vendors for bills",
    account_patterns="300,301,302,303",
    is_inflow=False
)

# Investing Activity Categories
CashFlowCategory.objects.create(
    name="Asset Purchases",
    activity_type="INVESTING",
    description="Capital expenditures on fixed assets",
    account_patterns="1000,1100,1200,1300",
    is_inflow=False
)

# Financing Activity Categories
CashFlowCategory.objects.create(
    name="Loan Proceeds",
    activity_type="FINANCING",
    description="New borrowing from financial institutions",
    account_patterns="2100,2101,2102",
    is_inflow=True
)
```

---

## Usage Guide

### Generating Your First Statement

#### Scenario: January 2026 Monthly Statement

1. **Navigate to Generate Page**
   ```
   http://192.168.20.10/cash/statements/generate/
   ```

2. **Select Parameters**
   - Period Type: Monthly
   - Start Date: 2026-01-01
   - End Date: 2026-01-31
   - Check: "Include detailed line items"
   - Check: "Calculate variance analysis"

3. **Optional: Add Notes**
   ```
   "Quarterly close statement. Note: Unexpected insurance claim received."
   ```

4. **Click: Generate Statement**
   - System processes GL entries
   - Creates statement record
   - Generates line items
   - Runs validation
   - Redirects to detail view

5. **Review Generated Statement**
   - Verify opening balance
   - Check net flows by category
   - Validate closing balance matches GL
   - Review line items for accuracy

### Viewing & Analyzing Statements

#### Browse All Statements
```
http://192.168.20.10/cash/statements/
```

Features:
- Sort by period (newest first)
- Filter by status (Reconciled, Balanced, Pending)
- Click any row to view detail
- One-click access to variance analysis

#### View Detailed Statement
```
http://192.168.20.10/cash/statements/123/
```

Components:
- Three-activity format (Operating/Investing/Financing)
- Line items with source document links
- Balance validation indicator
- Bank reconciliation section (if available)
- Related variance analysis

#### Analyze Variances
```
http://192.168.20.10/cash/statements/123/variance/
```

Shows:
- Actual vs. Forecasted by activity
- Variance percentages
- Interpretation guidance
- Root cause analysis section
- Management notes field

#### Compare Periods
```
http://192.168.20.10/cash/statements/compare/
```

Displays:
- 12-month trend chart (Chart.js)
- Monthly summary table
- Year-over-year comparison
- Trend analysis

---

## Integration with Cash Position Dashboard

### Data Flow Architecture

```
┌──────────────────────────────────┐
│   Daily Cash Position Dashboard  │
│  (Real-time point-in-time)       │
├──────────────────────────────────┤
│  • Opening balance                │
│  • Current cash position          │
│  • Pending receipts/payments      │
│  • 7-day & 30-day forecasts      │
│  • Payment release recommendations│
└──────────────────────────────────┘
          ↓
     [Daily transactions recorded in GL]
          ↓
┌──────────────────────────────────┐
│    Weekly/Monthly Reconciliation │
│    Run Cash Flow Statement Gen   │
└──────────────────────────────────┘
          ↓
┌──────────────────────────────────┐
│   Cash Flow Statement Report      │
│  (Period-based categorized flows) │
├──────────────────────────────────┤
│  • Operating cash flow             │
│  • Investing cash flow             │
│  • Financing cash flow             │
│  • Period-to-period trends         │
│  • Forecast variance analysis      │
└──────────────────────────────────┘
```

### Dashboard → CFS Mapping

**Daily Dashboard Metrics → CFS Categories**

| Dashboard Metric | CFS Activity | GL Account Range |
|------------------|--------------|------------------|
| Payment Releases Recommended | Operating Outflow | 300-310 |
| Collections Expected | Operating Inflow | 200-210 |
| Fund Transfers | Investing | 1000+ |
| Loan Repayments | Financing Outflow | 2100+ |
| Investment Purchases | Investing Outflow | 1100+ |

### Using Dashboard Data in Forecasting

The CashFlowForecastDetail model works with Cash Position Dashboard data:

```python
# Example: Auto-populate forecast from dashboard
def create_forecast_from_dashboard():
    from cash_management.views import CashPositionListView
    
    # Get dashboard metrics
    context = CashPositionListView().get_context_data()
    
    # Extract pending flows
    pending_payments = context.get('pending_payment_amount')
    expected_collections = context.get('expected_collections_7day')
    
    # Create forecast details
    CashFlowForecastDetail.objects.create(
        entity=entity,
        category=operating_category,
        forecast_date=date.today() + timedelta(days=1),
        forecasted_inflow=expected_collections,
        forecasted_outflow=pending_payments,
        confidence_level='HIGH'
    )
```

---

## Advanced Features

### 1. Automated Weekly Statements

```python
# In your task scheduler (Celery/APScheduler)

from django.db.models import Q
from datetime import datetime, timedelta

def generate_weekly_statements():
    """Generates CFS every Friday for the prior week"""
    
    today = datetime.now().date()
    if today.weekday() != 4:  # Friday = 4
        return
    
    start = today - timedelta(days=7)
    
    for entity in Entity.objects.all():
        CashFlowStatementGenerateView().generate_statement(
            entity=entity,
            period_type='WEEKLY',
            start_date=start,
            end_date=today
        )
```

### 2. Multi-Company Comparison

```python
# View template to compare cash flows across subsidiaries

from cash_management.models import CashFlowStatement

def compare_group_cash_flows():
    """Compare cash flows across all company entities"""
    
    statements = CashFlowStatement.objects.filter(
        start_date=today,
        period_type='DAILY'
    ).select_related('entity')
    
    # Group by entity
    by_entity = {}
    for stmt in statements:
        by_entity[stmt.entity.name] = stmt.net_operating_cash_flow
    
    return by_entity
```

### 3. Cash Conversion Cycle Calculation

```python
def calculate_cash_conversion_cycle(statement):
    """
    CCC = DSO + DIO - DPO
    Where:  DSO = Days Sales Outstanding
            DIO = Days Inventory Outstanding
            DPO = Days Payable Outstanding
    """
    
    operating_inflows = statement.operating_inflows
    days_in_period = (statement.end_date - statement.start_date).days
    
    daily_sales = operating_inflows / days_in_period
    daily_purchases = statement.operating_outflows / days_in_period
    
    # Using average AR/AP/Inventory from GL
    # This would integrate with your inventory and AR/AP modules
    
    return {
        'dso': ar_balance / daily_sales,
        'dio': inventory_balance / purchase_cost,
        'dpo': ap_balance / daily_purchases,
        'ccc': (ar_balance / daily_sales) + (inventory_balance / purchase_cost) - (ap_balance / daily_purchases)
    }
```

### 4. Budgeted vs. Actual CFS

```python
def generate_budget_comparison(statement, budget_version):
    """Compare actual CFS to budgeted amounts"""
    
    budget = CashFlowBudget.objects.get(
        entity=statement.entity,
        version=budget_version,
        period=statement.start_date.strftime('%Y-%m')
    )
    
    variance = CashFlowVarianceAnalysis.objects.create(
        cash_flow_statement=statement,
        operating_forecast=budget.operating_estimate,
        operating_variance=statement.net_operating_cash_flow - budget.operating_estimate,
        # ... similar for investing and financing
    )
    
    return variance
```

---

## Performance Optimization

### Query Optimization

```python
# Inefficient - N+1 Problem (7 queries per statement)
statements = CashFlowStatement.objects.all()
for stmt in statements:
    print(stmt.entity.name)  # Extra query per iteration
    print(stmt.variance_analysis.operating_variance)  # 2 more queries

# Optimized - 1 query with all data
statements = CashFlowStatement.objects.select_related(
    'entity',
    'currency',
    'variance_analysis'  # Prefetch related records
).prefetch_related(
    'line_items',
    'line_items__category'
)
```

### Caching Strategy

```python
from django.core.cache import cache

def get_statement_summary(statement_id):
    cache_key = f'cfs_summary_{statement_id}'
    
    # Try cache first
    result = cache.get(cache_key)
    if result:
        return result
    
    # Generate if not cached
    statement = CashFlowStatement.objects.get(id=statement_id)
    result = {
        'operating': statement.net_operating_cash_flow,
        'investing': statement.net_investing_cash_flow,
        'financing': statement.net_financing_cash_flow,
        'total': statement.total_net_cash_flow,
    }
    
    # Cache for 24 hours
    cache.set(cache_key, result, 86400)
    return result
```

### Index Strategy

```python
# In models.py Meta class

class CashFlowStatement(models.Model):
    # ... fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['entity', 'start_date']),
            models.Index(fields=['entity', 'period_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]
```

---

## Troubleshooting

### Issue: Statement Balance Doesn't Match GL

**Cause**: Missing GL entries or incorrect opening balance calculation

**Solution**:
```python
def validate_statement(statement):
    """Verify statement balances with GL"""
    
    # Recalculate opening from GL
    opening = LedgerEntry.objects.filter(
        entity=statement.entity,
        entry_date__lt=statement.start_date,
        account__number__in=[100, 101, 102]
    ).aggregate(
        balance=Sum('debit_amount') - Sum('credit_amount')
    )['balance'] or 0
    
    # Check for mismatch
    if abs(opening - statement.opening_balance) > Decimal('0.01'):
        print(f"Opening Balance Mismatch!")
        print(f"  Expected: {opening}")
        print(f"  Actual:   {statement.opening_balance}")
        print(f"  Difference: {opening - statement.opening_balance}")
    
    return opening == statement.opening_balance
```

### Issue: Variance Always Shows as Negative

**Cause**: Forecast data incomplete or values inverted

**Solution**:
```python
# Ensure forecast data exists
assert CashFlowForecastDetail.objects.filter(
    entity=statement.entity,
    forecast_date__range=[statement.start_date, statement.end_date]
).exists()

# Check forecast values are positive
for forecast in CashFlowForecastDetail.objects.filter(...):
    assert forecast.forecasted_inflow >= 0
    assert forecast.forecasted_outflow >= 0
```

### Issue: Slow Statement Generation

**Cause**: Large number of GL entries being processed

**Solution**:  
```python
# Use database batch operations instead of Python loops
from django.db.models import Q

# Instead of:
for entry in entries:
    process(entry)

# Use bulk create:
items_to_create = [
    CashFlowLineItem(...) for entry in entries
]
CashFlowLineItem.objects.bulk_create(items_to_create, batch_size=1000)
```

---

## Next Steps & Roadmap

### Immediate (1-2 weeks)
- [ ] Deploy models and views to production
- [ ] Pre-populate CashFlowCategory defaults
- [ ] Test with 3 months of historical data
- [ ] Validate calculations vs. manual CFS

### Short-term (1-2 months)
- [ ] Mobile-optimized statement views
- [ ] Dashboard widget showing latest cash flow
- [ ] Email delivery of weekly/monthly statements
- [ ] Automated variance alerts (> 20% deviation)

### Medium-term (2-3 months)
- [ ] Cash Conversion Cycle dashboard
- [ ] Free Cash Flow (FCF) calculations
- [ ] Budget vs. Actual comparisons
- [ ] Sensitivity analysis (what-if scenarios)

### Long-term (3+ months)
- [ ] Consolidation of multi-entity cash flows
- [ ] SEC-compliant CFS formatting
- [ ] Regulatory reporting (GST, tax compliance)
- [ ] Machine learning forecasting
- [ ] Real-time GL integration via webhooks

---

**End of Documentation**

For questions or issues, refer to the Django Admin console or check the system logs.

```
Location: /var/www/tradifyerp/cash_management/
Python Package: cash_flow_models.py, cash_flow_views.py
Templates: cash_management/
Database: tradifyerp_db (PostgreSQL)
```
