# Generated migration to add sub_account field and remove employee field from JournalVoucherLine

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0034_alter_account_account_type_add_sales_purchases'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journalvoucherline',
            name='employee',
        ),
        migrations.AddField(
            model_name='journalvoucherline',
            name='sub_account',
            field=models.ForeignKey(blank=True, help_text='Sub-account for detailed tracking (cascades from main account)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='journal_sub_lines', to='accounting.account'),
        ),
    ]
