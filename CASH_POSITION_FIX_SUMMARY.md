"""
CASH POSITION INTEGRITY ERROR - FIX SUMMARY
============================================

PROBLEM:
--------
IntegrityError at /cash/positions/create/
NOT NULL constraint failed: cash_management_cashposition.entity_id

The CashPosition model has a required ForeignKey to Entity, but the form was not
including this field and the view was not setting it when creating a new CashPosition.

ROOT CAUSE:
-----------
1. CashPositionForm.Meta.fields did not include 'entity'
2. CashPositionCreateView did not manually set entity_id before saving

SOLUTION:
---------
Two changes were made:

1. CASH_MANAGEMENT/FORMS.PY - Updated CashPositionForm
   - Added 'entity' to the fields list in Meta
   - Added widget configuration for entity field as a Select dropdown
   
2. CASH_MANAGEMENT/VIEWS.PY - Updated CashPositionCreateView.form_valid()
   - Added logic to auto-set entity from the selected bank account if not explicitly provided
   - This ensures entity_id is always populated before the object is saved

IMPLEMENTATION DETAILS:
-----------------------

Before:
    class CashPositionForm(forms.ModelForm):
        class Meta:
            model = CashPosition
            fields = ['bank_account', 'position_date', 'opening_balance', 'closing_balance', 'is_reconciled']

After:
    class CashPositionForm(forms.ModelForm):
        class Meta:
            model = CashPosition
            fields = ['entity', 'bank_account', 'position_date', 'opening_balance', 'closing_balance', 'is_reconciled']
            widgets = {
                'entity': forms.Select(attrs={
                    'class': 'form-select',
                    'required': 'required'
                }),
                ...
            }

And in the view:
    def form_valid(self, form):
        # Ensure entity is set - it can be set explicitly or derived from bank_account
        if not form.cleaned_data.get('entity') and form.cleaned_data.get('bank_account'):
            # Auto-set entity from the selected bank account
            bank_account = form.cleaned_data.get('bank_account')
            form.instance.entity = bank_account.entity
        
        messages.success(self.request, 'Cash position created successfully.')
        return super().form_valid(form)

WHY THIS WORKS:
---------------
- BankProfile model has a ForeignKey to Entity
- When user selects a bank account, we can derive the entity from it
- This provides two ways to handle entity:
  1. User explicitly selects entity in the form
  2. System automatically uses the entity from the selected bank account
  
Both approaches ensure entity_id is never NULL when saving.

TESTING:
--------
1. Navigate to http://localhost:8000/cash/positions/create/
2. Fill in the form:
   - Entity: (select an entity)
   - Bank Account: (select a bank account)
   - Position Date: (select a date)
   - Opening Balance: (enter a number)
   - Closing Balance: (enter a number)
3. Click "Create"
4. Should see success message: "Cash position created successfully."
5. No IntegrityError should occur

RELATED MODELS:
---------------
Entity <- (FK) <- BankProfile <- (FK) <- CashPosition
         <- (FK) <- CashPosition

All CashPositions must belong to an Entity, either directly or through the bank account.
"""
