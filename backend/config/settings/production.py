# ============================================
# eFootball Arena — Production Settings
# ============================================

from .base import *  # noqa
from decouple import config, Csv

# ── Security ───────────────────────────────────
DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# ── HTTPS Security Headers ─────────────────────
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# ── Cookies ────────────────────────────────────
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# ── CORS ───────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# ── Email (Production) ─────────────────────────
# استخدام SMTP provider حقيقي (SES / SendGrid / Mailgun)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST          = config("EMAIL_HOST",          default="")
EMAIL_PORT          = config("EMAIL_PORT",          default=587, cast=int)
EMAIL_HOST_USER     = config("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS       = True
DEFAULT_FROM_EMAIL  = config("DEFAULT_FROM_EMAIL",  default="noreply@efootball-arena.com")

# ── Celery Production Settings ─────────────────
# Redis Managed Service (AWS ElastiCache / Redis Cloud)
CELERY_BROKER_URL     = config("CELERY_BROKER_URL",     default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")

# Production: تشغيل Worker بعدد CPU محدد
CELERY_WORKER_CONCURRENCY = config("CELERY_WORKER_CONCURRENCY", default=4, cast=int)

# ── Logging في Production ───────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "/app/logs/django.log",
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    },
    "loggers": {
        "celery": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "users.tasks": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ── Media Storage (AWS S3 / MinIO) ─────────────────────
USE_S3 = config("USE_S3", default=False, cast=bool)

if USE_S3:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_ACCESS_KEY_ID       = config("AWS_ACCESS_KEY_ID",       default="")
    AWS_SECRET_ACCESS_KEY   = config("AWS_SECRET_ACCESS_KEY",   default="")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
    AWS_S3_REGION_NAME      = config("AWS_S3_REGION_NAME",      default="us-east-1")
    AWS_S3_FILE_OVERWRITE   = False
    AWS_DEFAULT_ACL         = "public-read"
    AWS_S3_CUSTOM_DOMAIN    = config("AWS_S3_CUSTOM_DOMAIN",    default="")
    AWS_S3_ENDPOINT_URL     = config("AWS_S3_ENDPOINT_URL",     default="")

    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    else:
        MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"