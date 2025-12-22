-- Check for any audit logs or recent activity around these stakeholders
\echo 'Checking recent activity in the system:'

-- Check if there are audit logs for these stakeholders
\echo 'Checking for any audit logs:'
SELECT 
    table_name,
    COUNT(*) as log_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND (table_name LIKE '%audit%' OR table_name LIKE '%log%' OR table_name LIKE '%history%')
GROUP BY table_name;

-- Check for any failed transactions or incomplete records
\echo 'Checking for incomplete contribution records (NULL values, etc.):'
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.created_at,
    cc.updated_at
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.amount IS NULL 
   OR cc.status IS NULL 
   OR cc.stakeholder_id IN (3, 7, 18)
   OR cc.created_at >= '2025-12-15'
ORDER BY cc.created_at DESC;

-- Check what entity is currently active/selected
\echo 'Checking current entity status:'
SELECT 
    id, 
    name, 
    code, 
    is_active, 
    created_at 
FROM accounting_entity 
ORDER BY is_active DESC, id;

-- Check recent contributions (last 10)
\echo 'Recent contributions in the system (last 10):'
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    e.name as entity_name,
    cc.created_at
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
LEFT JOIN accounting_entity e ON cc.entity_id = e.id
ORDER BY cc.created_at DESC
LIMIT 10;