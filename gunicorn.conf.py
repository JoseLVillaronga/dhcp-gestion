# Configuración de Gunicorn para Dashboard DHCP
import multiprocessing

# Servidor
bind = "0.0.0.0:5010"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Procesamiento
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
sendfile = True
reuse_port = True
chdir = "/home/jose/dhcp-gestion"

# Nombres
proc_name = "dhcp-dashboard"
default_proc_name = "dhcp-dashboard"

# RAW
raw_env = [
    'DJANGO_SETTINGS_MODULE=dashboard.settings',
]
