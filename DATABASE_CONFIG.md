# PostgreSQL Database Configuration

**Current Status**: Updated December 15, 2025

## Active Database (In Use)
- **Database Name**: `tradifyerp_db`
- **User**: `tradifyerp_user`
- **Password**: `Tradify@PostgreSQL2024`
- **Host**: `192.168.2.59`
- **Port**: `5432`
- **Django Settings**: `TradifyERP/settings.py` ✅ CONFIGURED

### Schema Information
- Created: December 15, 2025
- Migrated from: `tradify_backup_inactive`
- Status: **ACTIVE - ALL DEPLOYMENTS USE THIS**

---

## Inactive Backup Database (DO NOT USE)
- **Database Name**: `tradify_backup_inactive`
- **Status**: **INACTIVE - BACKUP ONLY**
- **Purpose**: Historical reference/disaster recovery
- **Action**: Keep as backup, do NOT deploy or migrate changes to this database

---

## Migration Notes

### Recent Changes
1. **Database Migration** (Dec 15, 2025):
   - Created new `tradifyerp_db` with schema from old `tradify`
   - Renamed old `tradify` → `tradify_backup_inactive`
   - Updated permissions for `tradifyerp_user`

2. **Capital Contribution Refactoring** (Dec 15, 2025):
   - Removed workflow approval system (approval now at transaction level)
   - Added 3 new columns:
     - `source_cash_receipt_id` (ForeignKey)
     - `source_bank_receipt_id` (ForeignKey)
     - `is_auto_posted` (Boolean, default: False)
   - Signal handlers auto-create contributions when receipts approved

3. **Account Name Corrections** (Dec 15, 2025):
   - Removed extra middle names from accounts 3000-11 and 3000-12
   - Both databases updated for consistency

---

## Deployment Checklist

When deploying new changes:
- ✅ Always deploy to `tradifyerp_db` (the active database)
- ✅ Verify Django settings point to `tradifyerp_db`
- ✅ Run migrations on `tradifyerp_db` only
- ❌ Do NOT use `tradify_backup_inactive` for any new deployments
- ✅ Keep `tradify_backup_inactive` as disaster recovery backup

---

## Technical Details

### Connection String (Django)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradifyerp_db',  # ← ACTIVE DATABASE
        'USER': 'tradifyerp_user',
        'PASSWORD': 'Tradify@PostgreSQL2024',
        'HOST': '192.168.2.59',
        'PORT': '5432',
    }
}
```

### Backup & Recovery
- Backup Location: `/tmp/tradify_backup.dump` (pg_dump format)
- Backup Date: December 15, 2025
- Recovery Command: `pg_restore -d tradifyerp_db /tmp/tradify_backup.dump`

---

## Support

For database-related issues, refer to:
- Active Database: `tradifyerp_db` on `192.168.2.59`
- Backup Database: `tradify_backup_inactive` (read-only)
- Database User: `tradifyerp_user` with appropriate permissions
