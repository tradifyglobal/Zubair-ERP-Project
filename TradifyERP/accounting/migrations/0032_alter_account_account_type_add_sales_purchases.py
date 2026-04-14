from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0031_alter_stakeholder_same_as_permanent'),
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
