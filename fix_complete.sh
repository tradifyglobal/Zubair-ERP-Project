#!/bin/bash
# Complete fix for ALL trial balance URL references

echo "=== Fixing ALL Trial Balance URL References ==="

# Fix all templates in both locations
find /var/www/tradifyerp/templates/ /var/www/tradifyerp/accounting/templates/ -type f -name "*.html" -exec sed -i \
    -e 's/trial-balance-dashboard/trial_balance_dashboard/g' \
    -e 's/trial-balance-monthly/trial_balance_monthly/g' \
    -e 's/trial-balances/trial_balance_list/g' \
    -e 's/trial-balance-list/trial_balance_list/g' \
    -e 's/trial-balance-detail/trial_balance_detail/g' \
    -e 's/trial-balance-report/trial_balance_report/g' \
    -e 's/trial-balance-comparison/trial_balance_comparison/g' \
    -e 's/trial-balance-export/trial_balance_export/g' \
    -e 's/monthly-trial-balances/monthly_trial_balance_list/g' \
    -e 's/monthly-trial-balance-list/monthly_trial_balance_list/g' \
    {} \;

echo "Fixed all template files!"
echo ""
echo "Restarting Gunicorn..."
systemctl restart gunicorn
sleep 2

echo ""
echo "Testing..."
curl -s -o /dev/null -w "Dashboard status: %{http_code}\n" http://localhost:8000/accounting/dashboard/

echo "Done!"
