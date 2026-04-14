# Passwordless SSH Setup Guide

## Objective
Set up passwordless SSH connections to:
- **App Server**: 192.168.20.10 (root)
- **DB Server**: 192.168.20.11 (zubair)

And configure passwordless database access for migrations.

---

## Step 1: Generate SSH Key Pair (Windows)

Run in PowerShell as Administrator:

```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N ""
```

This creates:
- `C:\Users\[YourUsername]\.ssh\id_rsa` (private key - keep secret)
- `C:\Users\[YourUsername]\.ssh\id_rsa.pub` (public key - share)

---

## Step 2: Copy Public Key to App Server (root@192.168.20.10)

```powershell
# Copy public key to app server
$pubKey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
ssh root@192.168.20.10 "mkdir -p ~/.ssh && echo '$pubKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

When prompted, enter password: `erp`

---

## Step 3: Copy Public Key to DB Server (zubair@192.168.20.11)

```powershell
# Copy public key to DB server
$pubKey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
ssh zubair@192.168.20.11 "mkdir -p ~/.ssh && echo '$pubKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

When prompted, enter password: `sql`

---

## Step 4: Create SSH Config File (Optional but Recommended)

Create `C:\Users\[YourUsername]\.ssh\config` file:

```
Host app-server
    HostName 192.168.20.10
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no

Host db-server
    HostName 192.168.20.11
    User zubair
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
```

Now you can connect simply:
```powershell
ssh app-server
ssh db-server
```

---

## Step 5: Passwordless Database Access

Create `C:\Users\[YourUsername]\.pgpass` file with:

```
192.168.20.11:5432:tradifyerp_db:zubair:sql
```

Make sure it's only readable by you:
```powershell
# On Windows, set file permissions
icacls "$env:USERPROFILE\.pgpass" /grant:r "$env:USERNAME`:F" /inheritance:r
```

---

## Step 6: Verify Passwordless Connection

Test SSH connections:
```powershell
ssh root@192.168.20.10 "echo 'Connected to App Server'"
ssh zubair@192.168.20.11 "echo 'Connected to DB Server'"
```

Test database connection:
```powershell
# Install pgpass support (if needed)
# Then test connection
psql -h 192.168.20.11 -U zubair -d tradifyerp_db -c "SELECT 1"
```

---

## Troubleshooting

### Issue: Still asking for password
- Verify key is in `~/.ssh/authorized_keys` on servers
- Check permissions: `~/.ssh` should be 700, `authorized_keys` should be 600
- Restart SSH service: `sudo systemctl restart ssh` on servers

### Issue: Permission denied (publickey)
- Ensure public key is properly copied
- Check SSH service is running on servers
- Verify .ssh directory exists in home folder

### Issue: Database connection still asks password
- Ensure .pgpass file has correct permissions
- File must not be readable by others
- Format must be exactly: `hostname:port:database:username:password`

---

## Quick Reference Commands

```powershell
# Test app server connection
ssh root@192.168.20.10 "ls -la"

# Test DB server connection
ssh zubair@192.168.20.11 "ls -la"

# Test database access
psql -h 192.168.20.11 -U zubair -d tradifyerp_db

# View current SSH keys
Get-ChildItem "$env:USERPROFILE\.ssh"
```

---

## Security Notes
⚠️ **Never share your private key** (`id_rsa`)
- Keep `id_rsa` secure and never commit to version control
- Public key (`id_rsa.pub`) is safe to share
- Restrict .pgpass permissions to owner only
