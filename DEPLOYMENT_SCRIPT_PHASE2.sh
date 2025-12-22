#!/bin/bash
# ERP Workflow Phase 2 Deployment Script
# This script deploys the ShareholderInvestmentRegister models and views
# to the production server

set -e  # Exit on error

PROD_SERVER="192.168.2.69"
PROD_USER="zubair"
PROD_PASSWORD="erp"
SUDO_PASSWORD="erp"

DJANGO_PATH="/var/www/tradifyerp/TradifyERP"
ACCOUNTING_PATH="$DJANGO_PATH/accounting"

echo "=========================================="
echo "ERP Workflow Phase 2 Deployment"
echo "=========================================="
echo "Target: $PROD_SERVER"
echo "Django Path: $DJANGO_PATH"
echo ""

# Step 1: Backup current files
echo "[Step 1/6] Backing up current accounting files..."
ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER << 'EOF'
cd /var/www/tradifyerp/TradifyERP
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp accounting/models.py backups/$(date +%Y%m%d_%H%M%S)/
cp accounting/urls.py backups/$(date +%Y%m%d_%H%M%S)/
cp accounting/apps.py backups/$(date +%Y%m%d_%H%M%S)/
echo "Backup complete"
EOF

echo "✓ Backup created"
echo ""

# Step 2: Prepare model files
echo "[Step 2/6] Transferring model files..."

# Read the new models
NEW_MODELS=$(cat MODELS_SHAREHOLDER_INVESTMENT_REGISTER.py)

# Create a temporary Python script to append to models.py
ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER << 'EOF'
cd /var/www/tradifyerp/TradifyERP

# Check if models already have the new classes
if grep -q "class ShareholderInvestmentRegister" accounting/models.py; then
    echo "Models already present, skipping..."
else
    echo "Appending new models to accounting/models.py"
    # Add new models to the end of models.py
    cat >> accounting/models.py << 'MODELS_EOF'


# ========== NEW MODELS: SHAREHOLDER INVESTMENT REGISTER ==========

class ShareholderInvestmentRegister(models.Model):
    """
    Sub-ledger tracking all shareholder/stakeholder contributions to the entity.
    
    Provides:
    - Individual shareholder investment history
    - Contribution tracking by type (capital, loan, reinvested dividends)
    - Currency-wise breakdown with exchange rates
    - Status tracking (pending, completed, cancelled)
    
    Auto-populated from CashReceiptLine/BankReceiptLine when status→AUTHORIZED
    """
    
    INVESTMENT_TYPE_CHOICES = [
        ('CAPITAL', 'Capital Contribution'),
        ('LOAN', 'Shareholder Loan'),
        ('DIVIDEND_REINVESTMENT', 'Dividend Reinvestment'),
        ('OTHER', 'Other Investment'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REVERSED', 'Reversed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name='shareholder_investments'
    )
    
    stakeholder = models.ForeignKey(
        'Stakeholder',
        on_delete=models.PROTECT,
        related_name='investment_register'
    )
    
    investment_date = models.DateField(default=timezone.now, db_index=True)
    investment_type = models.CharField(
        max_length=25,
        choices=INVESTMENT_TYPE_CHOICES,
        default='CAPITAL'
    )
    
    amount_company_currency = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Amount in entity's company currency"
    )
    
    original_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        related_name='investments',
        null=True,
        blank=True
    )
    
    exchange_rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=1.0
    )
    
    source_cash_receipt = models.ForeignKey(
        'CashReceiptLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investment_register_entries'
    )
    
    source_bank_receipt = models.ForeignKey(
        'BankReceiptLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investment_register_entries'
    )
    
    gl_reference = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shareholder_investments_created'
    )
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-investment_date', '-created_date']
        indexes = [
            models.Index(fields=['entity', 'stakeholder', '-investment_date']),
            models.Index(fields=['entity', 'status', '-investment_date']),
        ]
        verbose_name_plural = 'Shareholder Investment Register'
    
    def __str__(self):
        return f"{self.stakeholder.name} - {self.investment_date} - {self.amount_company_currency}"


class ShareholderInvestmentSummary(models.Model):
    """Cached summary view for performance optimization."""
    
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    stakeholder = models.ForeignKey('Stakeholder', on_delete=models.CASCADE)
    
    total_contributions = models.DecimalField(max_digits=18, decimal_places=2)
    contribution_count = models.IntegerField()
    first_contribution_date = models.DateField(null=True, blank=True)
    last_contribution_date = models.DateField(null=True, blank=True)
    average_contribution = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    
    completed_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    cancelled_count = models.IntegerField(default=0)
    
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('entity', 'stakeholder')
        verbose_name_plural = 'Shareholder Investment Summaries'
    
    def __str__(self):
        return f"{self.stakeholder.name} - Total: {self.total_contributions}"

MODELS_EOF
    echo "✓ New models appended to accounting/models.py"
fi
EOF

echo "✓ Model files transferred"
echo ""

# Step 3: Create and run migration
echo "[Step 3/6] Running database migration..."
ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER << EOF
cd $DJANGO_PATH

# Make migrations
echo "Creating migrations..."
python manage.py makemigrations accounting

# Apply migrations
echo "Applying migrations..."
python manage.py migrate accounting

echo "✓ Migration complete"
EOF

echo "✓ Database migration complete"
echo ""

# Step 4: Update apps.py for signal registration
echo "[Step 4/6] Updating apps.py for signal handlers..."
ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER << 'EOF'
cd /var/www/tradifyerp/TradifyERP

# Check if ready() method has signals import
if ! grep -q "import accounting.signals" accounting/apps.py; then
    echo "Adding signal handler import to apps.py"
    
    # Find the ready method and add the import
    sed -i '/def ready(self):/a\        from . import signals' accounting/apps.py
    
    echo "✓ Signal handlers registered"
else
    echo "Signal handlers already registered"
fi
EOF

echo "✓ Signal handlers configured"
echo ""

# Step 5: Add URL patterns
echo "[Step 5/6] Adding URL patterns..."
ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER << 'EOF'
cd /var/www/tradifyerp/TradifyERP

# Check if shareholder investment URLs already exist
if ! grep -q "shareholder-investment" accounting/urls.py; then
    echo "Adding shareholder investment URL patterns"
    
    cat >> accounting/urls.py << 'URLS_EOF'

# Shareholder Investment Reporting URLs
from .views_reports import (
    ShareholderInvestmentRegisterListView,
    ShareholderInvestmentReportView,
    ShareholderCapitalStatusView,
    ShareholderInvestmentDetailView,
    ShareholderInvestmentAuditTrailView,
)

urlpatterns += [
    path('shareholder-investments/', 
         ShareholderInvestmentRegisterListView.as_view(), 
         name='shareholder_investment_register'),
    
    path('shareholder-investment-report/', 
         ShareholderInvestmentReportView.as_view(), 
         name='shareholder_investment_report'),
    
    path('shareholder-capital-status/', 
         ShareholderCapitalStatusView.as_view(), 
         name='shareholder_capital_status'),
    
    path('shareholder-investment/<int:pk>/', 
         ShareholderInvestmentDetailView.as_view(), 
         name='shareholder_investment_detail'),
    
    path('shareholder-investment/<int:pk>/audit/', 
         ShareholderInvestmentAuditTrailView.as_view(), 
         name='shareholder_investment_audit'),
]
URLS_EOF
    
    echo "✓ URL patterns added"
else
    echo "URL patterns already exist"
fi
EOF

echo "✓ URL configuration complete"
echo ""

# Step 6: Restart services
echo "[Step 6/6] Restarting services..."
ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER << 'EOF'
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

# Wait for service to start
sleep 2

# Check status
STATUS=$(sudo systemctl status gunicorn | grep "active (running)")
if [ -n "$STATUS" ]; then
    echo "✓ Gunicorn restarted successfully"
else
    echo "⚠ Gunicorn restart may have issues - checking logs"
    sudo systemctl status gunicorn
fi
EOF

echo "✓ Services restarted"
echo ""

echo "=========================================="
echo "✓ DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "Summary of Changes:"
echo "- Added ShareholderInvestmentRegister model"
echo "- Added ShareholderInvestmentSummary model"
echo "- Created database migration and applied it"
echo "- Registered signal handlers in apps.py"
echo "- Added URL patterns for shareholder reports"
echo "- Restarted Gunicorn service"
echo ""
echo "Next Steps:"
echo "1. Verify template files are in place"
echo "2. Copy SIGNALS_INVESTMENT_REGISTER_UPDATES.py to accounting/signals.py"
echo "3. Copy VIEWS_SHAREHOLDER_INVESTMENT_REPORTS.py to accounting/views_reports.py"
echo "4. Test end-to-end workflow"
echo ""
echo "To check migration status:"
echo "  ssh $PROD_USER@$PROD_SERVER 'cd $DJANGO_PATH && python manage.py showmigrations accounting'"
echo ""
