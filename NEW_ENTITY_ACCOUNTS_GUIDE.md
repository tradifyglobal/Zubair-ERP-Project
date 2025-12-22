# Adding GL Accounts for New Entities

## Current Status
GL accounts (including Cash 100001) are **per-entity**. They are NOT automatically created when you add a new entity.

## Solution: Use Management Command

### Setup Accounts for Single New Entity
```bash
python manage.py setup_standard_accounts --entity MY-ENTITY-CODE
```

Example for a new entity "BRANCH-01":
```bash
python manage.py setup_standard_accounts --entity BRANCH-01
```

This creates all standard accounts:
- 1000 (Assets)
- 1100 (Cash and Bank)
- **100001 (Cash)** ← The account we deployed
- 3000 (Capital/Equity)
- 3100 (Shareholder Investment)
- 4000 (Income)
- 5000 (Expenses)

### Setup Accounts for All Entities
```bash
python manage.py setup_standard_accounts
```

This setup all accounts for MAIN, INT-001, Test, and any other entities you have.

### Skip Cash Account
```bash
python manage.py setup_standard_accounts --entity BRANCH-01 --skip-cash
```

## When to Use

1. **Creating a new entity?** 
   - Use: `python manage.py setup_standard_accounts --entity NEW-ENTITY-CODE`

2. **Missing accounts in an entity?**
   - Use: `python manage.py setup_standard_accounts --entity ENTITY-CODE`

3. **Onboarding multiple new entities?**
   - Use: `python manage.py setup_standard_accounts` (sets up all at once)

## Manual SQL Alternative

If you prefer SQL, you can also manually insert accounts:

```sql
INSERT INTO accounting_account (account_number, name, account_type, description, entity_id, currency_id, is_active, opening_balance, created_at, updated_at)
SELECT '100001', 'Cash', 'ASSET', 'Cash account', ae.id, ac.id, true, 0.00, NOW(), NOW()
FROM accounting_entity ae, accounting_currency ac
WHERE ae.code='NEW-ENTITY-CODE' AND ac.code='INR'
AND NOT EXISTS (SELECT 1 FROM accounting_account WHERE account_number='100001' AND entity_id=ae.id);
```

## Account Hierarchy (Auto-Created)

The accounts are created with parent-child relationships:
```
1000 (Assets)
  └─ 1100 (Cash and Bank)
      └─ 100001 (Cash)

3000 (Capital)
  └─ 3100 (Shareholder Investment)
      └─ 3100-01, 3100-02, ... (Per stakeholder - created by signal)
```

## Entity Mixin Support

All accounts respect `SessionEntityMixin`, so:
- Users only see accounts for their current entity
- GL posting filters by entity automatically
- No cross-entity account leakage

## Next Steps

1. Create a new entity in admin panel
2. Run: `python manage.py setup_standard_accounts --entity YOUR-CODE`
3. Users assigned to that entity will see all accounts including Cash 100001
