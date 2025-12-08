# Setup SSH Agent with the deployment key
# This script adds the SSH key to the agent so it won't ask for passphrase again in this session

$KeyPath = "$env:USERPROFILE\.ssh\tradifyerp_deploy"
$Passphrase = "Zub@ir0862"

Write-Host "Setting up SSH Agent..." -ForegroundColor Cyan

# Start SSH Agent if not already running
$Agent = Get-Service ssh-agent -ErrorAction SilentlyContinue
if ($null -eq $Agent) {
    Write-Host "SSH Agent service not found, installing..." -ForegroundColor Yellow
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -ErrorAction SilentlyContinue | Out-Null
}

# Start the agent
Start-Service ssh-agent -ErrorAction SilentlyContinue

# Add the key with passphrase using ssh-add
Write-Host "Adding SSH key to agent..." -ForegroundColor Green
$ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
$ProcessInfo.FileName = "ssh-add"
$ProcessInfo.Arguments = "`"$KeyPath`""
$ProcessInfo.RedirectStandardInput = $true
$ProcessInfo.UseShellExecute = $false
$ProcessInfo.CreateNoWindow = $true

$Process = [System.Diagnostics.Process]::Start($ProcessInfo)
$Process.StandardInput.WriteLine($Passphrase)
$Process.StandardInput.Close()
$Process.WaitForExit()

if ($Process.ExitCode -eq 0) {
    Write-Host "✅ SSH key successfully added to agent!" -ForegroundColor Green
    Write-Host "`nYou can now use SSH commands without entering the passphrase again in this terminal session." -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to add SSH key to agent" -ForegroundColor Red
    exit 1
}
