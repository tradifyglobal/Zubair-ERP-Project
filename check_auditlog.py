#!/usr/bin/env python3
import json
import sys

with open('/var/www/tradifyerp/TradifyERP/dev_data_export.json') as f:
    data = json.load(f)

auditlogs = [obj for obj in data if obj.get('model') == 'accounting.auditlog']
print(f"Total AuditLogs: {len(auditlogs)}")

actions = set()
long_actions = []

for obj in auditlogs:
    if 'fields' in obj and 'action' in obj['fields']:
        action = obj['fields']['action']
        actions.add(action)
        if len(action) > 20:
            long_actions.append(obj)

print(f"Unique actions: {actions}")
print(f"Max action length: {max(len(a) for a in actions) if actions else 0}")
print(f"Actions > 20 chars: {len(long_actions)}")

if long_actions:
    print(f"\nFirst long action record:")
    print(json.dumps(long_actions[0], indent=2))
