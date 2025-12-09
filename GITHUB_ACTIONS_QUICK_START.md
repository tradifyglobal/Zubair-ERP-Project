# GitHub Actions Automated Deployment - Quick Start

## What You Now Have

✅ **Automatic deployment pipeline** that:
- Tests every code change
- Automatically deploys to production
- Handles migrations
- Collects static files
- Verifies application health
- Allows one-click rollback

## 5-Minute Setup

### 1. Generate Deployment SSH Key (On Your Server)

```bash
# Run on production server (192.168.2.185)
ssh -i ~/.ssh/tradifyerp_deploy root@192.168.2.185

# Generate new key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions_deploy -N ""

# Add public key to authorized_keys
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Display private key (copy this)
cat ~/.ssh/github_actions_deploy

# Exit
exit
```

### 2. Add SSH Key to GitHub (In Your Browser)

1. Go to GitHub: https://github.com/tradifyglobal/Zubair-ERP-Project
2. Click **Settings** (top right of repo)
3. Click **Secrets and variables** → **Actions** (left menu)
4. Click **New repository secret** (green button)
5. Fill in:
   - **Name:** `DEPLOY_SSH_PRIVATE_KEY`
   - **Value:** Paste the private key from step 1
6. Click **Add secret**

Done! That's it. Deployment is now automated.

## How It Works

### When You Push Code

```bash
# Make changes
echo "# New feature" >> README.md

# Commit and push
git add .
git commit -m "Add new feature"
git push origin changes
```

**GitHub Actions automatically:**
1. ✅ Runs tests
2. ✅ Checks code syntax
3. ✅ Deploys to server
4. ✅ Runs migrations
5. ✅ Restarts application

**Your changes go live automatically!**

### Workflow Status

Check deployment status:
1. Go to GitHub repo
2. Click **Actions** tab
3. See workflow running
4. Click on it for detailed logs

## Three Deployment Workflows

### 1. Automatic Deployment (deploy-production.yml)

**Triggers:** Push to `changes` or `main` branch

**What it does:**
- Pulls latest code
- Installs Python packages
- Runs Django migrations
- Collects static files
- Restarts Gunicorn
- Verifies application

**You don't need to do anything - it's automatic!**

### 2. Testing & Linting (test-and-lint.yml)

**Triggers:** Every push

**What it checks:**
- Python syntax errors
- Django system checks
- Database migrations
- Code quality (flake8)

**Fails deployment if there are errors** (good for catching bugs!)

### 3. Rollback (rollback.yml)

**Triggers:** Manual via GitHub UI

**How to use it:**
1. Go to **Actions** tab
2. Click **Rollback to Previous Version**
3. Click **Run workflow** dropdown
4. Enter commit hash to restore
5. Click **Run workflow**

**Instantly restores previous version!**

## Example: Making a Change

### Step 1: Clone and Update Code

```bash
# Get latest code
cd F:\ERP-Production\Zubair-ERP-Project
git checkout changes
git pull origin changes

# Make your change
# Edit file, add feature, fix bug, etc.
```

### Step 2: Commit and Push

```bash
git add .
git commit -m "Feature: add awesome enhancement"
git push origin changes
```

### Step 3: Watch Deployment

```bash
# Option 1: Watch on GitHub
# Go to https://github.com/tradifyglobal/Zubair-ERP-Project/actions

# Option 2: Check server (after a few seconds)
# Visit https://tradifyglobal.com
# Your changes should be live!
```

## Common Scenarios

### Scenario: Bug Fix

```bash
# Fix the bug in your code
git add .
git commit -m "Fix: resolve login issue"
git push origin changes
# GitHub Actions deploys automatically
# Bug is fixed on production server
```

### Scenario: Add Database Migration

```bash
# Create migration
cd TradifyERP
python manage.py makemigrations myapp

# Push changes
git add .
git commit -m "Add migration: new field"
git push origin changes
# GitHub Actions runs migration automatically
```

### Scenario: Update Dependencies

```bash
# Update requirements.txt with new package
vim TradifyERP/requirements.txt

# Push
git add TradifyERP/requirements.txt
git commit -m "Update: new package version"
git push origin changes
# GitHub Actions installs new packages automatically
```

### Scenario: Deployment Failed

1. Check **Actions** tab on GitHub
2. Click the failed workflow
3. Expand failed step
4. Read error message
5. Fix issue locally
6. Commit and push again

### Scenario: Rollback Needed

```
If something breaks:

1. Go to GitHub → Actions tab
2. Click "Rollback to Previous Version"
3. Enter previous commit hash
4. Click "Run workflow"
5. Application instantly reverted!
```

## File Locations

**GitHub Actions Workflows:**
- `.github/workflows/deploy-production.yml` - Main deployment
- `.github/workflows/test-and-lint.yml` - Testing
- `.github/workflows/rollback.yml` - Rollback

**Documentation:**
- `GITHUB_ACTIONS_SETUP.md` - Complete setup guide
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Manual deployment
- `PRODUCTION_BACKUP_README.md` - Backup branch info

**Server Logs:**
- `/var/log/gunicorn.log` - Application logs
- `/var/log/nginx/access.log` - Web server logs
- `/var/log/nginx/error.log` - Web server errors

## Quick Reference Commands

```bash
# View recent commits
git log --oneline -10

# Check GitHub Actions status
# Visit: https://github.com/tradifyglobal/Zubair-ERP-Project/actions

# Manual deployment (if needed)
git push origin changes

# Check deployment logs on server
ssh -i ~/.ssh/tradifyerp_deploy root@192.168.2.185 "tail -50 /var/log/gunicorn.log"

# Check application status
curl -I https://192.168.2.185/

# View GitHub workflow files
ls -la .github/workflows/
```

## Troubleshooting

### Workflow Not Triggering

**Check:**
1. Did you push to `changes` or `main` branch?
2. Are there any workflow syntax errors?
3. Is the `.github/workflows/` directory in repo root?

**Fix:**
```bash
git push origin changes  # Make sure you pushed
```

### SSH Connection Failed

**In GitHub Secrets:**
1. Click **Settings** → **Secrets**
2. Check `DEPLOY_SSH_PRIVATE_KEY` is set
3. Value should start with `-----BEGIN RSA PRIVATE KEY-----`

### Deployment Timeout

**Check server:**
```bash
ssh -i ~/.ssh/tradifyerp_deploy root@192.168.2.185
ps aux | grep gunicorn
```

### Database Migration Failed

**Check:**
1. Is PostgreSQL running?
2. Are credentials correct in `settings.py`?
3. Review migration file for errors

## Next Steps

1. ✅ **Setup is complete!** SSH key added to GitHub
2. 📝 **Make a test change** to verify deployment works
3. 📚 **Read full guide** if you want more details (GITHUB_ACTIONS_SETUP.md)
4. 🚀 **Start developing!** Changes deploy automatically

## Support Resources

- **GitHub Actions Docs:** https://docs.github.com/actions
- **Django Docs:** https://docs.djangoproject.com/
- **Server Access:** `ssh -i ~/.ssh/tradifyerp_deploy root@192.168.2.185`
- **View Logs:** Check GitHub Actions tab for deployment logs

---

**You're ready to go! Your deployment pipeline is automated!** 🎉

Every push to `changes` or `main` will automatically:
1. Test your code
2. Deploy to production
3. Restart the application
4. Verify everything works

No more manual deployments needed!
