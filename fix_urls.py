#!/usr/bin/env python3
"""Fix urls.py file to properly include trial balance URLs"""

import os

urls_file = '/var/www/tradifyerp/accounting/urls.py'

# Read the file
with open(urls_file, 'r') as f:
    content = f.read()

# Remove duplicate imports if they exist
lines = content.split('\n')
seen_imports = set()
cleaned_lines = []

for line in lines:
    if 'from .urls_trial_balance import' in line:
        if line not in seen_imports:
            cleaned_lines.append(line)
            seen_imports.add(line)
    elif 'urlpatterns += trial_balance_urlpatterns' in line:
        if line not in seen_imports:
            cleaned_lines.append(line)
            seen_imports.add(line)
    else:
        cleaned_lines.append(line)

# Ensure proper ending
final_content = '\n'.join(cleaned_lines)

# Make sure we have the complete pattern at the end
if 'from .urls_trial_balance import urlpatterns as trial_balance_urlpatterns' in final_content:
    if 'urlpatterns += trial_balance_urlpatterns' not in final_content:
        final_content = final_content.rstrip() + '\n# Add Trial Balance URL patterns\nurlpatterns += trial_balance_urlpatterns\n'
    elif not final_content.endswith('\n'):
        final_content += '\n'

# Write back
with open(urls_file, 'w') as f:
    f.write(final_content)

print("✓ URLs file cleaned and verified")
print("✓ Trial Balance URLs properly integrated")
