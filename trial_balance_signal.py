# Add this to the end of /var/www/tradifyerp/accounting/signals.py

@receiver(post_save, sender='accounting.CashReceiptLine')
@receiver(post_save, sender='accounting.CashPaymentLine')
@receiver(post_save, sender='accounting.BankReceiptLine')
@receiver(post_save, sender='accounting.LedgerEntry')
def auto_generate_trial_balance(sender, instance, created, **kwargs):
    """
    Automatically generate/update Trial Balance when transactions are authorized.
    This keeps Trial Balances up-to-date without manual regeneration.
    """
    from accounting.models import TrialBalance
    from accounting.trial_balance import calculate_trial_balance, save_trial_balance
    from datetime import date

    # Only proceed if status is AUTHORIZED
    if hasattr(instance, 'workflow_status') and instance.workflow_status != 'AUTHORIZED':
        return

    try:
        entity = instance.entity
        
        # Use today's date for trial balance
        calc_date = date.today()

        # Calculate trial balance
        tb_data = calculate_trial_balance(entity, calc_date)

        if tb_data:
            # Save or update trial balance
            save_trial_balance(entity, calc_date, force_update=True)
            print(f"Auto-generated Trial Balance for {entity.code} as of {calc_date}")

    except Exception as e:
        print(f"Error auto-generating trial balance: {str(e)}")
