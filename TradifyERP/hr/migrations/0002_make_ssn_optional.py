# Generated migration to make SSN field optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='ssn',
            field=models.CharField(
                blank=True,
                help_text='Social Security Number or equivalent',
                max_length=20,
                null=True,
                unique=True
            ),
        ),
    ]
