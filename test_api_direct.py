from accounting.models import Entity, Account
from accounting.cash_views import get_sub_accounts_api
from django.test import RequestFactory
import json

# Get test data
entity = Entity.objects.get(id=9)
purchases = Account.objects.get(id=92107)

print(f'Entity: {entity.id} {entity.name}')
print(f'Purchases account: {purchases.id} {purchases.account_number}')

# Test the API directly
factory = RequestFactory()
request = factory.get('/accounting/api/get-sub-accounts/', {'main_account_id': purchases.id, 'entity_id': entity.id})
response = get_sub_accounts_api(request)

# Get the content as string and parse JSON
content = response.content.decode('utf-8')
data = json.loads(content)

print(f'\nAPI test with main_account_id={purchases.id}, entity_id={entity.id}:')
print(f'API Success: {data.get("success")}')
print(f'API Message: {data.get("message", "")}')
print(f'API Accounts count: {len(data.get("accounts", []))}')
if data.get('accounts'):
    for acc in data['accounts']:
        print(f'  - ID {acc["id"]}: {acc["account_number"]} - {acc["name"]}')
