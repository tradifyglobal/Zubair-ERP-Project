# SessionEntityMixin Implementation Guide
## Step-by-Step Fix for Entity Segregation

**Status:** Implementation Reference  
**Last Updated:** November 24, 2025

---

## Table of Contents
1. [Understanding SessionEntityMixin](#understanding-sessionentitymixin)
2. [Implementation Steps](#implementation-steps)
3. [Module-by-Module Fixes](#module-by-module-fixes)
4. [Testing Strategy](#testing-strategy)
5. [Common Patterns](#common-patterns)

---

## Understanding SessionEntityMixin

### What It Does
```python
class SessionEntityMixin:
    """
    Automatically filters views by session-selected entity.
    Ensures multi-entity data isolation.
    """
    def dispatch(self, request, *args, **kwargs):
        # Ensure entity_id exists in session
        if 'selected_entity_id' not in request.session:
            # Redirect to entity selector
            return redirect('entity_selector')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = super().get_queryset()
        return queryset.filter(entity_id=entity_id)
```

### Key Benefits
- **Automatic filtering** - No manual entity checks needed
- **Session-based** - Supports entity switching
- **Consistent** - Same pattern across all modules
- **Secure** - Prevents accidental data leakage

### Implementation Requirements
1. Entity model must have `id` field
2. All data models must have `entity` ForeignKey
3. Session must have `selected_entity_id`
4. Middleware must handle entity initialization

---

## Implementation Steps

### Step 1: Verify SessionEntityMixin Import
Every view file needs:
```python
from accounting.mixins import SessionEntityMixin
```

### Step 2: Add to List Views
**Before:**
```python
class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'ap/vendor_list.html'
    
    def get_queryset(self):
        return Vendor.objects.all()
```

**After:**
```python
class VendorListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'ap/vendor_list.html'
    
    def get_queryset(self):
        return super().get_queryset()  # Mixin handles filtering
```

**Key:** Put SessionEntityMixin FIRST in inheritance order

### Step 3: Add to Detail Views
**Before:**
```python
class VendorDetailView(LoginRequiredMixin, DetailView):
    model = Vendor
    template_name = 'ap/vendor_detail.html'
```

**After:**
```python
class VendorDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    model = Vendor
    template_name = 'ap/vendor_detail.html'
```

### Step 4: Add to Create Views
**Before:**
```python
class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    
    def form_valid(self, form):
        form.instance.entity = Entity.objects.first()  # WRONG!
        return super().form_valid(form)
```

**After:**
```python
class VendorCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        form.instance.entity_id = entity_id
        return super().form_valid(form)
```

### Step 5: Add to Update Views
**Before:**
```python
class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
```

**After:**
```python
class VendorUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
```

### Step 6: Add to Delete Views
**Before:**
```python
class VendorDeleteView(LoginRequiredMixin, DeleteView):
    model = Vendor
```

**After:**
```python
class VendorDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = Vendor
```

### Step 7: Dashboard Views
**Before:**
```python
class APDashboardView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bills'] = VendorBill.objects.all()  # ALL entities!
        return context
```

**After:**
```python
class APDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        context['bills'] = VendorBill.objects.filter(entity_id=entity_id)
        return context
```

---

## Module-by-Module Fixes

### CRITICAL PRIORITY MODULES

#### 1. AP Module (accounts/views.py)
**Affected:** 14 views  
**Fix Pattern:** Add SessionEntityMixin to all views

**Specific Changes:**

View Classes to Fix (in order):
```python
# 1. Dashboard
class APDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    # ... existing code ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        context['bills_total'] = VendorBill.objects.filter(entity_id=entity_id).count()
        # ... apply entity filter to all querysets ...
        return context

# 2. List Views
class VendorBillListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    # Just add mixin, no other changes needed

class VendorPaymentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    # Just add mixin

# 3. Detail/CRUD Views
class VendorBillDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    # Just add mixin

class VendorBillCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        form.instance.entity_id = entity_id
        return super().form_valid(form)

# ... Apply to all remaining views ...
```

**Forms to Update (ap/forms.py):**
```python
class VendorBillForm(forms.ModelForm):
    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            # Filter choices to this entity
            self.fields['vendor'].queryset = Vendor.objects.filter(entity=entity)
```

**Timeline:** 2-3 hours

---

#### 2. CRM Module (crm/views.py)
**Affected:** 72 views  
**Fix Pattern:** Add SessionEntityMixin + remove hardcoded entity_id=1

**Critical Issue:**
```python
# CURRENT (WRONG):
def form_valid(self, form):
    entity, _ = Entity.objects.get_or_create(id=1, defaults={...})
    form.instance.entity = entity  # FORCES ENTITY 1!
    return super().form_valid(form)

# CORRECT:
def form_valid(self, form):
    entity_id = self.request.session.get('selected_entity_id')
    form.instance.entity_id = entity_id
    return super().form_valid(form)
```

**Changes Required:**
```python
# Before - ALL CRM views use this pattern
class LeadCreateView(LoginRequiredMixin, CreateView):
    # ...
    def form_valid(self, form):
        entity, _ = Entity.objects.get_or_create(id=1, ...)  # BAD!
        form.instance.entity = entity

# After - Corrected for SessionEntityMixin
class LeadCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    # Add mixin + remove hardcoded entity
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        form.instance.entity_id = entity_id
        return super().form_valid(form)
```

**Views to Fix:** LeadCreateView, LeadUpdateView, OpportunityCreateView, OpportunityUpdateView, QuoteCreateView, QuoteUpdateView, ActivityCreateView, ActivityUpdateView, CampaignCreateView, TerritoryCreateView, TerritoryUpdateView, CustomerGroupCreateView, CustomerGroupUpdateView, ContactCreateView, ContactUpdateView, ProspectCreateView, ProspectUpdateView, SalesPersonCreateView, SalesPersonUpdateView, LeadSourceCreateView, LeadSourceUpdateView, ContractCreateView, ContractUpdateView, AppointmentCreateView, AppointmentUpdateView, CommunicationCreateView, CommunicationUpdateView, EmailCampaignCreateView, EmailCampaignUpdateView, SMSCenterCreateView, SMSCenterUpdateView, EmailGroupCreateView, EmailGroupUpdateView, MaintenanceScheduleCreateView, MaintenanceScheduleUpdateView, MaintenanceVisitCreateView, MaintenanceVisitUpdateView, WarrantyClaimCreateView, WarrantyClaimUpdateView, LoyaltyProgramCreateView, LoyaltyMemberCreateView, POSTransactionCreateView, PromotionCreateView, CustomerSegmentCreateView

**Timeline:** 4-6 hours (72 views)

---

#### 3. Cash Management (cash_management/views.py)
**Affected:** 16 views  
**Fix Pattern:** Add SessionEntityMixin to all

**Implementation:**
```python
# Dashboard
class CashManagementDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        today = timezone.now().date()
        latest_positions = CashPosition.objects.filter(
            entity_id=entity_id,
            position_date=today
        )
        # ... rest of code ...

# List Views (just add mixin)
class PaymentScheduleListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    # Existing code unchanged

# Create/Update Views
class PaymentScheduleCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        form.instance.entity_id = entity_id
        return super().form_valid(form)
```

**Timeline:** 2-3 hours

---

#### 4. Inventory (inventory/views.py)
**Affected:** 16 views  
**Issue:** Function-based views only

**Fix Strategy:** Convert to class-based views

**Example Conversion:**
```python
# Before (function-based)
@login_required
def product_list(request):
    products = Product.objects.all()
    # ...
    return render(request, 'inventory/product_list.html', context)

# After (class-based + SessionEntityMixin)
class ProductListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 25
```

**Timeline:** 4-6 hours (more complex due to conversion)

---

#### 5. Maintenance (maintenance/views.py)
**Affected:** 31 views  
**Fix Pattern:** Add SessionEntityMixin to all

**Example:**
```python
class MaintenanceAssetListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = MaintenanceAsset
    template_name = 'maintenance/maintenanceasset_list.html'
    context_object_name = 'assets'
    paginate_by = 20

    def get_queryset(self):
        # SessionEntityMixin handles filtering
        return super().get_queryset().order_by('-created_at')
```

**Timeline:** 3-4 hours

---

#### 6. Procurement (procurement/views.py)
**Affected:** 13 views  
**Fix Pattern:** Add SessionEntityMixin to all

**Timeline:** 2 hours

---

#### 7. Projects (projects/views.py)
**Affected:** 11 views  
**Fix Pattern:** Add SessionEntityMixin to all

**Timeline:** 1.5 hours

---

#### 8. Shareholder (shareholder/views.py)
**Affected:** 13 views  
**Fix Pattern:** Add SessionEntityMixin to all

**Timeline:** 2 hours

---

### HIGH PRIORITY MODULES

#### 9. Accounting (accounting/views.py)
**Status:** Already 36.6% implemented  
**Affected:** 52 remaining views

**Pattern:** Copy from existing SessionEntityMixin views

**Timeline:** 5-7 hours

---

#### 10. HR (hr/views.py)
**Status:** Partially implemented (23.5%)  
**Affected:** 13 remaining views
**Issue:** Some use UserRole filtering instead

**Fix:** Standardize to SessionEntityMixin

**Timeline:** 2-3 hours

---

### MEDIUM PRIORITY MODULES

#### 11. Manufacturing (manufacturing/views.py)
**Status:** Uses UserRole filtering (works but inconsistent)  
**Affected:** 32 views
**Issue:** Different pattern than rest of codebase

**Migration Path:**
```python
# Current pattern (works but not standard)
def get_filtered_queryset(model, user, base_queryset=None):
    user_entities = get_user_entities(user)
    return base_queryset.filter(entity_id__in=user_entities)

# New pattern (consistent with rest)
class ProductListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Product
    def get_queryset(self):
        return super().get_queryset()  # SessionEntityMixin handles it
```

**Timeline:** 4-5 hours

---

#### 12. Sales (sales/views.py)
**Status:** Uses UserRole filtering  
**Affected:** 13 views

**Fix:** Migrate to SessionEntityMixin like Manufacturing

**Timeline:** 2-3 hours

---

#### 13. AR (ar/views.py)
**Status:** Already 44.4% implemented  
**Affected:** 10 remaining views

**Fix:** Add SessionEntityMixin to remaining views

**Timeline:** 1-2 hours

---

## Testing Strategy

### Unit Test Template
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounting.models import Entity
from ap.models import VendorBill

class APViewSessionEntityTest(TestCase):
    def setUp(self):
        # Create test entities
        self.entity1 = Entity.objects.create(name='Entity 1', code='E1')
        self.entity2 = Entity.objects.create(name='Entity 2', code='E2')
        
        # Create users
        self.user1 = User.objects.create_user('user1', password='pass')
        self.user2 = User.objects.create_user('user2', password='pass')
        
        # Create test data
        self.bill1 = VendorBill.objects.create(
            entity=self.entity1,
            bill_number='B001'
        )
        self.bill2 = VendorBill.objects.create(
            entity=self.entity2,
            bill_number='B002'
        )
        
        self.client = Client()

    def test_vendor_bill_list_entity_filtering(self):
        """Verify list view only shows current entity bills"""
        self.client.login(username='user1', password='pass')
        session = self.client.session
        session['selected_entity_id'] = self.entity1.id
        session.save()
        
        response = self.client.get('/ap/bills/')
        self.assertEqual(response.status_code, 200)
        
        # Verify only entity1 bills shown
        bills = response.context['object_list']
        self.assertEqual(bills.count(), 1)
        self.assertEqual(bills[0].bill_number, 'B001')

    def test_vendor_bill_detail_entity_isolation(self):
        """Verify user cannot access other entity's bill"""
        self.client.login(username='user1', password='pass')
        session = self.client.session
        session['selected_entity_id'] = self.entity1.id
        session.save()
        
        # Try to access entity2 bill
        response = self.client.get(f'/ap/bills/{self.bill2.id}/')
        # Should be 404 due to filtering
        self.assertEqual(response.status_code, 404)

    def test_vendor_bill_create_assigns_entity(self):
        """Verify created bills get session entity"""
        self.client.login(username='user1', password='pass')
        session = self.client.session
        session['selected_entity_id'] = self.entity1.id
        session.save()
        
        response = self.client.post('/ap/bills/create/', {
            'bill_number': 'B003',
            'vendor': 1,
            # ... other required fields ...
        })
        
        # Verify bill created with correct entity
        new_bill = VendorBill.objects.get(bill_number='B003')
        self.assertEqual(new_bill.entity_id, self.entity1.id)
```

### Integration Test Template
```python
def test_multi_entity_user_entity_switching(self):
    """Verify user can switch between entities"""
    # User has access to both entities
    # ...
    
    # Switch to entity1
    session['selected_entity_id'] = entity1.id
    session.save()
    response = self.client.get('/ap/bills/')
    self.assertEqual(len(response.context['object_list']), entity1_bill_count)
    
    # Switch to entity2
    session['selected_entity_id'] = entity2.id
    session.save()
    response = self.client.get('/ap/bills/')
    self.assertEqual(len(response.context['object_list']), entity2_bill_count)
```

### Manual Test Checklist
- [ ] Create data in Entity A
- [ ] Login as Entity A user → Verify data visible
- [ ] Switch session to Entity B → Verify Entity A data NOT visible
- [ ] Create new record → Verify assigned to Entity B
- [ ] Try direct URL to Entity A record → Verify 404
- [ ] Logout and login as Entity B user → Verify correct data shown

---

## Common Patterns

### Pattern 1: List Views
```python
class ResourceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Resource
    template_name = 'module/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 20
    
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')
```

### Pattern 2: Detail Views
```python
class ResourceDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    model = Resource
    template_name = 'module/resource_detail.html'
    context_object_name = 'resource'
```

### Pattern 3: Create Views
```python
class ResourceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = Resource
    form_class = ResourceForm
    template_name = 'module/resource_form.html'
    success_url = reverse_lazy('module:resource_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        form.instance.entity_id = entity_id
        return super().form_valid(form)
```

### Pattern 4: Update Views
```python
class ResourceUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = 'module/resource_form.html'
    success_url = reverse_lazy('module:resource_list')
```

### Pattern 5: Delete Views
```python
class ResourceDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = Resource
    template_name = 'module/resource_confirm_delete.html'
    success_url = reverse_lazy('module:resource_list')
```

### Pattern 6: Dashboard Views
```python
class ModuleDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    template_name = 'module/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        context.update({
            'total_items': Resource.objects.filter(entity_id=entity_id).count(),
            'recent_items': Resource.objects.filter(entity_id=entity_id).order_by('-created_at')[:10],
        })
        
        return context
```

---

## Verification Checklist

Before committing changes:
- [ ] SessionEntityMixin imported in view file
- [ ] All List, Detail, Create, Update, Delete views have SessionEntityMixin
- [ ] All dashboard views filter by session entity
- [ ] All create/update views set entity_id from session
- [ ] No hardcoded entity IDs (like entity_id=1)
- [ ] Forms accept entity parameter for filtering
- [ ] Unit tests verify entity isolation
- [ ] Integration tests verify entity switching
- [ ] Manual testing done for CRUD operations
- [ ] Code review approved by team lead

---

## Summary

**Total Views to Fix:** 228  
**Estimated Implementation Time:** 55-75 hours  
**Priority Order:** Critical → High → Medium  

This guide provides the exact implementation pattern for each module. Follow consistently across all modules to ensure uniform security and maintainability.

