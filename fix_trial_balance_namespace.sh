#!/bin/bash
# Fix trial balance templates to use accounting: namespace prefix

echo "=== Adding accounting: namespace to trial balance template URLs ==="

# Fix all trial balance template files
for file in \
    /var/www/tradifyerp/templates/accounting/trial_balance_dashboard.html \
    /var/www/tradifyerp/templates/accounting/trial_balance_report.html \
    /var/www/tradifyerp/templates/accounting/trial_balance_list.html \
    /var/www/tradifyerp/templates/accounting/trial_balance_comparison.html \
    /var/www/tradifyerp/templates/accounting/trial_balance_detail.html \
    /var/www/tradifyerp/templates/accounting/monthly_trial_balance_list.html
do
    if [ -f "$file" ]; then
        echo "Fixing: $file"
        # Add accounting: namespace to trial balance URL references that don't have it
        sed -i "s/{% url 'trial_balance_/{% url 'accounting:trial_balance_/g" "$file"
        sed -i "s/{% url 'monthly_trial_balance_/{% url 'accounting:monthly_trial_balance_/g" "$file"
        # Fix any double namespace issues
        sed -i "s/'accounting:accounting:/'accounting:/g" "$file"
    fi
done

echo ""
echo "=== Verification ==="
echo "Checking for trial balance URLs without namespace:"
grep -n "{% url 'trial_balance" /var/www/tradifyerp/templates/accounting/trial_balance*.html /var/www/tradifyerp/templates/accounting/monthly_trial_balance*.html 2>/dev/null | grep -v "accounting:" | head -10 || echo "All trial balance URLs have namespace prefix!"

echo ""
echo "Restarting Gunicorn..."
systemctl restart gunicorn
sleep 2

echo ""
echo "Testing trial balance list page..."
curl -s -o /dev/null -w "Trial Balance List: %{http_code}\n" http://localhost:8000/accounting/trial-balances/

echo "Done!"
