#!/bin/bash
# Trial Balance Deployment Verification Script

cd /var/www/tradifyerp
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=TradifyERP.settings_production

echo "=== TRIAL BALANCE DEPLOYMENT VERIFICATION ==="
echo ""

# Test 1: Models Import
echo "Test 1: Testing TrialBalance model import..."
python -c "from accounting.models import TrialBalance; print('  ✓ TrialBalance model accessible')" 2>&1
if [ $? -eq 0 ]; then
  echo "  Status: PASSED"
else
  echo "  Status: FAILED"
  exit 1
fi
echo ""

# Test 2: Views Import  
echo "Test 2: Testing TrialBalance views import..."
python -c "from accounting.views_trial_balance import TrialBalanceListView; print('  ✓ Views imported successfully')" 2>&1
if [ $? -eq 0 ]; then
  echo "  Status: PASSED"
else
  echo "  Status: FAILED"
  exit 1
fi
echo ""

# Test 3: Signals Import
echo "Test 3: Testing TrialBalance signals import..."
python -c "from accounting.signals_trial_balance import auto_generate_trial_balance_on_posting; print('  ✓ Signals imported successfully')" 2>&1
if [ $? -eq 0 ]; then
  echo "  Status: PASSED"
else
  echo "  Status: FAILED"
  exit 1
fi
echo ""

# Test 4: URLs Import
echo "Test 4: Testing TrialBalance URLs import..."
python -c "from accounting.urls_trial_balance import urlpatterns; print(f'  ✓ URLs imported successfully ({len(urlpatterns)} patterns)')" 2>&1
if [ $? -eq 0 ]; then
  echo "  Status: PASSED"
else
  echo "  Status: FAILED"
  exit 1
fi
echo ""

# Test 5: Database Connectivity
echo "Test 5: Testing database connectivity..."
python -c "from django.db import connection; connection.ensure_connection(); print('  ✓ Database connection successful')" 2>&1
if [ $? -eq 0 ]; then
  echo "  Status: PASSED"
else
  echo "  Status: FAILED"
  exit 1
fi
echo ""

# Test 6: TrialBalance Table Exists
echo "Test 6: Testing TrialBalance table..."
python -c "from accounting.models import TrialBalance; count = TrialBalance.objects.count(); print(f'  ✓ TrialBalance table exists ({count} records)')" 2>&1
if [ $? -eq 0 ]; then
  echo "  Status: PASSED"
else
  echo "  Status: FAILED"
  exit 1
fi
echo ""

# Test 7: Check deployed template files
echo "Test 7: Checking deployed template files..."
TEMPLATE_COUNT=$(ls -1 /var/www/tradifyerp/templates/accounting/trial_balance*.html 2>/dev/null | wc -l)
if [ "$TEMPLATE_COUNT" -gt 0 ]; then
  echo "  ✓ Found $TEMPLATE_COUNT trial_balance template files"
  echo "  Status: PASSED"
else
  echo "  ✗ No trial_balance template files found"
  echo "  Status: FAILED"
  exit 1
fi
echo ""

echo "=== ALL VERIFICATION TESTS PASSED ✅ ==="
echo "Trial Balance system deployment verified successfully!"
echo ""
echo "Summary:"
echo "  • Models: ✓ Accessible"
echo "  • Views: ✓ Loaded"
echo "  • Signals: ✓ Registered"
echo "  • URLs: ✓ Configured"
echo "  • Database: ✓ Connected"
echo "  • Tables: ✓ Created"
echo "  • Templates: ✓ Deployed ($TEMPLATE_COUNT files)"
