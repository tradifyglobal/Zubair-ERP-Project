"""
Django Admin configuration for Expense module
"""

from django.contrib import admin
from .models import (
    ExpenseCategory, EmployeeExpenseReport, EmployeeExpense,
    ExpenseBudget, ExpenseApprovalWorkflow, ExpenseReimbursement
)


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity', 'category_type', 'daily_limit', 'monthly_limit', 'is_active')
    list_filter = ('entity', 'category_type', 'is_active', 'requires_receipt')
    search_fields = ('name', 'description')
    ordering = ('entity', 'name')


@admin.register(EmployeeExpenseReport)
class EmployeeExpenseReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'entity', 'period_start', 'period_end', 'status', 'total_amount')
    list_filter = ('entity', 'status', 'period_start', 'period_end')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'total_approved', 'total_rejected')
    fieldsets = (
        ('Basic Information', {
            'fields': ('entity', 'employee', 'period_start', 'period_end', 'description', 'status')
        }),
        ('Submission', {
            'fields': ('submitted_by', 'submitted_at')
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at', 'approval_notes')
        }),
        ('Rejection', {
            'fields': ('rejection_reason', 'rejected_at')
        }),
        ('Reimbursement', {
            'fields': ('reimbursement_date', 'reimbursement_method')
        }),
        ('GL Posting', {
            'fields': ('is_posted', 'posted_at')
        }),
        ('Totals', {
            'fields': ('total_amount', 'total_approved', 'total_rejected')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmployeeExpense)
class EmployeeExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'expense_date', 'amount', 'status', 'is_posted')
    list_filter = ('category', 'status', 'expense_date', 'is_posted')
    search_fields = ('description', 'receipt_number', 'report__employee__user__first_name')
    readonly_fields = ('created_at', 'updated_at', 'posted_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('report', 'category', 'expense_date', 'description', 'amount')
        }),
        ('Documentation', {
            'fields': ('receipt', 'receipt_number')
        }),
        ('Status', {
            'fields': ('status', 'approval_notes', 'rejection_reason')
        }),
        ('GL Posting', {
            'fields': ('is_posted', 'posted_at', 'ledger_entry')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpenseBudget)
class ExpenseBudgetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'category', 'period', 'budget_amount', 'spent_amount', 'is_active')
    list_filter = ('entity', 'period', 'is_active', 'period_start')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Budget Information', {
            'fields': ('entity', 'employee', 'category', 'period')
        }),
        ('Budget Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Amounts', {
            'fields': ('budget_amount', 'spent_amount', 'approved_amount')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpenseApprovalWorkflow)
class ExpenseApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ('report', 'status', 'manager_approved', 'finance_approved')
    list_filter = ('status', 'manager_approved', 'finance_approved')
    search_fields = ('report__employee__user__first_name', 'report__employee__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Workflow Information', {
            'fields': ('report', 'status')
        }),
        ('Manager Review', {
            'fields': ('manager', 'manager_approved', 'manager_review_at', 'manager_notes')
        }),
        ('Finance Approval', {
            'fields': ('finance_approver', 'finance_approved', 'finance_approved_at', 'finance_notes')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpenseReimbursement)
class ExpenseReimbursementAdmin(admin.ModelAdmin):
    list_display = ('report', 'amount', 'method', 'status', 'completion_date')
    list_filter = ('status', 'method', 'completion_date')
    search_fields = ('report__employee__user__first_name', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'posted_at')
    fieldsets = (
        ('Reimbursement Information', {
            'fields': ('report', 'amount')
        }),
        ('Payment Details', {
            'fields': ('method', 'status', 'transaction_id')
        }),
        ('Dates', {
            'fields': ('scheduled_date', 'completion_date')
        }),
        ('GL Posting', {
            'fields': ('is_posted', 'posted_at', 'ledger_entries')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
