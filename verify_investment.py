from accounting.models import (
    CashReceiptLine, CashPaymentLine, 
    BankReceiptLine, BankPaymentLine,
    CapitalContribution, Stakeholder, Account
)

print("\n" + "="*70)
print("SHAREHOLDER INVESTMENT TRACKING VERIFICATION")
print("="*70)

stakeholder = Stakeholder.objects.get(id=2)
print(f"\nStakeholder: {stakeholder.first_name} {stakeholder.middle_name} {stakeholder.last_name}")

capital_account = Account.objects.get(entity_id=7, account_number='3000-11')
print(f"Capital Account: {capital_account}")

print("\n" + "="*70)
print("TRANSACTIONS")
print("="*70)

# Cash receipts
cr_count = CashReceiptLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED').count()
print(f"\nCash Receipts: {cr_count}")
for r in CashReceiptLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED'):
    print(f"  {r.id}: {r.date} - {r.debit_amount:,.2f} - Posted: {r.is_capital_contribution_posted}")

# Cash payments
cp_count = CashPaymentLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED').count()
print(f"\nCash Payments: {cp_count}")
for p in CashPaymentLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED'):
    print(f"  {p.id}: {p.date} - {p.debit_amount:,.2f}")

# Bank receipts
br_count = BankReceiptLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED').count()
print(f"\nBank Receipts: {br_count}")
for r in BankReceiptLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED'):
    print(f"  {r.id}: {r.date} - {r.debit_amount:,.2f} - Posted: {r.is_capital_contribution_posted}")

# Bank payments
bp_count = BankPaymentLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED').count()
print(f"\nBank Payments: {bp_count}")
for p in BankPaymentLine.objects.filter(account=capital_account, workflow_status='AUTHORIZED'):
    print(f"  {p.id}: {p.date} - {p.debit_amount:,.2f}")

print("\n" + "="*70)
print("CAPITAL CONTRIBUTIONS")
print("="*70)

contributions = CapitalContribution.objects.filter(
    equity_account=capital_account
).order_by('contribution_date')

print(f"\nTotal: {contributions.count()}")

if contributions.exists():
    total_invested = 0
    total_withdrawn = 0
    
    for contrib in contributions:
        symbol = '✅' if contrib.status == 'APPROVED' else '⏳'
        print(f"\n{symbol} #{contrib.id}:")
        print(f"  Date: {contrib.contribution_date}")
        print(f"  Type: {contrib.workflow_status}")  
        print(f"  Amount: {contrib.amount:,.2f}")
        print(f"  Status: {contrib.status}")
        print(f"  Stakeholder: {contrib.stakeholder}")
        print(f"  Method: {contrib.payment_mode}")
        print(f"  Source Cash: {contrib.source_cash_receipt_id}")
        print(f"  Source Bank: {contrib.source_bank_receipt_id}")
        
        if contrib.status == 'APPROVED':
            if contrib.workflow_status == 'CONTRIBUTION':
                total_invested += contrib.amount
            elif contrib.workflow_status == 'WITHDRAWAL':
                total_withdrawn += contrib.amount
    
    print(f"\n{'='*70}")
    print(f"INVESTMENT SUMMARY:")
    print(f"{'='*70}")
    print(f"  Contributions: {total_invested:>12,.2f}")
    print(f"  Withdrawals:   {total_withdrawn:>12,.2f}")
    print(f"  {'─'*42}")
    print(f"  Net:           {(total_invested - total_withdrawn):>12,.2f}")
    print(f"{'='*70}")
else:
    print("\n⚠️  NO CAPITAL CONTRIBUTIONS!")

print("\n" + "="*70)
print("EXPECTED:")
print("="*70)
print("Cash Receipt 13:  100,000 → CONTRIBUTION")
print("Bank Receipt 7:     1,000 → CONTRIBUTION")
print("Cash Payment 15:      500 → WITHDRAWAL")
print("Bank Payment 4:       200 → WITHDRAWAL")
print("Net: 100,300")
print("="*70)
