#!/usr/bin/env python3
import os
import glob

# Find and rename all .disabled files
for f in glob.glob('/var/www/tradifyerp/TradifyERP/**/*.disabled', recursive=True):
    new_name = f[:-9]  # Remove '.disabled'
    try:
        os.rename(f, new_name)
        print(f"Renamed: {os.path.basename(f)} -> {os.path.basename(new_name)}")
    except Exception as e:
        print(f"Error renaming {f}: {e}")

# Count remaining disabled files
remaining = len(glob.glob('/var/www/tradifyerp/TradifyERP/**/*.disabled', recursive=True))
print(f"\nRemaining .disabled files: {remaining}")
