#!/bin/bash
# Comprehensive fix for trial balance URL references

echo "=== Fixing Trial Balance URL References ==="

# Fix all template files
for file in \
    /var/www/tradifyerp/templates/partials/sidebar.html \
    /var/www/tradifyerp/templates/partials/hori-sidebar.html \
    /var/www/tradifyerp/accounting/templates/accounting/dashboard.html \
    /var/www/tradifyerp/accounting/templates/accounting/dashboard_simple.html \
    /var/www/tradifyerp/accounting/templates/accounting/gl_dashboard.html
do
    if [ -f "$file" ]; then
        echo "Fixing: $file"
        sed -i 's/trial-balance-dashboard/trial_balance_dashboard/g' "$file"
        sed -i 's/trial-balance-list/trial_balance_list/g' "$file"
        sed -i 's/trial-balance-detail/trial_balance_detail/g' "$file"
        sed -i 's/trial-balance-report/trial_balance_report/g' "$file"
        sed -i 's/trial-balance-comparison/trial_balance_comparison/g' "$file"
        sed -i 's/trial-balance-export/trial_balance_export/g' "$file"
        sed -i 's/monthly-trial-balance-list/monthly_trial_balance_list/g' "$file"
    fi
done

echo ""
echo "=== Verification ===" 
echo "Checking for any remaining hyphens in trial balance URLs:"
grep -r "trial-balance" /var/www/tradifyerp/templates/ /var/www/tradifyerp/accounting/templates/ 2>/dev/null | grep -v ".pyc" | head -20 || echo "No hyphenated trial-balance URLs found!"

echo ""
echo "Restarting Gunicorn..."
systemctl restart gunicorn

echo "Done!"
