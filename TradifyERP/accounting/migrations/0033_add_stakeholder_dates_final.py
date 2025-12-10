# Generated migration for adding start_date and end_date fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0032_alter_modulepermission_module'),
    ]

    operations = [
        migrations.AddField(
            model_name='stakeholder',
            name='start_date',
            field=models.DateField(blank=True, null=True, help_text='Start date for profit calculation period'),
        ),
        migrations.AddField(
            model_name='stakeholder',
            name='end_date',
            field=models.DateField(blank=True, null=True, help_text='End date for profit calculation period (leave blank for ongoing)'),
        ),
    ]
