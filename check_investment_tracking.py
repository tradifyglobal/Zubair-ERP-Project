from accounting.models import (
    CashReceiptLine, CashPaymentLine, 
    BankReceiptLine, BankPaymentLine,
    CapitalContribution, Stakeholder
)

print("\n" + "="*70)
print("SHAREHOLDER INVESTMENT TRACKING VERIFICATION")
print("="*70)

# Check stakeholder
stakeholder = Stakeholder.objects.get(id=2)
print(f"\nStakeholder: {stakeholder.first_name} {stakeholder.middle_name} {stakeholder.last_name}")

# Check all transactions for this stakeholder
print("\n" + "="*70)
print("CASH RECEIPTS")
print("="*70)

cash_receipts = CashReceiptLine.objects.filter(
    stakeholder=stakeholder,
    workflow_status='AUTHORIZED'
).order_by('date')

for receipt in cash_receipts:
    print(f"\nCash Receipt {receipt.id}:")
    print(f"  Date: {receipt.date}")
    print(f"  Amount: {receipt.debit_amount:,.2f}")
    print(f"  Account: {receipt.account}")
    print(f"  Status: {receipt.workflow_status}")
    print(f"  Capital Posted: {receipt.is_capital_contribution_posted}")

print("\n" + "="*70)
print("CASH PAYMENTS")
print("="*70)

cash_payments = CashPaymentLine.objects.filter(
    stakeholder=stakeholder,
    workflow_status='AUTHORIZED'
).order_by('date')

for payment in cash_payments:
    print(f"\nCash Payment {payment.id}:")
    print(f"  Date: {payment.date}")
    print(f"  Amount: {payment.debit_amount:,.2f}")
    print(f"  Account: {payment.account}")
    print(f"  Status: {payment.workflow_status}")

print("\n" + "="*70)
print("BANK RECEIPTS")
print("="*70)

bank_receipts = BankReceiptLine.objects.filter(
    stakeholder=stakeholder,
    workflow_status='AUTHORIZED'
).order_by('date')

for receipt in bank_receipts:
    print(f"\nBank Receipt {receipt.id}:")
    print(f"  Date: {receipt.date}")
    print(f"  Amount: {receipt.debit_amount:,.2f}")
    print(f"  Account: {receipt.account}")
    print(f"  Status: {receipt.workflow_status}")
    print(f"  Capital Posted: {receipt.is_capital_contribution_posted}")

print("\n" + "="*70)
print("BANK PAYMENTS")
print("="*70)

bank_payments = BankPaymentLine.objects.filter(
    stakeholder=stakeholder,
    workflow_status='AUTHORIZED'
).order_by('date')

for payment in bank_payments:
    print(f"\nBank Payment {payment.id}:")
    print(f"  Date: {payment.date}")
    print(f"  Amount: {payment.debit_amount:,.2f}")
    print(f"  Account: {payment.account}")
    print(f"  Status: {payment.workflow_status}")

print("\n" + "="*70)
print("CAPITAL CONTRIBUTIONS (INVESTMENT HISTORY)")
print("="*70)

contributions = CapitalContribution.objects.filter(
    stakeholder=stakeholder
).order_by('contribution_date')

if contributions.exists():
    total_invested = 0
    total_withdrawn = 0
    
    for contrib in contributions:
        print(f"\nCapital Contribution {contrib.id}:")
        print(f"  Date: {contrib.contribution_date}")
        print(f"  Type: {contrib.contribution_type}")
        print(f"  Amount: {contrib.amount:,.2f}")
        print(f"  Status: {contrib.status}")
        print(f"  Account: {contrib.capital_account}")
        
        if contrib.contribution_type == 'CONTRIBUTION':
            total_invested += contrib.amount
        else:
            total_withdrawn += contrib.amount
    
    print(f"\n{'='*70}")
    print(f"INVESTMENT SUMMARY:")
    print(f"  Total Invested:   {total_invested:>12,.2f}")
    print(f"  Total Withdrawn:  {total_withdrawn:>12,.2f}")
    print(f"  Net Investment:   {(total_invested - total_withdrawn):>12,.2f}")
    print(f"{'='*70}")
else:
    print("\n⚠️  NO CAPITAL CONTRIBUTIONS FOUND!")
    print("   Capital contributions should be auto-created from authorized receipts/payments")

print("\n" + "="*70)
print("EXPECTED INVESTMENT TRACKING:")
print("="*70)
print("\nCash Receipt 13 (100,000) → Capital Contribution CONTRIBUTION")
print("Cash Payment 15 (500) → Capital Contribution WITHDRAWAL")
print("Bank Receipt 7 (1,000) → Capital Contribution CONTRIBUTION")
print("Bank Payment 4 (200) → Capital Contribution WITHDRAWAL")
print("\nExpected Net: 100,000 + 1,000 - 500 - 200 = 100,300")
print("="*70)
