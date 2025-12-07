#!/usr/bin/env python3
import sys

# Read the file with UTF-8 BOM
data = open('dev_final.json', 'rb').read()
print(f"File size: {len(data)} bytes", file=sys.stderr)
print(f"First 5 bytes: {list(data[:5])}", file=sys.stderr)

# Strip UTF-8 BOM if present
if data.startswith(b'\xef\xbb\xbf'):
    clean = data[3:]
    print(f"BOM found and removed", file=sys.stderr)
else:
    clean = data
    print(f"No BOM found", file=sys.stderr)

print(f"After strip first 5 bytes: {list(clean[:5])}", file=sys.stderr)

# Validate it's valid JSON
try:
    import json
    json.loads(clean.decode('utf-8'))
    print(f"Valid JSON", file=sys.stderr)
except Exception as e:
    print(f"Invalid JSON: {e}", file=sys.stderr)

# Write clean file
with open('dev_final_clean.json', 'wb') as f:
    f.write(clean)

print(f"Clean file written: {len(clean)} bytes", file=sys.stderr)
