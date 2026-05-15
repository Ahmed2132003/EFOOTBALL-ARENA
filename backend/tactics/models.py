"""
============================================================
eFootball Arena — Tactics Models
Production-Grade Tactical Database Architecture

Architecture Decisions:
------------------------
1. Formation      → Core model, all tactics revolve around it
2. PlayerPosition → SVG/Canvas-ready coordinates for frontend visualization
3. TacticCard     → Rich content cards attached to formations
4. CounterTactic  → Self-referencing M2M-style relation for counter analysis
5. MetaTracker    → OneToOne analytics model, future leaderboard/AI-ready

Design Principles:
------------------
- All coordinates use 0-100 range (percentage-based) → SVG/Canvas friendly
- All ratings use 1-10 scale → consistent UX
- Indexes on all filterable/sortable fields → query performance
- select_related / prefetch_related ready → no N+1 in admin or API
- Future-proof: ready for AI recommendations, ranking system, meta updates

How to add a new Formation:
-----------------------------
1. Create via Django Admin → Formations → Add Formation
2. Add PlayerPosition objects (use display_order for sorting)
3. Optionally add TacticCard and CounterTactic relations
4. MetaTracker is created automatically via signal (or manually)

Coordinate System (PlayerPosition):
--------------------------------------
  x=0   → left side of pitch
  x=50  → center
  x=100 → right side of pitch
  y=0   → goalkeeper line
  y=100 → attacking line

  Example 4-3-3:
    GK  → x=50, y=5
    LB  → x=10, y=25
    CB  → x=35, y=22
    CB  → x=65, y=22
    RB  → x=90, y=25
    CMF → x=30, y=50
    CMF → x=50, y=45
    CMF → x=70, y=50
    LWF → x=10, y=75
    CF  → x=50, y=85
    RWF → x=90, y=75
============================================================
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


# ============================================================
# 1️⃣  FORMATION MODEL
# ============================================================


class Formation(models.Model):
    """
    Core tactical formation model.

    Represents a football formation (e.g. 4-3-3, 4-2-1-3).
    All other tactical models (TacticCard, PlayerPosition,
    CounterTactic, MetaTracker) reference this model.

    Why slug?
    ---------
    Slug enables clean URLs: /tactics/4-3-3/ instead of /tactics/1/
    Also used as a stable identifier for fixtures and API.

    Why ratings 1-10?
    ------------------
    Consistent scale across all tactical attributes.
    Makes comparison and sorting straightforward.
    Future AI can use these as feature vectors.
    """

    class DifficultyLevel(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        PROFESSIONAL = "professional", "Professional"

    class PlayStyle(models.TextChoices):
        POSSESSION = "possession", "Possession"
        COUNTER_ATTACK = "counter_attack", "Counter Attack"
        TIKI_TAKA = "tiki_taka", "Tiki-Taka"
        HIGH_PRESS = "high_press", "High Press"
        DEFENSIVE = "defensive", "Defensive"
        BALANCED = "balanced", "Balanced"
        WING_PLAY = "wing_play", "Wing Play"

    # ── Core Identity ────────────────────────────────────────
    name = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Formation Name",
        help_text="e.g. 4-3-3, 4-2-1-3, 3-4-3",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Formation Code",
        help_text="Short code used in URLs and API (e.g. 4-3-3)",
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="Slug",
        help_text="Auto-generated from name. Used in URLs.",
    )

    # ── Description ──────────────────────────────────────────
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Tactical description of the formation.",
    )

    # ── Tactical Classification ──────────────────────────────
    play_style = models.CharField(
        max_length=20,
        choices=PlayStyle.choices,
        default=PlayStyle.BALANCED,
        db_index=True,
        verbose_name="Play Style",
    )
    difficulty_level = models.CharField(
        max_length=15,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.INTERMEDIATE,
        db_index=True,
        verbose_name="Difficulty Level",
        help_text="How difficult is this formation to master?",
    )

    # ── Tactical Ratings (1-10) ──────────────────────────────
    # Why separate ratings instead of a JSON field?
    # → Allows direct DB filtering: Formation.objects.filter(attacking_rating__gte=7)
    # → Type-safe, validated, indexed
    # → Future AI can use these as feature vectors
    attacking_rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Attacking Rating",
        help_text="Offensive threat level (1-10)",
    )
    defensive_rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Defensive Rating",
        help_text="Defensive solidity level (1-10)",
    )
    possession_rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Possession Rating",
        help_text="Ball retention capability (1-10)",
    )
    pressing_rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Pressing Rating",
        help_text="High press intensity (1-10)",
    )
    width_rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Width Rating",
        help_text="Pitch width utilization (1-10)",
    )
    tempo_rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Tempo Rating",
        help_text="Speed of play (1-10)",
    )

    # ── Meta Status ──────────────────────────────────────────
    is_meta = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Is Meta",
        help_text="Is this formation currently in the meta?",
    )

    # ── Timestamps ───────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        ordering = ["name"]
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        indexes = [
            models.Index(fields=["is_meta", "play_style"]),
            models.Index(fields=["difficulty_level"]),
            models.Index(fields=["attacking_rating", "defensive_rating"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(attacking_rating__gte=1)
                & models.Q(attacking_rating__lte=10),
                name="formation_attacking_rating_range",
            ),
            models.CheckConstraint(
                check=models.Q(defensive_rating__gte=1)
                & models.Q(defensive_rating__lte=10),
                name="formation_defensive_rating_range",
            ),
            models.CheckConstraint(
                check=models.Q(possession_rating__gte=1)
                & models.Q(possession_rating__lte=10),
                name="formation_possession_rating_range",
            ),
            models.CheckConstraint(
                check=models.Q(pressing_rating__gte=1)
                & models.Q(pressing_rating__lte=10),
                name="formation_pressing_rating_range",
            ),
            models.CheckConstraint(
                check=models.Q(width_rating__gte=1)
                & models.Q(width_rating__lte=10),
                name="formation_width_rating_range",
            ),
            models.CheckConstraint(
                check=models.Q(tempo_rating__gte=1)
                & models.Q(tempo_rating__lte=10),
                name="formation_tempo_rating_range",
            ),
        ]

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        # Sync code with name if code not explicitly set
        if not self.code:
            self.code = self.name
        super().save(*args, **kwargs)

    def __str__(self):
        meta_badge = " ⭐" if self.is_meta else ""
        return f"{self.name}{meta_badge}"

    @property
    def average_rating(self):
        """
        Computed average of all tactical ratings.
        Useful for formation comparison and sorting.
        """
        ratings = [
            self.attacking_rating,
            self.defensive_rating,
            self.possession_rating,
            self.pressing_rating,
            self.width_rating,
            self.tempo_rating,
        ]
        return round(sum(ratings) / len(ratings), 1)

    @property
    def total_positions(self):
        """Number of player positions defined for this formation."""
        return self.positions.count()


# ============================================================
# 2️⃣  PLAYER POSITION MODEL
# ============================================================


class PlayerPosition(models.Model):
    """
    Individual player position within a formation.

    SVG/Canvas Coordinate System:
    --------------------------------
    - x_coordinate: 0 (left) → 100 (right)  [percentage of pitch width]
    - y_coordinate: 0 (goal) → 100 (attack)  [percentage of pitch height]

    Why percentage-based coordinates?
    -----------------------------------
    → Works with any canvas/SVG size (responsive)
    → Frontend renders: position_x = x_coordinate% of canvas_width
    → No hardcoded pixel values
    → Works on mobile and desktop

    Usage in React/SVG:
    --------------------
    ```jsx
    const svgX = (position.x_coordinate / 100) * svgWidth;
    const svgY = (position.y_coordinate / 100) * svgHeight;
    <circle cx={svgX} cy={svgY} r={20} />
    <text x={svgX} y={svgY}>{position.short_name}</text>
    ```

    Tactical Role Examples:
    ------------------------
    GK  → Goalkeeper (y=5, x=50)
    CB  → Centre-Back (y=22, x=35 or x=65)
    LB  → Left-Back (y=25, x=10)
    RB  → Right-Back (y=25, x=90)
    DMF → Defensive Midfielder (y=40)
    CMF → Central Midfielder (y=50)
    AMF → Attacking Midfielder (y=65)
    LWF → Left Winger (y=75, x=10)
    RWF → Right Winger (y=75, x=90)
    SS  → Second Striker (y=80)
    CF  → Centre Forward (y=85, x=50)
    """

    class TacticalRole(models.TextChoices):
        GOALKEEPER = "GK", "Goalkeeper"
        CENTRE_BACK = "CB", "Centre-Back"
        LEFT_BACK = "LB", "Left-Back"
        RIGHT_BACK = "RB", "Right-Back"
        DEFENSIVE_MID = "DMF", "Defensive Midfielder"
        CENTRAL_MID = "CMF", "Central Midfielder"
        ATTACKING_MID = "AMF", "Attacking Midfielder"
        LEFT_WING = "LWF", "Left Winger"
        RIGHT_WING = "RWF", "Right Winger"
        SECOND_STRIKER = "SS", "Second Striker"
        CENTRE_FORWARD = "CF", "Centre Forward"
        LEFT_MID = "LMF", "Left Midfielder"
        RIGHT_MID = "RMF", "Right Midfielder"
        WING_BACK_LEFT = "LWB", "Left Wing-Back"
        WING_BACK_RIGHT = "RWB", "Right Wing-Back"

    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="positions",
        verbose_name="Formation",
        db_index=True,
    )

    # ── Position Identity ────────────────────────────────────
    position_name = models.CharField(
        max_length=50,
        verbose_name="Position Name",
        help_text="e.g. Left Centre-Back, Attacking Midfielder",
    )
    short_name = models.CharField(
        max_length=5,
        verbose_name="Short Name",
        help_text="e.g. LCB, AMF, CF — used in tactical board display",
    )

    # ── SVG/Canvas Coordinates (0-100 percentage scale) ──────
    x_coordinate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="X Coordinate",
        help_text="Horizontal position: 0=left, 50=center, 100=right",
    )
    y_coordinate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Y Coordinate",
        help_text="Vertical position: 0=goalkeeper end, 100=attacking end",
    )

    # ── Tactical Classification ──────────────────────────────
    tactical_role = models.CharField(
        max_length=5,
        choices=TacticalRole.choices,
        verbose_name="Tactical Role",
        db_index=True,
    )

    # ── Display Order ────────────────────────────────────────
    display_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Order for display (1=GK, ascending to forwards)",
    )

    class Meta:
        ordering = ["formation", "display_order"]
        verbose_name = "Player Position"
        verbose_name_plural = "Player Positions"
        # Each position within a formation must have unique display_order
        unique_together = [("formation", "display_order")]
        indexes = [
            models.Index(fields=["formation", "tactical_role"]),
            models.Index(fields=["display_order"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(x_coordinate__gte=0.0)
                & models.Q(x_coordinate__lte=100.0),
                name="position_x_coordinate_range",
            ),
            models.CheckConstraint(
                check=models.Q(y_coordinate__gte=0.0)
                & models.Q(y_coordinate__lte=100.0),
                name="position_y_coordinate_range",
            ),
        ]

    def __str__(self):
        return f"{self.formation.name} | {self.short_name} ({self.position_name})"

    @property
    def coordinates(self):
        """
        Returns coordinates as dict for JSON serialization.
        Ready for direct use in React/SVG components.
        """
        return {"x": self.x_coordinate, "y": self.y_coordinate}


# ============================================================
# 3️⃣  TACTIC CARD MODEL
# ============================================================


class TacticCard(models.Model):
    """
    Rich tactical guide card for a formation.

    A TacticCard contains detailed tactical instructions:
    - When to use this formation
    - Strengths and weaknesses
    - Offensive and defensive tips
    - Manager/player recommendations

    Why TextField for all content fields?
    ---------------------------------------
    → Rich text friendly (can store HTML/Markdown)
    → No length restriction for detailed tactical guides
    → Frontend can render with any markdown parser

    Relation:
    ----------
    Formation → TacticCard (one-to-one or one-to-many)
    One formation can have multiple tactical guides from different experts.
    """

    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="tactic_cards",
        verbose_name="Formation",
        db_index=True,
    )

    # ── Card Identity ────────────────────────────────────────
    title = models.CharField(
        max_length=200,
        verbose_name="Title",
        help_text="e.g. 'Complete 4-3-3 Attacking Guide'",
    )

    # ── Core Tactical Content ────────────────────────────────
    content = models.TextField(
        verbose_name="Content",
        help_text="Main tactical overview and explanation",
    )
    strengths = models.TextField(
        verbose_name="Strengths",
        help_text="Key advantages of this formation",
    )
    weaknesses = models.TextField(
        verbose_name="Weaknesses",
        help_text="Key vulnerabilities and limitations",
    )

    # ── Situational Guidance ─────────────────────────────────
    use_when = models.TextField(
        verbose_name="Use When",
        help_text="Situations and opponent types where this excels",
    )
    avoid_when = models.TextField(
        verbose_name="Avoid When",
        help_text="Situations where this formation struggles",
    )

    # ── Advanced Tips ────────────────────────────────────────
    recommended_manager = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Recommended Manager Style",
        help_text="e.g. 'Possession-focused manager with high passing stats'",
    )
    offensive_tips = models.TextField(
        blank=True,
        verbose_name="Offensive Tips",
        help_text="Advanced attacking strategies and triggers",
    )
    defensive_tips = models.TextField(
        blank=True,
        verbose_name="Defensive Tips",
        help_text="Advanced defensive organization and compactness tips",
    )

    # ── Timestamps ───────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tactic Card"
        verbose_name_plural = "Tactic Cards"
        indexes = [
            models.Index(fields=["formation", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.formation.name} — {self.title}"


# ============================================================
# 4️⃣  COUNTER TACTIC MODEL
# ============================================================


class CounterTactic(models.Model):
    """
    Formation counter relationships.

    Models the tactical rock-paper-scissors of eFootball:
    "Formation A is countered by Formation B"

    Design Decisions:
    ------------------
    1. Two separate FK fields (not ManyToManyField) to allow:
       - effectiveness_rating per counter relationship
       - explanation text per counter
       - future metadata (e.g. discovery date, patch version)

    2. unique_together prevents duplicate counter entries

    3. clean() prevents self-countering (a formation cannot counter itself)

    4. Symmetry is NOT enforced: if A counters B, B does NOT auto-counter A
       This is intentional — counters are directional in football tactics

    Example Counter Logic:
    -----------------------
    4-3-3  → countered by → 4-2-1-3 (effectiveness: 8/10)
    4-4-2  → countered by → 4-3-3   (effectiveness: 7/10)
    3-4-3  → countered by → 5-2-1-2 (effectiveness: 9/10)

    Future use:
    ------------
    Counter Finder API:
    GET /api/v1/tactics/counter/?formation=4-3-3
    → Returns all formations that counter 4-3-3

    AI Tactical Suggestions:
    GET /api/v1/tactics/suggest/?opponent=4-3-3
    → Returns best formation to use against 4-3-3
    """

    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="is_countered_by",
        verbose_name="Formation",
        help_text="The formation being countered",
        db_index=True,
    )
    countered_by = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="counters",
        verbose_name="Countered By",
        help_text="The formation that counters the above formation",
        db_index=True,
    )

    # ── Counter Details ──────────────────────────────────────
    explanation = models.TextField(
        verbose_name="Explanation",
        help_text="Why and how this counter works tactically",
    )
    effectiveness_rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Effectiveness Rating",
        help_text="How effective is this counter? (1-10)",
    )

    # ── Timestamp ────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ["-effectiveness_rating"]
        verbose_name = "Counter Tactic"
        verbose_name_plural = "Counter Tactics"
        # Prevent duplicate counter relationships
        unique_together = [("formation", "countered_by")]
        indexes = [
            models.Index(fields=["formation", "-effectiveness_rating"]),
            models.Index(fields=["countered_by"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(effectiveness_rating__gte=1)
                & models.Q(effectiveness_rating__lte=10),
                name="counter_effectiveness_rating_range",
            ),
        ]

    def clean(self):
        """
        Validation: A formation cannot counter itself.
        This check runs on full_clean() — Admin enforces this.
        """
        from django.core.exceptions import ValidationError

        if self.formation_id and self.countered_by_id:
            if self.formation_id == self.countered_by_id:
                raise ValidationError(
                    {
                        "countered_by": "A formation cannot counter itself. "
                        "Select a different formation."
                    }
                )

    def __str__(self):
        return (
            f"{self.formation.name} → countered by → {self.countered_by.name} "
            f"[{self.effectiveness_rating}/10]"
        )


# ============================================================
# 5️⃣  META TRACKER MODEL
# ============================================================


class MetaTracker(models.Model):
    """
    Analytics and meta-game tracking for a formation.

    OneToOne with Formation — each formation has exactly one MetaTracker.

    Purpose:
    ---------
    - Track real-world usage statistics
    - Power the Meta Rankings leaderboard
    - Feed data to AI tactical recommendations
    - Enable weekly meta updates

    Why OneToOne instead of fields on Formation?
    ---------------------------------------------
    - Separation of concerns: Formation = static config, MetaTracker = dynamic data
    - MetaTracker can be updated frequently without touching Formation
    - Easier to reset/recalculate analytics independently
    - Supports future time-series snapshots (add a date field for history)

    Future Architecture:
    ---------------------
    MetaSnapshot model (future):
    - ForeignKey to Formation
    - Copy of MetaTracker data + timestamp
    - Enables historical meta charts

    Weekly Update Task (Celery Beat):
    ```python
    @shared_task
    def update_meta_tracker():
        for tracker in MetaTracker.objects.all():
            # Calculate from match data
            tracker.win_rate = calculate_win_rate(tracker.formation)
            tracker.usage_count = count_usage(tracker.formation)
            tracker.popularity_rank = calculate_rank(tracker.formation)
            tracker.save(update_fields=[
                'win_rate', 'usage_count',
                'popularity_rank', 'last_meta_update', 'updated_at'
            ])
    ```
    """

    formation = models.OneToOneField(
        Formation,
        on_delete=models.CASCADE,
        related_name="meta_tracker",
        verbose_name="Formation",
        db_index=True,
    )

    # ── Usage Statistics ─────────────────────────────────────
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Usage Count",
        help_text="Number of times this formation was used in matches",
        db_index=True,
    )

    # ── Performance Metrics ──────────────────────────────────
    win_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        verbose_name="Win Rate (%)",
        help_text="Win percentage (0.00 - 100.00)",
    )
    average_goals_scored = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        verbose_name="Avg Goals Scored",
        help_text="Average goals scored per match",
    )
    average_goals_conceded = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        verbose_name="Avg Goals Conceded",
        help_text="Average goals conceded per match",
    )

    # ── Ranking ──────────────────────────────────────────────
    popularity_rank = models.PositiveIntegerField(
        default=0,
        verbose_name="Popularity Rank",
        help_text="Current rank in meta leaderboard (1 = most popular)",
        db_index=True,
    )

    # ── Timestamps ───────────────────────────────────────────
    last_meta_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Meta Update",
        help_text="When was the meta data last recalculated?",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        ordering = ["popularity_rank"]
        verbose_name = "Meta Tracker"
        verbose_name_plural = "Meta Trackers"
        indexes = [
            models.Index(fields=["popularity_rank"]),
            models.Index(fields=["-win_rate"]),
            models.Index(fields=["-usage_count"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(win_rate__gte=0) & models.Q(win_rate__lte=100),
                name="meta_tracker_win_rate_range",
            ),
            models.CheckConstraint(
                check=models.Q(average_goals_scored__gte=0),
                name="meta_tracker_goals_scored_positive",
            ),
            models.CheckConstraint(
                check=models.Q(average_goals_conceded__gte=0),
                name="meta_tracker_goals_conceded_positive",
            ),
        ]

    def __str__(self):
        return (
            f"{self.formation.name} | "
            f"Rank #{self.popularity_rank} | "
            f"Win Rate: {self.win_rate}%"
        )

    @property
    def goal_difference(self):
        """Average goal difference per match."""
        return round(
            float(self.average_goals_scored) - float(self.average_goals_conceded),
            2,
        )

    @property
    def is_top_meta(self):
        """True if formation is in top 3 of meta ranking."""
        return 1 <= self.popularity_rank <= 3