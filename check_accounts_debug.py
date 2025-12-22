import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TradifyERP.settings_production")
import sys
sys.path.insert(0, "/var/www/tradifyerp/TradifyERP")
django.setup()

from accounting.models import Account

print("=== GL ACCOUNTS CHECK ===")
print("Total Accounts:", Account.objects.count())
print("Active Accounts:", Account.objects.filter(is_active=True).count())
print("EXPENSE Accounts (Active):", Account.objects.filter(account_type="EXPENSE", is_active=True).count())
print("\nAll Active Accounts by Type:")

for account_type in ["ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"]:
    count = Account.objects.filter(account_type=account_type, is_active=True).count()
    if count > 0:
        print(f"\n{account_type} ({count}):")
        accounts = Account.objects.filter(account_type=account_type, is_active=True).order_by("account_number")[:5]
        for a in accounts:
            print(f"  {a.account_number} - {a.name}")
