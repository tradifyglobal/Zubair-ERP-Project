"""
Django Management Command to setup Cash Account and GL Integration
Usage: python manage.py setup_cash_account
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from accounting.models import Account, Entity, Currency, LedgerEntry, CashReceiptLine, AuditLog


class Command(BaseCommand):
    help = 'Setup Cash Account (100001) and verify GL integration for cash receipts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('CASH ACCOUNT & GL INTEGRATION SETUP'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        results = {
            'cash_account': self.create_cash_account(),
            'capital_account': self.verify_capital_account(),
            'model_verification': self.verify_cash_receipt_model(),
        }

        self.show_workflow_summary()

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('SETUP SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*80))

        for check, result in results.items():
            if result:
                self.stdout.write(self.style.SUCCESS(f'✅ PASS: {check}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ FAIL: {check}'))

        if all(results.values()):
            self.stdout.write(self.style.SUCCESS(
                '\n✅ ALL CHECKS PASSED - System is ready for Cash Receipts!\n'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  Some checks failed - Please review above errors\n'
            ))

    def create_cash_account(self):
        """Create the main Cash Account (100001) if it doesn't exist."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('CASH ACCOUNT SETUP'))
        self.stdout.write(self.style.SUCCESS('='*80))

        try:
            # Get default entity (INT001)
            entity = Entity.objects.filter(code='INT001').first()
            if not entity:
                entity = Entity.objects.filter(is_active=True).first()

            if not entity:
                self.stdout.write(self.style.ERROR('❌ ERROR: No active entity found!'))
                return False

            self.stdout.write(self.style.SUCCESS(f'\n✓ Using Entity: {entity.code} - {entity.name}'))

            # Get default currency (INR)
            currency = Currency.objects.filter(code='INR').first()
            if not currency:
                currency = Currency.objects.filter(is_active=True).first()

            if not currency:
                self.stdout.write(self.style.ERROR('❌ ERROR: No active currency found!'))
                return False

            self.stdout.write(self.style.SUCCESS(f'✓ Using Currency: {currency.code}'))

            # Create or get Cash Account
            with transaction.atomic():
                cash_account, created = Account.objects.get_or_create(
                    entity=entity,
                    account_number='100001',
                    defaults={
                        'name': 'Cash',
                        'account_type': 'ASSET',
                        'currency': currency,
                        'description': 'Cash account for receiving cash from shareholders and other receipts',
                        'is_active': True,
                        'opening_balance': Decimal('0.00'),
                        'parent_account': None,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'\n✅ CREATED: Cash Account'))
                    self.stdout.write(f'   Account #: 100001')
                    self.stdout.write(f'   Type: ASSET')
                    self.stdout.write(f'   Name: {cash_account.name}')
                    self.stdout.write(f'   Entity: {entity.code}')
                    self.stdout.write(f'   Currency: {currency.code}')
                else:
                    self.stdout.write(self.style.SUCCESS(f'\n✓ ALREADY EXISTS: Cash Account (100001)'))
                    self.stdout.write(f'   Name: {cash_account.name}')
                    self.stdout.write(f'   Type: {cash_account.account_type}')

            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ERROR creating cash account: {str(e)}'))
            import traceback
            traceback.print_exc()
            return False

    def verify_capital_account(self):
        """Verify the Capital Contribution Account (3000/3100) exists."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('CAPITAL ACCOUNT VERIFICATION'))
        self.stdout.write(self.style.SUCCESS('='*80))

        try:
            entity = Entity.objects.filter(code='INT001').first()
            if not entity:
                entity = Entity.objects.filter(is_active=True).first()

            # Check for account 3000 (main capital account)
            main_account = Account.objects.filter(
                entity=entity,
                account_number='3000'
            ).first()

            if main_account:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Main Capital Account Exists: {main_account.account_number}'))
                self.stdout.write(f'  Name: {main_account.name}')
                self.stdout.write(f'  Type: {main_account.account_type}')
            else:
                self.stdout.write(self.style.WARNING(f'\n⚠️  Main Capital Account NOT found (3000)'))

            # Check for account 3100 (shareholder investment account)
            sub_account = Account.objects.filter(
                entity=entity,
                account_number='3100'
            ).first()

            if sub_account:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Shareholder Investment Account Exists: {sub_account.account_number}'))
                self.stdout.write(f'  Name: {sub_account.name}')
                self.stdout.write(f'  Type: {sub_account.account_type}')
                self.stdout.write(f'  Parent: {sub_account.parent_account}')
            else:
                self.stdout.write(self.style.WARNING(f'\n⚠️  Shareholder Investment Account NOT found (3100)'))

            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ERROR verifying capital account: {str(e)}'))
            return False

    def verify_cash_receipt_model(self):
        """Verify CashReceiptLine model structure."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('CASH RECEIPT LINE MODEL VERIFICATION'))
        self.stdout.write(self.style.SUCCESS('='*80))

        try:
            # Check if CashReceiptLine has required fields
            cash_receipt_fields = [f.name for f in CashReceiptLine._meta.fields]

            required_fields = [
                'account',           # Debit account (e.g., 3100-01 Capital)
                'credit_account',    # Credit account (e.g., 100001 Cash)
                'debit_amount',      # Debit amount
                'credit_amount',     # Credit amount
                'status',            # Status (DRAFT, POSTED, etc.)
                'workflow_status',   # Workflow status
                'stakeholder',       # Stakeholder who contributed
            ]

            self.stdout.write(self.style.SUCCESS('\n✓ CashReceiptLine Model Fields:'))
            all_present = True
            for field in required_fields:
                if field in cash_receipt_fields:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {field}'))
                else:
                    self.stdout.write(self.style.ERROR(f'  ✗ MISSING: {field}'))
                    all_present = False

            return all_present

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ERROR verifying model: {str(e)}'))
            return False

    def show_workflow_summary(self):
        """Show the complete workflow."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('CASH RECEIPT WORKFLOW SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*80))

        workflow_text = """
✓ WORKFLOW STEPS:

1. CASH RECEIPT CREATION (User)
   └─ Navigate to: /accounting/cash-receipts/create/
   └─ Select: Capital Account (e.g., 3100-01)
   └─ Enter: Amount (both Debit and Credit)
   └─ Status: DRAFT

2. APPROVAL (Approver)
   └─ Click: Approve Button
   └─ Status: APPROVED

3. AUTHORIZATION & GL POSTING (Finance)
   └─ Click: Authorize & Post Button
   └─ System Creates GL Entries:
      ├─ DEBIT: 3100-01 (Capital) = Amount
      ├─ CREDIT: 100001 (Cash) = Amount
      └─ Both marked: AUTHORIZED & POSTED
   └─ Status: AUTHORIZED/POSTED

4. GENERAL LEDGER ENTRY
   └─ Both entries visible in GL
   └─ Reference: CASH-RECEIPT-{id}
   └─ Workflow Status: AUTHORIZED
   └─ Posted: Yes

5. SHAREHOLDER INVESTMENT SYNC
   └─ Capital contribution tracked
   └─ Stakeholder linked to receipt
   └─ Amount recorded for dividends/distributions

═══════════════════════════════════════════════════════════════════════════════

ACCOUNT MAPPING:

Debit Account (receipt.account):       3100-01 (Capital Contribution)
Credit Account (receipt.credit_account): 100001 (Cash)

Amount Field Mapping:
- receipt.debit_amount  → GL Debit Entry Amount
- receipt.credit_amount → GL Credit Entry Amount

═══════════════════════════════════════════════════════════════════════════════
"""
        self.stdout.write(workflow_text)
