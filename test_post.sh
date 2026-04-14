#!/bin/bash
# Get CSRF token from the page
TOKEN=$(curl -s http://192.168.20.10/accounting/cash-payments/create/ | grep 'csrfmiddlewaretoken' | head -1 | sed 's/.*value="\([^"]*\)".*/\1/')

echo "CSRF Token: $TOKEN"

# Try to POST a payment
curl -X POST http://192.168.20.10/accounting/cash-payments/create/ \
  -H "X-CSRFToken: $TOKEN" \
  -d "date=2026-04-08&description=Test+Payment&debit_amount=1000&credit_amount=1000&credit_account=92070&csrfmiddlewaretoken=$TOKEN" \
  -s -i -o /tmp/response.txt

cat /tmp/response.txt | head -50
