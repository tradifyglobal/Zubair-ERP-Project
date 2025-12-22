import shutil
import os

source = '/tmp/stakeholder_models.py'
dest = '/var/www/tradifyerp/accounting/stakeholder_models.py'

try:
    # First copy to tmp
    shutil.copy('/tmp/stakeholder_models_new.py', dest)
    print(f'File copied successfully to {dest}')
except Exception as e:
    print(f'Error: {e}')
