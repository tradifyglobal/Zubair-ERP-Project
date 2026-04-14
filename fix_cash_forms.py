#!/usr/bin/env python3
import re

filepath = '/var/www/tradifyerp/accounting/cash_forms.py'

with open(filepath, 'r') as f:
    content = f.read()

# Remove the line with 'account': 'Sub-Account (Debit)' from labels dict
content = re.sub(r"\s*'account':\s*'Sub-Account \(Debit\)',\n", "", content)

# Remove or comment out the line: self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
# Keep only the first occurrence in CashPaymentLineForm (around line 494)
lines = content.split('\n')
new_lines = []
account_field_removed = False

for i, line in enumerate(lines):
    # Skip the problematic line (only first occurrence after line 480)
    if i > 480 and i < 510 and "self.fields['account'].queryset" in line and not account_field_removed:
        new_lines.append('            # account field removed - field no longer exists')
        account_field_removed = True
    else:
        new_lines.append(line)

with open(filepath, 'w') as f:
    f.write('\n'.join(new_lines))

print("Fixed cash_forms.py")
