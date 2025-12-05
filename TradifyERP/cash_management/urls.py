from django.urls import path
from . import views

app_name = 'cash_management'

urlpatterns = [
    path('dashboard/', views.CashManagementDashboardView.as_view(), name='dashboard'),
    
    # Payment Schedule
    path('payments/', views.PaymentScheduleListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentScheduleCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/', views.PaymentScheduleDetailView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/edit/', views.PaymentScheduleUpdateView.as_view(), name='payment_edit'),
    
    # Cash Position
    path('positions/', views.CashPositionListView.as_view(), name='position_list'),
    path('positions/create/', views.CashPositionCreateView.as_view(), name='position_create'),
    path('positions/<int:pk>/', views.CashPositionDetailView.as_view(), name='position_detail'),
    path('positions/<int:pk>/edit/', views.CashPositionUpdateView.as_view(), name='position_edit'),
    
    # Liquidity Forecast
    path('forecasts/', views.LiquidityForecastListView.as_view(), name='forecast_list'),
    path('forecasts/create/', views.LiquidityForecastCreateView.as_view(), name='forecast_create'),
    path('forecasts/<int:pk>/', views.LiquidityForecastDetailView.as_view(), name='forecast_detail'),
    path('forecasts/<int:pk>/edit/', views.LiquidityForecastUpdateView.as_view(), name='forecast_edit'),
    
    # Treasury Account
    path('treasury/', views.TreasuryAccountListView.as_view(), name='treasury_list'),
    path('treasury/create/', views.TreasuryAccountCreateView.as_view(), name='treasury_create'),
    path('treasury/<int:pk>/', views.TreasuryAccountDetailView.as_view(), name='treasury_detail'),
    path('treasury/<int:pk>/edit/', views.TreasuryAccountUpdateView.as_view(), name='treasury_edit'),
    
    # FX Exposure
    path('fx-exposure/', views.FXExposureListView.as_view(), name='fx_list'),
    path('fx-exposure/create/', views.FXExposureCreateView.as_view(), name='fx_create'),
    path('fx-exposure/<int:pk>/', views.FXExposureDetailView.as_view(), name='fx_detail'),
    path('fx-exposure/<int:pk>/edit/', views.FXExposureUpdateView.as_view(), name='fx_edit'),
    
    # API Endpoints
    path('api/bank-account/<int:bank_account_id>/currency/', views.bank_account_currency, name='api_bank_account_currency'),
]
