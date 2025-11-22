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
]
