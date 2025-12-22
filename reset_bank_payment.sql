-- Reset bank payment status to allow re-authorization with correct DR/CR
UPDATE accounting_bankpaymentline
SET workflow_status = 'APPROVED', status = 'PENDING'
WHERE id = 4 AND entity_id = 7;

-- Check the update
SELECT id, date, description, debit_amount, credit_amount, workflow_status, status 
FROM accounting_bankpaymentline 
WHERE id = 4;
