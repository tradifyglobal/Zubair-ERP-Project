-- Check entity currency settings and available currencies
\echo 'Entity currency settings:';
SELECT 
    e.id, 
    e.name, 
    e.code, 
    c.code as company_currency,
    c.symbol,
    c.is_default
FROM accounting_entity e 
LEFT JOIN accounting_currency c ON e.company_currency_id = c.id 
ORDER BY e.id;

\echo 'All available currencies:';
SELECT 
    id,
    code,
    name,
    symbol,
    is_default,
    exchange_rate
FROM accounting_currency 
ORDER BY is_default DESC, code;