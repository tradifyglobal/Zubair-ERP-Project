from accounting.models import Entity, Account
from accounting.cash_forms import CashReceiptLineForm

# Get test data
entity = Entity.objects.get(id=9)
purchases = Account.objects.get(id=92107)
sub_account = Account.objects.filter(parent_account=purchases).first()

print(f'Entity: {entity.id} {entity.name}')
print(f'Purchases account: {purchases.id} {purchases.account_number} {purchases.name}')
print(f'Sub-account: {sub_account.id} {sub_account.account_number} {sub_account.name}')

# Test form initialization
form = CashReceiptLineForm(entity=entity)
print(f'\nForm initialized with entity={entity.id}')
print(f'main_account options count: {form.fields["main_account"].queryset.count()}')
print(f'account options count: {form.fields["account"].queryset.count()}')

# Check if Purchases account is in the field
accounts_qs = form.fields['account'].queryset
purchases_in_accounts = accounts_qs.filter(id=purchases.id).exists()
print(f'Purchases in account field: {purchases_in_accounts}')

# Check if sub-account is in the field
sub_in_accounts = accounts_qs.filter(id=sub_account.id).exists()
print(f'Sub-account in account field: {sub_in_accounts}')

# Try the API directly
from accounting.cash_views import get_sub_accounts_api
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/accounting/api/get-sub-accounts/', {'main_account_id': purchases.id, 'entity_id': entity.id})
response = get_sub_accounts_api(request)
data = response.json()

print(f'\nAPI test with main_account_id={purchases.id}, entity_id={entity.id}:')
print(f'API Success: {data.get("success")}')
print(f'API Message: {data.get("message", "")}')
print(f'API Accounts: {len(data.get("accounts", []))}')
if data.get('accounts'):
    for acc in data['accounts']:
        print(f'  - {acc["id"]}: {acc["account_number"]} {acc["name"]}')
else:
    print('No accounts returned!')
