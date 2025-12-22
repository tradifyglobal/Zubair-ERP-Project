#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

django.setup()

from django.urls import get_resolver

resolver = get_resolver()

print("Checking for trial_balance URLs in 'accounting' namespace...\n")

print("\nAll URL names with 'trial' in them:")
def find_urls(patterns, namespace=''):
    for pattern in patterns:
        if hasattr(pattern, 'url_patterns'):
            # This is an include, recurse
            ns = f"{namespace}:{pattern.namespace}" if pattern.namespace else namespace
            find_urls(pattern.url_patterns, ns)
        elif hasattr(pattern, 'name') and pattern.name and 'trial' in pattern.name.lower():
            full_name = f"{namespace}:{pattern.name}" if namespace else pattern.name
            print(f"  - {full_name}")

find_urls(resolver.url_patterns)
