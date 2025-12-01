"""
Gunicorn configuration file for TradifyERP
Place this file in the project root directory
"""

import multiprocessing
import os

# Server settings
bind = "127.0.0.1:8001"
backlog = 2048
timeout = 30
keepalive = 2

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = os.path.join(os.path.dirname(__file__), "logs", "access.log")
errorlog = os.path.join(os.path.dirname(__file__), "logs", "error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "tradifyerp"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL/TLS (will be handled by Nginx, not Gunicorn)
# But you can enable here if needed
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
# ssl_version = "TLSv1_2"
# cert_reqs = "cert_required"
# ca_certs = "/path/to/ca_certs"

# Application setup
raw_env = [
    "DJANGO_SETTINGS_MODULE=TradifyERP.settings",
]

# Server hooks
def on_starting(server):
    print("[Gunicorn] Starting TradifyERP server...")

def when_ready(server):
    print("[Gunicorn] Gunicorn server is ready. Spawning workers")

def on_exit(server):
    print("[Gunicorn] Gunicorn server shutting down...")
