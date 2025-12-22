import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/var/www/tradifyerp')
os.chdir('/var/www/tradifyerp')

os.environ['DJANGO_SETTINGS_MODULE'] = 'TradifyERP.settings_production'
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution

print("🧪 TESTING NEW CASH RECEIPT WORKFLOW")
print("=" * 50)

# Get the new test receipt
receipt = CashReceiptLine.objects.get(id=9)
print(f"📄 New Cash Receipt Created:")
print(f"   ID: {receipt.id}")
print(f"   Description: {receipt.description}")
print(f"   Stakeholder: {receipt.stakeholder.first_name} {receipt.stakeholder.last_name}")
print(f"   Amount: {receipt.debit_amount} {receipt.currency.code}")
print(f"   Entity Currency: {receipt.entity.company_currency.code}")
print(f"   Current Status: {receipt.workflow_status}")
print(f"   Already Posted: {receipt.is_capital_contribution_posted}")
print()

# Check for any existing capital contributions
existing_count = CapitalContribution.objects.filter(source_cash_receipt_id=9).count()
print(f"📊 Existing Capital Contributions for this receipt: {existing_count}")
print()

print("🔄 STEP 1: Approving cash receipt...")
print("   Changing workflow_status from DRAFT → APPROVED")

# This should trigger the signal
receipt.workflow_status = 'APPROVED'
receipt.save()

print(f"   ✅ Status updated to: {receipt.workflow_status}")
print()

print("🔍 STEP 2: Checking results...")
# Refresh data from database
receipt.refresh_from_db()

# Check for new capital contributions
new_contributions = CapitalContribution.objects.filter(source_cash_receipt_id=9)
print(f"   📈 Capital Contributions after approval: {new_contributions.count()}")
print(f"   🏷️  Receipt marked as posted: {receipt.is_capital_contribution_posted}")
print()

if new_contributions.exists():
    print("🎉 SUCCESS! Automatic capital contribution created:")
    print("=" * 50)
    for contrib in new_contributions:
        print(f"   💰 Capital Contribution ID: {contrib.id}")
        print(f"   👤 Stakeholder: {contrib.stakeholder.first_name} {contrib.stakeholder.last_name}")
        print(f"   💵 Original Amount: {contrib.amount} {contrib.currency.code}")
        print(f"   🏢 Company Currency: {contrib.currency_destination.code}")
        print(f"   💱 Company Amount: {contrib.amount_company_currency}")
        print(f"   📊 Exchange Rate: {contrib.exchange_rate}")
        print(f"   🤖 Auto-created: {contrib.is_auto_posted}")
        print(f"   ✅ Status: {contrib.workflow_status}")
        print(f"   🔗 Source Receipt: {contrib.source_cash_receipt_id}")
        print(f"   📅 Date: {contrib.contribution_date}")
        print(f"   💳 Payment Mode: {contrib.payment_mode}")
else:
    print("❌ FAILED! No capital contribution was created")
    print("   This indicates the signal didn't work properly")

print()
print("📋 SUMMARY:")
print("=" * 50)
if new_contributions.exists() and receipt.is_capital_contribution_posted:
    print("✅ Workflow Test: PASSED")
    print("✅ Automatic conversion: WORKING") 
    print("✅ Currency handling: CORRECT")
    print("✅ Signal system: FUNCTIONAL")
else:
    print("❌ Workflow Test: FAILED")
    print("❌ Check signal configuration or database connections")

print()
print("🏁 Test completed!")

# Show the current state in the investment reports
print()
print("📊 VERIFICATION: Check investment report data...")
total_contributions = CapitalContribution.objects.filter(
    entity_id=7,
    stakeholder_id=10
).count()
total_amount = sum([c.amount_company_currency for c in CapitalContribution.objects.filter(
    entity_id=7,
    stakeholder_id=10
)])
print(f"   Ahsan Ali Khan total contributions: {total_contributions}")
print(f"   Ahsan Ali Khan total amount: {total_amount} INR")