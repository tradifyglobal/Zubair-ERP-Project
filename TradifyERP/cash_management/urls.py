from django.urls import path
from . import views

app_name = 'cash_management'

urlpatterns = [
    path('dashboard/', views.CashManagementDashboardView.as_view(), name='dashboard'),
    path('payments/', views.PaymentScheduleListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentScheduleDetailView.as_view(), name='payment_detail'),
    path('positions/', views.CashPositionListView.as_view(), name='position_list'),
    path('forecasts/', views.LiquidityForecastListView.as_view(), name='forecast_list'),
    path('forecasts/<int:pk>/', views.LiquidityForecastDetailView.as_view(), name='forecast_detail'),
    path('treasury/', views.TreasuryAccountListView.as_view(), name='treasury_list'),
    path('fx-exposure/', views.FXExposureListView.as_view(), name='fx_list'),
]
