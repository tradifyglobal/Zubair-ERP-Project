#!/bin/bash
# Remove duplicate Trial Balance URL imports

TEMP_FILE="/tmp/urls_temp.py"

# Read file and keep everything except the last duplicate block
echo 'erp' | sudo -S bash << 'BASHEOF'
# Get total line count
TOTAL_LINES=$(wc -l </var/www/tradifyerp/accounting/urls.py)

# Calculate: remove last 8 lines (the duplicate block we added by mistake)
KEEP_LINES=$((TOTAL_LINES - 8))

# Use head to keep only first KEEP_LINES
head -n $KEEP_LINES /var/www/tradifyerp/accounting/urls.py > /tmp/urls_fixed.py

# Replace original file
mv /tmp/urls_fixed.py /var/www/tradifyerp/accounting/urls.py
chown www-data:www-data /var/www/tradifyerp/accounting/urls.py

echo "✓ Duplicate URLs removed"
echo "✓ File ownership reset to www-data"
BASHEOF
