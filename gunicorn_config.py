from src.core.config import settings

bind = f"{settings.gunicorn.host}:{settings.gunicorn.port}"
workers = settings.gunicorn.workers
worker_class = settings.gunicorn.worker_class
worker_connections = settings.gunicorn.worker_connections
keepalive = settings.gunicorn.keepalive
max_requests = settings.gunicorn.max_requests
max_requests_jitter = settings.gunicorn.max_requests_jitter
timeout = settings.gunicorn.timeout
graceful_timeout = settings.gunicorn.graceful_timeout
reload = settings.gunicorn.reload
preload_app = settings.gunicorn.preload_app
access_log_format = settings.gunicorn.access_log_format
