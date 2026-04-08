from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0033_internationaltransfertracking_intermediary_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_type',
            field=models.CharField(
                choices=[
                    ('ASSET', 'Asset'),
                    ('LIABILITY', 'Liability'),
                    ('EQUITY', 'Equity'),
                    ('INCOME', 'Income'),
                    ('EXPENSE', 'Expense'),
                    ('SALES', 'Sales'),
                    ('PURCHASES', 'Purchases'),
                ],
                max_length=20,
            ),
        ),
    ]
