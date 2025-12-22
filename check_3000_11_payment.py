#!/usr/bin/env python3
"""Check ledger entries and shareholder account for 3000-11 cash payment."""

import psycopg2

conn = psycopg2.connect(
    host="192.168.2.59",
    database="tradify_erp",
    user="zubair",
    password="Tradify@PostgreSQL2024"
)

cur = conn.cursor()

print("=" * 80)
print("LEDGER ENTRIES FOR ACCOUNT 3000-11 (Fayazuddin Zubair Mohammed - Capital)")
print("=" * 80)

# Get account ID first
cur.execute("SELECT id, account_number, name, account_type FROM accounting_account WHERE account_number = '3000-11'")
account = cur.fetchone()
if account:
    account_id, acc_num, acc_name, acc_type = account
    print(f"\nAccount: {acc_num} - {acc_name} (Type: {acc_type})\n")
    
    # Get ledger entries
    cur.execute("""
        SELECT id, entry_date, entry_type, amount, description, workflow_status, created_at 
        FROM accounting_ledgerentry 
        WHERE account_id = %s 
        ORDER BY entry_date DESC, created_at DESC 
        LIMIT 10
    """, (account_id,))
    
    entries = cur.fetchall()
    if entries:
        print(f"{'ID':<8} {'Date':<12} {'Type':<8} {'Amount':<15} {'Status':<12} {'Description'}")
        print("-" * 100)
        for row in entries:
            eid, edate, etype, amt, desc, status, created = row
            print(f"{eid:<8} {str(edate):<12} {etype:<8} {float(amt):>14,.2f} {status:<12} {desc[:40]}")
    else:
        print("No ledger entries found")

print("\n" + "=" * 80)
print("CASH PAYMENT LINES FOR ACCOUNT 3000-11")
print("=" * 80)

cur.execute("""
    SELECT id, date, amount, description, workflow_status, created_at
    FROM accounting_cashpaymentline
    WHERE account_id = %s
    ORDER BY date DESC, created_at DESC
    LIMIT 5
""", (account_id,))

payments = cur.fetchall()
if payments:
    print(f"\n{'ID':<8} {'Date':<12} {'Amount':<15} {'Status':<12} {'Description'}")
    print("-" * 100)
    for row in payments:
        pid, pdate, pamt, pdesc, pstatus, pcreated = row
        print(f"{pid:<8} {str(pdate):<12} {float(pamt):>14,.2f} {pstatus:<12} {pdesc[:40]}")
else:
    print("No cash payment lines found")

print("\n" + "=" * 80)
print("SHAREHOLDER ACCOUNT FOR FAYAZUDDIN")
print("=" * 80)

cur.execute("""
    SELECT s.id, s.name, sa.total_investment, sa.total_returns, sa.net_investment
    FROM accounting_stakeholder s
    LEFT JOIN accounting_shareholderaccount sa ON s.id = sa.stakeholder_id
    WHERE s.name LIKE '%Fayazuddin%'
""")

shareholders = cur.fetchall()
if shareholders:
    print(f"\n{'ID':<8} {'Name':<40} {'Investment':<15} {'Returns':<15} {'Net':<15}")
    print("-" * 100)
    for row in shareholders:
        sid, sname, invest, returns, net = row
        invest_amt = float(invest) if invest else 0.0
        returns_amt = float(returns) if returns else 0.0
        net_amt = float(net) if net else 0.0
        print(f"{sid:<8} {sname:<40} {invest_amt:>14,.2f} {returns_amt:>14,.2f} {net_amt:>14,.2f}")
else:
    print("No shareholder records found")

print("\n" + "=" * 80)
print("ACCOUNTING LOGIC EXPLANATION")
print("=" * 80)
print("""
CAPITAL ACCOUNTS (Type: EQUITY):
- When owner INVESTS money (Cash Receipt): CREDIT the capital account (increases equity)
- When owner WITHDRAWS money (Cash Payment): DEBIT the capital account (decreases equity)

EQUITY ACCOUNTS have CREDIT balance:
- Credits = Increases (owner puts money IN)
- Debits = Decreases (owner takes money OUT)

LEDGER ENTRY DISPLAY:
- DEBIT entries show as negative (withdrawals)
- CREDIT entries show as positive (investments)

For account 3000-11 (Fayazuddin - Capital):
- Cash Payment should create a DEBIT entry (withdrawal = negative)
- Cash Receipt should create a CREDIT entry (investment = positive)

This is CORRECT accounting behavior!
""")

cur.close()
conn.close()
