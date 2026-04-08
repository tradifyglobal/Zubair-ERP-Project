# Generated migration using RunPython
# This allows flexible error handling

from django.db import migrations
from django.db.migrations.operations.raw import Raw


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0002_alter_complianceaudit_entity_and_more'),
    ]

    operations = [
        Raw(
            sql="""
                ALTER TABLE maintenance_asset
                ADD COLUMN IF NOT EXISTS purchase_account_id BIGINT;
            """,
            reverse_sql="ALTER TABLE maintenance_asset DROP COLUMN IF EXISTS purchase_account_id;",
        ),
        Raw(
            sql="""
                ALTER TABLE maintenance_asset
                ADD CONSTRAINT maintenance_asset_purchase_account_id_fk
                FOREIGN KEY (purchase_account_id)
                REFERENCES accounting_account(id)
                ON DELETE SET NULL;
            """,
            reverse_sql="ALTER TABLE maintenance_asset DROP CONSTRAINT IF EXISTS maintenance_asset_purchase_account_id_fk;",
        ),
        Raw(
            sql="""
                CREATE INDEX IF NOT EXISTS maintenance_asset_purchase_account_id_idx
                ON maintenance_asset(purchase_account_id);
            """,
            reverse_sql="DROP INDEX IF EXISTS maintenance_asset_purchase_account_id_idx;",
        ),
    ]
