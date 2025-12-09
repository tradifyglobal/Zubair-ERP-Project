"""
HR Module Signals
Automatic GL integration for payroll, benefits, and salary changes.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

from .models import (
    Employee, Payroll, PayrollRecord, SalaryHistory, EmployeeBenefit
)
from accounting.models import LedgerEntry, Account, AuditLog


@receiver(post_save, sender=PayrollRecord)
def calculate_payroll_record(sender, instance, created, **kwargs):
    """Auto-calculate payroll record totals when created/updated."""
    # Skip if flag is set to prevent recursion
    if getattr(instance, '_skip_payroll_signal', False):
        return
    
    if created or not instance.id:
        return
    
    instance.calculate()


@receiver(post_save, sender=PayrollRecord)
def update_payroll_totals(sender, instance, created, update_fields, **kwargs):
    """Update payroll totals when payroll records change."""
    if instance.payroll:
        instance.payroll.calculate_totals()


@receiver(post_save, sender=SalaryHistory)
def create_audit_log_for_salary(sender, instance, created, **kwargs):
    """Log salary changes to audit trail."""
    if not created:
        return
    
    try:
        AuditLog.objects.create(
            user=instance.approved_by or None,
            entity=instance.employee.entity,
            action='SALARY_CHANGE',
            description=f"Salary change: {instance.employee.full_name} from ${instance.salary_before:,.2f} to ${instance.salary_after:,.2f}",
            object_id=instance.id,
            object_type='SalaryHistory',
            old_value=str(instance.salary_before),
            new_value=str(instance.salary_after),
        )
    except Exception:
        pass  # Don't break payroll if audit log fails


@receiver(pre_save, sender=Employee)
def track_employee_changes(sender, instance, **kwargs):
    """Track employee status/salary changes."""
    if not instance.id:
        return
    
    try:
        old_instance = Employee.objects.get(id=instance.id)
        
        # Track salary changes
        if old_instance.base_salary != instance.base_salary:
            SalaryHistory.objects.create(
                employee=instance,
                effective_date=timezone.now().date(),
                salary_before=old_instance.base_salary,
                salary_after=instance.base_salary,
                change_reason='ADJUSTMENT',
                approval_notes='System adjustment'
            )
        
        # Track status changes to GL audit
        if old_instance.status != instance.status:
            AuditLog.objects.create(
                user=None,
                entity=instance.entity,
                action='EMPLOYEE_STATUS_CHANGE',
                description=f"Employee {instance.full_name} status changed from {old_instance.status} to {instance.status}",
                object_id=instance.id,
                object_type='Employee',
                old_value=old_instance.status,
                new_value=instance.status,
            )
    except Employee.DoesNotExist:
        pass


@receiver(post_save, sender=EmployeeBenefit)
def update_benefit_costs(sender, instance, created, **kwargs):
    """Update employee costs when benefits are enrolled."""
    if not created and not instance.is_active:
        return
    
    # This would be used for updating payroll deductions
    # in a full implementation, you'd trigger payroll recalculation


@receiver(post_save, sender=Payroll)
def auto_post_payroll_to_gl(sender, instance, created, update_fields, **kwargs):
    """
    Auto-post payroll to GL if configured.
    Called when payroll status changes to APPROVED.
    """
    if not instance.status == 'APPROVED' or instance.is_posted:
        return
    
    # This is handled by the explicit payroll_post_to_gl view
    # to maintain proper approval workflow
    pass
