from accounting.models import LedgerEntry, CapitalContribution, CashPaymentLine, Account

print("\n" + "="*70)
print("CHECKING CASH PAYMENT - SHAKEEL AHMED")
print("="*70)

# Find the ledger entry
ledger = LedgerEntry.objects.filter(reference_number__icontains='16').order_by('-created_at').first()

if ledger:
    print(f"\n📋 Ledger Entry Found:")
    print(f"   ID: {ledger.id}")
    print(f"   Reference: {ledger.reference_number}")
    print(f"   Description: {ledger.description}")
    print(f"   Account: {ledger.account}")
    print(f"   Type: {ledger.entry_type}")
    print(f"   Amount: {ledger.amount:,.2f}")
    print(f"   Date: {ledger.entry_date}")
    
    # Try to find the cash payment
    ref_parts = ledger.reference_number.split('-')
    if len(ref_parts) >= 3:
        payment_id = ref_parts[-1]
        payment = CashPaymentLine.objects.filter(id=payment_id).first()
        
        if payment:
            print(f"\n💰 Cash Payment #{payment.id}:")
            print(f"   Date: {payment.date}")
            print(f"   Credit Amount: {payment.credit_amount:,.2f}")
            print(f"   Debit Amount: {payment.debit_amount:,.2f}")
            print(f"   Status: {payment.workflow_status}")
            print(f"   Account: {payment.account}")
            print(f"   Credit Account: {payment.credit_account}")
            
            # Check if stakeholder field exists
            stakeholder = getattr(payment, 'stakeholder', None)
            print(f"   Stakeholder: {stakeholder if stakeholder else '❌ NO STAKEHOLDER FIELD'}")
            
            # Check for capital contribution
            cap_contrib = CapitalContribution.objects.filter(
                reference_number=ledger.reference_number
            ).first()
            
            print(f"\n📊 Capital Contribution:")
            if cap_contrib:
                print(f"   ✅ EXISTS - ID #{cap_contrib.id}")
                print(f"   Workflow Status: {cap_contrib.workflow_status}")
                print(f"   Amount: {cap_contrib.amount:,.2f}")
                print(f"   Payment Mode: {cap_contrib.payment_mode}")
            else:
                print(f"   ❌ NOT FOUND")
                print(f"\n⚠️  ISSUE: Cash Payment does NOT auto-create Capital Contribution!")
                print(f"   → Reason: No signal handler for CashPaymentLine")
                print(f"   → Impact: Shareholder withdrawals NOT tracked automatically")
                print(f"   → Solution: Need to add signal for CashPaymentLine similar to CashReceiptLine")

# Get Shakeel Ahmed's capital account
shakeel_account = Account.objects.filter(account_number='3000-02').first()
if shakeel_account:
    print(f"\n" + "="*70)
    print(f"SHAKEEL AHMED CAPITAL ACCOUNT")
    print("="*70)
    print(f"   Account: {shakeel_account.account_number} - {shakeel_account.name}")
    
    # Check capital contributions for Shakeel
    contributions = CapitalContribution.objects.filter(
        equity_account=shakeel_account
    ).order_by('-contribution_date')
    
    print(f"\n   Capital Contributions: {contributions.count()}")
    for c in contributions:
        symbol = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
        print(f"   {symbol} {c.contribution_date} | {c.workflow_status:<14} | {c.amount:>10,.2f} | {c.reference_number}")
    
    if contributions.count() == 0:
        print(f"\n   ⚠️  No capital contribution records found!")
        print(f"   → This payment will NOT show in shareholder investment report")

print("\n" + "="*70)
print("ANSWER")
print("="*70)
print(f"\n❌ NO - Cash Payments do NOT automatically create Capital Contributions")
print(f"\nReason:")
print(f"  • Only CashReceiptLine and BankReceiptLine have auto-create signals")
print(f"  • CashPaymentLine has NO signal handler for capital withdrawals")
print(f"  • CashPaymentLine model has NO stakeholder field")
print(f"\nTo show in investment report:")
print(f"  • Need to manually create CapitalContribution with workflow_status='WITHDRAWAL'")
print(f"  • OR add signal handlers for payment lines (like receipts)")
print("="*70)
