#!/usr/bin/env python3
"""
Script to run Django OTP migration on production server
"""
import paramiko
import sys

# Server credentials
SERVER_IP = "192.168.20.10"
SSH_USER = "root"
SSH_PASSWORD = None  # Use key-based auth first
SSH_KEY = None

# Django settings
DJANGO_PATH = "/var/www/tradifyerp"
VENV_PYTHON = f"{DJANGO_PATH}/venv/bin/python"

def run_migration():
    """SSH into server and run Django OTP migration"""
    
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to server
        print(f"Connecting to {SERVER_IP} as {SSH_USER}...")
        
        # Try key-based authentication first, fall back to password
        client.connect(
            SERVER_IP,
            username=SSH_USER,
            password=SSH_PASSWORD,
            key_filename=SSH_KEY,
            timeout=10
        )
        
        print("✓ SSH connection established")
        
        # Run the migration
        cmd = f"cd {DJANGO_PATH} && {VENV_PYTHON} manage.py migrate django_otp"
        print(f"\nRunning: {cmd}\n")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Print output
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        
        if output:
            print("STDOUT:")
            print(output)
        
        if errors:
            print("STDERR:")
            print(errors)
        
        # Check exit status
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print("\n✓ Migration completed successfully!")
        else:
            print(f"\n✗ Migration failed with exit code {exit_code}")
            return False
            
    except paramiko.ssh_exception.AuthenticationException:
        print("✗ SSH Authentication failed. Check credentials.")
        return False
    except paramiko.ssh_exception.SSHException as e:
        print(f"✗ SSH Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        client.close()
    
    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
