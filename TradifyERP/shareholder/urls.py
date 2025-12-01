from django.urls import path
from . import views

app_name = 'shareholder'

urlpatterns = [
    # Dashboard
    path('', views.ShareholderDashboardView.as_view(), name='dashboard'),
    
    # Shareholder URLs
    path('shareholders/', views.ShareholderListView.as_view(), name='stakeholder-list'),
    path('shareholders/<int:pk>/', views.ShareholderDetailView.as_view(), name='stakeholder-detail'),
    path('shareholders/<int:pk>/investment-history/', views.InvestmentHistoryView.as_view(), name='investment-history'),
    path('shareholders/create/', views.ShareholderCreateView.as_view(), name='stakeholder-create'),
    path('shareholders/<int:pk>/edit/', views.ShareholderUpdateView.as_view(), name='stakeholder-edit'),
    path('shareholders/<int:pk>/delete/', views.ShareholderDeleteView.as_view(), name='stakeholder-delete'),

    # Capital Contribution URLs
    path('capital-contributions/', views.CapitalContributionListView.as_view(), name='capital-contribution-list'),
    path('capital-contributions/<int:pk>/', views.CapitalContributionDetailView.as_view(), name='capital-contribution-detail'),
    path('capital-contributions/create/', views.CapitalContributionCreateView.as_view(), name='capital-contribution-create'),
    path('capital-contributions/create/<int:stakeholder_id>/', views.CapitalContributionCreateView.as_view(), name='capital-contribution-create-for-stakeholder'),
    path('capital-contributions/<int:pk>/edit/', views.CapitalContributionUpdateView.as_view(), name='capital-contribution-edit'),

    # Shareholding URLs
    path('shareholdings/', views.ShareholdingListView.as_view(), name='shareholding-list'),
    path('shareholdings/<int:pk>/', views.ShareholdingDetailView.as_view(), name='shareholding-detail'),
    path('shareholdings/create/', views.ShareholdingCreateView.as_view(), name='shareholding-create'),
    path('shareholdings/create/<int:stakeholder_id>/', views.ShareholdingCreateView.as_view(), name='shareholding-create-for-stakeholder'),
    path('shareholdings/<int:pk>/edit/', views.ShareholdingUpdateView.as_view(), name='shareholding-edit'),

    # Investment Tracking URLs
    path('investment-report/', views.ShareholderInvestmentReportView.as_view(), name='investment_report'),
    path('investment-limits/create/', views.ShareholderInvestmentLimitCreateView.as_view(), name='investment_limit_create'),
    path('investment-limits/<int:pk>/edit/', views.ShareholderInvestmentLimitUpdateView.as_view(), name='investment_limit_edit'),
    path('payment-commitments/create/', views.ShareholderPaymentCommitmentCreateView.as_view(), name='payment_commitment_create'),
    path('payment-commitments/<int:pk>/edit/', views.ShareholderPaymentCommitmentUpdateView.as_view(), name='payment_commitment_edit'),
]
