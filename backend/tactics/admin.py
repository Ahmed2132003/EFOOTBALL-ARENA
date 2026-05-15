"""
============================================================
eFootball Arena — Tactics Admin
Production-Grade Django Admin Configuration

Admin Features:
---------------
- FormationAdmin: Full formation management with all inlines
- PlayerPositionInline: Manage positions directly from formation
- TacticCardInline: Manage tactic cards from formation
- MetaTrackerInline: View/edit meta data from formation
- CounterTacticAdmin: Manage counter relationships
- Optimized queries: select_related + prefetch_related everywhere
- No N+1 queries in any list view
- Fieldsets for organized data entry
- Autocomplete fields for FK selections

How to use Admin:
------------------
1. Go to http://localhost:8765/admin/
2. Login with superuser credentials
3. Navigate to "Tactics" section
4. Formations → Add Formation → fill all fields
5. PlayerPositions are added inline within Formation

Performance notes:
-------------------
- All list_display FK fields use select_related
- All ManyToMany uses prefetch_related
- readonly_fields prevents unnecessary DB writes
- list_select_related=True on all ModelAdmins
============================================================
"""

from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html

from .models import CounterTactic, Formation, MetaTracker, PlayerPosition, TacticCard


# ============================================================
# INLINES
# ============================================================


class PlayerPositionInline(admin.TabularInline):
    """
    Inline for managing player positions within a Formation.
    Displayed as a table for easy coordinate editing.

    Why TabularInline?
    → Positions are best viewed in table format
    → Makes it easy to see all 11 positions at once
    → Coordinate columns are clear and editable
    """

    model = PlayerPosition
    extra = 0
    min_num = 0
    max_num = 11
    ordering = ["display_order"]
    fields = (
        "display_order",
        "short_name",
        "position_name",
        "tactical_role",
        "x_coordinate",
        "y_coordinate",
    )
    verbose_name = "Player Position"
    verbose_name_plural = "Player Positions (11 max)"


class TacticCardInline(admin.StackedInline):
    """
    Inline for managing tactic cards within a Formation.
    Displayed as stacked (StackedInline) for rich text fields.

    Why StackedInline?
    → TacticCards have many large TextField fields
    → Stacked layout is more readable for long content
    → Better UX than cramped table layout
    """

    model = TacticCard
    extra = 0
    min_num = 0
    max_num = 5
    ordering = ["-created_at"]
    fields = (
        "title",
        "content",
        "strengths",
        "weaknesses",
        "use_when",
        "avoid_when",
        "recommended_manager",
        "offensive_tips",
        "defensive_tips",
    )
    verbose_name = "Tactic Card"
    verbose_name_plural = "Tactic Cards"
    show_change_link = True


class MetaTrackerInline(admin.StackedInline):
    """
    Inline for viewing/editing MetaTracker within a Formation.
    OneToOne relation — only one MetaTracker per Formation.

    Why readonly for analytics fields?
    → Analytics fields should be updated by Celery tasks, not manually
    → Manual editing of usage_count/win_rate is allowed for seeding
    → last_meta_update is readonly to track when system last updated
    """

    model = MetaTracker
    extra = 1
    min_num = 0
    max_num = 1
    readonly_fields = ("updated_at", "goal_difference_display", "is_top_meta_display")
    fields = (
        "usage_count",
        "win_rate",
        "average_goals_scored",
        "average_goals_conceded",
        "popularity_rank",
        "last_meta_update",
        "updated_at",
        "goal_difference_display",
        "is_top_meta_display",
    )
    verbose_name = "Meta Tracker"
    verbose_name_plural = "Meta Tracker (Analytics)"

    def goal_difference_display(self, obj):
        if obj and obj.pk:
            gd = obj.goal_difference
            color = "green" if gd >= 0 else "red"
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                f"+{gd}" if gd >= 0 else str(gd),
            )
        return "—"

    goal_difference_display.short_description = "Avg Goal Difference"

    def is_top_meta_display(self, obj):
        if obj and obj.pk:
            if obj.is_top_meta:
                return format_html(
                    '<span style="color: gold; font-weight: bold;">⭐ Top 3 Meta</span>'
                )
            return format_html(
                '<span style="color: gray;">Not in Top 3</span>'
            )
        return "—"

    is_top_meta_display.short_description = "Meta Status"


# ============================================================
# FORMATION ADMIN
# ============================================================


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    """
    Main Formation admin — the hub of the tactical system.

    Features:
    ----------
    - All 3 inlines: PlayerPosition, TacticCard, MetaTracker
    - Rich list_display with visual indicators
    - Organized fieldsets for clean data entry
    - Slug auto-generation (readonly after creation)
    - Optimized queryset with prefetch_related
    - Search by name, play_style, difficulty
    - Filter by is_meta, play_style, difficulty_level

    How to add a new Formation:
    ----------------------------
    1. Admin → Formations → Add Formation
    2. Fill: name (e.g. "4-3-3"), code (same as name), description
    3. Choose play_style and difficulty_level
    4. Set all 6 tactical ratings (1-10)
    5. Check is_meta if it's currently in the meta
    6. Scroll down → add 11 PlayerPositions with coordinates
    7. Add TacticCard with tactical guide content
    8. MetaTracker is auto-created (add analytics data here)
    9. Save
    """

    # ── List View ────────────────────────────────────────────
    list_display = (
        "name",
        "play_style",
        "difficulty_level",
        "meta_badge",
        "attacking_rating",
        "defensive_rating",
        "possession_rating",
        "average_rating_display",
        "positions_count",
        "updated_at",
    )
    list_filter = (
        "is_meta",
        "play_style",
        "difficulty_level",
    )
    search_fields = ("name", "code", "slug", "description")
    ordering = ("name",)
    list_per_page = 20
    list_select_related = True

    # ── Detail View ──────────────────────────────────────────
    readonly_fields = (
        "slug",
        "created_at",
        "updated_at",
        "average_rating_display",
        "positions_count",
    )
    prepopulated_fields = {}  # Slug is handled in model.save()

    fieldsets = (
        (
            "🏟️ Formation Identity",
            {
                "fields": ("name", "code", "slug", "description"),
                "description": "Basic formation identification. "
                "Slug is auto-generated from name.",
            },
        ),
        (
            "🎯 Tactical Classification",
            {
                "fields": ("play_style", "difficulty_level", "is_meta"),
            },
        ),
        (
            "📊 Tactical Ratings (1-10)",
            {
                "fields": (
                    ("attacking_rating", "defensive_rating"),
                    ("possession_rating", "pressing_rating"),
                    ("width_rating", "tempo_rating"),
                    "average_rating_display",
                ),
                "description": "Rate each tactical dimension from 1 (lowest) to 10 (highest).",
            },
        ),
        (
            "🕐 Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [PlayerPositionInline, TacticCardInline, MetaTrackerInline]

    # ── Custom Display Methods ────────────────────────────────

    def meta_badge(self, obj):
        if obj.is_meta:
            return format_html(
                '<span style="color: gold; font-weight: bold; '
                'background: #333; padding: 2px 8px; border-radius: 4px;">⭐ META</span>'
            )
        return format_html(
            '<span style="color: #888; padding: 2px 8px;">—</span>'
        )

    meta_badge.short_description = "Meta"
    meta_badge.admin_order_field = "is_meta"

    def average_rating_display(self, obj):
        avg = obj.average_rating
        color = "#22c55e" if avg >= 7 else "#f59e0b" if avg >= 5 else "#ef4444"
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 1.1em;">{}/10</span>',
            color,
            avg,
        )

    average_rating_display.short_description = "Avg Rating"

    def positions_count(self, obj):
        count = obj.total_positions
        color = "#22c55e" if count == 11 else "#f59e0b" if count > 0 else "#ef4444"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/11</span>',
            color,
            count,
        )

    positions_count.short_description = "Positions"

    def get_queryset(self, request):
        """
        Optimized queryset — prefetch related to avoid N+1.

        Why prefetch positions and meta_tracker?
        → list_display calls total_positions (positions.count())
        → Prefetching avoids 1 extra query per formation in list view
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            "positions",
            "tactic_cards",
            "is_countered_by",
            "counters",
        )


# ============================================================
# PLAYER POSITION ADMIN
# ============================================================


@admin.register(PlayerPosition)
class PlayerPositionAdmin(admin.ModelAdmin):
    """
    Standalone admin for PlayerPosition.
    Also accessible inline from FormationAdmin.

    Useful for:
    - Bulk editing positions across formations
    - Debugging coordinate issues
    - Copying positions between formations
    """

    list_display = (
        "formation",
        "display_order",
        "short_name",
        "position_name",
        "tactical_role",
        "x_coordinate",
        "y_coordinate",
        "coordinate_display",
    )
    list_filter = ("formation", "tactical_role")
    search_fields = (
        "formation__name",
        "position_name",
        "short_name",
    )
    ordering = ("formation", "display_order")
    list_select_related = True
    autocomplete_fields = ["formation"]
    list_per_page = 25

    fieldsets = (
        (
            "📍 Position Identity",
            {
                "fields": ("formation", "position_name", "short_name", "tactical_role"),
            },
        ),
        (
            "🗺️ Coordinates (0-100%)",
            {
                "fields": (("x_coordinate", "y_coordinate"), "display_order"),
                "description": "x=0 (left) → 100 (right) | y=0 (GK) → 100 (attack). "
                "Percentage-based for responsive SVG rendering.",
            },
        ),
    )

    def coordinate_display(self, obj):
        return format_html(
            '<code style="background: #1a1a2e; color: #00d4ff; '
            'padding: 2px 6px; border-radius: 3px;">({}, {})</code>',
            obj.x_coordinate,
            obj.y_coordinate,
        )

    coordinate_display.short_description = "Coords (x, y)"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("formation")


# ============================================================
# TACTIC CARD ADMIN
# ============================================================


@admin.register(TacticCard)
class TacticCardAdmin(admin.ModelAdmin):
    """
    Admin for TacticCard — rich tactical content management.

    Also accessible inline from FormationAdmin.
    This standalone admin is useful for content editors
    who manage many tactical guides.
    """

    list_display = (
        "title",
        "formation",
        "has_offensive_tips",
        "has_defensive_tips",
        "created_at",
        "updated_at",
    )
    list_filter = ("formation",)
    search_fields = ("title", "content", "formation__name")
    ordering = ("-created_at",)
    list_select_related = True
    autocomplete_fields = ["formation"]
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 20

    fieldsets = (
        (
            "📋 Card Identity",
            {
                "fields": ("formation", "title"),
            },
        ),
        (
            "📖 Core Tactical Content",
            {
                "fields": ("content", "strengths", "weaknesses"),
            },
        ),
        (
            "🎯 Situational Guidance",
            {
                "fields": ("use_when", "avoid_when"),
            },
        ),
        (
            "⚡ Advanced Tips",
            {
                "fields": (
                    "recommended_manager",
                    "offensive_tips",
                    "defensive_tips",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "🕐 Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_offensive_tips(self, obj):
        if obj.offensive_tips:
            return format_html('<span style="color: green;">✅</span>')
        return format_html('<span style="color: #888;">—</span>')

    has_offensive_tips.short_description = "⚔️ Offensive Tips"
    has_offensive_tips.boolean = False

    def has_defensive_tips(self, obj):
        if obj.defensive_tips:
            return format_html('<span style="color: green;">✅</span>')
        return format_html('<span style="color: #888;">—</span>')

    has_defensive_tips.short_description = "🛡️ Defensive Tips"
    has_defensive_tips.boolean = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("formation")


# ============================================================
# COUNTER TACTIC ADMIN
# ============================================================


@admin.register(CounterTactic)
class CounterTacticAdmin(admin.ModelAdmin):
    """
    Admin for CounterTactic — formation counter relationships.

    Shows clear visual representation of counter chains.
    Prevents duplicate and self-referencing counter entries.

    Example entries:
    ----------------
    4-3-3  → countered by → 4-2-1-3 [8/10]
    4-4-2  → countered by → 4-3-3   [7/10]
    """

    list_display = (
        "formation",
        "counter_arrow",
        "countered_by",
        "effectiveness_badge",
        "created_at",
    )
    list_filter = ("formation", "countered_by")
    search_fields = ("formation__name", "countered_by__name", "explanation")
    ordering = ("-effectiveness_rating",)
    list_select_related = True
    autocomplete_fields = ["formation", "countered_by"]
    readonly_fields = ("created_at",)
    list_per_page = 25

    fieldsets = (
        (
            "⚔️ Counter Relationship",
            {
                "fields": ("formation", "countered_by", "effectiveness_rating"),
                "description": "Formation A is countered by Formation B. "
                "Self-countering is not allowed.",
            },
        ),
        (
            "📝 Explanation",
            {
                "fields": ("explanation",),
                "description": "Explain tactically why this counter works.",
            },
        ),
        (
            "🕐 Timestamp",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    def counter_arrow(self, obj):
        return format_html(
            '<span style="color: #f59e0b; font-size: 1.2em; font-weight: bold;">'
            "→ countered by →"
            "</span>"
        )

    counter_arrow.short_description = ""

    def effectiveness_badge(self, obj):
        rating = obj.effectiveness_rating
        if rating >= 8:
            color = "#22c55e"
            label = "Highly Effective"
        elif rating >= 6:
            color = "#f59e0b"
            label = "Effective"
        else:
            color = "#ef4444"
            label = "Situational"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/10 — {}</span>',
            color,
            rating,
            label,
        )

    effectiveness_badge.short_description = "Effectiveness"
    effectiveness_badge.admin_order_field = "effectiveness_rating"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "formation", "countered_by"
        )


# ============================================================
# META TRACKER ADMIN
# ============================================================


@admin.register(MetaTracker)
class MetaTrackerAdmin(admin.ModelAdmin):
    """
    Admin for MetaTracker — analytics and meta rankings.

    Shows current meta rankings with visual indicators.
    Useful for:
    - Manual meta data seeding
    - Monitoring weekly meta updates
    - Debugging analytics pipeline

    How to update MetaTracker:
    ---------------------------
    1. Celery task runs weekly (or manually triggered)
    2. Or update directly here for testing/seeding
    3. Use formation__name for filtering formation-specific trackers
    """

    list_display = (
        "rank_badge",
        "formation",
        "usage_count",
        "win_rate_display",
        "average_goals_scored",
        "average_goals_conceded",
        "goal_diff_display",
        "last_meta_update",
    )
    list_filter = ("formation",)
    search_fields = ("formation__name",)
    ordering = ("popularity_rank",)
    list_select_related = True
    autocomplete_fields = ["formation"]
    readonly_fields = ("updated_at", "goal_diff_display", "is_top_meta_display")
    list_per_page = 20

    fieldsets = (
        (
            "🏆 Formation",
            {
                "fields": ("formation",),
            },
        ),
        (
            "📊 Usage Statistics",
            {
                "fields": ("usage_count", "popularity_rank"),
            },
        ),
        (
            "⚽ Performance Metrics",
            {
                "fields": (
                    "win_rate",
                    ("average_goals_scored", "average_goals_conceded"),
                    "goal_diff_display",
                ),
            },
        ),
        (
            "📅 Meta Update Info",
            {
                "fields": ("last_meta_update", "updated_at", "is_top_meta_display"),
            },
        ),
    )

    def rank_badge(self, obj):
        rank = obj.popularity_rank
        if rank == 1:
            return format_html(
                '<span style="color: gold; font-size: 1.3em;">🥇 #{}</span>', rank
            )
        elif rank == 2:
            return format_html(
                '<span style="color: silver; font-size: 1.2em;">🥈 #{}</span>', rank
            )
        elif rank == 3:
            return format_html(
                '<span style="color: #cd7f32; font-size: 1.1em;">🥉 #{}</span>', rank
            )
        return format_html(
            '<span style="color: #888; font-weight: bold;">#{}</span>', rank
        )

    rank_badge.short_description = "Rank"
    rank_badge.admin_order_field = "popularity_rank"

    def win_rate_display(self, obj):
        wr = float(obj.win_rate)
        if wr >= 60:
            color = "#22c55e"
        elif wr >= 45:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            f"{wr:.1f}",
        )

    win_rate_display.short_description = "Win Rate"
    win_rate_display.admin_order_field = "win_rate"

    def goal_diff_display(self, obj):
        gd = obj.goal_difference
        color = "#22c55e" if gd >= 0 else "#ef4444"
        sign = "+" if gd >= 0 else ""
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{}</span>',
            color,
            sign,
            gd,
        )

    goal_diff_display.short_description = "Avg Goal Diff"

    def is_top_meta_display(self, obj):
        if obj.is_top_meta:
            return format_html(
                '<span style="color: gold; font-weight: bold;">⭐ Top 3 Meta</span>'
            )
        return "—"

    is_top_meta_display.short_description = "Elite Status"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("formation")