# Secure Production Deployment Setup

## Server Details
- **IP Address**: 192.168.2.185
- **Username**: Zubair
- **Protocol**: SSH (key-based authentication)

## Step 1: Generate SSH Keys (If you don't have them)

Run this on your local machine (Windows PowerShell):

```powershell
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N ""
```

This creates:
- `~\.ssh\id_rsa` (private key - keep secret)
- `~\.ssh\id_rsa.pub` (public key - share with server)

## Step 2: Copy Public Key to Server

On Windows PowerShell:

```powershell
# Copy your public key to the server
$publicKey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
ssh zubair@192.168.2.185 "mkdir -p ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

You'll be prompted for the password ONE TIME. After this, future connections will be passwordless.

## Step 3: Verify Passwordless SSH

```powershell
# This should connect WITHOUT asking for a password
ssh zubair@192.168.2.185 "echo 'SSH key authentication successful!'"
```

## Step 4: Deploy the Application

Once SSH is configured, run:

```powershell
# Run the deployment script
python deploy_production.py
```

## Security Notes

⚠️ **IMPORTANT**:
- Never share your private key (`id_rsa`)
- Keep your private key secure - it authenticates as you
- Once SSH keys are set up, change your password on the server for additional security
- Remove credentials from any scripts or configuration files

## Troubleshooting

**SSH connection still asks for password?**
- Verify public key was added: `ssh zubair@192.168.2.185 cat ~/.ssh/authorized_keys`
- Check permissions on server: `ssh zubair@192.168.2.185 ls -la ~/.ssh/`
- Should show: `-rw------- 1 zubair zubair` for authorized_keys

**Permission denied (publickey)?**
- Ensure `~/.ssh/authorized_keys` on server has the correct public key content
- Verify file permissions are 600
