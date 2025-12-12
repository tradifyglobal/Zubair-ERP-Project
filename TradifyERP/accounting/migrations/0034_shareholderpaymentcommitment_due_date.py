# Generated migration for adding due_date field to ShareholderPaymentCommitment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0033_add_stakeholder_dates_final'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='due_date',
            field=models.DateField(blank=True, null=True, help_text='Company-set due date for payment'),
        ),
    ]
