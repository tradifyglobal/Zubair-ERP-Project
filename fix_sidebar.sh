#!/bin/bash
# Fix sidebar.html to use trial_balance_list instead of trial-balance-list

sed -i 's/trial-balance-list/trial_balance_list/g' /var/www/tradifyerp/templates/partials/sidebar.html

echo "Fixed sidebar.html - verifying:"
grep 'trial.*balance' /var/www/tradifyerp/templates/partials/sidebar.html
