# Setup passwordless SSH
$sshKeyPath = "$env:USERPROFILE\.ssh\id_ed25519.pub"
$publicKey = Get-Content $sshKeyPath

# For zubair@192.168.20.10
Write-Host "Setting up passwordless SSH for zubair@192.168.20.10..." -ForegroundColor Cyan

# Use ssh to append the public key to authorized_keys
$cmd = "mkdir -p ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'Key added successfully'"

Write-Host "Sending public key to server..." -ForegroundColor Yellow

# This approach uses ssh directly - you'll need to enter password once
ssh zubair@192.168.20.10 $cmd

Write-Host "`n✅ SSH key setup complete. Testing passwordless connection..." -ForegroundColor Green

# Test passwordless connection
ssh zubair@192.168.20.10 "echo 'Passwordless SSH is working!'"
