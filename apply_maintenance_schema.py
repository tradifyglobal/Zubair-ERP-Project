#!/usr/bin/env python3
"""
Apply database schema changes for maintenance asset GL integration
Handles table ownership issues by connecting directly to PostgreSQL
"""

import psycopg2
import sys

# Database credentials
DB_HOST = "192.168.20.11"
DB_NAME = "tradifyerp_db"
DB_USER = "tradifyerp_user"
DB_PASSWORD = "Tradify@PostgreSQL2024"
DB_PORT = 5432

def main():
    try:
        print("[*] Connecting to PostgreSQL database...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("✓ Connected successfully")
        
        # Add the purchase_account column if it doesn't exist
        print("\n[*] Adding purchase_account column...")
        cur.execute("""
            ALTER TABLE maintenance_asset
            ADD COLUMN IF NOT EXISTS purchase_account_id INTEGER
        """)
        print("✓ Column added (or already exists)")
        
        # Add the foreign key constraint if it doesn't exist
        print("\n[*] Adding foreign key constraint...")
        try:
            cur.execute("""
                ALTER TABLE maintenance_asset
                ADD CONSTRAINT fk_maintenance_asset_purchase_account
                FOREIGN KEY (purchase_account_id)
                REFERENCES accounting_account(id)
                ON DELETE SET NULL
            """)
            print("✓ Foreign key constraint added")
        except psycopg2.errors.IntegrityError:
            print("✓ Constraint already exists (ignoring error)")
            conn.rollback()
        
        # Mark migration as applied in Django's migration table
        print("\n[*] Marking migration as applied...")
        cur.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('maintenance', '0003_maintenanceasset_purchase_account', NOW())
            ON CONFLICT DO NOTHING
        """)
        print("✓ Migration recorded")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✓ Database schema updated successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
