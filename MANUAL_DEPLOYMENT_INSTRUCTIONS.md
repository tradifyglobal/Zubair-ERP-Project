# URGENT DEPLOYMENT - Copy & Paste Commands for Production Server

**Status:** Code is ready, needs to be deployed manually to production  
**Server:** 192.168.2.185  
**Path:** /var/www/tradifyerp/TradifyERP/expenses/

---

## Option 1: SSH Direct Command (Fast - 30 seconds)

Run this command directly on the production server console/terminal:

```bash
# Stop Gunicorn
systemctl stop gunicorn

# Update the two files
cd /var/www/tradifyerp/TradifyERP/expenses

# Get the latest code from GitHub
cd /var/www/tradifyerp
git pull origin changes
cd /var/www/tradifyerp/TradifyERP

# Restart Gunicorn
systemctl restart gunicorn

# Verify it's running
systemctl status gunicorn
```

---

## Option 2: Manual File Copy (If git doesn't work)

If git pull doesn't work, manually copy these two files to the server:

### File 1: notifications.py
**Location on server:** `/var/www/tradifyerp/TradifyERP/expenses/notifications.py`
**Location on this computer:** `TradifyERP/expenses/notifications.py`

Use WinSCP, FileZilla, or scp to copy this file to the server.

### File 2: context_processors.py
**Location on server:** `/var/www/tradifyerp/TradifyERP/expenses/context_processors.py`
**Location on this computer:** `TradifyERP/expenses/context_processors.py`

Then restart Gunicorn:
```bash
systemctl restart gunicorn
```

---

## Option 3: Git Pull (Recommended)

If the server has git access:

```bash
cd /var/www/tradifyerp
git fetch origin
git checkout changes
git pull origin changes

# Restart Gunicorn
systemctl restart gunicorn
```

---

## Verify Deployment

After copying files and restarting Gunicorn, run:

```bash
# Check Gunicorn is running
systemctl status gunicorn

# Check the logs for errors
journalctl -u gunicorn -n 20

# Test the code directly
cd /var/www/tradifyerp
python manage.py shell
from expenses.notifications import get_pending_approvals_for_user
from django.contrib.auth.models import User
burhan = User.objects.get(username='Burhan')
pending = get_pending_approvals_for_user(burhan)
print(f"Pending approvals for Burhan: {pending.count()}")
# Should output: Pending approvals for Burhan: 1 (or more)
exit()
```

---

## Then Tell Burhan To

1. **Clear browser cache** - Ctrl+Shift+Delete, select "Cookies" and "Cached images and files"
2. **Logout completely** - Click logout in the top right
3. **Close browser entirely** - Close all tabs/windows
4. **Open fresh browser** - Open a new browser window
5. **Login again** - Login as Burhan
6. **Check bell icon** - The notification should now appear

---

## File Contents (For Reference)

These are the two files that need to be on the server:

### notifications.py
- Simplified logic
- Staff users see all pending approvals
- Better error handling

### context_processors.py
- Makes notification data available to templates
- Better error handling and logging
- Converts QuerySets to lists for templates

---

## Commits

All code is committed to GitHub:
- Commit: `df2a3df`
- Branch: `changes`
- Repository: `tradifyglobal/Zubair-ERP-Project`

If the server has git, you can pull directly:
```bash
cd /var/www/tradifyerp
git pull origin changes
```

---

**Important:** After deployment, Burhan MUST clear his browser cache and login fresh. The old cached JavaScript and HTML is preventing him from seeing the new notification data.
