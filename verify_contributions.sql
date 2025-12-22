-- Final verification of the created contributions
\echo 'Verifying all contributions for target stakeholders:';

SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || chr(32) || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    e.name as entity_name,
    cc.entity_id
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
JOIN accounting_entity e ON cc.entity_id = e.id
WHERE cc.stakeholder_id IN (3, 7, 18)  -- Syed Safi, Ansaar Mohammed, Burhanuddin Shaik
ORDER BY cc.contribution_date DESC, cc.id;

\echo '';
\echo 'Summary by stakeholder:';

SELECT 
    s.first_name || chr(32) || s.last_name as stakeholder_name,
    COUNT(cc.id) as total_contributions,
    SUM(cc.amount) as total_amount,
    COUNT(CASE WHEN cc.workflow_status = 'APPROVED' THEN 1 END) as approved_contributions
FROM accounting_stakeholder s
LEFT JOIN accounting_capitalcontribution cc ON s.id = cc.stakeholder_id
WHERE s.id IN (3, 7, 18)
GROUP BY s.id, s.first_name, s.last_name
ORDER BY s.id;