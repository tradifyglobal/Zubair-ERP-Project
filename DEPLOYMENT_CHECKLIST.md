# Production Deployment Checklist

## Pre-Deployment (One-time setup)

- [ ] **SSH Keys Setup**
  - [ ] Read `SECURE_DEPLOYMENT_SETUP.md`
  - [ ] Generate SSH key pair on your machine
  - [ ] Copy public key to server
  - [ ] Verify passwordless SSH works
  - [ ] Change server password after SSH setup

- [ ] **Environment Setup**
  - [ ] Verify server IP: 192.168.2.185
  - [ ] Verify username: Zubair
  - [ ] Test SSH connection works without password
  - [ ] Ensure rsync is available on both machines

- [ ] **Application Setup on Server**
  - [ ] Create application directory (`/home/Zubair/tradifyerp`)
  - [ ] Create `.env` file with production settings
  - [ ] Install Python 3.8+
  - [ ] Install PostgreSQL (if using)
  - [ ] Set up Gunicorn or other WSGI server
  - [ ] Set up Nginx as reverse proxy (optional)

## Before Each Deployment

- [ ] **Code Quality**
  - [ ] Run tests locally: `pytest`
  - [ ] Check for linting issues: `flake8`
  - [ ] Review recent changes: `git log --oneline -10`
  - [ ] Verify no hardcoded credentials in code

- [ ] **Database Safety**
  - [ ] Backup production database
  - [ ] Review migration files
  - [ ] Test migrations locally first

- [ ] **Configuration**
  - [ ] Verify `requirements.txt` is up to date
  - [ ] Check all environment variables are set
  - [ ] Verify static file settings
  - [ ] Check DEBUG = False for production

## Deployment Steps

Run this command from PowerShell:

```powershell
python deploy_production.py
```

This will automatically:
1. ✅ Verify SSH connection
2. ✅ Get server information
3. ✅ Backup existing application
4. ✅ Sync repository to server
5. ✅ Install dependencies
6. ✅ Run database migrations
7. ✅ Collect static files
8. ✅ Restart application
9. ✅ Verify deployment

## Post-Deployment

- [ ] **Verification**
  - [ ] Check application is running: `http://192.168.2.185`
  - [ ] Test main features work
  - [ ] Check server logs for errors
  - [ ] Verify database connection works
  - [ ] Test user authentication

- [ ] **Monitoring**
  - [ ] Monitor server CPU/Memory
  - [ ] Check application logs
  - [ ] Set up uptime monitoring
  - [ ] Set up error logging/alerting

- [ ] **Rollback Plan**
  - [ ] Know where backups are stored
  - [ ] Have rollback procedure documented
  - [ ] Keep previous deployment backup for 7 days

## Troubleshooting

### SSH Connection Issues
```powershell
# Test SSH
ssh zubair@192.168.2.185 "echo test"

# Check public key on server
ssh zubair@192.168.2.185 "cat ~/.ssh/authorized_keys"
```

### Rsync Issues
```powershell
# Install rsync on Windows (via chocolatey)
choco install rsync

# Or use WSL if available
wsl rsync --version
```

### Python/Dependency Issues
```bash
# On server, manually test
cd /home/Zubair/tradifyerp
python3 -m pip install -r requirements.txt
python3 manage.py migrate
```

### Application Won't Start
```bash
# Check server logs
ssh zubair@192.168.2.185 "tail -f /var/log/gunicorn/*.log"

# Check application directory
ssh zubair@192.168.2.185 "ls -la /home/Zubair/tradifyerp"
```

## Security Reminders

⚠️ **CRITICAL**:
- Never commit `.env` files with secrets
- Never share private SSH key
- Use SSH keys instead of passwords
- Regularly update server packages
- Monitor server access logs
- Use strong passwords for other accounts
- Enable firewall and only allow necessary ports
- Keep database credentials in environment variables only

## Rollback Procedure

If deployment fails or causes issues:

```bash
# On server, restore from backup
ssh zubair@192.168.2.185 << 'EOF'
# Find the backup
ls -la /home/Zubair/tradifyerp_backup_*

# Restore (replace TIMESTAMP with actual backup)
rm -rf /home/Zubair/tradifyerp
cp -r /home/Zubair/tradifyerp_backup_TIMESTAMP /home/Zubair/tradifyerp

# Restart application
sudo systemctl restart gunicorn
EOF
```

## Support

For issues or questions:
1. Check the logs: `ssh zubair@192.168.2.185 "tail -f /var/log/gunicorn/*.log"`
2. Review this deployment guide
3. Check application error logs in remote app directory
4. Test components individually
