# CRITICAL: Django Template Path Resolution for Accounting Dashboard

## IMPORTANT DISCOVERY - January 2, 2026

### Problem
When deploying changes to the Accounting Dashboard, modifications were being made to the wrong file location, causing all changes to be invisible to production users.

### Root Cause
Django's template resolution follows a specific order. For the accounting module dashboard, the production server serves templates from:
- **Actively served**: `/var/www/tradifyerp/templates/accounting/dashboard.html` ✅
- **NOT served**: `/var/www/tradifyerp/accounting/templates/accounting/dashboard.html` ❌

### The Issue
Multiple `dashboard.html` files exist across the server:
```
/var/www/tradifyerp/templates/accounting/dashboard.html           ← ACTIVE (use this)
/var/www/tradifyerp/accounting/templates/accounting/dashboard.html ← NOT served
/var/www/tradifyerp/templates/dashboard.html                       
/var/www/tradifyerp/templates/sales/dashboard.html
/var/www/tradifyerp/templates/procurement/dashboard.html
/var/www/tradifyerp/templates/ap/dashboard.html
/var/www/tradifyerp/templates/maintenance/dashboard.html
/var/www/tradifyerp/manufacturing/templates/manufacturing/dashboard.html
/var/www/tradifyerp/sales/templates/sales/dashboard.html
/var/www/tradifyerp/crm/templates/crm/dashboard.html
```

### Solution
When deploying dashboard changes, **ALWAYS** modify:
```
/var/www/tradifyerp/templates/accounting/dashboard.html
```

NOT the module-specific path:
```
/var/www/tradifyerp/accounting/templates/accounting/dashboard.html
```

### How to Deploy
```bash
# SSH into production server
ssh zubair@192.168.20.10

# Navigate to the correct location
cd /var/www/tradifyerp/templates/accounting/

# Edit the file
nano dashboard.html

# Or use SCP to copy from local
scp local_dashboard.html zubair@192.168.20.10:/var/www/tradifyerp/templates/accounting/dashboard.html

# After changes, clear caches and restart services
sudo rm -rf /var/cache/nginx/*
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

### Verification
To verify which file is being served:
```bash
# Check if file has your marker (e.g., CACHE_BUST comment)
ssh zubair@192.168.20.10 "grep 'CACHE_BUST' /var/www/tradifyerp/templates/accounting/dashboard.html"
```

### Cache Clearing Steps
After deploying to the correct location:

1. **Nginx Cache**: `sudo rm -rf /var/cache/nginx/*`
2. **Django Staticfiles**: `sudo rm -rf /var/www/tradifyerp/staticfiles/`
3. **Python Bytecode**: `find /var/www/tradifyerp -type d -name __pycache__ -exec rm -rf {} \;`
4. **Restart Services**:
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl reload nginx
   ```
5. **Browser**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Example Case Study: Accounting Dashboard Spacing Fix

**Problem**: Excessive white space at top of Accounting Dashboard  
**Root Cause**: Bootstrap applying `padding-bottom: 8rem !important`  
**Initial Mistake**: Deployed to `/var/www/tradifyerp/accounting/templates/accounting/dashboard.html`  
**Result**: No visible changes despite all cache clearing  
**Fix**: Modified `/var/www/tradifyerp/templates/accounting/dashboard.html` and it worked immediately

### Key Takeaway
Django uses a template loader that searches multiple paths in order:
1. App-specific template directories (if defined in INSTALLED_APPS)
2. Root templates directory (`/var/www/tradifyerp/templates/`)

The root templates directory takes precedence when multiple paths exist with the same filename.

### Prevention Going Forward
- Always verify the actual file being served before deploying
- Check production server directly: `grep -r "marker_text" /var/www/tradifyerp/templates/`
- After deployment, verify changes appear on the live site
- Document the correct paths for all critical templates

---
**Last Updated**: January 2, 2026  
**Status**: Critical - Follow this for all dashboard deployments
