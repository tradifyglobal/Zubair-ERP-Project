from django.core.management.base import BaseCommand
from accounting.models import Account

class Command(BaseCommand):
    help = 'Delete Capital accounts (3100 and its children)'

    def handle(self, *args, **options):
        # Check what Capital accounts exist
        self.stdout.write("=== Current Capital Accounts ===")
        accounts = Account.objects.filter(account_number__startswith='3100').order_by('account_number')
        for acc in accounts:
            self.stdout.write(f"{acc.account_number} - {acc.name} - {acc.account_type}")
        
        self.stdout.write(f"Total Capital accounts found: {accounts.count()}")
        
        # Delete the accounts
        self.stdout.write("=== Deleting Capital Accounts ===")
        deleted_count = 0
        
        # First delete child accounts (3100-XX)
        child_accounts = Account.objects.filter(account_number__startswith='3100-')
        for acc in child_accounts:
            self.stdout.write(f"Deleting child account: {acc.account_number} - {acc.name}")
            acc.delete()
            deleted_count += 1
        
        # Then delete parent account (3100)
        parent_account = Account.objects.filter(account_number='3100').first()
        if parent_account:
            self.stdout.write(f"Deleting parent account: {parent_account.account_number} - {parent_account.name}")
            parent_account.delete()
            deleted_count += 1
        
        self.stdout.write(f"Total accounts deleted: {deleted_count}")
        
        # Verify deletion
        self.stdout.write("=== Verification - Remaining Capital Accounts ===")
        remaining_accounts = Account.objects.filter(account_number__startswith='3100').order_by('account_number')
        if remaining_accounts:
            for acc in remaining_accounts:
                self.stdout.write(f"{acc.account_number} - {acc.name} - {acc.account_type}")
        else:
            self.stdout.write(self.style.SUCCESS("No Capital accounts remaining - deletion successful!"))