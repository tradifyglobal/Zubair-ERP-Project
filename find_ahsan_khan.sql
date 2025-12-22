-- Find Ahsan Ali Khan and create the missing capital contribution

\echo 'Looking for Ahsan Ali Khan in stakeholders:';
SELECT id, first_name, last_name FROM accounting_stakeholder 
WHERE first_name ILIKE '%Ahsan%' OR last_name ILIKE '%Khan%' 
ORDER BY id;

\echo 'All stakeholders with Khan in name:';
SELECT id, first_name, last_name FROM accounting_stakeholder 
WHERE last_name ILIKE '%Khan%'
ORDER BY id;