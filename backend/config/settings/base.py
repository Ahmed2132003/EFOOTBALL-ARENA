from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="localhost,127.0.0.1")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    # ─── Celery Beat — Periodic Tasks ───────────
    # يتيح إنشاء المهام المجدولة من Django Admin
    "django_celery_beat",
]

LOCAL_APPS = [
    "users",
    "tactics",
    "tournaments",
    "marketplace",
    "notifications",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "users.CustomUser"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {"connect_timeout": 10},
        "CONN_MAX_AGE": 60,
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "login": "5/minute",
        "register": "10/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.CustomTokenObtainPairSerializer",
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Cairo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================
# ⚡ CELERY CONFIGURATION — Async Task Queue
# ============================================

# ─── Broker (Redis) ───────────────────────────────────────────────────────────
# Redis يستقبل المهام من Django ويوزعها على Workers
# داخل Docker: redis هو اسم الـ service
CELERY_BROKER_URL = config(
    "CELERY_BROKER_URL",
    default="redis://redis:6379/0"
)

# ─── Result Backend (Redis) ───────────────────────────────────────────────────
# تخزين نتائج المهام في Redis (مفيد للـ monitoring)
CELERY_RESULT_BACKEND = config(
    "CELERY_RESULT_BACKEND",
    default="redis://redis:6379/0"
)

# ─── Serialization — Security ─────────────────────────────────────────────────
# JSON فقط — منع pickle لأنه غير آمن في Production
CELERY_TASK_SERIALIZER          = "json"
CELERY_RESULT_SERIALIZER        = "json"
CELERY_ACCEPT_CONTENT           = ["json"]
CELERY_EVENT_SERIALIZER         = "json"

# ─── Timezone ─────────────────────────────────────────────────────────────────
CELERY_TIMEZONE                 = "Africa/Cairo"
CELERY_ENABLE_UTC               = True

# ─── Beat Scheduler ───────────────────────────────────────────────────────────
# DatabaseScheduler يخزن الجداول في PostgreSQL
# يتيح إنشاء وتعديل المهام المجدولة من Django Admin
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ─── Task Tracking ────────────────────────────────────────────────────────────
# تتبع حالة المهام (PENDING → STARTED → SUCCESS/FAILURE)
CELERY_TASK_TRACK_STARTED       = True

# ─── Time Limits ──────────────────────────────────────────────────────────────
# منع المهام من الاستمرار إلى الأبد
# soft limit: يرسل SoftTimeLimitExceeded exception
# hard limit: يقتل الـ task بالقوة
CELERY_TASK_SOFT_TIME_LIMIT     = 300   # 5 دقائق
CELERY_TASK_TIME_LIMIT          = 600   # 10 دقائق

# ─── Worker Settings ──────────────────────────────────────────────────────────
# عدد العمليات المتزامنة في كل Worker
CELERY_WORKER_CONCURRENCY       = 4

# ─── Result Expiry ────────────────────────────────────────────────────────────
# حذف نتائج المهام من Redis بعد يوم واحد
CELERY_RESULT_EXPIRES           = 86400  # 24 ساعة

# ─── Retry on Startup ─────────────────────────────────────────────────────────
# إعادة محاولة الاتصال بـ Redis عند البدء إذا لم يكن متاحاً
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ─── Prefetch Multiplier ──────────────────────────────────────────────────────
# عدد المهام التي يجلبها Worker مسبقاً
# القيمة 1 تضمن توزيع عادل للمهام
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# ─── Acks Late ────────────────────────────────────────────────────────────────
# تأكيد المهمة بعد إتمامها وليس قبل
# يحمي من فقدان المهام عند crash الـ Worker
CELERY_TASK_ACKS_LATE           = True

# ─── Periodic Tasks (Beat Schedule) ──────────────────────────────────────────
# مثال على جدولة مهام دورية بدون Django Admin
# يمكن أيضاً إضافتها من Django Admin عبر django-celery-beat
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # تحديث الرانك اليومي — كل يوم الساعة 2 صباحاً
    "daily-rank-update": {
        "task": "users.tasks.daily_rank_update",
        "schedule": crontab(hour=2, minute=0),
        "options": {"expires": 3600},  # تنتهي صلاحيتها بعد ساعة
    },
}