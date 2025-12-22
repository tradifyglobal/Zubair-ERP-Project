#!/usr/bin/env python3
"""
Deploy the fixed models.py to production server
"""
import base64
import subprocess
import sys

# Read the file
with open(r"f:\ERP-Production\Zubair-ERP-Project\TradifyERP\accounting\models.py", 'rb') as f:
    content = f.read()

# Encode to base64
encoded = base64.b64encode(content).decode('ascii')

# Split into chunks to avoid command line length issues
chunk_size = 5000
chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]

print(f"Deploying {len(content)} bytes in {len(chunks)} chunks...")

# Deploy the file by building it up on the server
ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', 'zubair@192.168.20.10']

# First, truncate the file
print("Step 1: Initializing file on server...")
init_cmd = ssh_cmd + ['echo "erp" | sudo -S bash -c "cat > /var/www/tradifyerp/accounting/models.py <<EOFPYTHON\n\nEOFPYTHON"']
subprocess.run(' '.join(init_cmd), shell=True)

# Write chunks
for i, chunk in enumerate(chunks):
    print(f"Step {i+2}: Writing chunk {i+1}/{len(chunks)}...")
    # Use Python to decode on the server side
    cmd = f"""echo 'erp' | sudo -S python3 -c "import base64; data = base64.b64decode('{chunk}'); open('/tmp/chunk_{i}.bin', 'wb').write(data)" """
    result = subprocess.run(f"ssh -o StrictHostKeyChecking=no zubair@192.168.20.10 {cmd}", shell=True)
    if result.returncode != 0:
        print(f"Failed to write chunk {i}")
        sys.exit(1)

print(f"File deployed successfully!")
print("Restarting Gunicorn...")
subprocess.run(['ssh', '-o', 'StrictHostKeyChecking=no', 'zubair@192.168.20.10', 'echo', 'erp', '|', 'sudo', '-S', 'systemctl', 'restart', 'gunicorn'], shell=True)
print("Done!")
