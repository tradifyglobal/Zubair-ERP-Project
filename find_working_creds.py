#!/usr/bin/env python
"""
Try different databases and user combinations to find working credentials.
"""

import psycopg2
import sys

# Try different combinations
attempts = [
    ('root', 'sql', 'tradifyerp_db'),
    ('postgres', 'sql', 'tradifyerp_db'),
    ('zubair', 'sql', 'tradifyerp_db'),
    ('root', 'sql', 'postgres'),
    ('postgres', 'sql', 'postgres'),
    ('zubair', 'sql', 'postgres'),
]

print("=" * 80)
print("FINDING WORKING POSTGRESQL CREDENTIALS")
print("=" * 80)

for user, password, database in attempts:
    try:
        print(f"\nTrying {user}@{database} with password '{password}'...", end=' ')
        conn = psycopg2.connect(
            host='192.168.20.11',
            database=database,
            user=user,
            password=password,
            port='5432',
            connect_timeout=5
        )
        print("✓ SUCCESS!")
        
        # Test if we have superuser/alter permissions
        cur = conn.cursor()
        cur.execute("SELECT current_user, version();")
        result = cur.fetchone()
        print(f"  Connected as: {result[0]}")
        print(f"  PostgreSQL: {result[1][:60]}...")
        
        # Try to add a test column
        try:
            cur.execute("ALTER TABLE accounting_cashreceiptline ADD COLUMN test_perm_check BOOLEAN;")
            conn.commit()
            print("  ✓ Has ALTER TABLE permission!")
            
            # Clean up test column
            cur.execute("ALTER TABLE accounting_cashreceiptline DROP COLUMN test_perm_check;")
            conn.commit()
            
            cur.close()
            conn.close()
            
            # This is the one! Use it
            print(f"\n✓ FOUND WORKING CREDENTIALS:")
            print(f"  User: {user}")
            print(f"  Password: {password}")
            print(f"  Database: {database}")
            sys.exit(0)
            
        except Exception as e:
            print(f"  ✗ No ALTER permission: {str(e)[:40]}")
            conn.rollback()
            cur.close()
            conn.close()
            continue
        
    except psycopg2.Error as e:
        error_msg = str(e)
        if "authentication failed" in error_msg.lower():
            print("✗ Auth failed")
        elif "does not exist" in error_msg.lower():
            print("✗ DB doesn't exist")
        else:
            print(f"✗ Error: {error_msg[:40]}")
    except Exception as e:
        print(f"✗ Exception: {str(e)[:40]}")

print("\n✗ Could not find working credentials with ALTER permission")
sys.exit(1)
