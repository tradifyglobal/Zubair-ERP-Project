# Generated migration for adding workflow fields to ShareholderPaymentCommitment

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0035_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='workflow_status',
            field=models.CharField(
                choices=[('DRAFT', 'Draft'), ('SUBMITTED', 'Submitted'), ('FIRST_REVIEW_COMPLETED', 'First Review Completed'), ('REVIEWED', 'Both Reviews Completed'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')],
                default='DRAFT',
                help_text='Workflow approval status',
                max_length=30
            ),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='submitted_by',
            field=models.ForeignKey(blank=True, help_text='User who submitted the commitment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_payment_commitments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, help_text='First reviewer of the commitment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_payment_commitments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='review_notes',
            field=models.TextField(blank=True, help_text='Notes from first reviewer', null=True),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='reviewed_by_2',
            field=models.ForeignKey(blank=True, help_text='Second reviewer of the commitment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_payment_commitments_2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='reviewed_at_2',
            field=models.DateTimeField(blank=True, help_text='When second reviewer completed review', null=True),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='review_notes_2',
            field=models.TextField(blank=True, help_text='Notes from second reviewer', null=True),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='approved_by',
            field=models.ForeignKey(blank=True, help_text='User who approved the commitment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_payment_commitments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='approval_notes',
            field=models.TextField(blank=True, help_text='Notes from approver', null=True),
        ),
        migrations.AddField(
            model_name='shareholderpaymentcommitment',
            name='rejection_reason',
            field=models.TextField(blank=True, help_text='Reason for rejection', null=True),
        ),
    ]
