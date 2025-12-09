# GitHub Actions Automated Deployment Setup Guide

This guide explains how to set up GitHub Actions for automatic deployment of TradifyERP to your production server.

## Overview

Two GitHub Actions workflows are configured:

1. **test-and-lint.yml** - Runs tests on every push and pull request
2. **deploy-production.yml** - Automatically deploys to production server

## Prerequisites

- GitHub repository access
- Production server SSH access
- SSH private key for authentication

## Setup Instructions

### Step 1: Generate SSH Key for GitHub Actions

On your production server, create a dedicated key for deployments:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions_deploy -N ""
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Step 2: Add SSH Private Key to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `DEPLOY_SSH_PRIVATE_KEY`
5. Value: Copy the contents of `~/.ssh/github_actions_deploy` (the private key)
6. Click **Add secret**

### Step 3: Verify Server Configuration

Ensure your production server has:

```bash
# Check Python virtual environment exists
ls -la /var/www/tradifyerp/venv/bin/python

# Check git is installed
git --version

# Check gunicorn socket directory permissions
ls -la /var/www/tradifyerp/
```

### Step 4: Test the Workflow

Make a small change to your code:

```bash
git checkout changes
echo "# Test change" >> README.md
git add README.md
git commit -m "Test GitHub Actions deployment"
git push origin changes
```

Watch the GitHub Actions workflow execute:
1. Go to your GitHub repo
2. Click **Actions** tab
3. See the deployment workflow running

## Workflow Details

### deploy-production.yml

**Triggers:**
- Push to `changes` or `main` branch
- Manual trigger via `workflow_dispatch`

**Steps:**
1. Checkout code
2. Setup SSH connection
3. Stop Gunicorn on server
4. Pull latest code
5. Update Python dependencies
6. Run database migrations
7. Collect static files
8. Clear cache
9. Start Gunicorn
10. Verify application health
11. Check worker status

**Environment Variables:**
```
DEPLOY_USER: root
DEPLOY_HOST: 192.168.2.185
DEPLOY_PATH: /var/www/tradifyerp
PYTHON_VERSION: 3.12
```

### test-and-lint.yml

**Triggers:**
- Push to `changes` branch
- Pull requests to `changes` or `main`

**Steps:**
1. Setup Python environment
2. Start test PostgreSQL database
3. Install dependencies
4. Check syntax
5. Run Django checks
6. Test migrations
7. Lint code with flake8

## Making Code Changes and Deploying

### Normal Development Workflow

```bash
# 1. Create feature branch
git checkout changes
git pull origin changes

# 2. Make your changes
# Edit files, add features, fix bugs

# 3. Commit changes
git add .
git commit -m "Add feature or fix: description"

# 4. Push to GitHub
git push origin changes

# 5. GitHub Actions automatically:
#    - Runs tests (test-and-lint.yml)
#    - Runs deployment (deploy-production.yml)
#    - Updates production server

# 6. Verify deployment
# Check https://192.168.2.185 or https://tradifyglobal.com
```

### If Deployment Fails

1. Check GitHub Actions logs:
   - Go to **Actions** tab
   - Click failed workflow
   - Expand step that failed
   - Read error message

2. Common issues and fixes:

   **SSH Connection Failed:**
   - Verify `DEPLOY_SSH_PRIVATE_KEY` is correct
   - Check server firewall allows SSH

   **Database Migration Failed:**
   - Check PostgreSQL is running
   - Verify database credentials in settings.py
   - Review migration files for errors

   **Gunicorn Failed to Start:**
   - Check Python dependencies installed
   - Review `/var/log/gunicorn.log` on server
   - Verify PYTHONPATH is set correctly

   **Static Files Not Updated:**
   - Manually run: `python manage.py collectstatic --noinput`
   - Check file permissions on staticfiles directory

## Manual Deployment Override

If you need to deploy without pushing code:

1. Go to **Actions** tab
2. Click **Deploy to Production Server** workflow
3. Click **Run workflow** dropdown
4. Select branch
5. Click **Run workflow**

## Monitoring Deployments

### View Workflow Status

```bash
# In GitHub repository
1. Click Actions tab
2. View workflow runs
3. Click on a run to see details
```

### Check Server After Deployment

```bash
ssh -i ~/.ssh/tradifyerp_deploy root@192.168.2.185

# Check Gunicorn status
ps aux | grep gunicorn

# Check logs
tail -50 /var/log/gunicorn.log

# Check application
curl -I https://192.168.2.185/
```

## Security Best Practices

1. **Keep SSH key secret**
   - Never commit private keys to repository
   - GitHub Secrets are encrypted

2. **Rotate keys regularly**
   - Generate new key: `ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions_deploy -N ""`
   - Update GitHub Secret
   - Remove old key from `authorized_keys`

3. **Use read-only deployment user (Optional)**
   - For extra security, create dedicated user: `useradd -m -s /bin/bash deploy`
   - Grant only necessary permissions
   - Use this user in deployment workflow

4. **Monitor deployment logs**
   - Check GitHub Actions logs after each deployment
   - Set up email notifications for failed deployments

## Customization

### Change Deployment Branch

Edit `.github/workflows/deploy-production.yml`:

```yaml
on:
  push:
    branches:
      - production  # Change from 'changes' to 'production'
      - main
```

### Change Server Address

Edit `.github/workflows/deploy-production.yml`:

```yaml
env:
  DEPLOY_HOST: your.new.ip.address  # Change to new server IP
```

### Add Custom Deployment Steps

Add new steps before "Start Gunicorn":

```yaml
      - name: My custom step
        run: |
          ssh -i ~/.ssh/deploy_key ${{ env.DEPLOY_USER }}@${{ env.DEPLOY_HOST }} \
            "your command here"
```

## Troubleshooting

### Workflow doesn't trigger

- Verify workflow file is in `.github/workflows/` directory
- Check branch name matches trigger condition
- Try `workflow_dispatch` to manually trigger

### SSH timeout

- Check server is accessible: `ping 192.168.2.185`
- Verify SSH port 22 is open
- Check server firewall rules

### Dependencies not installing

- Update requirements.txt with all packages
- Check pip has internet access on server
- Verify Python version compatibility

## Common Deployment Scenarios

### Scenario 1: Bug Fix Deployment

```bash
git checkout changes
git pull origin changes
# Fix the bug
git add .
git commit -m "Fix: bug description"
git push origin changes
# GitHub Actions automatically deploys
```

### Scenario 2: Feature Addition

```bash
git checkout changes
git pull origin changes
# Add new feature
git add .
git commit -m "Feature: new feature description"
git push origin changes
# GitHub Actions tests and deploys
```

### Scenario 3: Database Migration

```bash
git checkout changes
# Add new migration file to TradifyERP/migrations/
git add TradifyERP/migrations/
git commit -m "Add migration: description"
git push origin changes
# GitHub Actions runs migration automatically
```

### Scenario 4: Security Update

```bash
# Update requirements.txt with new package version
git checkout changes
git add TradifyERP/requirements.txt
git commit -m "Security: update package version"
git push origin changes
# GitHub Actions tests and deploys
```

## Rollback Procedure

If deployment causes issues:

```bash
# 1. Stop current deployment in GitHub Actions (usually automatic)

# 2. Revert changes locally
git revert <commit-hash>

# 3. Push revert commit
git push origin changes

# 4. GitHub Actions deploys reverted code

# 5. Verify rollback
# Check https://tradifyglobal.com
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/latest/source/gunicorn.app.base.html)

## Support

For issues with GitHub Actions deployment:

1. Check GitHub Actions logs
2. Review error messages
3. Check server logs: `/var/log/gunicorn.log`
4. Verify server configuration matches production setup

---

**Last Updated:** December 9, 2025  
**Status:** ✅ Production Ready
