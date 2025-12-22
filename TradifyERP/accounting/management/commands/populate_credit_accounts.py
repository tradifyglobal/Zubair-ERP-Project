from django.core.management.base import BaseCommand
from accounting.models import CashReceiptLine, Account, Entity

class Command(BaseCommand):
    help = 'Populate credit_account for existing cash receipts'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Populating credit_account for cash receipts...")
        self.stdout.write("=" * 60)
        
        entities = Entity.objects.filter(is_active=True)
        total_updated = 0
        
        for entity in entities:
            self.stdout.write(f"\n📍 Processing entity: {entity.name}")
            
            # Try to find Cash account
            cash_account = Account.objects.filter(
                entity=entity,
                account_number='100001',
                is_active=True
            ).first()
            
            if not cash_account:
                cash_account = Account.objects.filter(
                    entity=entity,
                    account_number='1000',
                    is_active=True
                ).first()
            
            if not cash_account:
                self.stdout.write("   ⚠️  No cash account found")
                continue
            
            self.stdout.write(f"   ✓ Found: {cash_account.account_number} - {cash_account.name}")
            
            # Find receipts without credit_account
            receipts_without_credit = CashReceiptLine.objects.filter(
                entity=entity,
                credit_account__isnull=True
            )
            
            count = receipts_without_credit.count()
            if count == 0:
                self.stdout.write("   ✓ All receipts have credit_account")
                continue
            
            self.stdout.write(f"   📦 Found {count} receipts without credit_account")
            
            # Update them
            updated = receipts_without_credit.update(credit_account=cash_account)
            total_updated += updated
            
            self.stdout.write(self.style.SUCCESS(f"   ✅ Updated {updated} receipts"))
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✅ COMPLETE: Updated {total_updated} total receipts"))
