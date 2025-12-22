#!/bin/bash
# Deploy cash workflow URLs and restart

echo "Copying urls.py..."
sudo cp /tmp/accounting_urls.py /var/www/tradifyerp/accounting/urls.py

echo "Verifying cash_receipt_authorize URL..."
grep -n "cash_receipt_authorize" /var/www/tradifyerp/accounting/urls.py

echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

sleep 3

echo "Testing cash receipts page..."
curl -s -o /dev/null -w "Cash Receipts Page: %{http_code}\n" http://localhost:8000/accounting/cash-receipts/

echo "Done!"
