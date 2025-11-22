from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q, F, Count, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from .models import Lead, Opportunity, Quote, Activity, Campaign, SalesStage
from .forms import LeadForm, OpportunityForm, QuoteForm, ActivityForm, CampaignForm
from .retail_models import LoyaltyProgram, LoyaltyMember, POSTransaction, Promotion, CustomerSegment
from .retail_forms import LoyaltyProgramForm, LoyaltyMemberForm, POSTransactionForm, PromotionForm, CustomerSegmentForm
from manufacturing.models import Distributor, DistributorOrder, AfterSalesService, WarrantyRegistration, OrderShipment
from accounting.models import Entity


class CRMDashboardView(LoginRequiredMixin, TemplateView):
    """CRM Dashboard."""
    template_name = 'crm/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        
        # Lead metrics
        total_leads = Lead.objects.filter(status__in=['NEW', 'CONTACTED', 'QUALIFIED']).count()
        qualified_leads = Lead.objects.filter(status='QUALIFIED').count()
        
        # Opportunity metrics
        open_opportunities = Opportunity.objects.filter(status='OPEN')
        total_opportunity_value = open_opportunities.aggregate(Sum('deal_amount'))['deal_amount__sum'] or Decimal('0')
        
        # Sales forecast (weighted by probability)
        forecasted_revenue = sum(
            opp.weighted_value for opp in open_opportunities
        )
        
        # Today's activities
        today_activities = Activity.objects.filter(
            activity_date__date=today,
            is_completed=False
        ).select_related('assigned_to')
        
        # Recent opportunities
        recent_opps = open_opportunities.order_by('-expected_close_date')[:5]
        
        # Win rate
        won_count = Opportunity.objects.filter(status='WON').count()
        total_count = Opportunity.objects.filter(status__in=['WON', 'LOST']).count()
        win_rate = (won_count / total_count * 100) if total_count > 0 else 0
        
        # RETAIL & E-COMMERCE METRICS
        active_loyalty_programs = LoyaltyProgram.objects.filter(status='ACTIVE').count()
        total_loyalty_members = LoyaltyMember.objects.filter(status='ACTIVE').count()
        pos_revenue_today = POSTransaction.objects.filter(
            created_at__date=today
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        active_promotions = Promotion.objects.filter(
            status='ACTIVE',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).count()
        total_customer_segments = CustomerSegment.objects.count()
        
        # MANUFACTURING METRICS
        total_distributors = Distributor.objects.filter(status='ACTIVE').count()
        pending_orders = DistributorOrder.objects.filter(status='PENDING').count()
        open_service_tickets = AfterSalesService.objects.filter(status__in=['OPEN', 'IN_PROGRESS']).count()
        active_warranties = WarrantyRegistration.objects.filter(is_active=True).count()
        
        context.update({
            'total_leads': total_leads,
            'qualified_leads': qualified_leads,
            'total_opportunity_value': total_opportunity_value,
            'forecasted_revenue': forecasted_revenue,
            'today_activities': today_activities,
            'recent_opportunities': recent_opps,
            'open_opportunity_count': open_opportunities.count(),
            'win_rate': win_rate,
            # Retail metrics
            'active_loyalty_programs': active_loyalty_programs,
            'total_loyalty_members': total_loyalty_members,
            'pos_revenue_today': pos_revenue_today,
            'active_promotions': active_promotions,
            'total_customer_segments': total_customer_segments,
            # Manufacturing metrics
            'total_distributors': total_distributors,
            'pending_orders': pending_orders,
            'open_service_tickets': open_service_tickets,
            'active_warranties': active_warranties,
        })
        
        return context


class LeadListView(LoginRequiredMixin, ListView):
    """List all leads."""
    model = Lead
    template_name = 'crm/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Lead.objects.select_related('assigned_to').order_by('-created_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class LeadDetailView(LoginRequiredMixin, DetailView):
    """Detail view for lead."""
    model = Lead
    template_name = 'crm/lead_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = self.object.activities.all().order_by('-activity_date')
        context['opportunities'] = self.object.opportunities.all()
        return context


class OpportunityListView(LoginRequiredMixin, ListView):
    """List all opportunities."""
    model = Opportunity
    template_name = 'crm/opportunity_list.html'
    context_object_name = 'opportunities'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Opportunity.objects.select_related('customer', 'stage', 'assigned_to').order_by('-expected_close_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class OpportunityDetailView(LoginRequiredMixin, DetailView):
    """Detail view for opportunity."""
    model = Opportunity
    template_name = 'crm/opportunity_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotes'] = self.object.quotes.all()
        context['activities'] = self.object.activities.all().order_by('-activity_date')
        return context


class QuoteListView(LoginRequiredMixin, ListView):
    """List all quotes."""
    model = Quote
    template_name = 'crm/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 50
    
    def get_queryset(self):
        return Quote.objects.select_related('customer', 'opportunity').order_by('-quote_date')


class ActivityListView(LoginRequiredMixin, ListView):
    """List all activities."""
    model = Activity
    template_name = 'crm/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 50
    
    def get_queryset(self):
        return Activity.objects.select_related('assigned_to').order_by('-activity_date')


class CampaignListView(LoginRequiredMixin, ListView):
    """List all campaigns."""
    model = Campaign
    template_name = 'crm/campaign_list.html'
    context_object_name = 'campaigns'
    paginate_by = 20
    
    def get_queryset(self):
        return Campaign.objects.order_by('-start_date')


# CREATE VIEWS
class LeadCreateView(LoginRequiredMixin, CreateView):
    """Create a new lead."""
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('crm:lead_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1  # Set default entity
        form.instance.lead_number = f"LEAD-{uuid4().hex[:8].upper()}"
        return super().form_valid(form)


class OpportunityCreateView(LoginRequiredMixin, CreateView):
    """Create a new opportunity."""
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'crm/opportunity_form.html'
    success_url = reverse_lazy('crm:opportunity_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1  # Set default entity
        return super().form_valid(form)


class QuoteCreateView(LoginRequiredMixin, CreateView):
    """Create a new quote."""
    model = Quote
    form_class = QuoteForm
    template_name = 'crm/quote_form.html'
    success_url = reverse_lazy('crm:quote_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1  # Set default entity
        return super().form_valid(form)


class ActivityCreateView(LoginRequiredMixin, CreateView):
    """Create a new activity."""
    model = Activity
    form_class = ActivityForm
    template_name = 'crm/activity_form.html'
    success_url = reverse_lazy('crm:activity_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1  # Set default entity
        return super().form_valid(form)


class CampaignCreateView(LoginRequiredMixin, CreateView):
    """Create a new campaign."""
    model = Campaign
    form_class = CampaignForm
    template_name = 'crm/campaign_form.html'
    success_url = reverse_lazy('crm:campaign_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1  # Set default entity
        return super().form_valid(form)


# ===== RETAIL & E-COMMERCE VIEWS =====

class LoyaltyProgramListView(LoginRequiredMixin, ListView):
    """List all loyalty programs."""
    model = LoyaltyProgram
    template_name = 'crm/retail/loyaltyprogram_list.html'
    context_object_name = 'programs'
    paginate_by = 20


class LoyaltyProgramCreateView(LoginRequiredMixin, CreateView):
    """Create loyalty program."""
    model = LoyaltyProgram
    form_class = LoyaltyProgramForm
    template_name = 'crm/retail/loyaltyprogram_form.html'
    success_url = reverse_lazy('crm:loyaltyprogram_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1
        return super().form_valid(form)


class LoyaltyMemberListView(LoginRequiredMixin, ListView):
    """List all loyalty members."""
    model = LoyaltyMember
    template_name = 'crm/retail/loyaltymember_list.html'
    context_object_name = 'members'
    paginate_by = 20


class LoyaltyMemberCreateView(LoginRequiredMixin, CreateView):
    """Create loyalty member."""
    model = LoyaltyMember
    form_class = LoyaltyMemberForm
    template_name = 'crm/retail/loyaltymember_form.html'
    success_url = reverse_lazy('crm:loyaltymember_list')


class POSTransactionListView(LoginRequiredMixin, ListView):
    """List POS transactions."""
    model = POSTransaction
    template_name = 'crm/retail/postransaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    ordering = ['-created_at']


class POSTransactionCreateView(LoginRequiredMixin, CreateView):
    """Create POS transaction."""
    model = POSTransaction
    form_class = POSTransactionForm
    template_name = 'crm/retail/postransaction_form.html'
    success_url = reverse_lazy('crm:postransaction_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1
        return super().form_valid(form)


class PromotionListView(LoginRequiredMixin, ListView):
    """List promotions."""
    model = Promotion
    template_name = 'crm/retail/promotion_list.html'
    context_object_name = 'promotions'
    paginate_by = 20


class PromotionCreateView(LoginRequiredMixin, CreateView):
    """Create promotion."""
    model = Promotion
    form_class = PromotionForm
    template_name = 'crm/retail/promotion_form.html'
    success_url = reverse_lazy('crm:promotion_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1
        return super().form_valid(form)


class CustomerSegmentListView(LoginRequiredMixin, ListView):
    """List customer segments."""
    model = CustomerSegment
    template_name = 'crm/retail/customersegment_list.html'
    context_object_name = 'segments'
    paginate_by = 20


class CustomerSegmentCreateView(LoginRequiredMixin, CreateView):
    """Create customer segment."""
    model = CustomerSegment
    form_class = CustomerSegmentForm
    template_name = 'crm/retail/customersegment_form.html'
    success_url = reverse_lazy('crm:customersegment_list')
    
    def form_valid(self, form):
        form.instance.entity_id = 1
        return super().form_valid(form)


# ===== MANUFACTURING CRM VIEWS =====

class DistributorListView(LoginRequiredMixin, ListView):
    """List distributors."""
    model = Distributor
    template_name = 'crm/manufacturing/distributor_list.html'
    context_object_name = 'distributors'
    paginate_by = 20


class DistributorOrderListView(LoginRequiredMixin, ListView):
    """List distributor orders."""
    model = DistributorOrder
    template_name = 'crm/manufacturing/distributororder_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    ordering = ['-order_date']


class OrderShipmentListView(LoginRequiredMixin, ListView):
    """List order shipments."""
    model = OrderShipment
    template_name = 'crm/manufacturing/ordershipment_list.html'
    context_object_name = 'shipments'
    paginate_by = 20


class AfterSalesServiceListView(LoginRequiredMixin, ListView):
    """List after-sales service tickets."""
    model = AfterSalesService
    template_name = 'crm/manufacturing/aftersalesservice_list.html'
    context_object_name = 'services'
    paginate_by = 20


class WarrantyRegistrationListView(LoginRequiredMixin, ListView):
    """List warranty registrations."""
    model = WarrantyRegistration
    template_name = 'crm/manufacturing/warrantyregistration_list.html'
    context_object_name = 'warranties'
    paginate_by = 20
