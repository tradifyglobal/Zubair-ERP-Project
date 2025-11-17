from django.core.management.base import BaseCommand
from django.db.models import Sum, Q
from accounting.models import ProfitLossReport, Entity, Account, LedgerEntry
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Generate P&L reports from income and expense accounts'

    def handle(self, *args, **options):
        self.stdout.write('Generating P&L reports...')

        # Get all active entities
        entities = Entity.objects.filter(is_active=True)

        if not entities.exists():
            self.stdout.write(self.style.WARNING('No active entities found. Creating default entity...'))
            entity, created = Entity.objects.get_or_create(
                code='DEFAULT',
                defaults={
                    'name': 'Default Entity',
                    'description': 'Default business entity'
                }
            )
        else:
            entity = entities.first()

        # Define reporting period (current month or custom period)
        today = datetime.now().date()
        period_start = today.replace(day=1)
        period_end = today

        self.stdout.write(f'Generating P&L for {entity.code} from {period_start} to {period_end}')

        # Get income accounts
        income_accounts = Account.objects.filter(
            entity=entity,
            account_type='INCOME'
        )

        # Get expense accounts
        expense_accounts = Account.objects.filter(
            entity=entity,
            account_type='EXPENSE'
        )

        # Calculate total income
        income_entries = LedgerEntry.objects.filter(
            account__in=income_accounts,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            is_posted=True
        )

        total_income = 0
        for entry in income_entries:
            if entry.entry_type == 'CREDIT':
                total_income += entry.amount
            else:
                total_income -= entry.amount

        # Calculate total expenses
        expense_entries = LedgerEntry.objects.filter(
            account__in=expense_accounts,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            is_posted=True
        )

        total_expenses = 0
        for entry in expense_entries:
            if entry.entry_type == 'DEBIT':
                total_expenses += entry.amount
            else:
                total_expenses -= entry.amount

        # Calculate net profit
        net_profit = total_income - total_expenses

        # Create or update P&L report
        pl_report, created = ProfitLossReport.objects.get_or_create(
            entity=entity,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_profit': net_profit,
            }
        )

        if not created:
            pl_report.total_income = total_income
            pl_report.total_expenses = total_expenses
            pl_report.net_profit = net_profit
            pl_report.save()

        self.stdout.write(self.style.SUCCESS(f'\n✅ P&L Report Generated Successfully!'))
        self.stdout.write(f'  Period: {period_start} to {period_end}')
        self.stdout.write(f'  Total Income: ${total_income:.2f}')
        self.stdout.write(f'  Total Expenses: ${total_expenses:.2f}')
        self.stdout.write(f'  Net Profit: ${net_profit:.2f}')

        # Display income breakdown
        if income_entries.exists():
            self.stdout.write('\n📊 Income Accounts:')
            for account in income_accounts:
                account_income = 0
                entries = income_entries.filter(account=account)
                for entry in entries:
                    if entry.entry_type == 'CREDIT':
                        account_income += entry.amount
                    else:
                        account_income -= entry.amount
                if account_income > 0:
                    self.stdout.write(f'  {account.account_number} - {account.name}: ${account_income:.2f}')

        # Display expense breakdown
        if expense_entries.exists():
            self.stdout.write('\n💰 Expense Accounts:')
            for account in expense_accounts:
                account_expenses = 0
                entries = expense_entries.filter(account=account)
                for entry in entries:
                    if entry.entry_type == 'DEBIT':
                        account_expenses += entry.amount
                    else:
                        account_expenses -= entry.amount
                if account_expenses > 0:
                    self.stdout.write(f'  {account.account_number} - {account.name}: ${account_expenses:.2f}')
