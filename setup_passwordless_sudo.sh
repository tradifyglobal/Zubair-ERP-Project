#!/bin/bash
# This script must be run with sudo password once to set up passwordless sudo for zubair user
# Usage: echo '<password>' | sudo -S bash setup_passwordless_sudo.sh

# Add zubair to sudoers with NOPASSWD for specific commands
echo "Setting up passwordless sudo for zubair user..."

# Create a sudoers file entry for zubair
sudo tee /etc/sudoers.d/zubair-nopass > /dev/null <<EOF
# Allow zubair to run specific commands without password
zubair ALL=(ALL) NOPASSWD: /usr/sbin/ufw

# Allow all sudo commands without password (less secure but more convenient)
# zubair ALL=(ALL) NOPASSWD: ALL
EOF

# Fix permissions on sudoers file
sudo chmod 0440 /etc/sudoers.d/zubair-nopass

# Verify the change
echo "Verifying sudoers configuration..."
sudo visudo -c

if [ $? -eq 0 ]; then
    echo "✅ Passwordless sudo configured successfully"
    echo "zubair can now run 'sudo ufw ...' without entering a password"
else
    echo "❌ Error in sudoers configuration"
    exit 1
fi
