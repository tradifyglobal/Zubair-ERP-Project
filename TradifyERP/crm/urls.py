from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('dashboard/', views.CRMDashboardView.as_view(), name='dashboard'),
    
    # Lead URLs
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/new/', views.LeadCreateView.as_view(), name='lead_create'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<int:pk>/edit/', views.LeadUpdateView.as_view(), name='lead_update'),
    path('leads/<int:pk>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
    
    # Opportunity URLs
    path('opportunities/', views.OpportunityListView.as_view(), name='opportunity_list'),
    path('opportunities/new/', views.OpportunityCreateView.as_view(), name='opportunity_create'),
    path('opportunities/<int:pk>/', views.OpportunityDetailView.as_view(), name='opportunity_detail'),
    path('opportunities/<int:pk>/edit/', views.OpportunityUpdateView.as_view(), name='opportunity_update'),
    path('opportunities/<int:pk>/delete/', views.OpportunityDeleteView.as_view(), name='opportunity_delete'),
    
    # Quote URLs
    path('quotes/', views.QuoteListView.as_view(), name='quote_list'),
    path('quotes/new/', views.QuoteCreateView.as_view(), name='quote_create'),
    path('quotes/<int:pk>/', views.QuoteDetailView.as_view(), name='quote_detail'),
    path('quotes/<int:pk>/edit/', views.QuoteUpdateView.as_view(), name='quote_update'),
    path('quotes/<int:pk>/delete/', views.QuoteDeleteView.as_view(), name='quote_delete'),
    
    # Activity URLs
    path('activities/', views.ActivityListView.as_view(), name='activity_list'),
    path('activities/new/', views.ActivityCreateView.as_view(), name='activity_create'),
    path('activities/<int:pk>/', views.ActivityDetailView.as_view(), name='activity_detail'),
    path('activities/<int:pk>/edit/', views.ActivityUpdateView.as_view(), name='activity_update'),
    path('activities/<int:pk>/delete/', views.ActivityDeleteView.as_view(), name='activity_delete'),
    
    # Campaign URLs
    path('campaigns/', views.CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/new/', views.CampaignCreateView.as_view(), name='campaign_create'),
    
    # ===== MASTERS URLs =====
    
    # Territory URLs
    path('territories/', views.TerritoryListView.as_view(), name='territories'),
    path('territories/new/', views.TerritoryCreateView.as_view(), name='territory_create'),
    path('territories/<int:pk>/', views.TerritoryDetailView.as_view(), name='territory_detail'),
    path('territories/<int:pk>/edit/', views.TerritoryUpdateView.as_view(), name='territory_update'),
    path('territories/<int:pk>/delete/', views.TerritoryDeleteView.as_view(), name='territory_delete'),
    
    # Customer Group URLs
    path('customer-groups/', views.CustomerGroupListView.as_view(), name='customer-groups'),
    path('customer-groups/new/', views.CustomerGroupCreateView.as_view(), name='customergroup_create'),
    path('customer-groups/<int:pk>/', views.CustomerGroupDetailView.as_view(), name='customergroup_detail'),
    path('customer-groups/<int:pk>/edit/', views.CustomerGroupUpdateView.as_view(), name='customergroup_update'),
    path('customer-groups/<int:pk>/delete/', views.CustomerGroupDeleteView.as_view(), name='customergroup_delete'),
    
    # Contact URLs
    path('contacts/', views.ContactListView.as_view(), name='contacts'),
    path('contacts/new/', views.ContactCreateView.as_view(), name='contact_create'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/edit/', views.ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),
    
    # Prospect URLs
    path('prospects/', views.ProspectListView.as_view(), name='prospects'),
    path('prospects/new/', views.ProspectCreateView.as_view(), name='prospect_create'),
    path('prospects/<int:pk>/', views.ProspectDetailView.as_view(), name='prospect_detail'),
    path('prospects/<int:pk>/edit/', views.ProspectUpdateView.as_view(), name='prospect_update'),
    path('prospects/<int:pk>/delete/', views.ProspectDeleteView.as_view(), name='prospect_delete'),
    
    # Sales Person URLs
    path('salespersons/', views.SalesPersonListView.as_view(), name='salespersons'),
    path('salespersons/new/', views.SalesPersonCreateView.as_view(), name='salesperson_create'),
    path('salespersons/<int:pk>/', views.SalesPersonDetailView.as_view(), name='salesperson_detail'),
    path('salespersons/<int:pk>/edit/', views.SalesPersonUpdateView.as_view(), name='salesperson_update'),
    path('salespersons/<int:pk>/delete/', views.SalesPersonDeleteView.as_view(), name='salesperson_delete'),
    
    # Lead Source URLs
    path('lead-sources/', views.LeadSourceListView.as_view(), name='lead-sources'),
    path('lead-sources/new/', views.LeadSourceCreateView.as_view(), name='leadsource_create'),
    path('lead-sources/<int:pk>/', views.LeadSourceDetailView.as_view(), name='leadsource_detail'),
    path('lead-sources/<int:pk>/edit/', views.LeadSourceUpdateView.as_view(), name='leadsource_update'),
    path('lead-sources/<int:pk>/delete/', views.LeadSourceDeleteView.as_view(), name='leadsource_delete'),
    
    # ===== SALES PIPELINE URLs =====
    
    # Contract URLs
    path('contracts/', views.ContractListView.as_view(), name='contracts'),
    path('contracts/new/', views.ContractCreateView.as_view(), name='contract_create'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_update'),
    path('contracts/<int:pk>/delete/', views.ContractDeleteView.as_view(), name='contract_delete'),
    
    # Appointment URLs
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),
    path('appointments/new/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment_delete'),
    
    # Communication URLs
    path('communications/', views.CommunicationListView.as_view(), name='communications'),
    path('communications/new/', views.CommunicationCreateView.as_view(), name='communication_create'),
    path('communications/<int:pk>/', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('communications/<int:pk>/edit/', views.CommunicationUpdateView.as_view(), name='communication_update'),
    path('communications/<int:pk>/delete/', views.CommunicationDeleteView.as_view(), name='communication_delete'),
    
    # ===== CAMPAIGN URLs =====
    
    # Email Campaign URLs
    path('email-campaigns/', views.EmailCampaignListView.as_view(), name='email-campaigns'),
    path('email-campaigns/new/', views.EmailCampaignCreateView.as_view(), name='emailcampaign_create'),
    path('email-campaigns/<int:pk>/', views.EmailCampaignDetailView.as_view(), name='emailcampaign_detail'),
    path('email-campaigns/<int:pk>/edit/', views.EmailCampaignUpdateView.as_view(), name='emailcampaign_update'),
    path('email-campaigns/<int:pk>/delete/', views.EmailCampaignDeleteView.as_view(), name='emailcampaign_delete'),
    
    # SMS Campaign URLs
    path('sms-campaigns/', views.SMSCenterListView.as_view(), name='sms-campaigns'),
    path('sms-campaigns/new/', views.SMSCenterCreateView.as_view(), name='smscenter_create'),
    path('sms-campaigns/<int:pk>/', views.SMSCenterDetailView.as_view(), name='smscenter_detail'),
    path('sms-campaigns/<int:pk>/edit/', views.SMSCenterUpdateView.as_view(), name='smscenter_update'),
    path('sms-campaigns/<int:pk>/delete/', views.SMSCenterDeleteView.as_view(), name='smscenter_delete'),
    
    # Email Group URLs
    path('email-groups/', views.EmailGroupListView.as_view(), name='email-groups'),
    path('email-groups/new/', views.EmailGroupCreateView.as_view(), name='emailgroup_create'),
    path('email-groups/<int:pk>/', views.EmailGroupDetailView.as_view(), name='emailgroup_detail'),
    path('email-groups/<int:pk>/edit/', views.EmailGroupUpdateView.as_view(), name='emailgroup_update'),
    path('email-groups/<int:pk>/delete/', views.EmailGroupDeleteView.as_view(), name='emailgroup_delete'),
    
    # ===== MAINTENANCE URLs =====
    
    # Maintenance Schedule URLs
    path('maintenance-schedules/', views.MaintenanceScheduleListView.as_view(), name='maintenance-schedules'),
    path('maintenance-schedules/new/', views.MaintenanceScheduleCreateView.as_view(), name='maintenanceschedule_create'),
    path('maintenance-schedules/<int:pk>/', views.MaintenanceScheduleDetailView.as_view(), name='maintenanceschedule_detail'),
    path('maintenance-schedules/<int:pk>/edit/', views.MaintenanceScheduleUpdateView.as_view(), name='maintenanceschedule_update'),
    path('maintenance-schedules/<int:pk>/delete/', views.MaintenanceScheduleDeleteView.as_view(), name='maintenanceschedule_delete'),
    
    # Maintenance Visit URLs
    path('maintenance-visits/', views.MaintenanceVisitListView.as_view(), name='maintenance-visits'),
    path('maintenance-visits/new/', views.MaintenanceVisitCreateView.as_view(), name='maintenancevisit_create'),
    path('maintenance-visits/<int:pk>/', views.MaintenanceVisitDetailView.as_view(), name='maintenancevisit_detail'),
    path('maintenance-visits/<int:pk>/edit/', views.MaintenanceVisitUpdateView.as_view(), name='maintenancevisit_update'),
    path('maintenance-visits/<int:pk>/delete/', views.MaintenanceVisitDeleteView.as_view(), name='maintenancevisit_delete'),
    
    # Warranty Claim URLs
    path('warranty-claims/', views.WarrantyClaimListView.as_view(), name='warranty-claims'),
    path('warranty-claims/new/', views.WarrantyClaimCreateView.as_view(), name='warrantyclaim_create'),
    path('warranty-claims/<int:pk>/', views.WarrantyClaimDetailView.as_view(), name='warrantyclaim_detail'),
    path('warranty-claims/<int:pk>/edit/', views.WarrantyClaimUpdateView.as_view(), name='warrantyclaim_update'),
    path('warranty-claims/<int:pk>/delete/', views.WarrantyClaimDeleteView.as_view(), name='warrantyclaim_delete'),
    

    path('retail/loyalty-programs/', views.LoyaltyProgramListView.as_view(), name='loyaltyprogram_list'),
    path('retail/loyalty-programs/new/', views.LoyaltyProgramCreateView.as_view(), name='loyaltyprogram_create'),
    
    path('retail/loyalty-members/', views.LoyaltyMemberListView.as_view(), name='loyaltymember_list'),
    path('retail/loyalty-members/new/', views.LoyaltyMemberCreateView.as_view(), name='loyaltymember_create'),
    
    path('retail/pos-transactions/', views.POSTransactionListView.as_view(), name='postransaction_list'),
    path('retail/pos-transactions/new/', views.POSTransactionCreateView.as_view(), name='postransaction_create'),
    path('retail/pos-transactions/<int:pk>/', views.POSTransactionDetailView.as_view(), name='postransaction_detail'),
    
    path('retail/promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    path('retail/promotions/new/', views.PromotionCreateView.as_view(), name='promotion_create'),
    
    path('retail/customer-segments/', views.CustomerSegmentListView.as_view(), name='customersegment_list'),
    path('retail/customer-segments/new/', views.CustomerSegmentCreateView.as_view(), name='customersegment_create'),
    
    # MANUFACTURING CRM URLs
    path('manufacturing/distributors/', views.DistributorListView.as_view(), name='distributor_list'),
    path('manufacturing/orders/', views.DistributorOrderListView.as_view(), name='distributororder_list'),
    path('manufacturing/shipments/', views.OrderShipmentListView.as_view(), name='ordershipment_list'),
    path('manufacturing/service/', views.AfterSalesServiceListView.as_view(), name='aftersalesservice_list'),
    path('manufacturing/warranty/', views.WarrantyRegistrationListView.as_view(), name='warrantyregistration_list'),
]
