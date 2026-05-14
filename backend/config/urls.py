# ============================================
# eFootball Arena — URL Configuration
# ============================================

import redis
from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    """
    /health/ — Basic health check.
    يُستخدم في Load Balancers و CI/CD للتحقق أن التطبيق يعمل.
    """
    return JsonResponse(
        {"status": "ok", "version": "1.0.0", "service": "efootball-arena-backend"}
    )


def readiness_check(request):
    """
    /api/ready/ — Deep readiness check.
    يتحقق من:
    - اتصال قاعدة البيانات
    - اتصال Redis

    يُستخدم في Kubernetes readiness probes و CI/CD.
    """
    checks = {}
    overall_status = "ok"

    # ── Database Check ────────────────────────────────────────────────────
    try:
        connection.ensure_connection()
        checks["database"] = {"status": "ok", "message": "PostgreSQL connected"}
    except Exception as e:
        checks["database"] = {"status": "error", "message": str(e)}
        overall_status = "degraded"

    # ── Redis Check ───────────────────────────────────────────────────────
    try:
        redis_url = getattr(settings, "CELERY_BROKER_URL", "redis://redis:6379/0")
        r = redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        checks["redis"] = {"status": "ok", "message": "Redis connected"}
    except Exception as e:
        checks["redis"] = {"status": "error", "message": str(e)}
        overall_status = "degraded"

    http_status = 200 if overall_status == "ok" else 503

    return JsonResponse(
        {
            "status": overall_status,
            "version": "1.0.0",
            "service": "efootball-arena-backend",
            "checks": checks,
        },
        status=http_status,
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("api/ready/", readiness_check, name="readiness-check"),
    path("api/v1/auth/", include("users.urls", namespace="users")),
    path("api/v1/users/", include("users.profile_urls", namespace="users_profile")),
    path("api/v1/tactics/", include("tactics.urls", namespace="tactics")),
    path("api/v1/tournaments/", include("tournaments.urls", namespace="tournaments")),
    path("api/v1/marketplace/", include("marketplace.urls", namespace="marketplace")),
    path(
        "api/v1/notifications/",
        include("notifications.urls", namespace="notifications"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)