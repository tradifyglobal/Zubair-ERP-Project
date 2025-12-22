-- Check if the mentioned stakeholders exist in the stakeholder table
\echo 'Checking if stakeholders exist in the system:'

\echo 'All stakeholders with "Syed" in first name:'
SELECT id, first_name, last_name, full_name FROM accounting_stakeholder 
WHERE first_name ILIKE '%Syed%' OR last_name ILIKE '%Syed%';

\echo 'All stakeholders with "Safi" in name:'
SELECT id, first_name, last_name, full_name FROM accounting_stakeholder 
WHERE first_name ILIKE '%Safi%' OR last_name ILIKE '%Safi%';

\echo 'All stakeholders with "Burhanuddin" in name:'
SELECT id, first_name, last_name, full_name FROM accounting_stakeholder 
WHERE first_name ILIKE '%Burhanuddin%' OR last_name ILIKE '%Burhanuddin%';

\echo 'All stakeholders with "Shaik" in name:'
SELECT id, first_name, last_name, full_name FROM accounting_stakeholder 
WHERE first_name ILIKE '%Shaik%' OR last_name ILIKE '%Shaik%';

\echo 'All stakeholders with "Ansaar" in name:'
SELECT id, first_name, last_name, full_name FROM accounting_stakeholder 
WHERE first_name ILIKE '%Ansaar%' OR last_name ILIKE '%Ansaar%';

\echo 'All stakeholders with "Mohammed" in name:'
SELECT id, first_name, last_name, full_name FROM accounting_stakeholder 
WHERE first_name ILIKE '%Mohammed%' OR last_name ILIKE '%Mohammed%';

\echo ''
\echo 'Total stakeholders in the system:'
SELECT COUNT(*) as total_stakeholders FROM accounting_stakeholder;

\echo ''
\echo 'All existing stakeholders:'
SELECT id, first_name, last_name, full_name FROM accounting_stakeholder 
ORDER BY id;