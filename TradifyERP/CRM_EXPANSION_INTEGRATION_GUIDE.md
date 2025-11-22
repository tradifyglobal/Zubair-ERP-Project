# 🔗 CRM EXPANSION: INTEGRATION GUIDE

**Quick reference for integrating Retail & Manufacturing CRM into your Django admin and application.**

---

## 📝 STEP 1: Register Models in Admin

Add to `crm/admin.py`:

```python
from django.contrib import admin
from .retail_models import (
    LoyaltyProgram, LoyaltyMember, PointTransaction, 
    POSTransaction, Promotion, PromotionUsage, CustomerSegment
)
from .manufacturing_models import (
    Distributor, DistributorContact, DistributorOrder, 
    OrderShipment, AfterSalesService, WarrantyRegistration, 
    DistributorPerformance
)

# ===== RETAIL MODELS =====
@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'loyalty_type', 'status', 'created_at']
    list_filter = ['loyalty_type', 'status', 'enable_tiers']
    search_fields = ['program_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {'fields': ('entity', 'program_name', 'loyalty_type', 'status')}),
        ('Points Configuration', {'fields': ('points_per_currency', 'point_expiry_days', 'enable_tiers')}),
        ('GL Integration', {'fields': ('gl_account',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(LoyaltyMember)
class LoyaltyMemberAdmin(admin.ModelAdmin):
    list_display = ['membership_number', 'customer', 'current_tier', 'point_balance', 'status']
    list_filter = ['current_tier', 'status', 'loyalty_program']
    search_fields = ['membership_number', 'customer__name']
    readonly_fields = ['created_at', 'updated_at', 'total_points_earned', 'total_points_redeemed']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['loyalty_member', 'transaction_type', 'points', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['loyalty_member__membership_number', 'reference_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(POSTransaction)
class POSTransactionAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'store_location', 'transaction_date', 'total_amount']
    list_filter = ['store_location', 'transaction_date']
    search_fields = ['receipt_number', 'loyalty_member__membership_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['promotion_name', 'promotion_type', 'start_date', 'end_date', 'status']
    list_filter = ['promotion_type', 'status', 'loyalty_program']
    search_fields = ['promotion_name', 'promotion_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PromotionUsage)
class PromotionUsageAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'loyalty_member', 'usage_date', 'discount_given']
    list_filter = ['usage_date']
    search_fields = ['promotion__promotion_code']
    readonly_fields = ['created_at']


@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ['segment_name', 'segmentation_criteria', 'segment_status']
    list_filter = ['segmentation_criteria', 'segment_status']
    search_fields = ['segment_name', 'description']
    readonly_fields = ['created_at', 'updated_at']


# ===== MANUFACTURING MODELS =====
@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ['distributor_code', 'distributor_name', 'territory', 'status']
    list_filter = ['status', 'territory']
    search_fields = ['distributor_code', 'distributor_name']
    readonly_fields = ['created_at', 'updated_at', 'ytd_sales']
    fieldsets = (
        ('Basic Info', {'fields': ('entity', 'distributor_code', 'distributor_name', 'territory')}),
        ('Contact', {'fields': ('account_manager', 'website_url')}),
        ('Credit & Sales', {'fields': ('credit_limit', 'annual_sales_target', 'ytd_sales')}),
        ('Contract', {'fields': ('contract_start_date', 'contract_end_date', 'contract_terms')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(DistributorContact)
class DistributorContactAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'distributor', 'job_title', 'contact_method']
    list_filter = ['distributor', 'contact_method']
    search_fields = ['contact_name', 'distributor__distributor_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DistributorOrder)
class DistributorOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'distributor', 'order_date', 'order_status']
    list_filter = ['order_status', 'order_date']
    search_fields = ['order_number', 'distributor__distributor_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrderShipment)
class OrderShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_number', 'order', 'shipment_date', 'shipment_status']
    list_filter = ['shipment_status', 'shipment_date']
    search_fields = ['shipment_number', 'tracking_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AfterSalesService)
class AfterSalesServiceAdmin(admin.ModelAdmin):
    list_display = ['service_ticket_number', 'distributor', 'service_type', 'status']
    list_filter = ['service_type', 'status', 'issue_date']
    search_fields = ['service_ticket_number', 'product_serial_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WarrantyRegistration)
class WarrantyRegistrationAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'distributor', 'warranty_type', 'warranty_end_date']
    list_filter = ['warranty_type', 'warranty_end_date']
    search_fields = ['serial_number', 'product_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DistributorPerformance)
class DistributorPerformanceAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'performance_month', 'on_time_delivery_pct', 'rating']
    list_filter = ['performance_month', 'rating']
    search_fields = ['distributor__distributor_code']
    readonly_fields = ['created_at', 'updated_at']
```

---

## 🛣️ STEP 2: Update URL Routing

Add to `crm/urls.py`:

```python
from django.urls import path
from . import views
from .retail_views import (  # Will create in Phase 2
    LoyaltyProgramListView, LoyaltyProgramCreateView,
    LoyaltyMemberListView, LoyaltyMemberCreateView,
    # ... other retail views
)
from .manufacturing_views import (  # Will create in Phase 2
    DistributorListView, DistributorCreateView,
    DistributorOrderListView, DistributorOrderCreateView,
    # ... other manufacturing views
)

urlpatterns = [
    # === RETAIL URLS ===
    path('loyalty/programs/', LoyaltyProgramListView.as_view(), name='loyalty_program_list'),
    path('loyalty/programs/create/', LoyaltyProgramCreateView.as_view(), name='loyalty_program_create'),
    
    path('loyalty/members/', LoyaltyMemberListView.as_view(), name='loyalty_member_list'),
    path('loyalty/members/create/', LoyaltyMemberCreateView.as_view(), name='loyalty_member_create'),
    
    # === MANUFACTURING URLS ===
    path('distributors/', DistributorListView.as_view(), name='distributor_list'),
    path('distributors/create/', DistributorCreateView.as_view(), name='distributor_create'),
    
    path('distributor-orders/', DistributorOrderListView.as_view(), name='distributor_order_list'),
    path('distributor-orders/create/', DistributorOrderCreateView.as_view(), name='distributor_order_create'),
]
```

---

## 🔌 STEP 3: Migrate Models

```bash
python manage.py makemigrations crm
python manage.py migrate crm
```

---

## 🗄️ STEP 4: Update settings.py

Ensure the apps are in INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ... existing apps
    'crm.apps.CrmConfig',  # This covers all CRM models
]
```

---

## 🔄 STEP 5: Import Models in Views (Phase 2)

```python
# crm/views.py
from .retail_models import (
    LoyaltyProgram, LoyaltyMember, PointTransaction,
    POSTransaction, Promotion, PromotionUsage, CustomerSegment
)
from .manufacturing_models import (
    Distributor, DistributorContact, DistributorOrder,
    OrderShipment, AfterSalesService, WarrantyRegistration,
    DistributorPerformance
)
from .retail_forms import (
    LoyaltyProgramForm, LoyaltyMemberForm, PointTransactionForm,
    POSTransactionForm, PromotionForm, CustomerSegmentForm
)
from .manufacturing_forms import (
    DistributorForm, DistributorContactForm, DistributorOrderForm,
    OrderShipmentForm, AfterSalesServiceForm, WarrantyRegistrationForm,
    DistributorPerformanceForm
)
```

---

## 🔗 STEP 6: GL Integration

### For POS Transactions (Auto Revenue Posting):
```python
# In POSTransaction.save() or post_save signal
from accounting.models import Account, DoubleEntryJournal

def post_save_pos_transaction(sender, instance, created, **kwargs):
    if created:
        # Post revenue to GL
        journal = DoubleEntryJournal.objects.create(
            entity=instance.entity,
            journal_date=instance.transaction_date,
            description=f"POS Transaction {instance.receipt_number}",
            currency=instance.currency
        )
        
        # Debit cash/card
        journal.journal_entries.create(
            account=instance.payment_method_gl_account,
            debit_amount=instance.total_amount,
            description="Cash/Card received"
        )
        
        # Credit revenue
        journal.journal_entries.create(
            account=instance.entity.default_sales_account,
            credit_amount=instance.total_amount,
            description="Sales revenue"
        )

from django.db.models.signals import post_save
post_save.connect(post_save_pos_transaction, sender=POSTransaction)
```

### For Distributor Orders (Linking to Sales GL):
```python
# Similar pattern for DistributorOrder
def post_save_distributor_order(sender, instance, created, **kwargs):
    if created and instance.sales_order:
        # Post to GL via sales order
        instance.sales_order.post_to_gl()

post_save.connect(post_save_distributor_order, sender=DistributorOrder)
```

---

## 📊 STEP 7: Dashboard Widgets (Optional)

Add to dashboard view:

```python
from django.db.models import Sum, Avg, Count
from .retail_models import LoyaltyMember, POSTransaction
from .manufacturing_models import Distributor, DistributorOrder

def dashboard(request):
    context = {
        # Retail metrics
        'total_loyalty_members': LoyaltyMember.objects.filter(
            entity=request.user.entity
        ).count(),
        'loyalty_member_growth': LoyaltyMember.objects.filter(
            entity=request.user.entity,
            created_at__month=now().month
        ).count(),
        'pos_revenue_this_month': POSTransaction.objects.filter(
            entity=request.user.entity,
            transaction_date__month=now().month
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        
        # Manufacturing metrics
        'total_distributors': Distributor.objects.filter(
            entity=request.user.entity
        ).count(),
        'pending_orders': DistributorOrder.objects.filter(
            entity=request.user.entity,
            order_status='PENDING'
        ).count(),
    }
    return render(request, 'crm/dashboard.html', context)
```

---

## ✅ STEP 8: Data Validation

Add constraints to settings.py:

```python
# Add to settings.py for development/testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'ATOMIC_REQUESTS': True,  # Ensures transaction integrity
        'CONN_MAX_AGE': 600,
    }
}
```

---

## 🚀 STEP 9: Load Sample Data (Optional)

```python
# crm/fixtures/sample_data.py
from crm.retail_models import LoyaltyProgram
from crm.manufacturing_models import Distributor

def load_sample_data():
    # Create sample loyalty program
    LoyaltyProgram.objects.get_or_create(
        program_name="Standard Points",
        defaults={
            'loyalty_type': 'POINTS',
            'points_per_currency': 1.0,
            'point_expiry_days': 365,
            'status': 'ACTIVE'
        }
    )
    
    # Create sample distributor
    Distributor.objects.get_or_create(
        distributor_code="DIST001",
        defaults={
            'distributor_name': "Sample Distributor",
            'territory': "North",
            'credit_limit': 50000.00,
            'annual_sales_target': 100000.00,
            'status': 'ACTIVE'
        }
    )

# Run: python manage.py shell
# >>> from crm.fixtures.sample_data import load_sample_data
# >>> load_sample_data()
```

---

## 🔍 VERIFICATION CHECKLIST

- [ ] Models imported correctly in admin.py
- [ ] No migration errors: `python manage.py migrate`
- [ ] Admin interface shows all models
- [ ] Can create records in Django admin
- [ ] URL patterns configured
- [ ] Forms import without errors
- [ ] GL accounts assigned to loyalty program
- [ ] Multi-entity filtering works correctly

---

## 📚 DOCUMENTATION FILES

See also:
- `CRM_EXPANSION_COMPLETE.md` - Full feature details
- `FORMS_IMPLEMENTATION_GUIDE.md` - Form patterns
- `COMPLETE_ERP_AUDIT_REPORT.md` - System overview

---

**Next: Phase 2 - Build Views & Templates**

These integration steps prepare the system for view implementation in Phase 2.
