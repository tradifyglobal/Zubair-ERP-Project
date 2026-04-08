#!/usr/bin/env python3
"""
Execute SQL directly on PostgreSQL using owner/superuser credentials
"""

import psycopg2
import sys

# Try different credentials
CONFIGS = [
    {
        "host": "192.168.20.11",
        "database": "tradifyerp_db",
        "user": "postgres",  # Try superuser first
        "password": None,  # Will try without password
        "port": 5432
    },
    {
        "host": "192.168.20.11",
        "database": "tradifyerp_db",
        "user": "tradifyerp_user",
        "password": "Tradify@PostgreSQL2024",
        "port": 5432
    },
]

def try_connect(config):
    """Try to connect with given config."""
    try:
        conn = psycopg2.connect(**{k: v for k, v in config.items() if v is not None})
        return conn
    except Exception as e:
        return None

def main():
    conn = None
    
    # Try to connect with any available credentials
    for i, config in enumerate(CONFIGS):
        print(f"\n[*] Attempting connection as {config['user']}...")
        conn = try_connect(config)
        if conn:
            print(f"✓ Connected as {config['user']}")
            break
    
    if not conn:
        print("\n✗ Could not establish database connection")
        sys.exit(1)
    
    try:
        cur = conn.cursor()
        
        # Check if column already exists
        print("\n[*] Checking if column exists...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'maintenance_asset' 
            AND column_name = 'purchase_account_id'
        """)
        
        if cur.fetchone():
            print("✓ Column already exists")
        else:
            print("✓ Column does not exist, adding now...")
            
            # Execute the migration SQL
            print("\n[*] Adding purchase_account_id column...")
            cur.execute('''
                ALTER TABLE "maintenance_asset" 
                ADD COLUMN "purchase_account_id" bigint NULL
            ''')
            print("✓ Column added")
            
            print("\n[*] Adding foreign key constraint...")
            try:
                cur.execute('''
                    ALTER TABLE "maintenance_asset" 
                    ADD CONSTRAINT "maintenance_asset_purchase_account_id_9a4ae286_fk_accountin" 
                    FOREIGN KEY ("purchase_account_id") 
                    REFERENCES "accounting_account"("id") 
                    DEFERRABLE INITIALLY DEFERRED
                ''')
                print("✓ Foreign key added")
            except psycopg2.errors.IntegrityError as e:
                print(f"⚠ FK constraint may already exist: {e}")
                conn.rollback()
            
            print("\n[*] Creating index...")
            cur.execute('''
                CREATE INDEX IF NOT EXISTS "maintenance_asset_purchase_account_id_9a4ae286" 
                ON "maintenance_asset" ("purchase_account_id")
            ''')
            print("✓ Index created")
        
        #Now mark migration as applied
        print("\n[*] Recording migration in Django...")
        cur.execute("""
            INSERT INTO django_migrations (app, name, applied)
            SELECT 'maintenance', '0003_maintenanceasset_purchase_account', NOW()
            WHERE NOT EXISTS (
                SELECT 1 FROM django_migrations 
                WHERE app = 'maintenance' 
                AND name = '0003_maintenanceasset_purchase_account'
            )
        """)
        
        conn.commit()
        print("✓ Migration recorded")
        
        print("\n" + "=" * 50)
        print("✓ Schema updated successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
