import re

template_path = '/var/www/tradifyerp/shareholder/templates/shareholder/investment_report.html'

with open(template_path, 'r') as f:
    content = f.read()

# Find the pending column and add debug output before it
old = '''                                    <td>
                                        {% if investment.pending_in_foreign_bank and investment.pending_in_foreign_bank > 0 %}'''

new = '''                                    <td>
                                        <!-- DEBUG: val={{ investment.pending_in_foreign_bank }} -->
                                        {% if investment.pending_in_foreign_bank and investment.pending_in_foreign_bank > 0 %}'''

content = content.replace(old, new)

with open(template_path, 'w') as f:
    f.write(content)

print("Debug output added to template")
