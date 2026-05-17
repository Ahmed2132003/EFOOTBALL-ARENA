"""
eFootball Arena — Tactics Serializers
Production-Grade DRF Serializer Architecture

Architecture Decisions:
------------------------
1. FormationListSerializer  → lightweight for list endpoints (mobile-friendly)
2. FormationDetailSerializer → full nested data for detail endpoint
3. Separate serializers eliminate N+1 by controlling what gets serialized
4. Read-only nested serializers prevent accidental writes through nested routes

Why separate List/Detail serializers?
→ List endpoint returns 10-50 formations: needs minimal payload
→ Detail endpoint returns 1 formation: can afford nested relations
→ Frontend list view needs: name, ratings, is_meta, play_style
→ Frontend detail view needs: positions (SVG), tactic cards, counters, meta
"""

from rest_framework import serializers

from .models import CounterTactic, Formation, MetaTracker, PlayerPosition, TacticCard


# ============================================================
# 1️⃣  PLAYER POSITION SERIALIZER
# ============================================================


class PlayerPositionSerializer(serializers.ModelSerializer):
    """
    Serializes player positions with SVG-ready coordinates.

    Frontend usage:
```jsx
    const x = (position.x_coordinate / 100) * svgWidth;
    const y = (position.y_coordinate / 100) * svgHeight;
```

    sorted_by: display_order (enforced in queryset)
    """

    class Meta:
        model = PlayerPosition
        fields = [
            "id",
            "position_name",
            "short_name",
            "x_coordinate",
            "y_coordinate",
            "tactical_role",
            "display_order",
        ]
        read_only_fields = fields


# ============================================================
# 2️⃣  TACTIC CARD SERIALIZER
# ============================================================


class TacticCardSerializer(serializers.ModelSerializer):
    """
    Full tactic card content serializer.
    All fields are read-only — content managed via Admin.
    """

    class Meta:
        model = TacticCard
        fields = [
            "id",
            "title",
            "content",
            "strengths",
            "weaknesses",
            "use_when",
            "avoid_when",
            "recommended_manager",
            "offensive_tips",
            "defensive_tips",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ============================================================
# 3️⃣  META TRACKER SERIALIZER
# ============================================================


class MetaTrackerSerializer(serializers.ModelSerializer):
    """
    Analytics serializer for formation meta data.
    Includes computed properties as extra fields.
    """

    goal_difference = serializers.SerializerMethodField()
    is_top_meta = serializers.SerializerMethodField()

    class Meta:
        model = MetaTracker
        fields = [
            "usage_count",
            "win_rate",
            "average_goals_scored",
            "average_goals_conceded",
            "goal_difference",
            "popularity_rank",
            "is_top_meta",
            "last_meta_update",
            "updated_at",
        ]
        read_only_fields = fields

    def get_goal_difference(self, obj):
        return obj.goal_difference

    def get_is_top_meta(self, obj):
        return obj.is_top_meta


# ============================================================
# 4️⃣  COUNTER FORMATION SERIALIZER (minimal)
# ============================================================


class CounterFormationMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal formation info used inside CounterTacticSerializer.
    Avoids deep nesting while giving frontend enough context.
    """

    class Meta:
        model = Formation
        fields = [
            "id",
            "name",
            "code",
            "slug",
            "play_style",
            "difficulty_level",
            "is_meta",
        ]
        read_only_fields = fields


class CounterTacticSerializer(serializers.ModelSerializer):
    """
    Counter tactic serializer.
    Includes minimal formation info for the counter formation.

    Why not full FormationDetailSerializer?
    → Prevents circular nesting (Formation → Counter → Formation → ...)
    → Frontend only needs: which formation counters, why, how effective
    """

    countered_by = CounterFormationMinimalSerializer(read_only=True)

    class Meta:
        model = CounterTactic
        fields = [
            "id",
            "countered_by",
            "explanation",
            "effectiveness_rating",
            "created_at",
        ]
        read_only_fields = fields


# ============================================================
# 5️⃣  FORMATION LIST SERIALIZER (lightweight)
# ============================================================


class FormationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list endpoints.

    Design principle:
    → Include only what the list view needs
    → No nested relations (avoids N+1 even without prefetch)
    → Mobile-friendly small payload
    → average_rating computed on the fly (no DB hit)

    Payload size: ~200-300 bytes per formation
    """

    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Formation
        fields = [
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
            "average_rating",
            "is_meta",
            "updated_at",
        ]
        read_only_fields = fields

    def get_average_rating(self, obj):
        """Computed average — no DB query."""
        return obj.average_rating


# ============================================================
# 6️⃣  FORMATION DETAIL SERIALIZER (full nested)
# ============================================================


class FormationDetailSerializer(serializers.ModelSerializer):
    """
    Full detailed serializer for single formation endpoint.

    Includes:
    - All Formation fields
    - positions (PlayerPosition list, sorted by display_order)
    - tactic_cards (TacticCard list)
    - counter_tactics (CounterTactic list with counter formation info)
    - meta_tracker (OneToOne MetaTracker)

    Performance:
    → Requires prefetch_related('positions', 'tactic_cards', 'is_countered_by__countered_by')
    → select_related('meta_tracker') for OneToOne
    → Views must handle this — see views.py
    """

    positions = PlayerPositionSerializer(many=True, read_only=True)
    tactic_cards = TacticCardSerializer(many=True, read_only=True)
    counter_tactics = CounterTacticSerializer(
        source="is_countered_by", many=True, read_only=True
    )
    meta_tracker = MetaTrackerSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_positions = serializers.SerializerMethodField()

    class Meta:
        model = Formation
        fields = [
            "id",
            "name",
            "code",
            "slug",
            "description",
            "play_style",
            "difficulty_level",
            "attacking_rating",
            "defensive_rating",
            "possession_rating",
            "pressing_rating",
            "width_rating",
            "tempo_rating",
            "average_rating",
            "total_positions",
            "is_meta",
            "created_at",
            "updated_at",
            # Nested
            "positions",
            "tactic_cards",
            "counter_tactics",
            "meta_tracker",
        ]
        read_only_fields = fields

    def get_average_rating(self, obj):
        return obj.average_rating

    def get_total_positions(self, obj):
        # positions already prefetched → no extra query
        return len(obj.positions.all())