# ============================================
# eFootball Arena — Development Settings
# ============================================

from .base import *  # noqa
from decouple import config, Csv

# ── Debug Mode ─────────────────────────────────
DEBUG = config("DEBUG", default=True, cast=bool)

# ── Allowed Hosts ──────────────────────────────
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,0.0.0.0,backend",
    cast=Csv()
)

# ── CORS — بورتات React/Vite المحلية ───────────────
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default=(
        "http://localhost:5500,http://127.0.0.1:5500,"
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173"
    ),
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True

# ── Email Backend ──────────────────────────────
# في Development: البريد يظهر في Terminal logs فقط
# في Production: يُستبدل بـ SMTP (SendGrid / SES / Mailgun)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@efootballarena.com"
EMAIL_SUBJECT_PREFIX = "[eFootball Arena] "

# ── Celery — Development Overrides ────────────
# في Development: Redis داخل Docker
CELERY_BROKER_URL    = config("CELERY_BROKER_URL",    default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")

# ── Logging ────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "celery_format": {
            "format": "🔄 CELERY | {levelname} {asctime} {module} | {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "celery_console": {
            "class": "logging.StreamHandler",
            "formatter": "celery_format",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",  # تقليل SQL logs في Dev
            "propagate": False,
        },
        # ─── Celery Loggers ──────────────────────────
        "celery": {
            "handlers": ["celery_console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["celery_console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.worker": {
            "handlers": ["celery_console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.beat": {
            "handlers": ["celery_console"],
            "level": "INFO",
            "propagate": False,
        },
        # ─── App Loggers ─────────────────────────────
        "users.tasks": {
            "handlers": ["celery_console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}