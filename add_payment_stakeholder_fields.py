# Generated migration for adding stakeholder fields to payment models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),  # Replace with your latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='cashpaymentline',
            name='is_capital_contribution_posted',
            field=models.BooleanField(default=False, help_text='Whether capital contribution (withdrawal) was auto-posted from this payment'),
        ),
        migrations.AddField(
            model_name='cashpaymentline',
            name='stakeholder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cash_payment_lines_as_withdrawer', to='accounting.stakeholder'),
        ),
        migrations.AddField(
            model_name='bankpaymentline',
            name='is_capital_contribution_posted',
            field=models.BooleanField(default=False, help_text='Whether capital contribution (withdrawal) was auto-posted from this payment'),
        ),
        migrations.AddField(
            model_name='bankpaymentline',
            name='stakeholder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bank_payment_lines_as_withdrawer', to='accounting.stakeholder'),
        ),
    ]
