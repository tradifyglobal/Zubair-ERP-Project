"""
HR Module URL Configuration
"""

from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Dashboard
    path('', views.hr_dashboard, name='dashboard'),
    
    # Employee Management
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<int:pk>/payroll-history/', views.employee_payroll_history, name='employee-payroll-history'),
    
    # Payroll Management
    path('payroll/', views.PayrollListView.as_view(), name='payroll-list'),
    path('payroll/create/', views.PayrollCreateView.as_view(), name='payroll-create'),
    path('payroll/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll-detail'),
    path('payroll/<int:pk>/approve/', views.PayrollApproveView.as_view(), name='payroll-approve'),
    path('payroll/<int:pk>/post-to-gl/', views.payroll_post_to_gl, name='payroll-post-gl'),
    
    # Leave Management
    path('leave-requests/', views.LeaveRequestListView.as_view(), name='leave-request-list'),
    path('leave-requests/create/', views.LeaveRequestCreateView.as_view(), name='leave-request-create'),
    path('leave-requests/<int:pk>/approve/', views.approve_leave_request, name='leave-request-approve'),
    
    # Performance Management
    path('performance/', views.PerformanceListView.as_view(), name='performance-list'),
    path('performance/create/', views.PerformanceCreateView.as_view(), name='performance-create'),
    
    # Reports
    path('departments/<int:department_id>/report/', views.department_report, name='department-report'),
]
