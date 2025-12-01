from django.contrib import admin
from .models import (
    Lead, SalesStage, Opportunity, Quote, Activity, Campaign, CRMSettings,
    Territory, CustomerGroup, Contact, Prospect, SalesPerson, LeadSource,
    Contract, Appointment, Communication,
    EmailCampaign, SMSCenter, SMSLog, EmailGroup,
    MaintenanceSchedule, MaintenanceVisit, WarrantyClaim, SMSSettings
)
from .retail_models import (
    LoyaltyProgram, LoyaltyMember, PointTransaction, 
    POSTransaction, Promotion, PromotionUsage, CustomerSegment
)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('lead_number', 'lead_name', 'company_name', 'email', 'status', 'lead_score', 'assigned_to')
    list_filter = ('status', 'source', 'created_date', 'lead_score')
    search_fields = ('lead_name', 'company_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_date'


@admin.register(SalesStage)
class SalesStageAdmin(admin.ModelAdmin):
    list_display = ('stage_name', 'sequence', 'win_probability', 'is_active', 'is_final_stage')
    list_filter = ('is_active', 'is_final_stage')


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('opportunity_number', 'opportunity_name', 'customer', 'deal_amount', 'stage', 'status', 'expected_close_date')
    list_filter = ('status', 'stage', 'expected_close_date', 'assigned_to')
    search_fields = ('opportunity_number', 'opportunity_name', 'customer__customer_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'expected_close_date'


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'customer', 'total_amount', 'status', 'quote_date', 'valid_until')
    list_filter = ('status', 'quote_date')
    search_fields = ('quote_number', 'customer__customer_name')
    date_hierarchy = 'quote_date'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('subject', 'activity_type', 'activity_date', 'assigned_to', 'is_completed', 'priority')
    list_filter = ('activity_type', 'is_completed', 'priority', 'activity_date')
    search_fields = ('subject', 'description')
    date_hierarchy = 'activity_date'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign_name', 'campaign_type', 'status', 'start_date', 'end_date', 'budget', 'revenue_generated')
    list_filter = ('status', 'campaign_type', 'start_date')
    search_fields = ('campaign_name',)
    date_hierarchy = 'start_date'


@admin.register(CRMSettings)
class CRMSettingsAdmin(admin.ModelAdmin):
    list_display = ('entity', 'auto_assign_leads', 'lead_qualification_score_threshold', 'sales_forecast_method')
    readonly_fields = ('created_at', 'updated_at')


# ===== RETAIL & E-COMMERCE MODELS =====
@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'loyalty_type', 'status', 'created_at']
    list_filter = ['loyalty_type', 'status']
    search_fields = ['program_name', 'program_code', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoyaltyMember)
class LoyaltyMemberAdmin(admin.ModelAdmin):
    list_display = ['membership_number', 'customer', 'tier_level', 'current_points', 'status']
    list_filter = ['tier_level', 'status']
    search_fields = ['membership_number', 'customer__customer_name']
    readonly_fields = ['created_at', 'updated_at', 'lifetime_points_earned', 'lifetime_points_redeemed']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['member', 'transaction_type', 'points', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['member__membership_number', 'reference_number']
    readonly_fields = ['created_at']


@admin.register(POSTransaction)
class POSTransactionAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'store_location', 'created_at', 'total_amount']
    list_filter = ['store_location', 'created_at']
    search_fields = ['receipt_number', 'member__membership_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['promotion_name', 'promotion_type', 'start_date', 'end_date', 'status']
    list_filter = ['promotion_type', 'status']
    search_fields = ['promotion_name', 'promotion_code']
    readonly_fields = ['created_at']


@admin.register(PromotionUsage)
class PromotionUsageAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'customer', 'usage_date', 'discount_amount']
    list_filter = ['usage_date']
    search_fields = ['promotion__promotion_code']


@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ['segment_name', 'criteria_type', 'is_active']
    list_filter = ['criteria_type', 'is_active']
    search_fields = ['segment_name', 'description']
    readonly_fields = ['created_at', 'updated_at']


# ===== MASTERS MODELS =====

@admin.register(Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ['territory_name', 'region', 'manager', 'annual_target', 'is_active']
    list_filter = ['is_active', 'region']
    search_fields = ['territory_name', 'region']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'group_code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['group_name', 'group_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'company', 'email', 'phone', 'designation', 'department']
    list_filter = ['company', 'department']
    search_fields = ['contact_name', 'email', 'phone', 'company']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ['prospect_name', 'company', 'email', 'phone', 'status', 'probability', 'estimated_value', 'assigned_to']
    list_filter = ['status', 'probability', 'created_date']
    search_fields = ['prospect_name', 'company', 'email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_date'


@admin.register(SalesPerson)
class SalesPersonAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'territory', 'manager', 'monthly_target', 'annual_target', 'is_active']
    list_filter = ['is_active', 'territory', 'manager']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ['source_name', 'source_code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['source_name', 'source_code']
    readonly_fields = ['created_at', 'updated_at']


# ===== SALES PIPELINE MODELS =====

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'contract_name', 'customer', 'contract_value', 'currency', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'currency', 'start_date']
    search_fields = ['contract_number', 'contract_name', 'customer__customer_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'appointment_date', 'assigned_to', 'status', 'duration_minutes', 'location']
    list_filter = ['status', 'appointment_date']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'appointment_date'


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'communication_type', 'communication_date', 'sender', 'recipient_name', 'recipient_email']
    list_filter = ['communication_type', 'communication_date']
    search_fields = ['subject', 'message', 'recipient_email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'communication_date'


# ===== CAMPAIGN MODELS =====

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['campaign_name', 'subject', 'status', 'sent_date', 'opened_count', 'clicked_count']
    list_filter = ['status', 'sent_date']
    search_fields = ['campaign_name', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'opened_count', 'clicked_count']
    date_hierarchy = 'sent_date'


@admin.register(SMSCenter)
class SMSCenterAdmin(admin.ModelAdmin):
    list_display = ['campaign_name', 'status', 'sent_date', 'success_count', 'failed_count']
    list_filter = ['status', 'sent_date']
    search_fields = ['campaign_name', 'message']
    readonly_fields = ['created_at', 'updated_at', 'success_count', 'failed_count']
    date_hierarchy = 'sent_date'


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_phone', 'recipient_name', 'status', 'sent_at', 'delivered_at']
    list_filter = ['status', 'sent_at', 'delivered_at']
    search_fields = ['recipient_phone', 'recipient_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(EmailGroup)
class EmailGroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['group_name', 'description']
    readonly_fields = ['created_at', 'updated_at']


# ===== MAINTENANCE MODELS =====

@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ['schedule_name', 'customer', 'frequency', 'next_maintenance_date', 'assigned_to', 'is_active']
    list_filter = ['frequency', 'is_active', 'next_maintenance_date']
    search_fields = ['schedule_name', 'customer__customer_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'next_maintenance_date'


@admin.register(MaintenanceVisit)
class MaintenanceVisitAdmin(admin.ModelAdmin):
    list_display = ['visit_number', 'maintenance_schedule', 'visit_date', 'status', 'technician', 'total_cost']
    list_filter = ['status', 'visit_date']
    search_fields = ['visit_number', 'work_description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'visit_date'


@admin.register(WarrantyClaim)
class WarrantyClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_number', 'customer', 'product_description', 'claimed_amount', 'approved_amount', 'status', 'claim_date']
    list_filter = ['status', 'claim_date']
    search_fields = ['claim_number', 'product_description', 'customer__customer_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'claim_date'


# ===== SETTINGS MODELS =====

@admin.register(SMSSettings)
class SMSSettingsAdmin(admin.ModelAdmin):
    list_display = ['entity', 'sms_provider', 'sender_id', 'is_enabled']
    list_filter = ['is_enabled', 'sms_provider']
    readonly_fields = ['created_at', 'updated_at']




# ===== MANUFACTURING MODELS =====
# Note: Manufacturing models have been moved to the manufacturing app.
# See: manufacturing/admin.py for Distributor, DistributorContact, DistributorOrder,
# OrderShipment, AfterSalesService, WarrantyRegistration, DistributorPerformance

