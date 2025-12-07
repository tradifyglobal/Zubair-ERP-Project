"""
Employee Expense Module URLs
"""

from django.urls import path
from .views import (
    ExpenseDashboardView,
    EmployeeExpenseReportListView, EmployeeExpenseReportDetailView,
    EmployeeExpenseReportCreateView, EmployeeExpenseCreateView,
    EmployeeExpenseSubmitView, EmployeeExpenseApproveView, EmployeeExpenseRejectView,
    ExpenseBudgetListView, ExpenseBudgetDetailView,
    ExpenseReimbursementListView, ExpenseReimbursementCreateView,
    ExpenseReimbursementDetailView, ExpenseReimbursementProcessView,
    ExpenseCategoryListView, ExpenseCategoryCreateView,
)

app_name = 'expenses'

urlpatterns = [
    # Dashboard
    path('', ExpenseDashboardView.as_view(), name='dashboard'),
    
    # Expense Reports
    path('reports/', EmployeeExpenseReportListView.as_view(), name='report_list'),
    path('reports/<int:pk>/', EmployeeExpenseReportDetailView.as_view(), name='report_detail'),
    path('reports/create/', EmployeeExpenseReportCreateView.as_view(), name='report_create'),
    path('reports/<int:report_id>/expense/add/', EmployeeExpenseCreateView.as_view(), name='expense_add'),
    path('reports/<int:pk>/submit/', EmployeeExpenseSubmitView.as_view(), name='report_submit'),
    path('reports/<int:pk>/approve/', EmployeeExpenseApproveView.as_view(), name='report_approve'),
    path('reports/<int:pk>/reject/', EmployeeExpenseRejectView.as_view(), name='report_reject'),
    
    # Budgets
    path('budgets/', ExpenseBudgetListView.as_view(), name='budget_list'),
    path('budgets/<int:pk>/', ExpenseBudgetDetailView.as_view(), name='budget_detail'),
    
    # Reimbursements
    path('reimbursements/', ExpenseReimbursementListView.as_view(), name='reimbursement_list'),
    path('reimbursements/<int:report_id>/create/', ExpenseReimbursementCreateView.as_view(), name='reimbursement_create'),
    path('reimbursements/<int:pk>/', ExpenseReimbursementDetailView.as_view(), name='reimbursement_detail'),
    path('reimbursements/<int:pk>/process/', ExpenseReimbursementProcessView.as_view(), name='reimbursement_process'),
    
    # Categories
    path('categories/', ExpenseCategoryListView.as_view(), name='category_list'),
    path('categories/create/', ExpenseCategoryCreateView.as_view(), name='category_create'),
]
