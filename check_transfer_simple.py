from accounting.models import CapitalContribution, InternationalTransferTracking

# Check contribution 282
try:
    contrib_282 = CapitalContribution.objects.get(id=282)
    print(f"Contribution 282 FOUND")
    print(f"  Entity ID: {contrib_282.entity_id}")
    print(f"  Entity Name: {contrib_282.entity.name if contrib_282.entity else 'NONE'}")
    
    # Check for transfer
    try:
        transfer = contrib_282.international_transfer
        print(f"  Transfer FOUND: ID {transfer.id}, Status: {transfer.transfer_status}")
    except:
        print(f"  No transfer tracking")
except:
    print("Contribution 282 NOT FOUND")

# Count all transfers
all_transfers = InternationalTransferTracking.objects.all()
print(f"Total transfers in DB: {all_transfers.count()}")

# Check transfers for entity 9 (Pristine-01)
transfers_9 = InternationalTransferTracking.objects.filter(capital_contribution__entity_id=9)
print(f"Transfers for entity 9: {transfers_9.count()}")

# List all transfers
for t in all_transfers:
    contrib = t.capital_contribution
    print(f"  Transfer {t.id}: Contrib {contrib.id}, Entity {contrib.entity_id}, Status {t.transfer_status}")
