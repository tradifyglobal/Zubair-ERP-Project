from accounting.models import Account, LedgerEntry, Stakeholder, CashPaymentLine, ShareholderInvestmentSummary

print("\n" + "="*80)
print("ACCOUNT 3000-11 ANALYSIS")
print("="*80)

# Get account
acc = Account.objects.get(account_number="3000-11")
print(f"\nAccount: {acc.account_number} - {acc.name}")
print(f"Type: {acc.account_type}")

# Get ledger entries
print("\n" + "="*80)
print("RECENT LEDGER ENTRIES:")
print("="*80)
entries = LedgerEntry.objects.filter(account=acc).order_by('-entry_date', '-created_at')[:10]
print(f"\n{'ID':<8} {'Date':<12} {'Type':<8} {'Amount':<15} {'Status':<12} {'Description'}")
print("-"*100)
for e in entries:
    print(f"{e.id:<8} {e.entry_date} {e.entry_type:<8} {e.amount:>14,.2f} {e.workflow_status:<12} {e.description[:40]}")

# Get cash payment lines
print("\n" + "="*80)
print("CASH PAYMENT LINES:")
print("="*80)
payments = CashPaymentLine.objects.filter(account=acc).order_by('-date', '-created_at')[:5]
if payments:
    print(f"\n{'ID':<8} {'Date':<12} {'Amount':<15} {'Status':<12} {'Description'}")
    print("-"*100)
    for p in payments:
        print(f"{p.id:<8} {p.date} {p.amount:>14,.2f} {p.workflow_status:<12} {p.description[:40]}")
else:
    print("No cash payment lines found")

# Get shareholder info
print("\n" + "="*80)
print("SHAREHOLDER INVESTMENT SUMMARY:")
print("="*80)
stakeholders = Stakeholder.objects.filter(name__icontains='Fayazuddin')
for s in stakeholders:
    print(f"\nStakeholder: {s.name}")
    try:
        summary = ShareholderInvestmentSummary.objects.get(stakeholder=s)
        print(f"Total Investment: {summary.total_investment:,.2f}")
        print(f"Total Distributions: {summary.total_distributions:,.2f}")
        print(f"Net Investment: {summary.net_investment:,.2f}")
    except ShareholderInvestmentSummary.DoesNotExist:
        print("No investment summary found")

print("\n" + "="*80)
print("ACCOUNTING LOGIC EXPLANATION:")
print("="*80)
print("""
CAPITAL ACCOUNTS (Equity Type):
- Normal balance: CREDIT (liability/equity side of balance sheet)
- Owner invests money (Cash Receipt): CREDIT capital account = INCREASES equity
- Owner withdraws money (Cash Payment): DEBIT capital account = DECREASES equity

LEDGER DISPLAY LOGIC:
- For EQUITY accounts: CREDIT = positive, DEBIT = negative
- Cash Payment to capital account = Owner withdrawal = DEBIT = Shows NEGATIVE
- Cash Receipt to capital account = Owner investment = CREDIT = Shows POSITIVE

REAL-LIFE SCENARIO:
When you make a Cash Payment to account 3000-11 (Fayazuddin - Capital):
- This means Fayazuddin is WITHDRAWING money from the business
- Business owes him LESS now
- Equity DECREASES
- Shows as NEGATIVE (correct!)

If you did a Cash Receipt instead:
- Fayazuddin is INVESTING money into the business  
- Business owes him MORE now
- Equity INCREASES
- Shows as POSITIVE

THE NEGATIVE AMOUNT IS CORRECT! It represents a withdrawal/return of capital.
""")
