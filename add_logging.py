#!/usr/bin/env python3
# Add logging to views.py to debug pending amounts

import re

filepath = '/var/www/tradifyerp/shareholder/views.py'

with open(filepath, 'r') as f:
    content = f.read()

# Find line 900 (context['investment_data'] = investment_data)
# and add logging before return context

logging_code = '''
        # DEBUG: Log pending amounts for  
        import logging
        logger = logging.getLogger(__name__)
        pending_amounts = [(inv['stakeholder'].first_name, inv.get('pending_in_foreign_bank')) for inv in investment_data]
        logger.warning(f"DEBUG INVESTMENT REPORT: Pending amounts being sent to template: {pending_amounts}")
        '''

# Find the return context line and insert logging before it
pattern = r'(\s+return context\n)'
replacement = logging_code + r'\n\1'
content = re.sub(pattern, replacement, content)

with open(filepath, 'w') as f:
    f.write(content)

print("Logging added to views.py")
