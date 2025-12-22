import json

with open('/tmp/shareholder_final.json') as f:
    all_data = json.load(f)

# Extract only contributions 
contrib_only = [item for item in all_data if 'contribution' in item['model'].lower()]

with open('/tmp/contributions_only.json', 'w') as f:
    json.dump(contrib_only, f)

print(f'Extracted {len(contrib_only)} contribution items')
for model in sorted(set(item['model'] for item in contrib_only)):
    count = sum(1 for i in contrib_only if i['model'] == model)
    print(f'  {model}: {count}')
