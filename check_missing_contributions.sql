-- Check for missing capital contributions on Dec 15, 2025
\echo 'Checking contributions on Dec 15, 2025:'
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.contribution_date = '2025-12-15'
ORDER BY cc.id;

\echo ''
\echo 'Checking by stakeholder names:'

-- Check for Syed Safi
\echo 'Syed Safi contributions:'
SELECT 
    cc.id,
    cc.contribution_date,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE s.first_name ILIKE '%Syed%' AND s.last_name ILIKE '%Safi%'
ORDER BY cc.contribution_date DESC
LIMIT 5;

-- Check for Burhanuddin Shaik
\echo 'Burhanuddin Shaik contributions:'
SELECT 
    cc.id,
    cc.contribution_date,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE s.first_name ILIKE '%Burhanuddin%' AND s.last_name ILIKE '%Shaik%'
ORDER BY cc.contribution_date DESC
LIMIT 5;

-- Check for Ansaar Mohammed
\echo 'Ansaar Mohammed contributions:'
SELECT 
    cc.id,
    cc.contribution_date,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE s.first_name ILIKE '%Ansaar%' AND s.last_name ILIKE '%Mohammed%'
ORDER BY cc.contribution_date DESC
LIMIT 5;

\echo ''
\echo 'Checking by reference numbers:'

-- Check for specific reference numbers
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.reference_number ILIKE '%3000-16%' 
   OR cc.reference_number ILIKE '%3000-18%' 
   OR cc.reference_number ILIKE '%3000-09%'
ORDER BY cc.id;

\echo ''
\echo 'Checking by amounts (5000 and 6000) in December 2025:'

-- Check for specific amounts in December 2025
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE (cc.amount = 5000 OR cc.amount = 6000)
  AND cc.contribution_date >= '2025-12-01'
  AND cc.contribution_date <= '2025-12-31'
ORDER BY cc.contribution_date DESC, cc.id;

\echo ''
\echo 'Status distribution in the system:'

-- Check status distribution
SELECT 
    status,
    COUNT(*) as count
FROM accounting_capitalcontribution
GROUP BY status
ORDER BY count DESC;

\echo ''
\echo 'Workflow status distribution:'

-- Check workflow status distribution  
SELECT 
    workflow_status,
    COUNT(*) as count
FROM accounting_capitalcontribution
GROUP BY workflow_status
ORDER BY count DESC;