-- Check contributions for specific stakeholders regardless of workflow status or entity
\echo 'Checking ALL contributions for specific stakeholders (regardless of status/entity):'

-- Check Syed Safi (ID: 3)
\echo 'All contributions for Syed Safi (ID: 3):'
SELECT 
    cc.id,
    cc.contribution_date,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.entity_id,
    e.name as entity_name
FROM accounting_capitalcontribution cc
LEFT JOIN accounting_entity e ON cc.entity_id = e.id
WHERE cc.stakeholder_id = 3
ORDER BY cc.contribution_date DESC;

-- Check Burhanuddin Shaik (ID: 18)
\echo 'All contributions for Burhanuddin Shaik (ID: 18):'
SELECT 
    cc.id,
    cc.contribution_date,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.entity_id,
    e.name as entity_name
FROM accounting_capitalcontribution cc
LEFT JOIN accounting_entity e ON cc.entity_id = e.id
WHERE cc.stakeholder_id = 18
ORDER BY cc.contribution_date DESC;

-- Check Ansaar Mohammed (ID: 7)
\echo 'All contributions for Ansaar Mohammed (ID: 7):'
SELECT 
    cc.id,
    cc.contribution_date,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.entity_id,
    e.name as entity_name
FROM accounting_capitalcontribution cc
LEFT JOIN accounting_entity e ON cc.entity_id = e.id
WHERE cc.stakeholder_id = 7
ORDER BY cc.contribution_date DESC;

\echo ''
\echo 'Checking all entities in the system:'
SELECT id, name, code, is_active FROM accounting_entity ORDER BY id;

\echo ''
\echo 'Checking all contributions on Dec 15, 2025 (any status, any entity):'
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.entity_id,
    e.name as entity_name
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
LEFT JOIN accounting_entity e ON cc.entity_id = e.id
WHERE cc.contribution_date = '2025-12-15'
ORDER BY cc.id;

\echo ''
\echo 'Checking contributions with reference numbers 3000-16, 3000-18, 3000-09 (any entity, any status):'
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.entity_id,
    e.name as entity_name
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
LEFT JOIN accounting_entity e ON cc.entity_id = e.id
WHERE cc.reference_number IN ('3000-16', '3000-18', '3000-09')
   OR cc.reference_number LIKE '%3000-16%'
   OR cc.reference_number LIKE '%3000-18%'  
   OR cc.reference_number LIKE '%3000-09%'
ORDER BY cc.id;