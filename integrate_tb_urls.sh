#!/bin/bash
# Add Trial Balance URLs to main accounting URLs

echo 'erp' | sudo -S bash << 'EOF'
cat >> /var/www/tradifyerp/accounting/urls.py << 'URLEOF'

# Import Trial Balance URLs  
from .urls_trial_balance import urlpatterns as trial_balance_urlpatterns

# Add Trial Balance URL patterns
urlpatterns += trial_balance_urlpatterns
URLEOF
EOF
