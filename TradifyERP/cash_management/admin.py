from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Q
from decimal import Decimal
from .models import (
    CashPosition, PaymentSchedule, LiquidityForecast, LiquidityForecastLine,
    TreasuryAccount, CashFlowForecastDetail, FXExposure, CashManagementSettings
)


@admin.register(CashPosition)
class CashPositionAdmin(admin.ModelAdmin):
    list_display = (
        'entity', 'bank_account', 'position_date', 
        'opening_balance_display', 'closing_balance_display', 
        'variance_display', 'reconciliation_status'
    )
    list_filter = ('entity', 'bank_account', 'position_date', 'is_reconciled', 'created_at')
    search_fields = ('bank_account__bank_name', 'entity__name')
    readonly_fields = ('created_at', 'updated_at', 'variance_display')
    date_hierarchy = 'position_date'
    
    fieldsets = (
        ('Position Information', {
            'fields': ('entity', 'bank_account', 'position_date')
        }),
        ('Balances', {
            'fields': ('opening_balance', 'closing_balance', 'variance_display')
        }),
        ('Reconciliation', {
            'fields': ('is_reconciled', 'reconciliation_notes')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def opening_balance_display(self, obj):
        return f"₹{obj.opening_balance:,.2f}"
    opening_balance_display.short_description = 'Opening Balance'
    opening_balance_display.admin_order_field = 'opening_balance'
    
    def closing_balance_display(self, obj):
        return f"₹{obj.closing_balance:,.2f}"
    closing_balance_display.short_description = 'Closing Balance'
    closing_balance_display.admin_order_field = 'closing_balance'
    
    def variance_display(self, obj):
        variance = obj.closing_balance - obj.opening_balance
        color = 'green' if variance >= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">₹{:,.2f}</span>',
            color, variance
        )
    variance_display.short_description = 'Daily Variance'
    
    def reconciliation_status(self, obj):
        if obj.is_reconciled:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Reconciled</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⧗ Pending</span>'
        )
    reconciliation_status.short_description = 'Status'
    
    actions = ['mark_as_reconciled', 'mark_as_unreconciled']
    
    def mark_as_reconciled(self, request, queryset):
        updated = queryset.update(is_reconciled=True)
        self.message_user(request, f'{updated} positions marked as reconciled.')
    mark_as_reconciled.short_description = 'Mark selected as reconciled'
    
    def mark_as_unreconciled(self, request, queryset):
        updated = queryset.update(is_reconciled=False)
        self.message_user(request, f'{updated} positions marked as pending reconciliation.')
    mark_as_unreconciled.short_description = 'Mark selected as pending'


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'entity', 'reference_document', 'amount_display', 
        'scheduled_date', 'status_badge', 'days_to_payment'
    )
    list_filter = ('entity', 'status', 'scheduled_date', 'currency', 'created_at')
    search_fields = ('reference_document', 'to_account_details', 'entity__name')
    readonly_fields = ('created_at', 'updated_at', 'days_to_payment')
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('entity', 'reference_document', 'currency', 'payment_amount')
        }),
        ('Payment Details', {
            'fields': ('to_account_details', 'from_account', 'payment_method')
        }),
        ('Scheduling', {
            'fields': ('due_date', 'scheduled_date', 'days_to_payment')
        }),
        ('Status', {
            'fields': ('status', 'remarks')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        return f"{obj.currency.symbol if obj.currency else '₹'}{obj.payment_amount:,.2f}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'payment_amount'
    
    def status_badge(self, obj):
        status_colors = {
            'PENDING': '#FFA500',
            'APPROVED': '#4CAF50',
            'SCHEDULED': '#2196F3',
            'PAID': '#8BC34A',
            'CANCELLED': '#F44336',
        }
        color = status_colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def days_to_payment(self, obj):
        from datetime import date
        days = (obj.scheduled_date - date.today()).days
        if days < 0:
            color = 'red'
            text = f'{abs(days)} days ago'
        elif days == 0:
            color = 'orange'
            text = 'Today'
        else:
            color = 'green'
            text = f'{days} days'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    days_to_payment.short_description = 'Days'
    
    actions = ['mark_as_approved', 'mark_as_paid', 'mark_as_cancelled']
    
    def mark_as_approved(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='APPROVED')
        self.message_user(request, f'{updated} payments approved.')
    mark_as_approved.short_description = 'Approve selected payments'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='PAID')
        self.message_user(request, f'{updated} payments marked as paid.')
    mark_as_paid.short_description = 'Mark selected as paid'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} payments cancelled.')
    mark_as_cancelled.short_description = 'Cancel selected payments'


class LiquidityForecastLineInline(admin.TabularInline):
    model = LiquidityForecastLine
    extra = 0
    fields = ('forecast_date', 'opening_balance', 'inflows', 'outflows', 'closing_balance')
    readonly_fields = ('closing_balance',)


@admin.register(LiquidityForecast)
class LiquidityForecastAdmin(admin.ModelAdmin):
    list_display = (
        'entity', 'period_display', 'forecasted_balance_display', 
        'risk_level_badge', 'confidence_level'
    )
    list_filter = ('entity', 'risk_level', 'forecast_start_date', 'created_at')
    search_fields = ('entity__name',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'forecast_start_date'
    inlines = [LiquidityForecastLineInline]
    
    fieldsets = (
        ('Forecast Period', {
            'fields': ('entity', 'forecast_start_date', 'forecast_end_date')
        }),
        ('Forecast Data', {
            'fields': ('forecasted_opening_balance', 'forecasted_closing_balance', 'forecasted_inflows', 'forecasted_outflows')
        }),
        ('Risk Assessment', {
            'fields': ('risk_level', 'confidence_level', 'risk_notes')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def period_display(self, obj):
        return f"{obj.forecast_start_date.strftime('%d %b')} - {obj.forecast_end_date.strftime('%d %b %Y')}"
    period_display.short_description = 'Forecast Period'
    period_display.admin_order_field = 'forecast_start_date'
    
    def forecasted_balance_display(self, obj):
        return f"₹{obj.forecasted_closing_balance:,.2f}"
    forecasted_balance_display.short_description = 'Forecasted Balance'
    forecasted_balance_display.admin_order_field = 'forecasted_closing_balance'
    
    def risk_level_badge(self, obj):
        risk_colors = {
            'LOW': '#4CAF50',
            'MEDIUM': '#FFC107',
            'HIGH': '#FF5722',
        }
        color = risk_colors.get(obj.risk_level, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_risk_level_display()
        )
    risk_level_badge.short_description = 'Risk Level'
    risk_level_badge.admin_order_field = 'risk_level'


@admin.register(TreasuryAccount)
class TreasuryAccountAdmin(admin.ModelAdmin):
    list_display = (
        'account_code', 'account_name', 'account_type_display', 
        'currency', 'balance_display', 'active_status'
    )
    list_filter = ('entity', 'account_type', 'is_active', 'currency', 'created_at')
    search_fields = ('account_code', 'account_name', 'entity__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Account Information', {
            'fields': ('entity', 'account_code', 'account_name', 'account_type')
        }),
        ('Account Details', {
            'fields': ('currency', 'current_balance', 'opening_balance')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def account_type_display(self, obj):
        type_icons = {
            'CASH': '💵',
            'CHECKING': '🏦',
            'SAVINGS': '💰',
            'INVESTMENT': '📈',
            'OTHER': '📑',
        }
        icon = type_icons.get(obj.account_type, '📋')
        return f"{icon} {obj.get_account_type_display()}"
    account_type_display.short_description = 'Type'
    account_type_display.admin_order_field = 'account_type'
    
    def balance_display(self, obj):
        return f"{obj.currency.symbol if obj.currency else '₹'}{obj.current_balance:,.2f}"
    balance_display.short_description = 'Current Balance'
    balance_display.admin_order_field = 'current_balance'
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactive</span>')
    active_status.short_description = 'Status'
    active_status.admin_order_field = 'is_active'


@admin.register(CashFlowForecastDetail)
class CashFlowForecastDetailAdmin(admin.ModelAdmin):
    list_display = (
        'entity', 'period_display', 'category_display', 
        'description', 'variance_display'
    )
    list_filter = ('entity', 'category', 'period_start', 'created_at')
    search_fields = ('description', 'entity__name')
    date_hierarchy = 'period_start'
    readonly_fields = ('created_at', 'updated_at', 'variance')
    
    fieldsets = (
        ('Forecast Information', {
            'fields': ('entity', 'period_start', 'period_end', 'category')
        }),
        ('Amounts', {
            'fields': ('forecasted_amount', 'actual_amount', 'variance')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def period_display(self, obj):
        if obj.period_end:
            return f"{obj.period_start.strftime('%d %b')} - {obj.period_end.strftime('%d %b %Y')}"
        return obj.period_start.strftime('%d %b %Y')
    period_display.short_description = 'Period'
    period_display.admin_order_field = 'period_start'
    
    def category_display(self, obj):
        category_icons = {
            'INFLOW': '💰',
            'OUTFLOW': '💸',
            'OPERATING': '⚙️',
            'INVESTMENT': '📈',
            'FINANCING': '🏦',
        }
        icon = category_icons.get(obj.category, '📊')
        return f"{icon} {obj.get_category_display()}" if hasattr(obj, 'get_category_display') else f"{icon} {obj.category}"
    category_display.short_description = 'Category'
    category_display.admin_order_field = 'category'
    
    def variance_display(self, obj):
        if obj.actual_amount is None:
            return '—'
        variance = obj.actual_amount - obj.forecasted_amount
        color = 'green' if variance <= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">₹{:,.2f}</span>',
            color, abs(variance)
        )
    variance_display.short_description = 'Variance'


@admin.register(FXExposure)
class FXExposureAdmin(admin.ModelAdmin):
    list_display = (
        'entity', 'reference_number', 'exposure_type_display', 
        'amount_display', 'hedging_status', 'exposure_date'
    )
    list_filter = ('entity', 'exposure_type', 'is_hedged', 'exposure_date', 'created_at')
    search_fields = ('reference_number', 'entity__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'exposure_date'
    
    fieldsets = (
        ('Exposure Information', {
            'fields': ('entity', 'reference_number', 'exposure_type', 'exposure_date')
        }),
        ('Currencies & Amounts', {
            'fields': ('foreign_currency', 'home_currency', 'foreign_amount', 'home_amount')
        }),
        ('Hedging', {
            'fields': ('is_hedged', 'hedge_instrument', 'hedge_rate')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def exposure_type_display(self, obj):
        type_icons = {
            'RECEIVABLE': '📥',
            'PAYABLE': '📤',
            'INVESTMENT': '📈',
            'LOAN': '🏦',
        }
        icon = type_icons.get(obj.exposure_type, '💱')
        return f"{icon} {obj.get_exposure_type_display()}" if hasattr(obj, 'get_exposure_type_display') else f"{icon} {obj.exposure_type}"
    exposure_type_display.short_description = 'Type'
    exposure_type_display.admin_order_field = 'exposure_type'
    
    def amount_display(self, obj):
        return f"{obj.foreign_currency.code if obj.foreign_currency else 'N/A'} {obj.foreign_amount:,.2f} / ₹{obj.home_amount:,.2f}"
    amount_display.short_description = 'Exposure'
    amount_display.admin_order_field = 'foreign_amount'
    
    def hedging_status(self, obj):
        if obj.is_hedged:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">✓ Hedged</span>'
            )
        return format_html(
            '<span style="background-color: #FF9800; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">⧗ Unhedged</span>'
        )
    hedging_status.short_description = 'Hedging'
    hedging_status.admin_order_field = 'is_hedged'
    
    actions = ['mark_as_hedged', 'mark_as_unhedged']
    
    def mark_as_hedged(self, request, queryset):
        updated = queryset.update(is_hedged=True)
        self.message_user(request, f'{updated} exposures marked as hedged.')
    mark_as_hedged.short_description = 'Mark selected as hedged'
    
    def mark_as_unhedged(self, request, queryset):
        updated = queryset.update(is_hedged=False)
        self.message_user(request, f'{updated} exposures marked as unhedged.')
    mark_as_unhedged.short_description = 'Mark selected as unhedged'


@admin.register(CashManagementSettings)
class CashManagementSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'entity', 'minimum_balance_display', 'auto_scheduling_status', 
        'forecast_horizon', 'updated_ago'
    )
    list_filter = ('entity', 'auto_schedule_payments', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Entity Settings', {
            'fields': ('entity',)
        }),
        ('Cash Management Policies', {
            'fields': (
                'minimum_operating_cash',
                'maximum_credit_limit',
                'auto_schedule_payments',
                'forecast_horizon_days'
            )
        }),
        ('Notification Settings', {
            'fields': (
                'notify_on_low_balance',
                'low_balance_threshold',
                'notify_email'
            )
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def minimum_balance_display(self, obj):
        return f"₹{obj.minimum_operating_cash:,.2f}"
    minimum_balance_display.short_description = 'Min Operating Cash'
    minimum_balance_display.admin_order_field = 'minimum_operating_cash'
    
    def auto_scheduling_status(self, obj):
        if obj.auto_schedule_payments:
            return format_html('<span style="color: green; font-weight: bold;">✓ Enabled</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Disabled</span>')
    auto_scheduling_status.short_description = 'Auto Schedule'
    auto_scheduling_status.admin_order_field = 'auto_schedule_payments'
    
    def forecast_horizon(self, obj):
        return f"{obj.forecast_horizon_days} days"
    forecast_horizon.short_description = 'Forecast Horizon'
    forecast_horizon.admin_order_field = 'forecast_horizon_days'
    
    def updated_ago(self, obj):
        from django.utils.timezone import now
        from django.utils.timesince import timesince
        return timesince(obj.updated_at) + ' ago'
    updated_ago.short_description = 'Last Updated'
    updated_ago.admin_order_field = 'updated_at'
