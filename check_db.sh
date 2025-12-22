#!/bin/bash
# Direct PostgreSQL query to check the actual values

PGPASSWORD="Tradify@PostgreSQL2024" psql -h localhost -U tradifyerp_user -d tradifyerp_db -c "
SELECT 
    cc.id,
    cc.status,
    cc.amount,
    cc.amount_company_currency,
    c.code as currency,
    s.full_name
FROM accounting_capitalcontribution cc
LEFT JOIN accounting_currency c ON cc.currency_id = c.id
LEFT JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.status = 'PENDING'
AND cc.entity_id = 2
ORDER BY cc.id DESC
LIMIT 10;
"

echo "===== TOTALS ====="
PGPASSWORD="Tradify@PostgreSQL2024" psql -h localhost -U tradifyerp_user -d tradifyerp_db -c "
SELECT 
    SUM(amount) as total_original,
    SUM(amount_company_currency) as total_company_currency
FROM accounting_capitalcontribution
WHERE status = 'PENDING'
AND entity_id = 2;
"
