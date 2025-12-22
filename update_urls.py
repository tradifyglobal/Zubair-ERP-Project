#!/usr/bin/env python3
"""Add shareholder investment URLs to accounting/urls.py"""

urls_file = '/var/www/tradifyerp/accounting/urls.py'

# Read the file
with open(urls_file, 'r') as f:
    content = f.read()

# Check if shareholder investment URLs already exist
if 'shareholder-investment-report' in content:
    print('URLs already exist')
    exit(0)

# New URLs to add
new_urls = '''
# Shareholder Investment Reporting URLs
from .views_reports import (
    ShareholderInvestmentRegisterListView,
    ShareholderInvestmentReportView,
    ShareholderCapitalStatusView,
    ShareholderInvestmentDetailView,
    ShareholderInvestmentAuditTrailView,
)

urlpatterns += [
    path('shareholder-investments/', ShareholderInvestmentRegisterListView.as_view(), name='shareholder_investment_register'),
    path('shareholder-investment-report/', ShareholderInvestmentReportView.as_view(), name='shareholder_investment_report'),
    path('shareholder-capital-status/', ShareholderCapitalStatusView.as_view(), name='shareholder_capital_status'),
    path('shareholder-investment/<int:pk>/', ShareholderInvestmentDetailView.as_view(), name='shareholder_investment_detail'),
    path('shareholder-investment/<int:pk>/audit/', ShareholderInvestmentAuditTrailView.as_view(), name='shareholder_investment_audit'),
]
'''

# Insert before the last urlpatterns += block (just before theme import)
insertion_point = content.rfind('# Import dashboard views')

if insertion_point > 0:
    # Insert just before the dashboard views comment
    new_content = content[:insertion_point] + new_urls + '\n\n' + content[insertion_point:]
else:
    # If not found, append to end
    new_content = content + '\n' + new_urls

# Write back
with open(urls_file, 'w') as f:
    f.write(new_content)

print('URLs updated successfully')
