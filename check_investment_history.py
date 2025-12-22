from accounting.models import (
    CashReceiptLine, CashPaymentLine, 
    BankReceiptLine, BankPaymentLine,
    CapitalContribution, Stakeholder, Account
)

print("\n" + "="*70)
print("SHAREHOLDER INVESTMENT TRACKING VERIFICATION")
print("="*70)

# Check stakeholder
stakeholder = Stakeholder.objects.get(id=2)
print(f"\nStakeholder: {stakeholder.first_name} {stakeholder.middle_name} {stakeholder.last_name}")

# Get their capital account
capital_account = Account.objects.get(
    entity_id=7,
    account_number='3000-11'
)
print(f"Capital Account: {capital_account}")

# Check all transactions
print("\n" + "="*70)
print("CASH RECEIPTS (Money IN from shareholder)")
print("="*70)

cash_receipts = CashReceiptLine.objects.filter(
    account=capital_account,
    workflow_status='AUTHORIZED'
).order_by('date')

for receipt in cash_receipts:
    print(f"\n✅ Cash Receipt {receipt.id}:")
    print(f"  Date: {receipt.date}")
    print(f"  Amount: {receipt.debit_amount:,.2f}")
    print(f"  Description: {receipt.description}")
    print(f"  Capital Posted: {receipt.is_capital_contribution_posted}")

print("\n" + "="*70)
print("CASH PAYMENTS (Money OUT to shareholder)")
print("="*70)

cash_payments = CashPaymentLine.objects.filter(
    account=capital_account,
    workflow_status='AUTHORIZED'
).order_by('date')

for payment in cash_payments:
    print(f"\n✅ Cash Payment {payment.id}:")
    print(f"  Date: {payment.date}")
    print(f"  Amount: {payment.debit_amount:,.2f}")
    print(f"  Description: {payment.description}")

print("\n" + "="*70)
print("BANK RECEIPTS (Money IN from shareholder via bank)")
print("="*70)

bank_receipts = BankReceiptLine.objects.filter(
    account=capital_account,
    workflow_status='AUTHORIZED'
).order_by('date')

for receipt in bank_receipts:
    print(f"\n✅ Bank Receipt {receipt.id}:")
    print(f"  Date: {receipt.date}")
    print(f"  Amount: {receipt.debit_amount:,.2f}")
    print(f"  Description: {receipt.description}")
    print(f"  Capital Posted: {receipt.is_capital_contribution_posted}")

print("\n" + "="*70)
print("BANK PAYMENTS (Money OUT to shareholder via bank)")
print("="*70)

bank_payments = BankPaymentLine.objects.filter(
    account=capital_account,
    workflow_status='AUTHORIZED'
).order_by('date')

for payment in bank_payments:
    print(f"\n✅ Bank Payment {payment.id}:")
    print(f"  Date: {payment.date}")
    print(f"  Amount: {payment.debit_amount:,.2f}")
    print(f"  Description: {payment.description}")

print("\n" + "="*70)
print("CAPITAL CONTRIBUTIONS (INVESTMENT HISTORY)")
print("="*70)

contributions = CapitalContribution.objects.filter(
    capital_account=capital_account
).order_by('contribution_date')

if contributions.exists():
    total_invested = 0
    total_withdrawn = 0
    
    for contrib in contributions:
        print(f"\n{'✅' if contrib.status == 'APPROVED' else '⏳'} Capital Contribution {contrib.id}:")
        print(f"  Date: {contrib.contribution_date}")
        print(f"  Type: {contrib.contribution_type}")
        print(f"  Amount: {contrib.amount:,.2f}")
        print(f"  Status: {contrib.status}")
        print(f"  Stakeholder: {contrib.stakeholder}")
        print(f"  Method: {contrib.payment_method}")
        
        if contrib.status == 'APPROVED':
            if contrib.contribution_type == 'CONTRIBUTION':
                total_invested += contrib.amount
                print(f"  → Investment IN: {contrib.amount:,.2f}")
            else:
                total_withdrawn += contrib.amount
                print(f"  → Withdrawal OUT: {contrib.amount:,.2f}")
    
    print(f"\n{'='*70}")
    print(f"INVESTMENT SUMMARY FOR {stakeholder.first_name} {stakeholder.last_name}:")
    print(f"{'='*70}")
    print(f"  Total Invested:   {total_invested:>12,.2f}")
    print(f"  Total Withdrawn:  {total_withdrawn:>12,.2f}")
    print(f"  {'─'*42}")
    print(f"  Net Investment:   {(total_invested - total_withdrawn):>12,.2f}")
    print(f"{'='*70}")
else:
    print("\n⚠️  NO CAPITAL CONTRIBUTIONS FOUND!")
    print("   Capital contributions should be auto-created from authorized receipts/payments")
    print("   Check if the signal handler is working correctly.")

print("\n" + "="*70)
print("EXPECTED TRACKING:")
print("="*70)
print("Receipts (CONTRIBUTION):")
print("  Cash Receipt 13:   100,000")
print("  Bank Receipt 7:      1,000")
print("Payments (WITHDRAWAL):")
print("  Cash Payment 15:       500")
print("  Bank Payment 4:        200")
print("─" * 70)
print("Expected Net: 100,000 + 1,000 - 500 - 200 = 100,300")
print("="*70)
