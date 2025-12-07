"""
Initial migration for expenses module
"""

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounting', '0001_initial'),
        ('hr', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_type', models.CharField(choices=[('TRAVEL', 'Travel'), ('MEALS', 'Meals & Entertainment'), ('OFFICE_SUPPLIES', 'Office Supplies'), ('ACCOMMODATION', 'Accommodation'), ('TRANSPORTATION', 'Transportation'), ('UTILITIES', 'Utilities'), ('MAINTENANCE', 'Maintenance'), ('EQUIPMENT', 'Equipment'), ('PROFESSIONAL_SERVICES', 'Professional Services'), ('TRAINING', 'Training & Development'), ('COMMUNICATIONS', 'Communications'), ('OTHER', 'Other')], max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('daily_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('monthly_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('requires_receipt', models.BooleanField(default=True)),
                ('requires_approval', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_categories', to='accounting.entity')),
                ('expense_account', models.ForeignKey(help_text='GL account to post approved expenses', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expense_categories', to='accounting.account')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EmployeeExpenseReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_date', models.DateField(auto_now_add=True)),
                ('period_start', models.DateField(help_text='Period start date for expenses')),
                ('period_end', models.DateField(help_text='Period end date for expenses')),
                ('description', models.TextField(blank=True, help_text='Additional notes about the report')),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('SUBMITTED', 'Submitted'), ('PENDING_REVIEW', 'Pending Review'), ('PENDING_APPROVAL', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('REIMBURSED', 'Reimbursed'), ('POSTED', 'Posted to GL')], default='DRAFT', max_length=20)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_notes', models.TextField(blank=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approval_notes', models.TextField(blank=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('rejected_at', models.DateTimeField(blank=True, null=True)),
                ('reimbursement_date', models.DateField(blank=True, null=True)),
                ('reimbursement_method', models.CharField(blank=True, choices=[('BANK_TRANSFER', 'Bank Transfer'), ('CHECK', 'Check'), ('CASH', 'Cash'), ('PAYROLL', 'Payroll Deduction')], max_length=50)),
                ('is_posted', models.BooleanField(default=False)),
                ('posted_at', models.DateTimeField(blank=True, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total expense amount', max_digits=12)),
                ('total_approved', models.DecimalField(decimal_places=2, default=0, help_text='Total approved amount', max_digits=12)),
                ('total_rejected', models.DecimalField(decimal_places=2, default=0, help_text='Total rejected amount', max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_expense_reports', to='auth.user')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_reports', to='hr.employee')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_reports', to='accounting.entity')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_expense_reports', to='auth.user')),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_expense_reports', to='auth.user')),
            ],
            options={
                'verbose_name_plural': 'Employee Expense Reports',
                'ordering': ['-period_end'],
            },
        ),
        migrations.CreateModel(
            name='EmployeeExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense_date', models.DateField()),
                ('description', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('receipt', models.FileField(blank=True, help_text='Receipt or supporting document', null=True, upload_to='expense_receipts/%Y/%m/')),
                ('receipt_number', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('SUBMITTED', 'Submitted'), ('PENDING_APPROVAL', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('POSTED', 'Posted to GL')], default='DRAFT', max_length=20)),
                ('approval_notes', models.TextField(blank=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('is_posted', models.BooleanField(default=False)),
                ('posted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='expenses.expensecategory')),
                ('ledger_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expense_items', to='accounting.ledgerentry')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='expenses.employeeexpensereport')),
            ],
            options={
                'ordering': ['-expense_date'],
            },
        ),
        migrations.CreateModel(
            name='ExpenseReimbursement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('SCHEDULED', 'Scheduled'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='DRAFT', max_length=20)),
                ('method', models.CharField(choices=[('BANK_TRANSFER', 'Bank Transfer'), ('CHECK', 'Check'), ('CASH', 'Cash'), ('PAYROLL', 'Payroll Deduction')], default='BANK_TRANSFER', max_length=50)),
                ('scheduled_date', models.DateField(blank=True, null=True)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=100, unique=True)),
                ('notes', models.TextField(blank=True)),
                ('is_posted', models.BooleanField(default=False)),
                ('posted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ledger_entries', models.ManyToManyField(blank=True, related_name='reimbursements', to='accounting.ledgerentry')),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reimbursement', to='expenses.employeeexpensereport')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ExpenseBudget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('ANNUAL', 'Annual')], default='MONTHLY', max_length=20)),
                ('budget_amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('spent_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('approved_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='expenses.expensecategory')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_budgets', to='hr.employee')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_budgets', to='accounting.entity')),
            ],
            options={
                'ordering': ['-period_end'],
            },
        ),
        migrations.CreateModel(
            name='ExpenseApprovalWorkflow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING_MANAGER_REVIEW', 'Pending Manager Review'), ('PENDING_FINANCE_APPROVAL', 'Pending Finance Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='DRAFT', max_length=30)),
                ('manager_review_at', models.DateTimeField(blank=True, null=True)),
                ('manager_approved', models.BooleanField(default=False)),
                ('manager_notes', models.TextField(blank=True)),
                ('finance_approved_at', models.DateTimeField(blank=True, null=True)),
                ('finance_approved', models.BooleanField(default=False)),
                ('finance_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('finance_approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_expense_workflows', to='auth.user')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_expense_workflows', to='hr.employee')),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='approval_workflow', to='expenses.employeeexpensereport')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='expensebudget',
            constraint=models.UniqueConstraint(fields=('employee', 'category', 'period_start'), name='unique_employee_category_period'),
        ),
        migrations.AddConstraint(
            model_name='expensecategory',
            constraint=models.UniqueConstraint(fields=('entity', 'category_type'), name='unique_entity_category'),
        ),
    ]
