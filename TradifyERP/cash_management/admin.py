from django.contrib import admin
from .models import (
    CashPosition, PaymentSchedule, LiquidityForecast, LiquidityForecastLine,
    TreasuryAccount, CashFlowForecastDetail, FXExposure, CashManagementSettings
)


@admin.register(CashPosition)
class CashPositionAdmin(admin.ModelAdmin):
    list_display = ('entity', 'bank_account', 'position_date', 'opening_balance', 'closing_balance', 'is_reconciled')
    list_filter = ('entity', 'bank_account', 'position_date', 'is_reconciled')
    search_fields = ('bank_account__bank_name',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'position_date'


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('entity', 'reference_document', 'payment_amount', 'scheduled_date', 'status')
    list_filter = ('entity', 'status', 'scheduled_date', 'currency')
    search_fields = ('reference_document', 'to_account_details')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'scheduled_date'


@admin.register(LiquidityForecast)
class LiquidityForecastAdmin(admin.ModelAdmin):
    list_display = ('entity', 'forecast_start_date', 'forecast_end_date', 'forecasted_closing_balance', 'risk_level')
    list_filter = ('entity', 'risk_level', 'forecast_start_date')
    search_fields = ('entity__name',)
    readonly_fields = ('created_at', 'updated_at')


class LiquidityForecastLineInline(admin.TabularInline):
    model = LiquidityForecastLine
    extra = 0
    fields = ('forecast_date', 'opening_balance', 'inflows', 'outflows', 'closing_balance')


@admin.register(LiquidityForecastLine)
class LiquidityForecastLineAdmin(admin.ModelAdmin):
    list_display = ('forecast', 'forecast_date', 'opening_balance', 'inflows', 'outflows', 'closing_balance')
    list_filter = ('forecast_date',)
    date_hierarchy = 'forecast_date'


@admin.register(TreasuryAccount)
class TreasuryAccountAdmin(admin.ModelAdmin):
    list_display = ('account_code', 'account_name', 'account_type', 'currency', 'current_balance', 'is_active')
    list_filter = ('entity', 'account_type', 'is_active')
    search_fields = ('account_code', 'account_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CashFlowForecastDetail)
class CashFlowForecastDetailAdmin(admin.ModelAdmin):
    list_display = ('entity', 'period_start', 'category', 'description', 'forecasted_amount', 'actual_amount')
    list_filter = ('entity', 'category', 'period_start')
    search_fields = ('description',)
    date_hierarchy = 'period_start'


@admin.register(FXExposure)
class FXExposureAdmin(admin.ModelAdmin):
    list_display = ('entity', 'exposure_type', 'foreign_currency', 'home_currency', 'foreign_amount', 'is_hedged')
    list_filter = ('entity', 'exposure_type', 'is_hedged', 'exposure_date')
    search_fields = ('reference_number',)
    date_hierarchy = 'exposure_date'


@admin.register(CashManagementSettings)
class CashManagementSettingsAdmin(admin.ModelAdmin):
    list_display = ('entity', 'minimum_operating_cash', 'auto_schedule_payments', 'forecast_horizon_days')
    readonly_fields = ('created_at', 'updated_at')
