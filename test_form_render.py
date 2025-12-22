import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.stakeholder_forms import StakeholderForm

# Create a form instance
form = StakeholderForm()

# Render the form to HTML
html = str(form)

# Check if date inputs are in the HTML
if 'start_date' in html and 'end_date' in html:
    print("✓ SUCCESS: Date fields are in the rendered HTML!")
    
    # Check specifically for the form input elements
    if 'type="date"' in html and 'start_date' in html:
        print("✓ start_date input found")
    if 'type="date"' in html and 'end_date' in html:
        print("✓ end_date input found")
    
    # Show a snippet
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if 'start_date' in line.lower() or 'profit' in line.lower():
            # Print surrounding context
            start = max(0, i-1)
            end = min(len(lines), i+3)
            print("\nHTML snippet:")
            for j in range(start, end):
                print(lines[j])
            break
else:
    print("✗ FAILED: Date fields NOT found in rendered HTML")
    print("\nSearching for 'Profit' in HTML...")
    if 'Profit' in html:
        print("Found 'Profit' text")
    else:
        print("'Profit' text not found either")
