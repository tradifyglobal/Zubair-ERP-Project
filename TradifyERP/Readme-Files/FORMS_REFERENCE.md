# 🎯 FORMS REFERENCE CARD - QUICK LOOKUP

## All 89 Forms at a Glance

### 📊 ACCOUNTING (13 forms)
**File:** `accounting/forms.py`
- DoubleEntryJournalForm
- SimpleLedgerEntryForm  
- QuickAddCustomerForm
- QuickAddVendorForm
- QuickAddAccountForm
- QuickAddVendorInvoiceForm
- QuickAddVendorPaymentForm
- QuickAddFixedAssetForm
- QuickAddCashTransactionForm
- QuickAddBankProfileForm
- QuickAddTaxRateForm
- QuickAddDeferredExpenseForm
- QuickAddDeferredRevenueForm

### 💳 ACCOUNTS PAYABLE (6 forms)
**File:** `ap/forms.py`
- VendorBillForm
- VendorBillLineItemForm
- VendorPaymentForm
- APDiscountForm
- APReconciliationForm
- BulkVendorBillForm

### 📥 ACCOUNTS RECEIVABLE (7 forms) ⭐ NEW
**File:** `ar/forms.py`
- CustomerInvoiceForm
- InvoiceLineItemForm
- CustomerPaymentForm
- ARDiscountForm
- ARReconciliationForm
- BulkInvoiceForm
- BulkPaymentForm

### 🛍️ PROCUREMENT (8 forms)
**File:** `procurement/forms.py`
- PurchaseOrderForm
- POLineItemForm
- GoodsReceiptForm
- GoodsReceiptLineItemForm
- RequestForQuotationForm
- VendorQuotationForm
- QuoteSelectionForm
- ThreeWayMatchingForm

### 📦 INVENTORY (7 forms) ⭐ NEW
**File:** `inventory/forms.py`
- CategoryForm
- ProductForm
- WarehouseForm
- StockForm
- StockMovementForm
- InventoryReconciliationForm
- BulkStockUpdateForm

### 🎯 SALES (3 forms)
**File:** `sales/forms.py`
- CustomerForm
- SalesOrderForm
- SalesOrderLineForm
- InvoiceForm

### 🏭 MANUFACTURING (13 forms)
**File:** `manufacturing/forms.py`
- ProductCategoryForm
- ProductForm
- RawMaterialForm
- BOMLineForm
- BillOfMaterialsForm
- WorkCenterForm
- RoutingForm
- RoutingLineForm
- ProductionOrderForm
- QualityInspectionForm
- EquipmentForm
- (+ 2 more)

### 👥 HR (10 forms)
**File:** `hr/forms.py`
- EmployeeForm
- DepartmentForm
- PositionForm
- PayrollForm
- PayrollRecordForm
- LeaveRequestForm
- PerformanceForm
- DisciplinaryForm
- BenefitForm
- EmployeeBenefitForm
- SalaryHistoryForm

### 💼 CRM (7 forms) ⭐ NEW
**File:** `crm/forms.py`
- LeadForm
- OpportunityForm
- QuoteForm
- ActivityForm
- CampaignForm
- ContactForm
- SalesStageForm

### 💰 CASH MANAGEMENT (6 forms) ⭐ NEW
**File:** `cash_management/forms.py`
- CashPositionForm
- PaymentScheduleForm
- LiquidityForecastForm
- TreasuryAccountForm
- FXExposureForm
- BulkPaymentScheduleForm

### 📊 PROJECTS (8 forms) ⭐ NEW
**File:** `projects/forms.py`
- ProjectForm
- ProjectPhaseForm
- ProjectTaskForm
- TimeEntryForm
- ResourceAllocationForm
- ProjectBudgetForm
- ProjectKPIForm
- BulkTimeEntryForm

---

## 🎨 Form Widget Types Used

### Text Inputs
```python
widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'text'})
```

### Numbers
```python
widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
```

### Dates
```python
widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
```

### DateTime
```python
widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
```

### Selects (Dropdowns)
```python
widget=forms.Select(attrs={'class': 'form-select'})
```

### Checkboxes
```python
widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
```

### TextAreas
```python
widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
```

### File Upload
```python
widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx'})
```

---

## 🔗 How to Use a Form in a View

### Step 1: Import the form
```python
from .forms import CustomerInvoiceForm
```

### Step 2: Use in CreateView
```python
from django.views.generic import CreateView

class CustomerInvoiceCreateView(CreateView):
    model = CustomerInvoice
    form_class = CustomerInvoiceForm
    template_name = 'ar/customer_invoice_form.html'
    success_url = reverse_lazy('ar:invoice_list')
```

### Step 3: Create template
```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
</form>
```

### Step 4: Add URL
```python
path('invoices/create/', CustomerInvoiceCreateView.as_view(), name='invoice_create')
```

---

## ✨ Special Form Features

### Bulk Import Forms
These forms support CSV/Excel uploads:
- BulkVendorBillForm (AP)
- BulkInvoiceForm (AR)
- BulkPaymentForm (AR)
- BulkStockUpdateForm (Inventory)
- BulkPaymentScheduleForm (Cash)
- BulkTimeEntryForm (Projects)

### Validation Examples
```python
def clean(self):
    cleaned_data = super().clean()
    if condition_fails:
        raise forms.ValidationError("Error message")
    return cleaned_data
```

### Field Validation
```python
cost_price = forms.DecimalField(
    validators=[MinValueValidator(0), MaxValueValidator(999999)]
)
```

---

## 📝 Form Meta Options

All forms use these Meta options:

```python
class Meta:
    model = ModelName          # Database model
    fields = ['field1', 'field2']  # Which fields to show
    widgets = {...}             # Override default widgets
```

---

## 🎓 Bootstrap Classes Used

```
form-control    → Text inputs, textareas, selects
form-select     → Dropdown selects  
form-check-input → Checkboxes
form-label      → Labels
form-text       → Help text
```

---

## 🚀 Quick Copy-Paste: Basic CRUD View

```python
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import MyModel
from .forms import MyModelForm

class MyModelCreateView(LoginRequiredMixin, CreateView):
    model = MyModel
    form_class = MyModelForm
    template_name = 'app/mymodel_form.html'
    success_url = reverse_lazy('app:mymodel_list')

class MyModelUpdateView(LoginRequiredMixin, UpdateView):
    model = MyModel
    form_class = MyModelForm
    template_name = 'app/mymodel_form.html'
    success_url = reverse_lazy('app:mymodel_list')

class MyModelDeleteView(LoginRequiredMixin, DeleteView):
    model = MyModel
    template_name = 'app/mymodel_confirm_delete.html'
    success_url = reverse_lazy('app:mymodel_list')
```

---

## 📋 Templates Needed

For each major model, create:

1. **List Template**
   ```
   templates/app/model_list.html
   ```

2. **Create/Edit Template**
   ```
   templates/app/model_form.html
   ```

3. **Delete Confirmation**
   ```
   templates/app/model_confirm_delete.html
   ```

4. **Detail Template** (optional)
   ```
   templates/app/model_detail.html
   ```

---

## 🔍 Finding What You Need

| Need | Location |
|------|----------|
| Customer Invoice form | `ar/forms.py` |
| Product form | `inventory/forms.py` |
| Lead form | `crm/forms.py` |
| Payment Schedule form | `cash_management/forms.py` |
| Project form | `projects/forms.py` |
| Purchase Order form | `procurement/forms.py` |
| Employee form | `hr/forms.py` |
| Journal Entry form | `accounting/forms.py` |

---

**Last Updated:** November 21, 2025  
**Total Forms:** 89  
**New Forms (Today):** 29  
**Status:** ✅ Ready for View Implementation
