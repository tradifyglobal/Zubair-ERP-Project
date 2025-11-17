#!/usr/bin/env python
"""Append stakeholder models to main models file."""

with open('accounting/stakeholder_models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Stakeholder class
lines = content.split('\n')
start_idx = None
for i, line in enumerate(lines):
    if 'class Stakeholder' in line:
        start_idx = i
        break

if start_idx:
    stakeholder_content = '\n'.join(lines[start_idx:])
    
    with open('accounting/models.py', 'a', encoding='utf-8') as f:
        f.write('\n\n# ============ STAKEHOLDER MODELS ============\n\n')
        f.write(stakeholder_content)
    print('Stakeholder models appended successfully')
else:
    print('Could not find Stakeholder class')
