# Gunicorn Configuration for Concurrent Users
# Use this configuration for production deployment with 7+ concurrent users

import multiprocessing
import os

# Check if running on PythonAnywhere
IS_PYTHONANYWHERE = os.environ.get('PYTHONANYWHERE_DOMAIN') is not None

# Server configuration
bind = "0.0.0.0:8000"
# Single worker with threads: this app uses global singletons, file-based sessions,
# and SQLite — multiple worker processes cause file corruption and lock contention.
workers = 1
worker_class = "gthread"
threads = 4
worker_connections = 1000

# Timeout settings — label generation can take >30s
timeout = 120
keepalive = 2
graceful_timeout = 30

# Memory and process settings
max_requests = 1000
max_requests_jitter = 100
preload_app = False  # Don't preload — avoids background threads forking into workers

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# PythonAnywhere specific settings
if IS_PYTHONANYWHERE:
    # PythonAnywhere limitations
    threads = 2
    worker_connections = 100
    timeout = 120
    max_requests = 500
    print("🐍 PythonAnywhere Gunicorn configuration applied")
else:
    print("🖥️  Local/Production Gunicorn configuration applied")

print(f"📊 Gunicorn Configuration:")
print(f"   Workers: {workers}")
print(f"   Worker connections: {worker_connections}")
print(f"   Timeout: {timeout}s")
print(f"   Max requests: {max_requests}")
print(f"   Concurrent users supported: {workers * worker_connections}")
