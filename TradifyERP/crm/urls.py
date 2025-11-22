from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('dashboard/', views.CRMDashboardView.as_view(), name='dashboard'),
    
    # Lead URLs
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/new/', views.LeadCreateView.as_view(), name='lead_create'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    
    # Opportunity URLs
    path('opportunities/', views.OpportunityListView.as_view(), name='opportunity_list'),
    path('opportunities/new/', views.OpportunityCreateView.as_view(), name='opportunity_create'),
    path('opportunities/<int:pk>/', views.OpportunityDetailView.as_view(), name='opportunity_detail'),
    
    # Quote URLs
    path('quotes/', views.QuoteListView.as_view(), name='quote_list'),
    path('quotes/new/', views.QuoteCreateView.as_view(), name='quote_create'),
    
    # Activity URLs
    path('activities/', views.ActivityListView.as_view(), name='activity_list'),
    path('activities/new/', views.ActivityCreateView.as_view(), name='activity_create'),
    
    # Campaign URLs
    path('campaigns/', views.CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/new/', views.CampaignCreateView.as_view(), name='campaign_create'),
    
    # RETAIL & E-COMMERCE URLs
    path('retail/loyalty-programs/', views.LoyaltyProgramListView.as_view(), name='loyaltyprogram_list'),
    path('retail/loyalty-programs/new/', views.LoyaltyProgramCreateView.as_view(), name='loyaltyprogram_create'),
    
    path('retail/loyalty-members/', views.LoyaltyMemberListView.as_view(), name='loyaltymember_list'),
    path('retail/loyalty-members/new/', views.LoyaltyMemberCreateView.as_view(), name='loyaltymember_create'),
    
    path('retail/pos-transactions/', views.POSTransactionListView.as_view(), name='postransaction_list'),
    path('retail/pos-transactions/new/', views.POSTransactionCreateView.as_view(), name='postransaction_create'),
    
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
