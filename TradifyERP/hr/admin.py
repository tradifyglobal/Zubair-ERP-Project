"""
HR Module Admin Interface
Django admin configuration with GL integration visualization.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count

from .models import (
    Department, Position, Employee, Payroll, PayrollRecord,
    Benefit, EmployeeBenefit, Leave, LeaveBalance, LeaveRequest,
    Performance, Disciplinary, SalaryHistory, Attendance
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin for departments with cost center tracking."""
    list_display = ('name', 'code', 'manager_name', 'employee_count', 'total_salary', 'is_active')
    list_filter = ('is_active', 'entity', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at', 'cost_center_link')
    
    fieldsets = (
        ('Department Info', {
            'fields': ('entity', 'name', 'code', 'description', 'is_active')
        }),
        ('GL Integration', {
            'fields': ('cost_center_account', 'cost_center_link'),
            'description': 'Cost center linked to accounting'
        }),
        ('Management', {
            'fields': ('manager', 'annual_budget')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.full_name}"
        return "—"
    manager_name.short_description = "Manager"
    
    def employee_count(self, obj):
        count = obj.employees.filter(status='ACTIVE').count()
        return format_html(
            '<span class="badge bg-primary">{}</span>',
            count
        )
    employee_count.short_description = "Active Employees"
    
    def total_salary(self, obj):
        total = obj.employees.filter(
            status='ACTIVE'
        ).aggregate(Sum('base_salary'))['base_salary__sum'] or 0
        return f"${total:,.2f}"
    total_salary.short_description = "Total Salary"
    
    def cost_center_link(self, obj):
        if obj.cost_center_account:
            url = reverse('admin:accounting_account_change', args=[obj.cost_center_account.id])
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.cost_center_account.account_name,
                obj.cost_center_account.account_code
            )
        return "—"
    cost_center_link.short_description = "Cost Center Account"


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Admin for job positions with salary ranges."""
    list_display = ('title', 'code', 'department', 'salary_grade', 'salary_range', 'employee_count', 'is_active')
    list_filter = ('is_active', 'entity', 'employment_type', 'salary_grade')
    search_fields = ('title', 'code')
    readonly_fields = ('created_at', 'updated_at', 'expense_account_link')
    
    fieldsets = (
        ('Position Info', {
            'fields': ('entity', 'title', 'code', 'description', 'department', 'is_active')
        }),
        ('Employment Details', {
            'fields': ('employment_type', 'salary_grade', 'min_salary', 'max_salary')
        }),
        ('GL Integration', {
            'fields': ('salary_expense_account', 'expense_account_link'),
            'description': 'GL account for salary postings'
        }),
        ('Reporting', {
            'fields': ('reports_to',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def salary_range(self, obj):
        return f"${obj.min_salary:,.0f} - ${obj.max_salary:,.0f}"
    salary_range.short_description = "Salary Range"
    
    def employee_count(self, obj):
        count = obj.employees.filter(status='ACTIVE').count()
        return format_html(
            '<span class="badge bg-info">{}</span>',
            count
        )
    employee_count.short_description = "Employees"
    
    def expense_account_link(self, obj):
        if obj.salary_expense_account:
            url = reverse('admin:accounting_account_change', args=[obj.salary_expense_account.id])
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.salary_expense_account.account_name,
                obj.salary_expense_account.account_code
            )
        return "—"
    expense_account_link.short_description = "Salary Expense Account"


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin for employee master data."""
    list_display = ('employee_id', 'full_name', 'department', 'position', 'status', 'base_salary', 'hire_date')
    list_filter = ('status', 'entity', 'department', 'position', 'hire_date')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'ssn')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'payroll_account_link')
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone', 'user')
        }),
        ('Tax & Legal', {
            'fields': ('ssn', 'tax_id')
        }),
        ('Employment', {
            'fields': ('entity', 'position', 'department', 'status', 'manager', 'hire_date', 'termination_date')
        }),
        ('Compensation', {
            'fields': ('base_salary', 'salary_currency', 'pay_frequency', 'payroll_account', 'payroll_account_link')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def payroll_account_link(self, obj):
        if obj.payroll_account:
            url = reverse('admin:accounting_account_change', args=[obj.payroll_account.id])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.payroll_account.account_name
            )
        return "—"
    payroll_account_link.short_description = "GL Payroll Account"


class PayrollRecordInline(admin.TabularInline):
    """Inline payroll records in payroll admin."""
    model = PayrollRecord
    extra = 0
    fields = ('employee', 'base_salary', 'gross_amount', 'total_deductions', 'net_amount')
    readonly_fields = ('gross_amount', 'total_deductions', 'net_amount')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    """Admin for payroll runs with GL posting status."""
    list_display = ('payroll_number', 'payroll_date', 'status', 'total_gross', 'total_net', 'posting_status', 'employee_count')
    list_filter = ('status', 'entity', 'payroll_date', 'is_posted')
    search_fields = ('payroll_number',)
    readonly_fields = ('created_at', 'updated_at', 'total_gross', 'total_net', 'journal_entry_link')
    inlines = [PayrollRecordInline]
    
    fieldsets = (
        ('Payroll Info', {
            'fields': ('entity', 'payroll_number', 'payroll_date', 'period_start', 'period_end', 'status')
        }),
        ('Totals', {
            'fields': ('total_gross', 'total_deductions', 'total_taxes', 'total_net'),
            'description': 'Auto-calculated from payroll records'
        }),
        ('GL Posting', {
            'fields': ('is_posted', 'posted_date', 'journal_entry', 'journal_entry_link'),
            'description': 'Integration with General Ledger'
        }),
        ('Approvals', {
            'fields': ('submitted_by', 'submitted_date', 'approved_by', 'approved_date'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def posting_status(self, obj):
        if obj.is_posted:
            return format_html(
                '<span class="badge bg-success">✓ Posted</span>'
            )
        return format_html(
            '<span class="badge bg-warning">Not Posted</span>'
        )
    posting_status.short_description = "GL Status"
    
    def employee_count(self, obj):
        count = obj.payroll_records.count()
        return format_html(
            '<span class="badge bg-primary">{}</span>',
            count
        )
    employee_count.short_description = "Employees"
    
    def journal_entry_link(self, obj):
        if obj.journal_entry:
            url = reverse('admin:accounting_journalentry_change', args=[obj.journal_entry.id])
            return format_html(
                '<a href="{}">View Journal Entry</a>',
                url
            )
        return "—"
    journal_entry_link.short_description = "Journal Entry"


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    """Admin for individual payroll records."""
    list_display = ('payroll', 'employee', 'gross_amount', 'total_deductions', 'net_amount')
    list_filter = ('payroll__payroll_date', 'employee__department')
    search_fields = ('employee__first_name', 'employee__last_name', 'payroll__payroll_number')
    readonly_fields = ('gross_amount', 'total_deductions', 'total_taxes', 'net_amount', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Payroll & Employee', {
            'fields': ('payroll', 'employee')
        }),
        ('Time', {
            'fields': ('days_worked', 'hours_worked')
        }),
        ('Earnings', {
            'fields': ('base_salary', 'overtime_amount', 'bonus', 'allowances', 'gross_amount')
        }),
        ('Deductions', {
            'fields': (
                'employee_tax', 'social_security', 'health_insurance',
                'other_deductions', 'total_deductions'
            )
        }),
        ('Tax & Net', {
            'fields': ('total_taxes', 'net_amount')
        }),
        ('Employer Costs', {
            'fields': ('employer_tax', 'employer_contribution')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    """Admin for benefits."""
    list_display = ('name', 'benefit_type', 'employee_cost', 'employer_cost', 'is_active')
    list_filter = ('benefit_type', 'is_active', 'entity')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmployeeBenefit)
class EmployeeBenefitAdmin(admin.ModelAdmin):
    """Admin for employee benefit enrollments."""
    list_display = ('employee', 'benefit', 'enrollment_date', 'termination_date', 'is_active')
    list_filter = ('benefit', 'enrollment_date', 'is_active')
    search_fields = ('employee__first_name', 'employee__last_name', 'benefit__name')


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    """Admin for leave types."""
    list_display = ('name', 'code', 'annual_allocation', 'can_carry_over', 'max_carryover')
    list_filter = ('accrual_method', 'can_carry_over')
    search_fields = ('name', 'code')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    """Admin for leave balances."""
    list_display = ('employee', 'leave_type', 'year', 'allocated', 'taken', 'available_display')
    list_filter = ('year', 'leave_type')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def available_display(self, obj):
        available = obj.available
        color = 'green' if available > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            f'{available:.1f}'
        )
    available_display.short_description = "Available Days"


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """Admin for leave requests."""
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'duration', 'status_display')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at', 'approval_date')
    
    fieldsets = (
        ('Request Info', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'duration', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'approval_date', 'rejection_reason')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        colors = {
            'DRAFT': 'secondary',
            'SUBMITTED': 'warning',
            'APPROVED': 'success',
            'REJECTED': 'danger',
            'CANCELLED': 'dark',
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_display.short_description = "Status"


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    """Admin for performance reviews."""
    list_display = ('employee', 'review_date', 'overall_rating_display', 'recommended_raise', 'reviewed_by')
    list_filter = ('overall_rating', 'review_date')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def overall_rating_display(self, obj):
        stars = '⭐' * obj.overall_rating
        return format_html('{} ({})', stars, obj.get_overall_rating_display())
    overall_rating_display.short_description = "Overall Rating"


@admin.register(Disciplinary)
class DisciplinaryAdmin(admin.ModelAdmin):
    """Admin for disciplinary actions."""
    list_display = ('employee', 'action_type', 'action_date', 'is_resolved', 'salary_deduction')
    list_filter = ('action_type', 'action_date', 'is_resolved')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SalaryHistory)
class SalaryHistoryAdmin(admin.ModelAdmin):
    """Admin for salary change history."""
    list_display = ('employee', 'effective_date', 'salary_before', 'salary_after', 'change_reason', 'approved_by')
    list_filter = ('change_reason', 'effective_date', 'approved_by')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin for attendance records."""
    list_display = ('employee', 'attendance_date', 'status', 'hours_worked')
    list_filter = ('status', 'attendance_date', 'employee__department')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')
