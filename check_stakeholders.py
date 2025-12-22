from accounting.models import Stakeholder, Entity

print('=== CHECKING STAKEHOLDERS ===')
print(f'Total Stakeholders: {Stakeholder.objects.count()}')
print(f'Active Stakeholders: {Stakeholder.objects.filter(status="ACTIVE").count()}')
print()

entities = Entity.objects.all()[:3]
for entity in entities:
    print(f'\nEntity: {entity.name} (ID: {entity.id})')
    stakeholders = Stakeholder.objects.filter(entity=entity)
    print(f'  Total stakeholders: {stakeholders.count()}')
    print(f'  Active stakeholders: {stakeholders.filter(status="ACTIVE").count()}')
    
    for s in stakeholders[:5]:
        name = f"{s.first_name or ''} {s.last_name or ''}".strip() or s.company_name or f"Stakeholder {s.id}"
        print(f'    - {s.id}: {name} (Status: {s.status})')

print('\n=== Done ===')
