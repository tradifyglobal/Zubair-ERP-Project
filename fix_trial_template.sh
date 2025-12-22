#!/bin/bash
# Fix trial balance template - remove Actions column

# Download production template 
cp /var/www/tradifyerp/templates/accounting/trial_balance_list.html /tmp/tb.html

# Remove Actions header (around line 113)
sed -i '/<th class="text-end pe-4">Actions<\/th>/d' /tmp/tb.html

# Remove action buttons td
sed -i '/trial_balance_detail\|trial_balance_report\|trial_balance_export/,+10d' /tmp/tb.html

# Update colspan
sed -i 's/colspan="8"/colspan="7"/g' /tmp/tb.html

# Deploy
sudo cp /tmp/tb.html /var/www/tradifyerp/templates/accounting/trial_balance_list.html
sudo systemctl restart gunicorn

echo "✓ Trial balance template fixed"
