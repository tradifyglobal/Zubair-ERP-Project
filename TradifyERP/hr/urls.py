"""
HR Module URL Configuration
"""

from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Employee Management
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<int:pk>/payroll-history/', views.employee_payroll_history, name='employee-payroll-history'),
    
    # Attendance Management
    path('attendances/', views.AttendanceListView.as_view(), name='attendance-list'),
    
    # Positions Management
    path('positions/', views.PositionListView.as_view(), name='position-list'),
    path('positions/create/', views.create_position, name='position-create'),
    path('positions/<int:pk>/', views.PositionDetailView.as_view(), name='position-detail'),
    path('positions/<int:pk>/update/', views.PositionUpdateView.as_view(), name='position-update'),
    
    # Departments Management
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department-create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department-update'),
    
    # Payroll Management
    path('payroll/', views.PayrollListView.as_view(), name='payroll-list'),
    path('payroll/create/', views.PayrollCreateView.as_view(), name='payroll-create'),
    path('payroll/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll-detail'),
    path('payroll/<int:pk>/approve/', views.PayrollApproveView.as_view(), name='payroll-approve'),
    path('payroll/<int:pk>/post-to-gl/', views.payroll_post_to_gl, name='payroll-post-gl'),
    
    # Payroll Records
    path('payroll-records/', views.PayrollRecordListView.as_view(), name='payrollrecord-list'),
    path('payroll-records/<int:pk>/', views.PayrollRecordDetailView.as_view(), name='payrollrecord-detail'),
    
    # Salary History
    path('salary-history/', views.SalaryHistoryListView.as_view(), name='salaryhistory-list'),
    path('salary-history/create/', views.SalaryHistoryCreateView.as_view(), name='salaryhistory-create'),
    path('salary-history/<int:pk>/', views.SalaryHistoryDetailView.as_view(), name='salaryhistory-detail'),
    path('salary-history/<int:pk>/update/', views.SalaryHistoryUpdateView.as_view(), name='salaryhistory-update'),
    
    # Benefits Management
    path('benefits/', views.BenefitListView.as_view(), name='benefit-list'),
    path('benefits/create/', views.BenefitCreateView.as_view(), name='benefit-create'),
    path('benefits/<int:pk>/', views.BenefitDetailView.as_view(), name='benefit-detail'),
    path('benefits/<int:pk>/update/', views.BenefitUpdateView.as_view(), name='benefit-update'),
    
    # Employee Benefits
    path('employee-benefits/', views.EmployeeBenefitListView.as_view(), name='employeebenefit-list'),
    path('employee-benefits/create/', views.EmployeeBenefitCreateView.as_view(), name='employeebenefit-create'),
    path('employee-benefits/<int:pk>/update/', views.EmployeeBenefitUpdateView.as_view(), name='employeebenefit-update'),
    
    # Leave Management
    path('leaves/', views.LeaveListView.as_view(), name='leave-list'),
    path('leaves/create/', views.LeaveCreateView.as_view(), name='leave-create'),
    path('leaves/<int:pk>/', views.LeaveDetailView.as_view(), name='leave-detail'),
    path('leaves/<int:pk>/update/', views.LeaveUpdateView.as_view(), name='leave-update'),
    path('leaves/<int:pk>/submit/', views.submit_leave_for_approval, name='leave-submit'),
    path('leaves/<int:pk>/approve/', views.approve_leave, name='leave-approve'),
    path('leaves/<int:pk>/reject/', views.reject_leave, name='leave-reject'),
    
    # Leave Balances
    path('leave-balances/', views.LeaveBalanceListView.as_view(), name='leavebalance-list'),
    path('leave-balances/create/', views.LeaveBalanceCreateView.as_view(), name='leavebalance-create'),
    path('leave-balances/<int:pk>/', views.LeaveBalanceDetailView.as_view(), name='leavebalance-detail'),
    path('leave-balances/<int:pk>/update/', views.LeaveBalanceUpdateView.as_view(), name='leavebalance-update'),
    
    # Leave Requests
    path('leave-requests/', views.LeaveRequestListView.as_view(), name='leave-request-list'),
    path('leave-requests/create/', views.LeaveRequestCreateView.as_view(), name='leave-request-create'),
    path('leave-requests/<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave-request-detail'),
    path('leave-requests/<int:pk>/approve/', views.approve_leave_request, name='leave-request-approve'),
    path('leave-requests/<int:pk>/reject/', views.reject_leave_request, name='leave-request-reject'),
    
    # Performance Management
    path('performance/', views.PerformanceListView.as_view(), name='performance-list'),
    path('performance/create/', views.PerformanceCreateView.as_view(), name='performance-create'),
    
    # Disciplinary Management
    path('disciplinary/', views.DisciplinaryListView.as_view(), name='disciplinary-list'),
    
    # Reports
    path('departments/<int:department_id>/report/', views.department_report, name='department-report'),
]
