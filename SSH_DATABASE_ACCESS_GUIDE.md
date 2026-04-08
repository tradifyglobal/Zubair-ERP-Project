# Passwordless SSH & Database Access - Quick Reference

## ✅ Setup Complete!

Your passwordless SSH and database access is now configured. No more entering passwords for connections or migrations!

---

## 🚀 Quick Connection Commands

### SSH Connections (No Password)

```powershell
# Using aliases (easiest)
ssh app-server
ssh db-server

# Using IP directly
ssh root@192.168.20.10
ssh zubair@192.168.20.11
```

### Database Connection (No Password)

```powershell
# Direct database connection
psql -h 192.168.20.11 -U zubair -d tradifyerp_db

# Or using shorthand
psql -h 192.168.20.11 -U zubair tradifyerp_db

# Execute SQL without password
psql -h 192.168.20.11 -U zubair -d tradifyerp_db -c "SELECT version();"
```

### Django Migrations (No Password)

```powershell
# Run migrations to remote database
python manage.py migrate --database=production

# Or via SSH
ssh root@192.168.20.10 "cd /path/to/project && python manage.py migrate"
```

---

## 🔍 Testing Your Setup

### Test SSH Access

```powershell
# Test app server
ssh root@192.168.20.10 "whoami"
# Expected output: root

# Test DB server
ssh zubair@192.168.20.11 "whoami"
# Expected output: zubair
```

### Test Database Access

```powershell
# Connect to database
psql -h 192.168.20.11 -U zubair -d tradifyerp_db -c "SELECT COUNT(*) FROM information_schema.tables;"
```

### Test Remote Command Execution

```powershell
# Check disk space on app server
ssh root@192.168.20.10 "df -h"

# Check PostgreSQL status on DB server
ssh zubair@192.168.20.11 "sudo systemctl status postgresql"
```

---

## 📁 Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `id_rsa` | Private SSH key (KEEP SECRET) | `C:\Users\Zubair\.ssh\id_rsa` |
| `id_rsa.pub` | Public SSH key (shared with servers) | `C:\Users\Zubair\.ssh\id_rsa.pub` |
| `config` | SSH host aliases & settings | `C:\Users\Zubair\.ssh\config` |
| `.pgpass` | PostgreSQL password file | `C:\Users\Zubair\.pgpass` |

---

## 📋 Server Information

### App Server
- **IP**: 192.168.20.10
- **User**: root
- **SSH Alias**: `app-server`
- **Connection**: `ssh app-server` or `ssh root@192.168.20.10`

### DB Server
- **IP**: 192.168.20.11
- **User**: zubair
- **SSH Alias**: `db-server`
- **Connection**: `ssh db-server` or `ssh zubair@192.168.20.11`
- **Database**: tradifyerp_db
- **DB User**: zubair

---

## 🛠️ Common Django/Database Tasks (No Password Required)

### Run Migrations via SSH

```powershell
# Connect to app server and run migrations
ssh root@192.168.20.10 "cd /path/to/erp/project && python manage.py migrate"
```

### Backup Database

```powershell
# Backup without password prompt
ssh zubair@192.168.20.11 "pg_dump -h localhost tradifyerp_db" > backup.sql
```

### Connect to Database Shell

```powershell
# Access PostgreSQL interactive shell
psql -h 192.168.20.11 -U zubair -d tradifyerp_db
```

### Run Python Script on App Server

```powershell
# Execute a Python script on the remote app server
ssh root@192.168.20.10 "cd /path/to/erp/project && python script_name.py"
```

---

## ⚠️ Security Notes

- ✅ Your **private key** (`id_rsa`) is kept locally and never shared
- ✅ Your **public key** (`id_rsa.pub`) is safely added to each server
- ✅ The `.pgpass` file is restricted to your user only
- ✅ All passwords are removed from command-line history
- ✅ SSH keys use 4096-bit RSA encryption (strong security)

---

## 🔧 Troubleshooting

### Still Asking for Password?

1. Verify the public key was added to servers:
   ```powershell
   ssh root@192.168.20.10 "cat ~/.ssh/authorized_keys"
   ```

2. Check SSH key permissions (should be 600):
   ```powershell
   ssh root@192.168.20.10 "ls -la ~/.ssh/authorized_keys"
   ```

3. Restart SSH on servers:
   ```powershell
   ssh root@192.168.20.10 "sudo systemctl restart ssh"
   ```

### Database Still Asking for Password?

1. Verify `.pgpass` file exists and has correct content:
   ```powershell
   Get-Content "$env:USERPROFILE\.pgpass"
   ```

2. Check file permissions (should be restricted to owner):
   ```powershell
   icacls "$env:USERPROFILE\.pgpass"
   ```

3. Format must be exactly: `hostname:port:database:username:password`

---

## 💾 Environment Variables (Optional)

For convenience, add these to your PowerShell profile:

```powershell
# Add to: $PROFILE

# Aliases for SSH
Set-Alias -Name sshapp -Value { ssh root@192.168.20.10 }
Set-Alias -Name sshdb -Value { ssh zubair@192.168.20.11 }

# Database connection shortcut
$env:PGPASSFILE = "$env:USERPROFILE\.pgpass"
```

---

## ✨ You're All Set!

All configurations are complete. You can now:
- ✅ Connect to servers without entering passwords
- ✅ Run database migrations without password prompts  
- ✅ Execute remote commands seamlessly
- ✅ Backup and manage databases easily

Enjoy passwordless access! 🎉
