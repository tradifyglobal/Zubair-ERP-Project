#!/usr/bin/env python
"""Check GL entries directly via psycopg2"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="192.168.2.59",
    database="tradifyerp_db",
    user="zubair",
    password="zabuPassword@123"
)

cursor = conn.cursor(cursor_factory=RealDictCursor)

# Get all accounts that start with 100
cursor.execute("""
    SELECT id, account_number, name, account_type
    FROM accounting_account
    WHERE entity_id = (SELECT id FROM accounting_entity WHERE name = 'Testing')
    AND account_type = 'ASSET'
    AND (name ILIKE '%cash%' OR name ILIKE '%bank%' OR account_number LIKE '100%')
    ORDER BY account_number
""")
accounts = cursor.fetchall()
print("\n" + "="*60)
print("CASH ACCOUNTS MATCHING FILTER")
print("="*60)
for acc in accounts:
    print(f"{acc['account_number']} - {acc['name']} (ID: {acc['id']})")

# Now check GL entries for each
print("\n" + "="*60)
print("GL ENTRIES PER CASH ACCOUNT")
print("="*60)

total_cash = 0
for acc in accounts:
    cursor.execute("""
        SELECT 
            id, entry_type, amount, description, reference_number, entry_date
        FROM accounting_ledgerentry
        WHERE account_id = %s
        ORDER BY entry_date DESC, id DESC
        LIMIT 10
    """, (acc['id'],))
    entries = cursor.fetchall()
    
    if entries:
        print(f"\nAccount {acc['account_number']} - {acc['name']}:")
        debits = 0
        credits = 0
        
        for entry in entries:
            print(f"  {entry['entry_date']} | {entry['entry_type']:6s} | {entry['amount']:8.2f} | {entry['reference_number']}")
            if entry['entry_type'] == 'DEBIT':
                debits += entry['amount']
            else:
                credits += entry['amount']
        
        balance = debits - credits
        print(f"  Debits: {debits:.2f} | Credits: {credits:.2f} | Balance: {balance:.2f}")
        total_cash += balance

print("\n" + "="*60)
print(f"TOTAL CASH BALANCE: {total_cash:.2f}")
print("EXPECTED: 100 (one cash receipt, 100 INR)")
print("ACTUAL: {}".format(total_cash))
if total_cash == 200:
    print("⚠️  BALANCE IS DOUBLE!")
print("="*60)

cursor.close()
conn.close()
