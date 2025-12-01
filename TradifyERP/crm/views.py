from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q, F, Count, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from .models import (
    Lead, Opportunity, Quote, Activity, Campaign, SalesStage,
    Territory, CustomerGroup, Contact, Prospect, SalesPerson, LeadSource,
    Contract, Appointment, Communication,
    EmailCampaign, SMSCenter, EmailGroup,
    MaintenanceSchedule, MaintenanceVisit, WarrantyClaim, SMSSettings
)
from .forms import (
    LeadForm, OpportunityForm, QuoteForm, ActivityForm, CampaignForm,
    TerritoryForm, CustomerGroupForm, ContactForm, ProspectForm, SalesPersonForm, LeadSourceForm,
    ContractForm, AppointmentForm, CommunicationForm,
    EmailCampaignForm, SMSCenterForm, EmailGroupForm,
    MaintenanceScheduleForm, MaintenanceVisitForm, WarrantyClaimForm, SMSSettingsForm
)
from .retail_models import LoyaltyProgram, LoyaltyMember, POSTransaction, Promotion, CustomerSegment
from .retail_forms import LoyaltyProgramForm, LoyaltyMemberForm, POSTransactionForm, PromotionForm, CustomerSegmentForm
from manufacturing.models import Distributor, DistributorOrder, AfterSalesService, WarrantyRegistration, OrderShipment
from accounting.models import Entity
from accounting.mixins import SessionEntityMixin


class CRMDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
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


class LeadListView(SessionEntityMixin, LoginRequiredMixin, ListView):
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


class LeadDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detail view for lead."""
    model = Lead
    template_name = 'crm/lead_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = self.object.activities.all().order_by('-activity_date')
        context['opportunities'] = self.object.opportunities.all()
        return context


class OpportunityListView(SessionEntityMixin, LoginRequiredMixin, ListView):
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


class OpportunityDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detail view for opportunity."""
    model = Opportunity
    template_name = 'crm/opportunity_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotes'] = self.object.quotes.all()
        context['activities'] = self.object.activities.all().order_by('-activity_date')
        return context


class QuoteListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all quotes."""
    model = Quote
    template_name = 'crm/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 50
    
    def get_queryset(self):
        return Quote.objects.select_related('customer', 'opportunity').order_by('-quote_date')


class ActivityListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all activities."""
    model = Activity
    template_name = 'crm/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 50
    
    def get_queryset(self):
        return Activity.objects.select_related('assigned_to').order_by('-activity_date')


class CampaignListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all campaigns."""
    model = Campaign
    template_name = 'crm/campaign_list.html'
    context_object_name = 'campaigns'
    paginate_by = 20
    
    def get_queryset(self):
        return Campaign.objects.order_by('-start_date')


# CREATE VIEWS
class LeadCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new lead."""
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('crm:lead_list')
    
    def form_valid(self, form):
        # Get entity from session instead of hardcoding
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        form.instance.lead_number = f"LEAD-{uuid4().hex[:8].upper()}"
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Log form errors for debugging."""
        print(f"Form errors: {form.errors}")
        print(f"Form data: {form.data}")
        return super().form_invalid(form)


class LeadUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an existing lead."""
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('crm:lead_list')


class LeadDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a lead."""
    model = Lead
    template_name = 'crm/lead_confirm_delete.html'
    success_url = reverse_lazy('crm:lead_list')


class OpportunityCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new opportunity."""
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'crm/opportunity_form.html'
    success_url = reverse_lazy('crm:opportunity_list')
    
    def _ensure_default_stages(self):
        """Ensure default sales stages exist for the session entity."""
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        default_stages = [
            ('Prospect', 1, 10),
            ('Contact', 2, 25),
            ('Proposal', 3, 50),
            ('Negotiation', 4, 75),
            ('Closed', 5, 100, True),
        ]
        
        for stage_data in default_stages:
            stage_name = stage_data[0]
            sequence = stage_data[1]
            probability = stage_data[2]
            is_final = stage_data[3] if len(stage_data) > 3 else False
            
            SalesStage.objects.get_or_create(
                entity=entity,
                sequence=sequence,
                defaults={
                    'stage_name': stage_name,
                    'win_probability': probability,
                    'is_final_stage': is_final,
                    'description': f'{stage_name} stage',
                    'is_active': True
                }
            )
        
        return entity
    
    def get_context_data(self, **kwargs):
        """Ensure stages exist before rendering form."""
        self._ensure_default_stages()
        return super().get_context_data(**kwargs)
    
    def get_form(self, form_class=None):
        """Override to populate stage choices with all stages."""
        # Ensure stages exist before rendering form
        entity = self._ensure_default_stages()
        form = super().get_form(form_class)
        # Get all sales stages for the dropdown (filtered by entity)
        form.fields['stage'].queryset = SalesStage.objects.filter(entity=entity).order_by('sequence')
        return form
    
    def form_valid(self, form):
        entity = self._ensure_default_stages()
        form.instance.entity = entity
        form.instance.opportunity_number = f"OPP-{uuid4().hex[:8].upper()}"
        return super().form_valid(form)


class OpportunityUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an existing opportunity."""
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'crm/opportunity_form.html'
    success_url = reverse_lazy('crm:opportunity_list')
    
    def get_form(self, form_class=None):
        """Override to populate stage choices."""
        form = super().get_form(form_class)
        form.fields['stage'].queryset = SalesStage.objects.all().order_by('sequence')
        return form


class OpportunityDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete an opportunity."""
    model = Opportunity
    template_name = 'crm/opportunity_confirm_delete.html'
    success_url = reverse_lazy('crm:opportunity_list')


class QuoteCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new quote."""
    model = Quote
    form_class = QuoteForm
    template_name = 'crm/quote_form.html'
    success_url = reverse_lazy('crm:quote_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        form.instance.quote_number = f"QUOTE-{uuid4().hex[:8].upper()}"
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class QuoteDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detail view for quote."""
    model = Quote
    template_name = 'crm/quote_detail.html'


class QuoteUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an existing quote."""
    model = Quote
    form_class = QuoteForm
    template_name = 'crm/quote_form.html'
    success_url = reverse_lazy('crm:quote_list')


class QuoteDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a quote."""
    model = Quote
    template_name = 'crm/quote_confirm_delete.html'
    success_url = reverse_lazy('crm:quote_list')


class ActivityCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new activity."""
    model = Activity
    form_class = ActivityForm
    template_name = 'crm/activity_form.html'
    success_url = reverse_lazy('crm:activity_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class ActivityDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detail view for activity."""
    model = Activity
    template_name = 'crm/activity_detail.html'


class ActivityUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an existing activity."""
    model = Activity
    form_class = ActivityForm
    template_name = 'crm/activity_form.html'
    success_url = reverse_lazy('crm:activity_list')


class ActivityDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete an activity."""
    model = Activity
    template_name = 'crm/activity_confirm_delete.html'
    success_url = reverse_lazy('crm:activity_list')


class CampaignCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new campaign."""
    model = Campaign
    form_class = CampaignForm
    template_name = 'crm/campaign_form.html'
    success_url = reverse_lazy('crm:campaign_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


# ===== RETAIL & E-COMMERCE VIEWS =====

class LoyaltyProgramListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all loyalty programs."""
    model = LoyaltyProgram
    template_name = 'crm/retail/loyaltyprogram_list.html'
    context_object_name = 'programs'
    paginate_by = 20


class LoyaltyProgramCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create loyalty program."""
    model = LoyaltyProgram
    form_class = LoyaltyProgramForm
    template_name = 'crm/retail/loyaltyprogram_form.html'
    success_url = reverse_lazy('crm:loyaltyprogram_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class LoyaltyMemberListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all loyalty members."""
    model = LoyaltyMember
    template_name = 'crm/retail/loyaltymember_list.html'
    context_object_name = 'members'
    paginate_by = 20


class LoyaltyMemberCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create loyalty member."""
    model = LoyaltyMember
    form_class = LoyaltyMemberForm
    template_name = 'crm/retail/loyaltymember_form.html'
    success_url = reverse_lazy('crm:loyaltymember_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class POSTransactionListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List POS transactions."""
    model = POSTransaction
    template_name = 'crm/retail/postransaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    ordering = ['-created_at']


class POSTransactionDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detail view for POS transaction."""
    model = POSTransaction
    template_name = 'crm/retail/postransaction_detail.html'


class POSTransactionCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create POS transaction."""
    model = POSTransaction
    form_class = POSTransactionForm
    template_name = 'crm/retail/postransaction_form.html'
    success_url = reverse_lazy('crm:postransaction_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class PromotionListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List promotions."""
    model = Promotion
    template_name = 'crm/retail/promotion_list.html'
    context_object_name = 'promotions'
    paginate_by = 20


class PromotionCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create promotion."""
    model = Promotion
    form_class = PromotionForm
    template_name = 'crm/retail/promotion_form.html'
    success_url = reverse_lazy('crm:promotion_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class CustomerSegmentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List customer segments."""
    model = CustomerSegment
    template_name = 'crm/retail/customersegment_list.html'
    context_object_name = 'segments'
    paginate_by = 20


class CustomerSegmentCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create customer segment."""
    model = CustomerSegment
    form_class = CustomerSegmentForm
    template_name = 'crm/retail/customersegment_form.html'
    success_url = reverse_lazy('crm:customersegment_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


# ===== MASTERS VIEWS =====

class TerritoryListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List territories."""
    model = Territory
    template_name = 'crm/territory_list.html'
    context_object_name = 'territories'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return Territory.objects.filter(entity=entity)


class TerritoryDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display territory details."""
    model = Territory
    template_name = 'crm/territory_detail.html'


class TerritoryCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new territory."""
    model = Territory
    form_class = TerritoryForm
    template_name = 'crm/territory_form.html'
    success_url = reverse_lazy('crm:territories')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class TerritoryUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a territory."""
    model = Territory
    form_class = TerritoryForm
    template_name = 'crm/territory_form.html'
    success_url = reverse_lazy('crm:territories')


class TerritoryDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a territory."""
    model = Territory
    template_name = 'crm/territory_confirm_delete.html'
    success_url = reverse_lazy('crm:territories')


class CustomerGroupListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List customer groups."""
    model = CustomerGroup
    template_name = 'crm/customergroup_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return CustomerGroup.objects.filter(entity=entity)


class CustomerGroupDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display customer group details."""
    model = CustomerGroup
    template_name = 'crm/customergroup_detail.html'


class CustomerGroupCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new customer group."""
    model = CustomerGroup
    form_class = CustomerGroupForm
    template_name = 'crm/customergroup_form.html'
    success_url = reverse_lazy('crm:customer-groups')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class CustomerGroupUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a customer group."""
    model = CustomerGroup
    form_class = CustomerGroupForm
    template_name = 'crm/customergroup_form.html'
    success_url = reverse_lazy('crm:customer-groups')


class CustomerGroupDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a customer group."""
    model = CustomerGroup
    template_name = 'crm/customergroup_confirm_delete.html'
    success_url = reverse_lazy('crm:customer-groups')


class ContactListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List contacts."""
    model = Contact
    template_name = 'crm/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return Contact.objects.filter(entity=entity)


class ContactDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display contact details."""
    model = Contact
    template_name = 'crm/contact_detail.html'


class ContactCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new contact."""
    model = Contact
    form_class = ContactForm
    template_name = 'crm/contact_form.html'
    success_url = reverse_lazy('crm:contacts')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class ContactUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a contact."""
    model = Contact
    form_class = ContactForm
    template_name = 'crm/contact_form.html'
    success_url = reverse_lazy('crm:contacts')


class ContactDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a contact."""
    model = Contact
    template_name = 'crm/contact_confirm_delete.html'
    success_url = reverse_lazy('crm:contacts')


class ProspectListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List prospects."""
    model = Prospect
    template_name = 'crm/prospect_list.html'
    context_object_name = 'prospects'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return Prospect.objects.filter(entity=entity)


class ProspectDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display prospect details."""
    model = Prospect
    template_name = 'crm/prospect_detail.html'


class ProspectCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new prospect."""
    model = Prospect
    form_class = ProspectForm
    template_name = 'crm/prospect_form.html'
    success_url = reverse_lazy('crm:prospects')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class ProspectUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a prospect."""
    model = Prospect
    form_class = ProspectForm
    template_name = 'crm/prospect_form.html'
    success_url = reverse_lazy('crm:prospects')


class ProspectDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a prospect."""
    model = Prospect
    template_name = 'crm/prospect_confirm_delete.html'
    success_url = reverse_lazy('crm:prospects')


class SalesPersonListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List sales persons."""
    model = SalesPerson
    template_name = 'crm/salesperson_list.html'
    context_object_name = 'salespersons'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return SalesPerson.objects.filter(entity=entity)


class SalesPersonDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display sales person details."""
    model = SalesPerson
    template_name = 'crm/salesperson_detail.html'


class SalesPersonCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new sales person."""
    model = SalesPerson
    form_class = SalesPersonForm
    template_name = 'crm/salesperson_form.html'
    success_url = reverse_lazy('crm:salespersons')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class SalesPersonUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a sales person."""
    model = SalesPerson
    form_class = SalesPersonForm
    template_name = 'crm/salesperson_form.html'
    success_url = reverse_lazy('crm:salespersons')


class SalesPersonDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a sales person."""
    model = SalesPerson
    template_name = 'crm/salesperson_confirm_delete.html'
    success_url = reverse_lazy('crm:salespersons')


class LeadSourceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List lead sources."""
    model = LeadSource
    template_name = 'crm/leadsource_list.html'
    context_object_name = 'sources'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return LeadSource.objects.filter(entity=entity)


class LeadSourceDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display lead source details."""
    model = LeadSource
    template_name = 'crm/leadsource_detail.html'


class LeadSourceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new lead source."""
    model = LeadSource
    form_class = LeadSourceForm
    template_name = 'crm/leadsource_form.html'
    success_url = reverse_lazy('crm:lead-sources')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class LeadSourceUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a lead source."""
    model = LeadSource
    form_class = LeadSourceForm
    template_name = 'crm/leadsource_form.html'
    success_url = reverse_lazy('crm:lead-sources')


class LeadSourceDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a lead source."""
    model = LeadSource
    template_name = 'crm/leadsource_confirm_delete.html'
    success_url = reverse_lazy('crm:lead-sources')


# ===== SALES PIPELINE VIEWS =====

class ContractListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List contracts."""
    model = Contract
    template_name = 'crm/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return Contract.objects.filter(entity=entity)


class ContractDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display contract details."""
    model = Contract
    template_name = 'crm/contract_detail.html'


class ContractCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new contract."""
    model = Contract
    form_class = ContractForm
    template_name = 'crm/contract_form.html'
    success_url = reverse_lazy('crm:contracts')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        form.instance.created_by = self.request.user
        
        # Auto-generate contract_number if not provided
        if not form.instance.contract_number:
            form.instance.contract_number = f"CON-{uuid4().hex[:8].upper()}"
        
        if not form.instance.contract_name:
            form.instance.contract_name = '[Contract pending]'
        if not form.instance.contract_value:
            form.instance.contract_value = Decimal('0.00')
        if not form.instance.start_date:
            form.instance.start_date = timezone.now().date()
        if not form.instance.end_date:
            form.instance.end_date = (timezone.now() + timedelta(days=365)).date()
        if not form.instance.status:
            form.instance.status = 'DRAFT'
        return super().form_valid(form)


class ContractUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a contract."""
    model = Contract
    form_class = ContractForm
    template_name = 'crm/contract_form.html'
    success_url = reverse_lazy('crm:contracts')


class ContractDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a contract."""
    model = Contract
    template_name = 'crm/contract_confirm_delete.html'
    success_url = reverse_lazy('crm:contracts')


class AppointmentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List appointments."""
    model = Appointment
    template_name = 'crm/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return Appointment.objects.filter(entity=entity)


class AppointmentDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display appointment details."""
    model = Appointment
    template_name = 'crm/appointment_detail.html'


class AppointmentCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new appointment."""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'crm/appointment_form.html'
    success_url = reverse_lazy('crm:appointments')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class AppointmentUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an appointment."""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'crm/appointment_form.html'
    success_url = reverse_lazy('crm:appointments')


class AppointmentDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete an appointment."""
    model = Appointment
    template_name = 'crm/appointment_confirm_delete.html'
    success_url = reverse_lazy('crm:appointments')


class CommunicationListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List communications."""
    model = Communication
    template_name = 'crm/communication_list.html'
    context_object_name = 'communications'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return Communication.objects.filter(entity=entity)


class CommunicationDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display communication details."""
    model = Communication
    template_name = 'crm/communication_detail.html'


class CommunicationCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new communication."""
    model = Communication
    form_class = CommunicationForm
    template_name = 'crm/communication_form.html'
    success_url = reverse_lazy('crm:communications')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        form.instance.sender = self.request.user
        if not form.instance.communication_type:
            form.instance.communication_type = 'EMAIL'
        if not form.instance.subject:
            form.instance.subject = '[Subject pending]'
        if not form.instance.message:
            form.instance.message = '[Message pending]'
        return super().form_valid(form)


class CommunicationUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a communication."""
    model = Communication
    form_class = CommunicationForm
    template_name = 'crm/communication_form.html'
    success_url = reverse_lazy('crm:communications')


class CommunicationDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a communication."""
    model = Communication
    template_name = 'crm/communication_confirm_delete.html'
    success_url = reverse_lazy('crm:communications')


# ===== CAMPAIGN VIEWS =====

class EmailCampaignListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List email campaigns."""
    model = EmailCampaign
    template_name = 'crm/emailcampaign_list.html'
    context_object_name = 'campaigns'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return EmailCampaign.objects.filter(entity=entity)


class EmailCampaignDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display email campaign details."""
    model = EmailCampaign
    template_name = 'crm/emailcampaign_detail.html'


class EmailCampaignCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new email campaign."""
    model = EmailCampaign
    form_class = EmailCampaignForm
    template_name = 'crm/emailcampaign_form.html'
    success_url = reverse_lazy('crm:email-campaigns')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        form.instance.created_by = self.request.user
        if not form.instance.campaign_name:
            form.instance.campaign_name = '[Campaign pending]'
        if not form.instance.subject:
            form.instance.subject = '[No subject]'
        if not form.instance.email_body:
            form.instance.email_body = '[Content pending]'
        if not form.instance.from_email:
            form.instance.from_email = self.request.user.email or 'noreply@tradifyerp.com'
        return super().form_valid(form)


class EmailCampaignUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an email campaign."""
    model = EmailCampaign
    form_class = EmailCampaignForm
    template_name = 'crm/emailcampaign_form.html'
    success_url = reverse_lazy('crm:email-campaigns')


class EmailCampaignDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete an email campaign."""
    model = EmailCampaign
    template_name = 'crm/emailcampaign_confirm_delete.html'
    success_url = reverse_lazy('crm:email-campaigns')


class SMSCenterListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List SMS campaigns."""
    model = SMSCenter
    template_name = 'crm/smscenter_list.html'
    context_object_name = 'campaigns'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return SMSCenter.objects.filter(entity=entity)


class SMSCenterDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display SMS campaign details."""
    model = SMSCenter
    template_name = 'crm/smscenter_detail.html'


class SMSCenterCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new SMS campaign."""
    model = SMSCenter
    form_class = SMSCenterForm
    template_name = 'crm/smscenter_form.html'
    success_url = reverse_lazy('crm:sms-campaigns')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SMSCenterUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an SMS campaign."""
    model = SMSCenter
    form_class = SMSCenterForm
    template_name = 'crm/smscenter_form.html'
    success_url = reverse_lazy('crm:sms-campaigns')


class SMSCenterDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete an SMS campaign."""
    model = SMSCenter
    template_name = 'crm/smscenter_confirm_delete.html'
    success_url = reverse_lazy('crm:sms-campaigns')


class EmailGroupListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List email groups."""
    model = EmailGroup
    template_name = 'crm/emailgroup_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return EmailGroup.objects.filter(entity=entity)


class EmailGroupDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display email group details."""
    model = EmailGroup
    template_name = 'crm/emailgroup_detail.html'


class EmailGroupCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new email group."""
    model = EmailGroup
    form_class = EmailGroupForm
    template_name = 'crm/emailgroup_form.html'
    success_url = reverse_lazy('crm:email-groups')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class EmailGroupUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an email group."""
    model = EmailGroup
    form_class = EmailGroupForm
    template_name = 'crm/emailgroup_form.html'
    success_url = reverse_lazy('crm:email-groups')


class EmailGroupDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete an email group."""
    model = EmailGroup
    template_name = 'crm/emailgroup_confirm_delete.html'
    success_url = reverse_lazy('crm:email-groups')


# ===== MAINTENANCE VIEWS =====

class MaintenanceScheduleListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List maintenance schedules."""
    model = MaintenanceSchedule
    template_name = 'crm/maintenanceschedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return MaintenanceSchedule.objects.filter(entity=entity)


class MaintenanceScheduleDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display maintenance schedule details."""
    model = MaintenanceSchedule
    template_name = 'crm/maintenanceschedule_detail.html'


class MaintenanceScheduleCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new maintenance schedule."""
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = 'crm/maintenanceschedule_form.html'
    success_url = reverse_lazy('crm:maintenance-schedules')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        return super().form_valid(form)


class MaintenanceScheduleUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a maintenance schedule."""
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = 'crm/maintenanceschedule_form.html'
    success_url = reverse_lazy('crm:maintenance-schedules')


class MaintenanceScheduleDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a maintenance schedule."""
    model = MaintenanceSchedule
    template_name = 'crm/maintenanceschedule_confirm_delete.html'
    success_url = reverse_lazy('crm:maintenance-schedules')


class MaintenanceVisitListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List maintenance visits."""
    model = MaintenanceVisit
    template_name = 'crm/maintenancevisit_list.html'
    context_object_name = 'visits'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return MaintenanceVisit.objects.filter(entity=entity)


class MaintenanceVisitDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display maintenance visit details."""
    model = MaintenanceVisit
    template_name = 'crm/maintenancevisit_detail.html'


class MaintenanceVisitCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new maintenance visit."""
    model = MaintenanceVisit
    form_class = MaintenanceVisitForm
    template_name = 'crm/maintenancevisit_form.html'
    success_url = reverse_lazy('crm:maintenance-visits')
    
    def form_valid(self, form):
        from django.utils import timezone
        from uuid import uuid4
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        
        # Set defaults
        if not form.instance.visit_date:
            form.instance.visit_date = timezone.now().date()
        if not form.instance.status:
            form.instance.status = 'SCHEDULED'
        if not form.instance.visit_number:
            form.instance.visit_number = f"VISIT-{uuid4().hex[:8].upper()}"
        
        return super().form_valid(form)


class MaintenanceVisitUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a maintenance visit."""
    model = MaintenanceVisit
    form_class = MaintenanceVisitForm
    template_name = 'crm/maintenancevisit_form.html'
    success_url = reverse_lazy('crm:maintenance-visits')


class MaintenanceVisitDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a maintenance visit."""
    model = MaintenanceVisit
    template_name = 'crm/maintenancevisit_confirm_delete.html'
    success_url = reverse_lazy('crm:maintenance-visits')


class WarrantyClaimListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List warranty claims."""
    model = WarrantyClaim
    template_name = 'crm/warrantyclaim_list.html'
    context_object_name = 'claims'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        return WarrantyClaim.objects.filter(entity=entity)


class WarrantyClaimDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display warranty claim details."""
    model = WarrantyClaim
    template_name = 'crm/warrantyclaim_detail.html'


class WarrantyClaimCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new warranty claim."""
    model = WarrantyClaim
    form_class = WarrantyClaimForm
    template_name = 'crm/warrantyclaim_form.html'
    success_url = reverse_lazy('crm:warranty-claims')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        form.instance.entity = entity
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class WarrantyClaimUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a warranty claim."""
    model = WarrantyClaim
    form_class = WarrantyClaimForm
    template_name = 'crm/warrantyclaim_form.html'
    success_url = reverse_lazy('crm:warranty-claims')


class WarrantyClaimDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    """Delete a warranty claim."""
    model = WarrantyClaim
    template_name = 'crm/warrantyclaim_confirm_delete.html'
    success_url = reverse_lazy('crm:warranty-claims')




class DistributorListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List distributors."""
    model = Distributor
    template_name = 'crm/manufacturing/distributor_list.html'
    context_object_name = 'distributors'
    paginate_by = 20


class DistributorOrderListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List distributor orders."""
    model = DistributorOrder
    template_name = 'crm/manufacturing/distributororder_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    ordering = ['-order_date']


class OrderShipmentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List order shipments."""
    model = OrderShipment
    template_name = 'crm/manufacturing/ordershipment_list.html'
    context_object_name = 'shipments'
    paginate_by = 20


class AfterSalesServiceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List after-sales service tickets."""
    model = AfterSalesService
    template_name = 'crm/manufacturing/aftersalesservice_list.html'
    context_object_name = 'services'
    paginate_by = 20


class WarrantyRegistrationListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List warranty registrations."""
    model = WarrantyRegistration
    template_name = 'crm/manufacturing/warrantyregistration_list.html'
    context_object_name = 'warranties'
    paginate_by = 20
