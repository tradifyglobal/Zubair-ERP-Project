#!/bin/bash
# Trial Balance Deployment Verification Script
# Run this on production to verify deployment status

echo "================================"
echo "Trial Balance Deployment Check"
echo "================================"
echo ""

# Check Gunicorn status
echo "1. Checking Gunicorn status..."
systemctl is-active gunicorn
if [ $? -eq 0 ]; then
    echo "   ✅ Gunicorn is RUNNING"
else
    echo "   ❌ Gunicorn is NOT running"
fi
echo ""

# Check views file exists and has correct imports
echo "2. Checking views_trial_balance.py..."
if [ -f /var/www/tradifyerp/accounting/views_trial_balance.py ]; then
    echo "   ✅ File exists"
    
    # Check for bad imports
    if grep -q "TrialBalanceLine\|MonthlyTrialBalance\|GLAccount\|SessionEntityMixin" /var/www/tradifyerp/accounting/views_trial_balance.py; then
        echo "   ❌ WARNING: Bad imports found!"
    else
        echo "   ✅ No bad imports detected"
    fi
    
    # Count view classes
    count=$(grep -c "^class.*View" /var/www/tradifyerp/accounting/views_trial_balance.py)
    echo "   ✅ Found $count View classes"
else
    echo "   ❌ File NOT found"
fi
echo ""

# Check urls file
echo "3. Checking urls_trial_balance.py..."
if [ -f /var/www/tradifyerp/accounting/urls_trial_balance.py ]; then
    echo "   ✅ File exists"
    
    if grep -q "TrialBalanceGenerateView" /var/www/tradifyerp/accounting/urls_trial_balance.py; then
        echo "   ❌ WARNING: Bad view import still present"
    else
        echo "   ✅ No bad view imports"
    fi
else
    echo "   ❌ File NOT found"
fi
echo ""

# Check templates
echo "4. Checking templates..."
template_dir="/var/www/tradifyerp/templates/accounting"
count=$(ls $template_dir/trial_balance_*.html 2>/dev/null | wc -l)
echo "   ✅ Found $count Trial Balance templates"
echo ""

# Check recent Gunicorn errors
echo "5. Recent Gunicorn logs (errors only)..."
journalctl -u gunicorn -n 20 --no-pager 2>/dev/null | grep -i "error\|traceback" || echo "   ✅ No recent errors found"
echo ""

# Test endpoint
echo "6. Testing Trial Balance Dashboard endpoint..."
response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8000/accounting/trial-balance-dashboard/)
if [ "$response" == "200" ]; then
    echo "   ✅ Dashboard endpoint responds with 200 OK"
elif [ "$response" == "302" ]; then
    echo "   ⚠️  Endpoint redirects (may be login redirect) - 302"
elif [ "$response" == "500" ]; then
    echo "   ❌ Server error - 500"
else
    echo "   ⚠️  Response code: $response"
fi
echo ""

# Check database connectivity
echo "7. Checking database connectivity..."
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()
from accounting.models import TrialBalance, Account, Entity
try:
    tb_count = TrialBalance.objects.count()
    print(f'   ✅ Database connected')
    print(f'      - Trial Balances in DB: {tb_count}')
    print(f'      - Entities in DB: {Entity.objects.count()}')
    print(f'      - Accounts in DB: {Account.objects.count()}')
except Exception as e:
    print(f'   ❌ Database error: {e}')
" 2>/dev/null || echo "   ⚠️  Could not run Django check"
echo ""

echo "================================"
echo "Verification Complete"
echo "================================"
