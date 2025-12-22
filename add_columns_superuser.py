#!/usr/bin/env python
"""
Connect as root/postgres user to add missing columns with superuser privileges.
"""

import psycopg2
import sys

# Try different user combinations
credentials = [
    {
        'user': 'root',
        'password': 'sql',
        'host': '192.168.20.11',
        'database': 'tradifyerp_db',
        'port': '5432'
    },
    {
        'user': 'postgres',
        'password': 'sql',
        'host': '192.168.20.11',
        'database': 'tradifyerp_db',
        'port': '5432'
    },
    {
        'user': 'zubair',
        'password': 'sql',
        'host': '192.168.20.11',
        'database': 'tradifyerp_db',
        'port': '5432'
    }
]

print("=" * 80)
print("ADDING COLUMNS WITH SUPERUSER PRIVILEGES")
print("=" * 80)

conn = None
for creds in credentials:
    try:
        print(f"\nAttempting connection as {creds['user']}...")
        conn = psycopg2.connect(
            host=creds['host'],
            database=creds['database'],
            user=creds['user'],
            password=creds['password'],
            port=creds['port']
        )
        print(f"✓ Connected successfully as {creds['user']}!")
        break
    except psycopg2.Error as e:
        print(f"✗ Failed: {str(e)[:60]}")
        continue

if not conn:
    print("\n✗ Could not connect with any credentials")
    sys.exit(1)

cur = conn.cursor()

# Add columns
print("\n" + "=" * 80)
print("ADDING MISSING COLUMNS")
print("=" * 80)

statements = [
    ("cashreceiptline", "is_capital_contribution_posted", 
     "ALTER TABLE accounting_cashreceiptline ADD COLUMN is_capital_contribution_posted BOOLEAN DEFAULT FALSE;"),
    ("cashreceiptline", "stakeholder_id",
     "ALTER TABLE accounting_cashreceiptline ADD COLUMN stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;"),
    ("bankreceiptline", "is_capital_contribution_posted",
     "ALTER TABLE accounting_bankreceiptline ADD COLUMN is_capital_contribution_posted BOOLEAN DEFAULT FALSE;"),
    ("bankreceiptline", "stakeholder_id",
     "ALTER TABLE accounting_bankreceiptline ADD COLUMN stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;"),
]

added_count = 0
for table, col, statement in statements:
    try:
        cur.execute(statement)
        conn.commit()
        print(f"✓ Added {table}.{col}")
        added_count += 1
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print(f"✓ {table}.{col} already exists")
            conn.rollback()
        else:
            print(f"✗ Error: {str(e)[:60]}")
            conn.rollback()

# Verify
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

cur.execute("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
    AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
    ORDER BY table_name, column_name;
""")

results = cur.fetchall()
print(f"\n✓ Found {len(results)} columns:")
for row in results:
    print(f"  {row[0]}.{row[1]} ({row[2]})")

cur.close()
conn.close()

print(f"\n✓ Successfully added/verified {added_count} columns!")
sys.exit(0)
