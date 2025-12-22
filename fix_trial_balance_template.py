#!/usr/bin/env python3
"""
Fix trial_balance_list.html template by removing non-existent URL references
"""

template_path = '/var/www/tradifyerp/templates/accounting/trial_balance_list.html'

# Read the template
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track changes
changes = []

# Remove Actions column header (line 113, 0-indexed = 112)
if 112 < len(lines) and 'Actions' in lines[112]:
    changes.append(f"Line 113: Removed Actions column header")
    lines.pop(112)

# After removing line 113, lines 165-175 become 164-174
# Remove the Actions td cell (lines 164-174 in 0-indexed after first removal)
# Find the line with the Actions td
for i, line in enumerate(lines):
    if '<td class="text-end pe-4">' in line and i > 150:
        # Found the Actions td, remove it and the next lines until </td>
        start_idx = i
        end_idx = i
        # Find the closing </td>
        for j in range(i, min(i + 20, len(lines))):
            if '</td>' in lines[j]:
                end_idx = j
                break
        
        # Remove lines from start_idx to end_idx (inclusive)
        removed_lines = lines[start_idx:end_idx+1]
        changes.append(f"Lines {start_idx+1}-{end_idx+1}: Removed Actions td with button links")
        del lines[start_idx:end_idx+1]
        break

# Fix colspan from 8 to 7
for i, line in enumerate(lines):
    if 'colspan="8"' in line:
        lines[i] = line.replace('colspan="8"', 'colspan="7"')
        changes.append(f"Line {i+1}: Changed colspan from 8 to 7")

# Write the fixed template
with open(template_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Template fixed successfully!")
print(f"Total changes made: {len(changes)}")
for change in changes:
    print(f"  - {change}")
print(f"\nTemplate saved to: {template_path}")
