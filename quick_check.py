from accounting.models import CapitalContribution, Account
from decimal import Decimal

capital_account = Account.objects.get(entity_id=7, account_number='3000-11')
contributions = CapitalContribution.objects.filter(equity_account=capital_account)

print(f"Total: {contributions.count()}")
for c in contributions:
    print(f"{c.workflow_status}: {c.amount} ({c.payment_mode})")
