import psycopg2
from decimal import Decimal

conn = psycopg2.connect(
    host="192.168.20.11",
    database="tradifyerp_db",
    user="tradifyerp_user",
    password="Tradify@PostgreSQL2024"
)

cursor = conn.cursor()

# Get cash account balance
cursor.execute("""
    SELECT 
        entry_type,
        SUM(amount) as total
    FROM accounting_ledgerentry
    WHERE account_id = '100001' 
    AND entity_id = 7
    GROUP BY entry_type
    ORDER BY entry_type;
""")

results = cursor.fetchall()

debits = Decimal('0')
credits = Decimal('0')

print("\nCash Account (100001) - Test Entity:")
print("=" * 50)
for entry_type, total in results:
    print(f"{entry_type}: {total:,.2f}")
    if entry_type == 'DEBIT':
        debits = total
    elif entry_type == 'CREDIT':
        credits = total

balance = debits - credits
print(f"\nCurrent Cash Balance: {balance:,.2f}")
print("=" * 50)

cursor.close()
conn.close()
