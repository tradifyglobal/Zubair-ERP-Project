#!/usr/bin/env python3
# Add debug output to investment_report.html template

filepath = '/var/www/tradifyerp/shareholder/templates/shareholder/investment_report.html'

with open(filepath, 'r') as f:
    content = f.read()

# Find the pending in foreign bank section and add debug output
old_line = '{% if investment.pending_in_foreign_bank and investment.pending_in_foreign_bank > 0 %}'
new_line = '''<!-- DEBUG: pending_in_foreign_bank={{ investment.pending_in_foreign_bank }}, type={{ investment.pending_in_foreign_bank|add:"" }} -->
                                        {% if investment.pending_in_foreign_bank and investment.pending_in_foreign_bank > 0 %}'''

content = content.replace(old_line, new_line)

with open(filepath, 'w') as f:
    f.write(content)

print("Template modified with debug output")
