# Generated migration for ExpenseAttachment model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_type', models.CharField(choices=[('RECEIPT', 'Receipt'), ('INVOICE', 'Invoice'), ('BILL', 'Bill'), ('PROOF_OF_PAYMENT', 'Proof of Payment'), ('OTHER', 'Other Supporting Document')], default='RECEIPT', max_length=20)),
                ('file', models.FileField(help_text='Upload receipt, invoice, or supporting document', upload_to='expense_attachments/%Y/%m/')),
                ('file_name', models.CharField(max_length=255)),
                ('file_size', models.BigIntegerField(default=0)),
                ('file_type', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True, help_text='Description of the attachment')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expense_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='expenses.employeeexpense')),
                ('report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='expenses.employeeexpensereport')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_expense_attachments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
