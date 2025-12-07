"""
Employee Expense Module Forms
"""

from django import forms
from .models import (
    EmployeeExpenseReport, EmployeeExpense, ExpenseCategory,
    ExpenseBudget, ExpenseReimbursement
)


class EmployeeExpenseReportForm(forms.ModelForm):
    """Form for creating/editing expense reports"""
    
    class Meta:
        model = EmployeeExpenseReport
        fields = ['employee', 'period_start', 'period_end', 'description']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this expense report'
            }),
        }


class EmployeeExpenseForm(forms.ModelForm):
    """Form for adding expense items to a report"""
    
    class Meta:
        model = EmployeeExpense
        fields = ['category', 'expense_date', 'description', 'amount', 'receipt', 'receipt_number']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Detailed description of expense'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Invoice/Receipt number (optional)'
            }),
        }


class ExpenseCategoryForm(forms.ModelForm):
    """Form for managing expense categories"""
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'category_type', 'name', 'description', 'expense_account',
            'daily_limit', 'monthly_limit', 'requires_receipt', 'requires_approval'
        ]
        widgets = {
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description'
            }),
            'expense_account': forms.Select(attrs={'class': 'form-select'}),
            'daily_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'monthly_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'requires_receipt': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExpenseBudgetForm(forms.ModelForm):
    """Form for managing employee expense budgets"""
    
    class Meta:
        model = ExpenseBudget
        fields = ['employee', 'category', 'period', 'budget_amount', 'period_start', 'period_end']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'budget_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ExpenseReimbursementForm(forms.ModelForm):
    """Form for processing reimbursements"""
    
    class Meta:
        model = ExpenseReimbursement
        fields = ['method', 'scheduled_date', 'notes']
        widgets = {
            'method': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }


class ExpenseApprovalForm(forms.Form):
    """Form for approving/rejecting expenses"""
    
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Approval or rejection notes'
        }),
        required=False
    )
