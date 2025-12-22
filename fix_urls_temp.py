with open('/var/www/tradifyerp/accounting/urls.py', 'r') as f:
    content = f.read()

old_line = "    path('trial-balances/', TrialBalanceListView.as_view(), name='trial_balance_list'),"
new_line = "    # path('trial-balances/', TrialBalanceListView.as_view(), name='trial_balance_list'),"

if old_line in content:
    content = content.replace(old_line, new_line)
    with open('/var/www/tradifyerp/accounting/urls.py', 'w') as f:
        f.write(content)
    print('SUCCESS: Commented out old trial-balances route')
else:
    print('WARNING: Could not find exact line to comment')
