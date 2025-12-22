#!/usr/bin/env python3
import subprocess
import sys

# Deploy the fixed urls.py using ssh directly
commands = [
    ("sudo cp /tmp/urls_fixed.py /var/www/tradifyerp/accounting/urls.py", "Deploy file"),
    ("grep urls_trial_balance /var/www/tradifyerp/accounting/urls.py | head -1", "Verify import"),
    ("grep \"^    # path('trial-balances/'\" /var/www/tradifyerp/accounting/urls.py", "Verify old route is commented"),
    ("sudo systemctl restart gunicorn", "Restart Gunicorn"),
    ("sleep 2 && curl -s -I http://localhost:8000/accounting/trial-balances/ | head -3", "Test endpoint"),
]

for cmd, desc in commands:
    print(f"\n{'='*60}")
    print(f"[{desc}]")
    print(f"{'='*60}")
    
    # Use echo to pass password to sudo
    full_cmd = f'echo "erp" | sudo -S bash -c "{cmd}"'
    
    try:
        result = subprocess.run(
            f'plink -ssh -batch -l zubair -pw erp 192.168.20.10 "{full_cmd}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print("STDERR:", result.stderr)
        print(f"Return code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Command took too long")
    except Exception as e:
        print(f"ERROR: {e}")

print(f"\n{'='*60}")
print("Deployment completed!")
print(f"{'='*60}")
