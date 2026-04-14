# Generated migration for ReportAccess model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0036_alter_cashpaymentline_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('accounts', 'Accounts'), ('trial_balance', 'Trial Balance'), ('profit_loss', 'Profit & Loss'), ('balance_sheet', 'Balance Sheet'), ('cash_flow', 'Cash Flow Forecast'), ('shareholder_investment', 'Shareholder Investment Report'), ('capital_contributions', 'Capital Contributions'), ('ledger_analysis', 'Ledger Analysis'), ('cash_transactions', 'Cash Transactions'), ('bank_transactions', 'Bank Transactions'), ('journal_voucher', 'Journal Voucher'), ('stakeholder_report', 'Stakeholder Report'), ('accounting_dashboard', 'Accounting Dashboard'), ('shareholder_dashboard', 'Shareholder Dashboard')], max_length=50)),
                ('access_level', models.CharField(choices=[('view_only', 'View Only'), ('edit', 'Edit'), ('full_access', 'Full Access')], default='view_only', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('entity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.entity')),
                ('granted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='report_access_grants', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'report_type', 'entity')},
            },
        ),
    ]
