# Gunicorn Configuration for Concurrent Users
# Use this configuration for production deployment with 7+ concurrent users

import multiprocessing
import os

# Check if running on PythonAnywhere
IS_PYTHONANYWHERE = os.environ.get('PYTHONANYWHERE_DOMAIN') is not None

# Server configuration
bind = "0.0.0.0:8000"
workers = 1 if IS_PYTHONANYWHERE else multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Timeout settings
timeout = 30
keepalive = 2
graceful_timeout = 30

# Memory and process settings
max_requests = 1000
max_requests_jitter = 100
preload_app = True

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
    workers = 1  # Free/Basic tier only allows 1 worker
    worker_connections = 100
    timeout = 600  # Increased to 10 minutes for large label generation (was 300)
    max_requests = 500
    print("🐍 PythonAnywhere Gunicorn configuration applied")
    print("⚠️  WARNING: 1 worker means all requests are queued during label generation")
    print("⚠️  Consider upgrading PythonAnywhere tier for better concurrency")
else:
    print("🖥️  Local/Production Gunicorn configuration applied")

print(f"📊 Gunicorn Configuration:")
print(f"   Workers: {workers}")
print(f"   Worker connections: {worker_connections}")
print(f"   Timeout: {timeout}s")
print(f"   Max requests: {max_requests}")
print(f"   Concurrent users supported: {workers * worker_connections}")
