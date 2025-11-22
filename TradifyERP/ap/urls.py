from django.urls import path
from . import views

app_name = 'ap'

urlpatterns = [
    # Vendor Bills
    path('bills/', views.VendorBillListView.as_view(), name='bill_list'),
    path('bills/create/', views.VendorBillCreateView.as_view(), name='bill_create'),
    path('bills/<int:pk>/', views.VendorBillDetailView.as_view(), name='bill_detail'),
    path('bills/<int:pk>/edit/', views.VendorBillUpdateView.as_view(), name='bill_update'),
    path('bills/<int:pk>/approve/', views.VendorBillApproveView.as_view(), name='bill_approve'),
    path('bills/<int:pk>/post/', views.VendorBillPostView.as_view(), name='bill_post'),
    
    # Vendor Payments
    path('payments/', views.VendorPaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.VendorPaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/', views.VendorPaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/edit/', views.VendorPaymentUpdateView.as_view(), name='payment_update'),
    
    # AP Aging
    path('aging/', views.APAgingReportView.as_view(), name='aging_report'),
    
    # AP Dashboard
    path('dashboard/', views.APDashboardView.as_view(), name='dashboard'),
]
