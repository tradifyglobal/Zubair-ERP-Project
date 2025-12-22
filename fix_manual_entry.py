import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/var/www/tradifyerp')
os.chdir('/var/www/tradifyerp')

os.environ['DJANGO_SETTINGS_MODULE'] = 'TradifyERP.settings_production'
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution

print("🔧 FIXING YOUR CASH RECEIPT ENTRY")
print("=" * 50)

# Get your cash receipt
receipt = CashReceiptLine.objects.get(id=10)
print(f"📄 Your Cash Receipt:")
print(f"   ID: {receipt.id}")
print(f"   Description: {receipt.description}")
print(f"   Amount: {receipt.debit_amount} {receipt.currency.code}")
print(f"   Account: {receipt.account.name}")
print(f"   Stakeholder: {receipt.stakeholder.first_name} {receipt.stakeholder.last_name if receipt.stakeholder else 'None'}")
print(f"   Status: {receipt.workflow_status}")
print(f"   Posted: {receipt.is_capital_contribution_posted}")
print()

# Check existing contributions
existing = CapitalContribution.objects.filter(source_cash_receipt_id=10).count()
print(f"📊 Existing contributions: {existing}")
print()

print("🚀 Triggering signal by saving the receipt...")
# This should trigger the capital contribution creation signal
receipt.save()

# Check results
receipt.refresh_from_db()
new_contributions = CapitalContribution.objects.filter(source_cash_receipt_id=10)

print(f"✅ Results after signal:")
print(f"   Contributions created: {new_contributions.count()}")
print(f"   Receipt posted flag: {receipt.is_capital_contribution_posted}")
print()

if new_contributions.exists():
    print("🎉 SUCCESS! Capital contribution created:")
    for contrib in new_contributions:
        print(f"   💰 ID: {contrib.id}")
        print(f"   👤 Stakeholder: {contrib.stakeholder.first_name} {contrib.stakeholder.last_name}")
        print(f"   💵 Amount: {contrib.amount} {contrib.currency.code}")
        print(f"   🏢 Company Currency: {contrib.currency_destination.code}")
        print(f"   💱 Converted Amount: {contrib.amount_company_currency}")
        print(f"   🤖 Auto-created: {contrib.is_auto_posted}")
        print(f"   📅 Date: {contrib.contribution_date}")
else:
    print("❌ Still no capital contribution created")

print()
print("📋 LESSON LEARNED:")
print("When creating cash receipts manually, always assign the stakeholder field")
print("for the automatic capital contribution workflow to work!")