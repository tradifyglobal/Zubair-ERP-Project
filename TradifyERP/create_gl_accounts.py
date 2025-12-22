"""
Script to create GL accounts for Sales, Purchases, and GST
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, Entity, Currency

def create_gl_accounts():
    # Get the first entity and currency (adjust as needed)
    entity = Entity.objects.first()
    currency = Currency.objects.filter(code='INR').first() or Currency.objects.first()
    
    if not entity or not currency:
        print("Error: Entity or Currency not found!")
        return
    
    print(f"Creating accounts for Entity: {entity.name}")
    print(f"Using Currency: {currency.code}")
    print("-" * 80)
    
    accounts_created = []
    
    # 1. GST - Main Account
    gst_main, created = Account.objects.get_or_create(
        entity=entity,
        account_number='2200',
        defaults={
            'name': 'GST',
            'account_type': 'LIABILITY',
            'currency': currency,
            'is_active': True,
            'description': 'Goods and Services Tax Main Account',
            'parent_account': None
        }
    )
    accounts_created.append(('GST Main Account', gst_main, created))
    
    # 1a. GST-Sales Sub account
    gst_sales, created = Account.objects.get_or_create(
        entity=entity,
        account_number='2200-01',
        defaults={
            'name': 'GST-Sales',
            'account_type': 'LIABILITY',
            'currency': currency,
            'is_active': True,
            'description': 'GST collected on Sales',
            'parent_account': gst_main
        }
    )
    accounts_created.append(('GST-Sales Sub Account', gst_sales, created))
    
    # 1b. GST-Purchases Sub account
    gst_purchases, created = Account.objects.get_or_create(
        entity=entity,
        account_number='2200-02',
        defaults={
            'name': 'GST-Purchases',
            'account_type': 'LIABILITY',
            'currency': currency,
            'is_active': True,
            'description': 'GST paid on Purchases (Input Tax Credit)',
            'parent_account': gst_main
        }
    )
    accounts_created.append(('GST-Purchases Sub Account', gst_purchases, created))
    
    # 2. Sales - Main Account
    sales_main, created = Account.objects.get_or_create(
        entity=entity,
        account_number='4000',
        defaults={
            'name': 'Sales',
            'account_type': 'INCOME',
            'currency': currency,
            'is_active': True,
            'description': 'Sales Revenue Main Account',
            'parent_account': None
        }
    )
    accounts_created.append(('Sales Main Account', sales_main, created))
    
    # 2a. Cash-Sales Sub account
    cash_sales, created = Account.objects.get_or_create(
        entity=entity,
        account_number='4000-01',
        defaults={
            'name': 'Cash-Sales',
            'account_type': 'INCOME',
            'currency': currency,
            'is_active': True,
            'description': 'Cash Sales Revenue',
            'parent_account': sales_main
        }
    )
    accounts_created.append(('Cash-Sales Sub Account', cash_sales, created))
    
    # 2b. Credit-Sales Sub account
    credit_sales, created = Account.objects.get_or_create(
        entity=entity,
        account_number='4000-02',
        defaults={
            'name': 'Credit-Sales',
            'account_type': 'INCOME',
            'currency': currency,
            'is_active': True,
            'description': 'Credit Sales Revenue',
            'parent_account': sales_main
        }
    )
    accounts_created.append(('Credit-Sales Sub Account', credit_sales, created))
    
    # 3. Sales-Return - Main Account (contra to Sales)
    sales_return, created = Account.objects.get_or_create(
        entity=entity,
        account_number='4100',
        defaults={
            'name': 'Sales-Return',
            'account_type': 'INCOME',  # Contra-revenue account (reduces income)
            'currency': currency,
            'is_active': True,
            'description': 'Sales Returns and Allowances - Contra account to Sales',
            'parent_account': None
        }
    )
    accounts_created.append(('Sales-Return Main Account', sales_return, created))
    
    # 4. Purchases - Main Account
    purchases_main, created = Account.objects.get_or_create(
        entity=entity,
        account_number='5000',
        defaults={
            'name': 'Purchases',
            'account_type': 'EXPENSE',
            'currency': currency,
            'is_active': True,
            'description': 'Purchases Main Account',
            'parent_account': None
        }
    )
    accounts_created.append(('Purchases Main Account', purchases_main, created))
    
    # 4a. Cash-Purchases Sub account
    cash_purchases, created = Account.objects.get_or_create(
        entity=entity,
        account_number='5000-01',
        defaults={
            'name': 'Cash-Purchases',
            'account_type': 'EXPENSE',
            'currency': currency,
            'is_active': True,
            'description': 'Cash Purchases',
            'parent_account': purchases_main
        }
    )
    accounts_created.append(('Cash-Purchases Sub Account', cash_purchases, created))
    
    # 4b. Credit-Purchases Sub account
    credit_purchases, created = Account.objects.get_or_create(
        entity=entity,
        account_number='5000-02',
        defaults={
            'name': 'Credit-Purchases',
            'account_type': 'EXPENSE',
            'currency': currency,
            'is_active': True,
            'description': 'Credit Purchases',
            'parent_account': purchases_main
        }
    )
    accounts_created.append(('Credit-Purchases Sub Account', credit_purchases, created))
    
    # 5. Purchase-Return - Main Account (contra to Purchases)
    purchase_return, created = Account.objects.get_or_create(
        entity=entity,
        account_number='5100',
        defaults={
            'name': 'Purchase-Return',
            'account_type': 'EXPENSE',  # Contra-expense account (reduces expenses)
            'currency': currency,
            'is_active': True,
            'description': 'Purchase Returns and Allowances - Contra account to Purchases',
            'parent_account': None
        }
    )
    accounts_created.append(('Purchase-Return Main Account', purchase_return, created))
    
    # Print summary
    print("\n" + "=" * 80)
    print("ACCOUNT CREATION SUMMARY")
    print("=" * 80)
    
    for account_desc, account, is_new in accounts_created:
        status = "CREATED" if is_new else "EXISTS"
        print(f"[{status}] {account_desc}: {account.account_number} - {account.name}")
    
    print("\n" + "=" * 80)
    print("ACCOUNT STRUCTURE:")
    print("=" * 80)
    
    print(f"\n📊 GST ({gst_main.account_number})")
    print(f"   ├── GST-Sales ({gst_sales.account_number})")
    print(f"   └── GST-Purchases ({gst_purchases.account_number})")
    
    print(f"\n💰 Sales ({sales_main.account_number})")
    print(f"   ├── Cash-Sales ({cash_sales.account_number})")
    print(f"   └── Credit-Sales ({credit_sales.account_number})")
    print(f"   ⮑ Contra: Sales-Return ({sales_return.account_number})")
    
    print(f"\n🛒 Purchases ({purchases_main.account_number})")
    print(f"   ├── Cash-Purchases ({cash_purchases.account_number})")
    print(f"   └── Credit-Purchases ({credit_purchases.account_number})")
    print(f"   ⮑ Contra: Purchase-Return ({purchase_return.account_number})")
    
    print("\n" + "=" * 80)
    print("✅ Account creation completed successfully!")
    print("=" * 80)

if __name__ == '__main__':
    create_gl_accounts()
