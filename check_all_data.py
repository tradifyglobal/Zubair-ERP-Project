from accounting.models import (
    Entity, CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine,
    LedgerEntry, Account, CapitalContribution, Stakeholder
)

print("\n" + "="*80)
print("COMPLETE DATABASE CHECK - ALL ENTITIES")
print("="*80)

# Check all entities
entities = Entity.objects.all()
print(f"\nTotal Entities: {entities.count()}")
for ent in entities:
    print(f"  - {ent.code}: {ent.name}")

print("\n" + "="*80)
print("CHECKING ALL TRANSACTIONS ACROSS ALL ENTITIES")
print("="*80)

for entity in entities:
    print(f"\n{'='*80}")
    print(f"Entity: {entity.code} - {entity.name}")
    print(f"{'='*80}")
    
    # Cash Receipts
    cash_receipts = CashReceiptLine.objects.filter(entity=entity)
    print(f"\nCash Receipts: {cash_receipts.count()}")
    if cash_receipts.exists():
        for r in cash_receipts[:5]:
            print(f"  ID {r.id}: {r.date} - {r.description[:40]} - {r.workflow_status} - Amount: {r.debit_amount}")
    
    # Cash Payments
    cash_payments = CashPaymentLine.objects.filter(entity=entity)
    print(f"Cash Payments: {cash_payments.count()}")
    if cash_payments.exists():
        for p in cash_payments[:5]:
            print(f"  ID {p.id}: {p.date} - {p.description[:40]} - {p.workflow_status} - Amount: {p.debit_amount}")
    
    # Bank Receipts
    bank_receipts = BankReceiptLine.objects.filter(entity=entity)
    print(f"Bank Receipts: {bank_receipts.count()}")
    if bank_receipts.exists():
        for r in bank_receipts[:5]:
            print(f"  ID {r.id}: {r.date} - {r.description[:40]} - {r.workflow_status} - Amount: {r.debit_amount}")
    
    # Bank Payments
    bank_payments = BankPaymentLine.objects.filter(entity=entity)
    print(f"Bank Payments: {bank_payments.count()}")
    if bank_payments.exists():
        for p in bank_payments[:5]:
            print(f"  ID {p.id}: {p.date} - {p.description[:40]} - {p.workflow_status} - Amount: {p.debit_amount}")
    
    # Ledger Entries
    ledger_entries = LedgerEntry.objects.filter(entity=entity)
    print(f"Ledger Entries: {ledger_entries.count()}")
    if ledger_entries.exists():
        for e in ledger_entries[:5]:
            print(f"  ID {e.id}: {e.entry_date} - {e.account.account_number} - {e.entry_type} - {e.amount} - {e.workflow_status}")
    
    # Capital Contributions
    contributions = CapitalContribution.objects.filter(entity=entity)
    print(f"Capital Contributions: {contributions.count()}")
    if contributions.exists():
        for c in contributions[:5]:
            print(f"  ID {c.id}: {c.contribution_date} - {c.stakeholder.first_name if c.stakeholder else 'None'} - Amount: {c.amount}")

print("\n" + "="*80)
print("STAKEHOLDERS")
print("="*80)
stakeholders = Stakeholder.objects.all()
print(f"\nTotal Stakeholders: {stakeholders.count()}")
for s in stakeholders[:10]:
    name = f"{s.first_name} {s.middle_name or ''} {s.last_name}".strip() if hasattr(s, 'first_name') else s.company_name
    print(f"  ID {s.id}: {name} - Type: {s.stakeholder_type}")

print("\n" + "="*80)
print("ACCOUNTS (CAPITAL ACCOUNTS)")
print("="*80)
capital_accounts = Account.objects.filter(account_type='EQUITY', account_number__startswith='3000')
print(f"\nTotal Capital Accounts (3000-xx): {capital_accounts.count()}")
for acc in capital_accounts:
    print(f"  {acc.account_number} - {acc.name} - Entity: {acc.entity.code}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"""
Total across all entities:
  - Cash Receipts: {CashReceiptLine.objects.count()}
  - Cash Payments: {CashPaymentLine.objects.count()}
  - Bank Receipts: {BankReceiptLine.objects.count()}
  - Bank Payments: {BankPaymentLine.objects.count()}
  - Ledger Entries: {LedgerEntry.objects.count()}
  - Capital Contributions: {CapitalContribution.objects.count()}
  - Stakeholders: {Stakeholder.objects.count()}
  - Capital Accounts: {capital_accounts.count()}
""")
