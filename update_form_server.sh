#!/bin/bash

# Create sed command to update cash_forms.py on the server
ssh root@192.168.20.10 << 'EOF'

# Backup the original file
cp /var/www/tradifyerp/accounting/cash_forms.py /var/www/tradifyerp/accounting/cash_forms.py.bak

# Update the main_account label
sed -i "s/label='Main Account'/label='Debit Account'/g" /var/www/tradifyerp/accounting/cash_forms.py

# Add disabled to the account widget
sed -i "/id_account.*,$/a\\                'disabled': True," /var/www/tradifyerp/accounting/cash_forms.py

# Verify the changes
echo "=== Verifying changes ==="
grep -n "label='Debit Account'" /var/www/tradifyerp/accounting/cash_forms.py | head -1
grep -n "'disabled': True," /var/www/tradifyerp/accounting/cash_forms.py | head -2

# Clear Python cache
find /var/www/tradifyerp -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Restart Gunicorn
systemctl restart gunicorn
sleep 3

echo "Done!"
EOF
