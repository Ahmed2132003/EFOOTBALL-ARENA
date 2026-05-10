from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    return JsonResponse({"status": "ok", "version": "1.0.0"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    # Auth endpoints — الـ prefix اتغير من api/v1/users/ لـ api/v1/auth/
    path("api/v1/auth/",          include("users.urls",         namespace="users")),
    path("api/v1/tactics/",       include("tactics.urls",       namespace="tactics")),
    path("api/v1/tournaments/",   include("tournaments.urls",   namespace="tournaments")),
    path("api/v1/marketplace/",   include("marketplace.urls",   namespace="marketplace")),
    path("api/v1/notifications/", include("notifications.urls", namespace="notifications")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)