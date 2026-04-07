# Asset GL Integration Setup Guide
## Feature: Automatic GL Posting for Asset Purchases

### Overview
This feature allows assets to be purchased from specific accounts (like Capital Investment) and automatically posts GL entries to maintain double-entry accounting.

When you create an asset and specify the "Purchase Account":
- **DEBIT**: Fixed Assets account
- **CREDIT**: Purchase Account (e.g., Capital Investment)

### Current Status
✓ Code deployed successfully
⚠ Database column pending manual addition (due to table ownership issue)

### What Has Been Deployed

1. **Model Changes** (`maintenance/models.py`):
   - Added `purchase_account` ForeignKey field to MaintenanceAsset
   - Links asset purchase to the originating account

2. **Form Updates** (`maintenance/forms.py`):
   - Added `purchase_account` field to MaintenanceAssetForm
   - Automatically filters accounts by entity
   - Excludes expense accounts (only shows assets, equity, capital accounts)

3. **GL Posting Logic** (`maintenance/signals.py`):
   - New signal handler `post_asset_purchase_to_gl`
   - Automatically creates GL entries when asset is created
   - Creates DEBIT entry in Fixed Assets account
   - Creates CREDIT entry in selected Purchase account
   - Reference: `ASSET-{asset_id}`

### Database Column Addition

Unfortunately, the database table `maintenance_asset` is not owned by the `tradifyerp_user` account, preventing direct ALTER TABLE operations from the application.

**You have two options:**

#### Option 1: Add Column as Database Admin (Recommended)

1. Log into your database server (192.168.20.11) as root or postgres user
2. Run the following SQL:

```bash
sudo -u postgres psql -d tradifyerp_db << 'EOF'
ALTER TABLE maintenance_asset ADD COLUMN purchase_account_id BIGINT;

ALTER TABLE maintenance_asset
ADD CONSTRAINT maintenance_asset_purchase_account_id_fk
FOREIGN KEY (purchase_account_id)
REFERENCES accounting_account(id)
ON DELETE SET NULL;

CREATE INDEX maintenance_asset_purchase_account_id_idx
ON maintenance_asset(purchase_account_id);
EOF
```

Or use the provided SQL file:
```bash
sudo -u postgres psql -d tradifyerp_db < /var/www/tradifyerp/add_purchase_account_column_admin.sql
```

#### Option 2: Fix Table Ownership

If you want to let the application manage schema changes in the future, use:

```bash
sudo -u postgres psql -d tradifyerp_db -c "ALTER TABLE maintenance_asset OWNER TO tradifyerp_user;"
```

Then manually run the migration from the app server:
```bash
ssh root@192.168.20.10
cd /var/www/tradifyerp
./venv/bin/python manage.py migrate maintenance
```

### Testing the Feature

1. **After adding the database column:**
   ```bash
   ssh root@192.168.20.10 "cd /var/www/tradifyerp && ./venv/bin/python manage.py migrate"
   ```

2. **Visit the asset creation page:**
   - Navigate to: `http://192.168.20.10/maintenance/assets/new/`
   - You should see a new "Purchase Account" dropdown field
   - Select the account from which the asset was purchased

3. **Verify GL entries are created:**
   - Go to: `http://192.168.20.10/accounting/ledger_entries/`
   - Look for entries with reference format: `ASSET-{number}`
   - Check that debits and credits are balanced

### Example Workflow

1. **Create Capital Investment Account** (if not already present):
   - Navigate to Chart of Accounts
   - Create account: "Capital Contribution - Equipment"
   - Account Type: Equity
   - Post a capital contribution to this account

2. **Purchase Equipment**:
   - Go to `/maintenance/assets/new/`
   - Fill in asset details:
     - Asset Code: `EQUIP-001`
     - Asset Name: `Industrial Laser Cutter`
     - Acquisition Cost: `50,000.00`
     - Purchase Date: `2026-04-07`
     - **Purchase Account**: `Capital Contribution - Equipment` ← NEW FIELD

3. **Automatic GL Posting**:
   - DEBIT: Fixed Assets... $50,000
   - CREDIT: Capital Contribution - Equipment... $50,000
   - Reference: `ASSET-{id}`
   - Status: Authorized (automatically posted)

### Troubleshooting

**Issue**: Purchase Account field not showing
- Solution: Ensure database column has been added (see "Database Column Addition" above)

**Issue**: GL entries not appearing after creating asset
- Check: `http://192.168.20.10/admin/logs/` for error messages
- Verify: The selected Purchase Account exists and is active
- Check if Django signal was triggered by reviewing logs

**Issue**: Can't select Purchase Account (field appears empty)
- Make sure: Your entity has accounts created
- Check: Accounts are marked as "Active"
- Filter: The form filters out Expense accounts intentionally

### Database Schema

The new column structure:

```sql
ALTER TABLE maintenance_asset ADD COLUMN purchase_account_id BIGINT;
ALTER TABLE maintenance_asset ADD FOREIGN KEY (purchase_account_id)
    REFERENCES accounting_account(id) ON DELETE SET NULL;
```

### Rollback Instructions

If you need to remove this feature:

1. Delete the asset GL entries (if needed)
2. Drop the column:
   ```sql
   ALTER TABLE maintenance_asset DROP COLUMN purchase_account_id;
   ```
3. Revert the code changes from git

### Next Steps

1. **Add the database column** (choose Option 1 or 2 above)
2. **Test the feature** using the workflow above
3. **Monitor GL postings** to ensure accuracy
4. **Document your account mapping** for your team

### Support

For issues or questions:
- Check the deployment logs: `/var/log/gunicorn.log`
- Review Django error pages: `http://192.168.20.10/` (if DEBUG=True)
- Check database connectivity with: `ssh root@192.168.20.10 "psql -d tradifyerp_db -U tradifyerp_user -c '\\dt maintenance_asset'"`
