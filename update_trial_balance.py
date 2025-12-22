from accounting.models import Entity, TrialBalance
from accounting.trial_balance import calculate_trial_balance
from datetime import date

# Get active entity
entity = Entity.objects.filter(is_active=True).first()
print(f"Active entity: {entity}")

if entity:
    # Calculate current trial balance
    today = date.today()
    tb_data = calculate_trial_balance(entity, today)
    
    print(f"Current calculation:")
    print(f"  Total debits: {tb_data['total_debits']}")
    print(f"  Total credits: {tb_data['total_credits']}")
    print(f"  Is balanced: {tb_data['is_balanced']}")
    print(f"  Account balances:")
    for balance in tb_data['account_balances']:
        print(f"    {balance['account_number']} {balance['account_name']}: Dr {balance['debit_balance']} Cr {balance['credit_balance']}")
    
    # Update saved trial balance record
    tb_record = TrialBalance.objects.filter(
        entity=entity,
        as_of_date=today
    ).first()
    
    if tb_record:
        print(f"\nUpdating saved trial balance record for {today}")
        tb_record.total_debits = tb_data['total_debits']
        tb_record.total_credits = tb_data['total_credits']
        tb_record.is_balanced = tb_data['is_balanced']
        tb_record.save()
        print(f"Updated: Dr {tb_record.total_debits} Cr {tb_record.total_credits} Balanced: {tb_record.is_balanced}")
    else:
        print(f"\nCreating new trial balance record for {today}")
        tb_record = TrialBalance.objects.create(
            entity=entity,
            as_of_date=today,
            total_debits=tb_data['total_debits'],
            total_credits=tb_data['total_credits'],
            is_balanced=tb_data['is_balanced']
        )
        print(f"Created: Dr {tb_record.total_debits} Cr {tb_record.total_credits} Balanced: {tb_record.is_balanced}")

print("Done!")