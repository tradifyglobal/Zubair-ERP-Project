# ERP Cash/Bank Receipt Workflow - Implementation Checklist

## Overview
Complete implementation of a 7-step ERP workflow for Cash and Bank Receipts with proper authorization hierarchy, GL posting, financial reporting, and audit trails.

---

## Phase 1: Database & Models ✅ (Current)

### Models Already Implemented ✅
- [x] `CashReceiptLine` - with workflow_status (DRAFT → APPROVED → AUTHORIZED)
- [x] `BankReceiptLine` - with workflow_status
- [x] `CashPaymentLine` - with workflow_status
- [x] `BankPaymentLine` - with workflow_status
- [x] `LedgerEntry` - GL posting with is_posted flag
- [x] `CapitalContribution` - auto-created from receipts
- [x] `Stakeholder` - shareholder master
- [x] `AuditLog` - compliance tracking
- [x] `Entity` - business unit segregation

### New Models to Add ❌
- [ ] **ShareholderInvestmentRegister** (Sub-ledger)
  - File: `MODELS_SHAREHOLDER_INVESTMENT_REGISTER.py`
  - Tracks all shareholder contributions by stakeholder
  - Links to source receipt (CashReceiptLine/BankReceiptLine)
  - Status tracking (PENDING, COMPLETED, REVERSED, CANCELLED)
  
- [ ] **ShareholderInvestmentSummary** (Cached)
  - Performance optimization for reporting
  - Denormalized totals by stakeholder

### Database Migration Required
```bash
python manage.py makemigrations accounting
python manage.py migrate accounting
```

**Create Migration File:**
```
TradifyERP/accounting/migrations/00XX_add_shareholder_investment_register.py

Operations:
- Create ShareholderInvestmentRegister table
- Create ShareholderInvestmentSummary table
- Add indexes: (entity, stakeholder), (entity, status)
```

---

## Phase 2: Views & API Endpoints

### Existing Workflow Views ✅
- [x] `CashReceiptApprovalView` (POST /approve/)
- [x] `CashReceiptAuthorizationView` (POST /authorize/)
- [x] `CashReceiptRejectView` (POST /reject/)
- [x] Similar for Bank/Payment transactions

### New Reporting Views to Add ❌
- [ ] **ShareholderInvestmentRegisterListView**
  - File: `VIEWS_SHAREHOLDER_INVESTMENT_REPORTS.py`
  - List all investments with filtering
  - URL: `/accounting/shareholder-investments/`
  
- [ ] **ShareholderInvestmentReportView**
  - Comprehensive summary report
  - Summary statistics, by type, by status, monthly trends
  - URL: `/accounting/shareholder-investment-report/`
  
- [ ] **ShareholderCapitalStatusView**
  - Dashboard of capital contributions only
  - URL: `/accounting/shareholder-capital-status/`
  
- [ ] **ShareholderInvestmentAuditTrailView**
  - Detailed audit trail for specific investment
  - Timeline visualization

### URL Configuration Required
```python
# accounting/urls.py

urlpatterns = [
    # ... existing URLs ...
    
    # NEW: Shareholder Investment Reporting
    path('shareholder-investments/', 
         ShareholderInvestmentRegisterListView.as_view(), 
         name='shareholder_investment_register'),
    
    path('shareholder-investment-report/', 
         ShareholderInvestmentReportView.as_view(), 
         name='shareholder_investment_report'),
    
    path('shareholder-capital-status/', 
         ShareholderCapitalStatusView.as_view(), 
         name='shareholder_capital_status'),
    
    path('shareholder-investment/<int:pk>/audit/', 
         ShareholderInvestmentAuditTrailView.as_view(), 
         name='shareholder_investment_audit'),
]
```

---

## Phase 3: Signal Handlers

### Signal to Add: Auto-create Investment Register Entries

File: `SIGNALS_INVESTMENT_REGISTER_UPDATES.py`

When `CashReceiptLine` or `BankReceiptLine` workflow_status → 'AUTHORIZED':
1. Auto-create entry in `ShareholderInvestmentRegister`
2. Link to source receipt
3. Update `ShareholderInvestmentSummary` cache
4. Set status to 'COMPLETED'

**Implementation:**
```python
@receiver(post_save, sender='accounting.CashReceiptLine')
def update_investment_register_on_cash_receipt_authorization(sender, instance, **kwargs):
    """
    Triggers when CashReceiptLine.workflow_status → AUTHORIZED
    Creates ShareholderInvestmentRegister entry
    """
```

### Register Signals

In `accounting/apps.py`:
```python
class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'
    
    def ready(self):
        import accounting.signals  # Import signal handlers
```

---

## Phase 4: Templates

### New Templates to Create

#### 1. Shareholder Investment Register List
- File: `shareholder_investment_register_list.html`
- Features:
  - Pagination (50 per page)
  - Filtering by shareholder, type, status, date range
  - Quick stats cards (total, pending, by type)
  - Action buttons to view detail/audit trail

#### 2. Shareholder Investment Report (Summary)
- File: `shareholder_investment_report.html`
  - **Status:** Partially created (`TEMPLATE_SHAREHOLDER_INVESTMENT_REPORT.html`)
- Features:
  - Summary cards (total received, pending, shareholders count)
  - Status breakdown table (completed, pending, cancelled)
  - By investment type table
  - Shareholder summary with totals and averages
  - Recent investments list
  - Pending authorizations list

#### 3. Shareholder Capital Status Dashboard
- File: `shareholder_capital_status.html`
- Features:
  - Summary of CAPITAL investment type only
  - Pie chart by shareholder
  - Contribution timeline
  - Capital contributor list with totals

#### 4. Audit Trail Timeline
- File: `shareholder_investment_audit_trail.html`
- Features:
  - Vertical timeline of all actions
  - Approvers, timestamps, status changes
  - GL entries linked to investment
  - Document attachments

### Permission Tags in Templates
```django
{% if perms.accounting.view_sharehoiderinvestmentregister %}
    <!-- Show report -->
{% endif %}
```

---

## Phase 5: Permissions & Security

### Permission Requirements

```python
# accounting/models.py - Meta.permissions

class ShareholderInvestmentRegister(models.Model):
    class Meta:
        permissions = [
            ('view_sharehoiderinvestmentregister', 'Can view shareholder investment register'),
            ('export_sharehoiderinvestmentregister', 'Can export shareholder investment data'),
        ]
```

### Role-based Access Control

```
┌─────────────────────────────────────────────┐
│ Finance Clerk (Maker)                       │
├─────────────────────────────────────────────┤
│ ✓ Create CRV/BRV (DRAFT)                   │
│ ✓ Submit for approval                       │
│ ✗ Cannot approve or authorize               │
│ ✓ View shareholder investment register      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Finance Manager (Checker)                   │
├─────────────────────────────────────────────┤
│ ✓ Approve transactions (DRAFT → APPROVED)   │
│ ✓ Add approval notes/comments               │
│ ✗ Cannot authorize (post GL)                │
│ ✓ View full shareholder reports             │
│ ✓ Export data                               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ CFO / Finance Head (Authorizer)             │
├─────────────────────────────────────────────┤
│ ✓ Authorize & post GL (APPROVED → AUTH)    │
│ ✓ Reject any transaction                    │
│ ✓ View audit trails                         │
│ ✓ Approve reversals                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Auditor / Compliance                        │
├─────────────────────────────────────────────┤
│ ✓ View all reports (read-only)             │
│ ✓ Access audit trail                        │
│ ✓ Export data                               │
│ ✗ Cannot modify or approve                  │
└─────────────────────────────────────────────┘
```

### Permission Django Groups Setup

```python
# Create in Django admin or management command
groups = {
    'Finance Clerk': ['add_cashreceiptline', 'change_cashreceiptline', 'view_sharehoiderinvestmentregister'],
    'Finance Manager': ['approve_cashreceiptline', 'view_sharehoiderinvestmentregister', 'export_sharehoiderinvestmentregister'],
    'Finance Head': ['authorize_cashreceiptline', 'view_auditlog', 'view_sharehoiderinvestmentregister'],
    'Auditor': ['view_sharehoiderinvestmentregister', 'view_auditlog', 'export_sharehoiderinvestmentregister'],
}
```

---

## Phase 6: Testing Checklist

### Unit Tests
- [ ] ShareholderInvestmentRegister auto-creation on receipt authorization
- [ ] Sum calculations (total, pending, by type)
- [ ] Status transitions (DRAFT → APPROVED → AUTHORIZED)
- [ ] GL entry creation verification
- [ ] Stakeholder linking

### Integration Tests
- [ ] End-to-end workflow:
  - Create CRV → Submit → Approve → Authorize
  - Verify GL entries created
  - Verify investment register populated
  - Verify audit trail logged
  
- [ ] Multi-shareholder scenario:
  - 3 shareholders with different contributions
  - Verify totals calculated correctly
  - Verify report summarization
  
- [ ] Edge cases:
  - Missing stakeholder
  - Duplicate entries
  - Currency conversions
  - Reversals/cancellations

### UI/UX Tests
- [ ] Approval workflow UI responsive
- [ ] Report loading time < 3 seconds
- [ ] Export functionality (CSV/PDF)
- [ ] Mobile responsiveness
- [ ] Permission-based button visibility

### Load Tests
- [ ] 1000+ investors
- [ ] 100,000+ transaction records
- [ ] Report generation performance

---

## Phase 7: Deployment Steps

### Step 1: Database Migration
```bash
cd /var/www/tradifyerp/TradifyERP

# Create migration
python manage.py makemigrations accounting

# Apply migration
python manage.py migrate accounting
```

### Step 2: Copy New Files
```bash
# Models
cp MODELS_SHAREHOLDER_INVESTMENT_REGISTER.py accounting/models.py (append)

# Views
cp VIEWS_SHAREHOLDER_INVESTMENT_REPORTS.py accounting/views.py (append/new file)

# Signals
cp SIGNALS_INVESTMENT_REGISTER_UPDATES.py accounting/signals.py (append)

# Templates
mkdir -p accounting/templates/accounting
cp TEMPLATE_SHAREHOLDER_INVESTMENT_REPORT.html accounting/templates/accounting/
```

### Step 3: Update URL Configuration
```bash
# Edit accounting/urls.py
# Add new URL patterns from Phase 2
```

### Step 4: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 5: Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx  # if applicable
```

### Step 6: Verify Deployment
```bash
# Check migration status
python manage.py showmigrations accounting

# Test signal handlers
python manage.py shell
>>> from accounting.models import CashReceiptLine, ShareholderInvestmentRegister
>>> # Create test receipt and authorize it
>>> # Verify investment register entry created
```

---

## Phase 8: Financial Reporting Integration

### Balance Sheet Integration
Update `views_dashboard.py` to include Shareholder Equity:

```python
# In Balance Sheet report
equity_section = {
    'Share Capital': {
        'balance': ShareholderInvestmentRegister.objects.filter(
            entity=entity,
            status='COMPLETED'
        ).aggregate(Sum('amount_company_currency'))
    }
}
```

### Cash Flow Statement
Add shareholder contributions to Operating/Financing Activities:

```python
shareholder_inflows = ShareholderInvestmentRegister.objects.filter(
    entity=entity,
    investment_date__gte=period_start,
    investment_date__lte=period_end,
    status='COMPLETED'
).aggregate(Sum('amount_company_currency'))
```

### GL Dashboard Enhancement
Add shareholder investment metrics:
- Total received vs. expected (if target set)
- Pending authorizations
- Top contributors this period

---

## Phase 9: Audit & Compliance

### Audit Trail Completeness ✅
- [x] All state changes logged (DRAFT → APPROVED → AUTH)
- [x] Approval comments tracked
- [x] GL entries created timestamp
- [x] User ID of approver captured

### Compliance Reports to Generate
- [ ] Investment authorization timeline
- [ ] Approvers' activity log (who approved/authorized what)
- [ ] Reconciliation: Receipts vs GL entries
- [ ] Missing approvals (stuck in PENDING)

### Digital Signature Support (Optional)
- [ ] Capture e-signature or digital sign-off
- [ ] PDF with signatures
- [ ] Timestamp verification

---

## Documentation & Training

### User Documentation
- [ ] Quick start guide (5-page PDF)
- [ ] Workflow overview diagram
- [ ] Video tutorials (create → approve → authorize)

### Admin Documentation
- [ ] System setup guide
- [ ] Permission configuration
- [ ] Report customization

### Developer Documentation
- [ ] API documentation
- [ ] Database schema diagram
- [ ] Signal/event flow diagram

---

## Summary & Current Status

### ✅ Completed (Already in Production)
- Workflow status tracking (DRAFT/APPROVED/AUTHORIZED)
- GL entry creation on authorization
- Auto-creation of CapitalContribution
- Audit logging
- Cash receipt and bank receipt workflows

### 🔄 In Progress
- ShareholderInvestmentRegister model definition
- Reporting views
- Signal handlers for auto-population

### ⏳ Todo
- Database migration
- Template creation
- Permission setup
- Testing
- Deployment
- Financial reporting integration
- Compliance reporting

### Quick Implementation Order
1. Create models & migration
2. Add views & URL configuration
3. Implement signals
4. Create templates
5. Set up permissions
6. Test end-to-end
7. Deploy to production
8. Add financial reporting
9. Create audit reports

---

## Success Criteria

- [x] All 7 workflow steps functional
- [x] GL entries automatically created and posted
- [x] Audit trail complete and accessible
- [ ] Shareholder investment reports working
- [ ] Financial statements reflecting contributions
- [ ] Approval workflow tested with 3+ users
- [ ] Performance < 3s for 100K records
- [ ] All permissions enforced correctly
- [ ] Audit trail exportable
- [ ] Dashboard updated with new metrics
