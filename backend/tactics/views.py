"""
eFootball Arena — Tactics API Views
Production-Grade REST API Views

View Architecture:
-------------------
1. FormationListView  → GET /api/v1/tactics/formations/
2. FormationDetailView → GET /api/v1/tactics/formations/<id>/
3. CounterFinderView  → GET /api/v1/tactics/counter/<id>/
4. MetaTrackerView    → GET /api/v1/tactics/meta/

Caching Strategy:
------------------
- Formation list: cached 1 hour, key includes query params
- Formation detail: cached 1 hour per formation ID
- Meta: cached 30 minutes (changes more frequently)
- Cache invalidation: done via Django cache.delete() when data changes

Query Optimization:
--------------------
- FormationListView: only() to fetch minimal fields
- FormationDetailView: select_related + prefetch_related for all nested data
- CounterFinderView: prefetch countered_by formation
- MetaTrackerView: select_related('formation')

How to add a new endpoint:
---------------------------
1. Create a new View class inheriting from generics.* or APIView
2. Add URL pattern in urls.py
3. Add serializer in serializers.py if needed
4. Add caching if endpoint is read-heavy
5. Write tests in tests/test_views.py
"""

import hashlib
import logging

from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CounterTactic, Formation, MetaTracker
from .pagination import TacticsPagination
from .serializers import (
    CounterTacticSerializer,
    FormationDetailSerializer,
    FormationListSerializer,
    MetaTrackerSerializer,
)

logger = logging.getLogger(__name__)

# ── Cache Timeouts ─────────────────────────────────────────────────────────────
FORMATION_LIST_CACHE_TTL = 60 * 60      # 1 hour
FORMATION_DETAIL_CACHE_TTL = 60 * 60   # 1 hour
META_CACHE_TTL = 60 * 30               # 30 minutes


def make_cache_key(prefix, request):
    """
    Generate a unique cache key based on query parameters.
    Ensures different filters get different cache entries.
    """
    params = dict(sorted(request.query_params.items()))
    params_str = str(params)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
    return f"tactics:{prefix}:{params_hash}"


# ============================================================
# 1️⃣  FORMATION LIST VIEW
# ============================================================


class FormationListView(generics.ListAPIView):
    """
    GET /api/v1/tactics/formations/

    Returns paginated list of formations with filtering, search, and ordering.

    Filtering:
        ?difficulty_level=advanced
        ?play_style=possession
        ?is_meta=true

    Search:
        ?search=4-3-3

    Ordering:
        ?ordering=name
        ?ordering=-attacking_rating
        ?ordering=difficulty_level

    Pagination:
        ?page=1&page_size=10  (max 50)

    Caching:
        Cached for 1 hour per unique query parameter combination.
        Cache key includes all query params to prevent stale data.
    """

    serializer_class = FormationListSerializer
    pagination_class = TacticsPagination
    permission_classes = [AllowAny]

    # Filtering backends
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # django-filter fields
    filterset_fields = {
        "difficulty_level": ["exact"],
        "play_style": ["exact"],
        "is_meta": ["exact"],
        "attacking_rating": ["gte", "lte"],
        "defensive_rating": ["gte", "lte"],
    }

    # SearchFilter fields
    search_fields = ["name", "code", "description"]

    # OrderingFilter fields
    ordering_fields = [
        "name",
        "attacking_rating",
        "defensive_rating",
        "possession_rating",
        "pressing_rating",
        "difficulty_level",
        "updated_at",
    ]
    ordering = ["name"]

    def get_queryset(self):
        """
        Optimized queryset for list view.

        Why only()? → We only need list serializer fields.
        No prefetch needed since FormationListSerializer has no nested relations.
        """
        return Formation.objects.only(
            "id",
            "name",
            "code",
            "slug",
            "play_style",
            "difficulty_level",
            "attacking_rating",
            "defensive_rating",
            "possession_rating",
            "pressing_rating",
            "width_rating",
            "tempo_rating",
            "is_meta",
            "updated_at",
        )

    def list(self, request, *args, **kwargs):
        """
        Override list to add Redis caching.

        Cache key is unique per query param combination.
        This ensures filters/search/ordering all get separate cache entries.
        """
        cache_key = make_cache_key("formations_list", request)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.debug(f"[CACHE HIT] {cache_key}")
            return Response(cached_data)

        logger.debug(f"[CACHE MISS] {cache_key}")
        response = super().list(request, *args, **kwargs)

        # Cache the response data
        cache.set(cache_key, response.data, FORMATION_LIST_CACHE_TTL)

        return response


# ============================================================
# 2️⃣  FORMATION DETAIL VIEW
# ============================================================


class FormationDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/tactics/formations/<id>/

    Returns full formation detail including:
    - All formation fields
    - 11 player positions (SVG-ready coordinates)
    - Tactic cards (tactical guides)
    - Counter tactics (what counters this formation)
    - Meta tracker (usage stats and win rate)

    Performance:
    → select_related('meta_tracker') — OneToOne, single JOIN
    → prefetch_related('positions') — 1 extra query for all positions
    → prefetch_related('tactic_cards') — 1 extra query
    → prefetch_related('is_countered_by__countered_by') — 2 extra queries
    Total: 5 queries for complete nested data (no N+1)

    Caching: 1 hour per formation ID.
    """

    serializer_class = FormationDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Formation.objects.select_related("meta_tracker")
            .prefetch_related(
                "positions",
                "tactic_cards",
                "is_countered_by__countered_by",
            )
        )

    def retrieve(self, request, *args, **kwargs):
        formation_id = kwargs.get("pk")
        cache_key = f"tactics:formation_detail:{formation_id}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"[CACHE HIT] {cache_key}")
            return Response(cached_data)

        logger.debug(f"[CACHE MISS] {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, FORMATION_DETAIL_CACHE_TTL)

        return response


# ============================================================
# 3️⃣  COUNTER FINDER VIEW
# ============================================================


class CounterFinderView(APIView):
    """
    GET /api/v1/tactics/counter/<id>/

    Returns tactical counter analysis for a given formation.

    Response structure:
    {
        "formation": { id, name, code, slug },
        "counters_found": 3,
        "best_counters": [
            {
                "countered_by": { formation info },
                "effectiveness_rating": 8,
                "explanation": "..."
            },
            ...
        ]
    }

    Ordered by effectiveness_rating descending.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk):
        cache_key = f"tactics:counter_finder:{pk}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.debug(f"[CACHE HIT] {cache_key}")
            return Response(cached_data)

        # Validate formation exists
        try:
            formation = Formation.objects.only(
                "id", "name", "code", "slug", "play_style", "is_meta"
            ).get(pk=pk)
        except Formation.DoesNotExist:
            return Response(
                {"error": f"Formation with id={pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch counters with prefetch to avoid N+1
        counters = (
            CounterTactic.objects.filter(formation=formation)
            .select_related("countered_by")
            .order_by("-effectiveness_rating")
        )

        serialized_counters = CounterTacticSerializer(counters, many=True).data

        response_data = {
            "formation": {
                "id": formation.id,
                "name": formation.name,
                "code": formation.code,
                "slug": formation.slug,
                "play_style": formation.play_style,
                "is_meta": formation.is_meta,
            },
            "counters_found": counters.count(),
            "best_counters": serialized_counters,
        }

        cache.set(cache_key, response_data, FORMATION_DETAIL_CACHE_TTL)
        logger.debug(f"[CACHE SET] {cache_key}")

        return Response(response_data, status=status.HTTP_200_OK)


# ============================================================
# 4️⃣  META TRACKER VIEW
# ============================================================


class MetaTrackerView(generics.ListAPIView):
    """
    GET /api/v1/tactics/meta/

    Returns meta analytics for all formations, ordered by popularity.

    Ordering options:
        ?ordering=popularity_rank      (default)
        ?ordering=-win_rate
        ?ordering=-usage_count

    Response includes formation info + meta analytics.

    Caching: 30 minutes (meta updates less frequently than formation data).
    """

    permission_classes = [AllowAny]
    pagination_class = TacticsPagination

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["popularity_rank", "win_rate", "usage_count"]
    ordering = ["popularity_rank"]

    def get_queryset(self):
        return MetaTracker.objects.select_related("formation").order_by(
            "popularity_rank"
        )

    def list(self, request, *args, **kwargs):
        cache_key = make_cache_key("meta_tracker", request)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.debug(f"[CACHE HIT] {cache_key}")
            return Response(cached_data)

        # Build custom response with formation info + meta data
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        data = []
        items = page if page is not None else queryset

        for tracker in items:
            data.append(
                {
                    "rank": tracker.popularity_rank,
                    "formation": {
                        "id": tracker.formation.id,
                        "name": tracker.formation.name,
                        "code": tracker.formation.code,
                        "slug": tracker.formation.slug,
                        "play_style": tracker.formation.play_style,
                        "is_meta": tracker.formation.is_meta,
                    },
                    "analytics": MetaTrackerSerializer(tracker).data,
                }
            )

        if page is not None:
            response = self.get_paginated_response(data)
        else:
            response = Response(data)

        cache.set(cache_key, response.data, META_CACHE_TTL)
        return response