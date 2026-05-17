"""
eFootball Arena — Tactics URL Configuration

URL Structure:
--------------
GET /api/v1/tactics/formations/          → Formation list (filtered, paginated)
GET /api/v1/tactics/formations/<id>/     → Formation detail (full nested)
GET /api/v1/tactics/counter/<id>/        → Counter finder for formation
GET /api/v1/tactics/meta/                → Meta analytics leaderboard

How to add a new endpoint:
---------------------------
1. Create view in views.py
2. Add path() here
3. Write tests in tests/test_urls.py
"""

from django.urls import path

from .views import (
    CounterFinderView,
    FormationDetailView,
    FormationListView,
    MetaTrackerView,
)

app_name = "tactics"

urlpatterns = [
    path("formations/", FormationListView.as_view(), name="formation-list"),
    path("formations/<int:pk>/", FormationDetailView.as_view(), name="formation-detail"),
    path("counter/<int:pk>/", CounterFinderView.as_view(), name="counter-finder"),
    path("meta/", MetaTrackerView.as_view(), name="meta-tracker"),
]