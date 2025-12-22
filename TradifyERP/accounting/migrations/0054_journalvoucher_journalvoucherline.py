# Generated manually for Journal Voucher feature

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0053_add_chart_color_preferences'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalVoucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('voucher_date', models.DateField()),
                ('voucher_type', models.CharField(choices=[('SALES_RETURN', 'Sales Return'), ('PURCHASE_RETURN', 'Purchase Return'), ('PAYMENT', 'Payment'), ('RECEIPT', 'Receipt'), ('SHAREHOLDER', 'Shareholder Transaction'), ('EMPLOYEE', 'Employee Transaction'), ('GENERAL', 'General Journal Entry'), ('ADJUSTMENT', 'Adjustment Entry')], max_length=20)),
                ('reference_number', models.CharField(blank=True, help_text='External reference number', max_length=100, null=True)),
                ('reference_type', models.CharField(blank=True, help_text='Type of referenced document', max_length=50, null=True)),
                ('description', models.TextField(help_text='Voucher description/narration')),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING_APPROVAL', 'Pending Approval'), ('APPROVED', 'Approved'), ('POSTED', 'Posted'), ('REJECTED', 'Rejected'), ('CANCELLED', 'Cancelled')], default='DRAFT', max_length=20)),
                ('is_posted', models.BooleanField(default=False)),
                ('posted_date', models.DateTimeField(blank=True, null=True)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='journal_vouchers/')),
                ('notes', models.TextField(blank=True, null=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='journal_vouchers', to='accounting.entity')),
                ('posted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_vouchers', to=settings.AUTH_USER_MODEL)),
                ('prepared_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prepared_vouchers', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_vouchers', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_vouchers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Journal Voucher',
                'verbose_name_plural': 'Journal Vouchers',
                'db_table': 'journal_voucher',
                'ordering': ['-voucher_date', '-voucher_number'],
            },
        ),
        migrations.CreateModel(
            name='JournalVoucherLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_number', models.IntegerField(help_text='Line sequence number')),
                ('entry_type', models.CharField(choices=[('DEBIT', 'Debit'), ('CREDIT', 'Credit')], max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=18)),
                ('description', models.TextField(blank=True, help_text='Line item description', null=True)),
                ('cost_center', models.CharField(blank=True, max_length=100, null=True)),
                ('project', models.CharField(blank=True, max_length=100, null=True)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='journal_lines', to='accounting.account')),
                ('voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='accounting.journalvoucher')),
                ('stakeholder', models.ForeignKey(blank=True, help_text='Link to shareholder if applicable', null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounting.stakeholder')),
                ('employee', models.ForeignKey(blank=True, help_text='Link to employee if applicable', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_journal_lines', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Journal Voucher Line',
                'verbose_name_plural': 'Journal Voucher Lines',
                'db_table': 'journal_voucher_line',
                'ordering': ['line_number'],
                'unique_together': {('voucher', 'line_number')},
            },
        ),
        migrations.AddIndex(
            model_name='journalvoucher',
            index=models.Index(fields=['voucher_date', 'entity'], name='journal_vou_voucher_e820cf_idx'),
        ),
        migrations.AddIndex(
            model_name='journalvoucher',
            index=models.Index(fields=['status'], name='journal_vou_status_fc8a3e_idx'),
        ),
        migrations.AddIndex(
            model_name='journalvoucher',
            index=models.Index(fields=['voucher_type'], name='journal_vou_voucher_05b8d2_idx'),
        ),
    ]
