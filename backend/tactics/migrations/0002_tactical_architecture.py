# Generated migration for Tactical Database Architecture
# Phase 2 — Part 1: Complete Tactical System
#
# This migration:
# 1. Drops the old Formation and TacticCard models (from 0001_initial)
# 2. Creates new Formation model with full tactical fields
# 3. Creates PlayerPosition model with SVG coordinates
# 4. Creates new TacticCard model with rich content fields
# 5. Creates CounterTactic model for counter analysis
# 6. Creates MetaTracker model for analytics
#
# ⚠️  WARNING: This migration drops existing tactics data.
# Run loaddata after migrate to restore fixtures.
#
# Commands:
#   docker-compose exec backend python manage.py migrate
#   docker-compose exec backend python manage.py loaddata tactics/fixtures/formations.json

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tactics", "0001_initial"),
    ]

    operations = [
        # ── Step 1: Drop old TacticCard (FK to old Formation) ────────────────
        migrations.DeleteModel(
            name="TacticCard",
        ),
        # ── Step 2: Drop old Formation ───────────────────────────────────────
        migrations.DeleteModel(
            name="Formation",
        ),
        # ── Step 3: Create new Formation ─────────────────────────────────────
        migrations.CreateModel(
            name="Formation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        help_text="e.g. 4-3-3, 4-2-1-3, 3-4-3",
                        max_length=20,
                        unique=True,
                        verbose_name="Formation Name",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        db_index=True,
                        help_text="Short code used in URLs and API (e.g. 4-3-3)",
                        max_length=20,
                        unique=True,
                        verbose_name="Formation Code",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        db_index=True,
                        help_text="Auto-generated from name. Used in URLs.",
                        max_length=30,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Tactical description of the formation.",
                        verbose_name="Description",
                    ),
                ),
                (
                    "play_style",
                    models.CharField(
                        choices=[
                            ("possession", "Possession"),
                            ("counter_attack", "Counter Attack"),
                            ("tiki_taka", "Tiki-Taka"),
                            ("high_press", "High Press"),
                            ("defensive", "Defensive"),
                            ("balanced", "Balanced"),
                            ("wing_play", "Wing Play"),
                        ],
                        db_index=True,
                        default="balanced",
                        max_length=20,
                        verbose_name="Play Style",
                    ),
                ),
                (
                    "difficulty_level",
                    models.CharField(
                        choices=[
                            ("beginner", "Beginner"),
                            ("intermediate", "Intermediate"),
                            ("advanced", "Advanced"),
                            ("professional", "Professional"),
                        ],
                        db_index=True,
                        default="intermediate",
                        help_text="How difficult is this formation to master?",
                        max_length=15,
                        verbose_name="Difficulty Level",
                    ),
                ),
                (
                    "attacking_rating",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="Offensive threat level (1-10)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Attacking Rating",
                    ),
                ),
                (
                    "defensive_rating",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="Defensive solidity level (1-10)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Defensive Rating",
                    ),
                ),
                (
                    "possession_rating",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="Ball retention capability (1-10)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Possession Rating",
                    ),
                ),
                (
                    "pressing_rating",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="High press intensity (1-10)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Pressing Rating",
                    ),
                ),
                (
                    "width_rating",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="Pitch width utilization (1-10)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Width Rating",
                    ),
                ),
                (
                    "tempo_rating",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="Speed of play (1-10)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Tempo Rating",
                    ),
                ),
                (
                    "is_meta",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Is this formation currently in the meta?",
                        verbose_name="Is Meta",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created At"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
            ],
            options={
                "verbose_name": "Formation",
                "verbose_name_plural": "Formations",
                "ordering": ["name"],
            },
        ),
        # ── Step 4: Create PlayerPosition ─────────────────────────────────────
        migrations.CreateModel(
            name="PlayerPosition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "position_name",
                    models.CharField(
                        help_text="e.g. Left Centre-Back, Attacking Midfielder",
                        max_length=50,
                        verbose_name="Position Name",
                    ),
                ),
                (
                    "short_name",
                    models.CharField(
                        help_text="e.g. LCB, AMF, CF — used in tactical board display",
                        max_length=5,
                        verbose_name="Short Name",
                    ),
                ),
                (
                    "x_coordinate",
                    models.FloatField(
                        help_text="Horizontal position: 0=left, 50=center, 100=right",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(100.0),
                        ],
                        verbose_name="X Coordinate",
                    ),
                ),
                (
                    "y_coordinate",
                    models.FloatField(
                        help_text="Vertical position: 0=goalkeeper end, 100=attacking end",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(100.0),
                        ],
                        verbose_name="Y Coordinate",
                    ),
                ),
                (
                    "tactical_role",
                    models.CharField(
                        choices=[
                            ("GK", "Goalkeeper"),
                            ("CB", "Centre-Back"),
                            ("LB", "Left-Back"),
                            ("RB", "Right-Back"),
                            ("DMF", "Defensive Midfielder"),
                            ("CMF", "Central Midfielder"),
                            ("AMF", "Attacking Midfielder"),
                            ("LWF", "Left Winger"),
                            ("RWF", "Right Winger"),
                            ("SS", "Second Striker"),
                            ("CF", "Centre Forward"),
                            ("LMF", "Left Midfielder"),
                            ("RMF", "Right Midfielder"),
                            ("LWB", "Left Wing-Back"),
                            ("RWB", "Right Wing-Back"),
                        ],
                        db_index=True,
                        max_length=5,
                        verbose_name="Tactical Role",
                    ),
                ),
                (
                    "display_order",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Order for display (1=GK, ascending to forwards)",
                        verbose_name="Display Order",
                    ),
                ),
                (
                    "formation",
                    models.ForeignKey(
                        db_index=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="tactics.formation",
                        verbose_name="Formation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Player Position",
                "verbose_name_plural": "Player Positions",
                "ordering": ["formation", "display_order"],
            },
        ),
        # ── Step 5: Create new TacticCard ─────────────────────────────────────
        migrations.CreateModel(
            name="TacticCard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="e.g. 'Complete 4-3-3 Attacking Guide'",
                        max_length=200,
                        verbose_name="Title",
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        help_text="Main tactical overview and explanation",
                        verbose_name="Content",
                    ),
                ),
                (
                    "strengths",
                    models.TextField(
                        help_text="Key advantages of this formation",
                        verbose_name="Strengths",
                    ),
                ),
                (
                    "weaknesses",
                    models.TextField(
                        help_text="Key vulnerabilities and limitations",
                        verbose_name="Weaknesses",
                    ),
                ),
                (
                    "use_when",
                    models.TextField(
                        help_text="Situations and opponent types where this excels",
                        verbose_name="Use When",
                    ),
                ),
                (
                    "avoid_when",
                    models.TextField(
                        help_text="Situations where this formation struggles",
                        verbose_name="Avoid When",
                    ),
                ),
                (
                    "recommended_manager",
                    models.CharField(
                        blank=True,
                        help_text="e.g. 'Possession-focused manager with high passing stats'",
                        max_length=200,
                        verbose_name="Recommended Manager Style",
                    ),
                ),
                (
                    "offensive_tips",
                    models.TextField(
                        blank=True,
                        help_text="Advanced attacking strategies and triggers",
                        verbose_name="Offensive Tips",
                    ),
                ),
                (
                    "defensive_tips",
                    models.TextField(
                        blank=True,
                        help_text="Advanced defensive organization and compactness tips",
                        verbose_name="Defensive Tips",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created At"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "formation",
                    models.ForeignKey(
                        db_index=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tactic_cards",
                        to="tactics.formation",
                        verbose_name="Formation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tactic Card",
                "verbose_name_plural": "Tactic Cards",
                "ordering": ["-created_at"],
            },
        ),
        # ── Step 6: Create CounterTactic ──────────────────────────────────────
        migrations.CreateModel(
            name="CounterTactic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "explanation",
                    models.TextField(
                        help_text="Why and how this counter works tactically",
                        verbose_name="Explanation",
                    ),
                ),
                (
                    "effectiveness_rating",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="How effective is this counter? (1-10)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        verbose_name="Effectiveness Rating",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created At"
                    ),
                ),
                (
                    "formation",
                    models.ForeignKey(
                        db_index=True,
                        help_text="The formation being countered",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="is_countered_by",
                        to="tactics.formation",
                        verbose_name="Formation",
                    ),
                ),
                (
                    "countered_by",
                    models.ForeignKey(
                        db_index=True,
                        help_text="The formation that counters the above formation",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="counters",
                        to="tactics.formation",
                        verbose_name="Countered By",
                    ),
                ),
            ],
            options={
                "verbose_name": "Counter Tactic",
                "verbose_name_plural": "Counter Tactics",
                "ordering": ["-effectiveness_rating"],
            },
        ),
        # ── Step 7: Create MetaTracker ────────────────────────────────────────
        migrations.CreateModel(
            name="MetaTracker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "usage_count",
                    models.PositiveIntegerField(
                        db_index=True,
                        default=0,
                        help_text="Number of times this formation was used in matches",
                        verbose_name="Usage Count",
                    ),
                ),
                (
                    "win_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        help_text="Win percentage (0.00 - 100.00)",
                        max_digits=5,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(100.0),
                        ],
                        verbose_name="Win Rate (%)",
                    ),
                ),
                (
                    "average_goals_scored",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        help_text="Average goals scored per match",
                        max_digits=4,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                        ],
                        verbose_name="Avg Goals Scored",
                    ),
                ),
                (
                    "average_goals_conceded",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        help_text="Average goals conceded per match",
                        max_digits=4,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                        ],
                        verbose_name="Avg Goals Conceded",
                    ),
                ),
                (
                    "popularity_rank",
                    models.PositiveIntegerField(
                        db_index=True,
                        default=0,
                        help_text="Current rank in meta leaderboard (1 = most popular)",
                        verbose_name="Popularity Rank",
                    ),
                ),
                (
                    "last_meta_update",
                    models.DateTimeField(
                        blank=True,
                        help_text="When was the meta data last recalculated?",
                        null=True,
                        verbose_name="Last Meta Update",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "formation",
                    models.OneToOneField(
                        db_index=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meta_tracker",
                        to="tactics.formation",
                        verbose_name="Formation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Meta Tracker",
                "verbose_name_plural": "Meta Trackers",
                "ordering": ["popularity_rank"],
            },
        ),
        # ── Step 8: Add Indexes ───────────────────────────────────────────────
        migrations.AddIndex(
            model_name="formation",
            index=models.Index(
                fields=["is_meta", "play_style"],
                name="formation_is_meta_play_style_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="formation",
            index=models.Index(
                fields=["difficulty_level"],
                name="formation_difficulty_level_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="formation",
            index=models.Index(
                fields=["attacking_rating", "defensive_rating"],
                name="formation_ratings_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="playerposition",
            index=models.Index(
                fields=["formation", "tactical_role"],
                name="position_formation_role_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="playerposition",
            index=models.Index(
                fields=["display_order"],
                name="position_display_order_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="tacticcard",
            index=models.Index(
                fields=["formation", "-created_at"],
                name="tacticcard_formation_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="countertactic",
            index=models.Index(
                fields=["formation", "-effectiveness_rating"],
                name="counter_formation_effectiveness_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="countertactic",
            index=models.Index(
                fields=["countered_by"],
                name="counter_countered_by_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="metatracker",
            index=models.Index(
                fields=["popularity_rank"],
                name="meta_popularity_rank_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="metatracker",
            index=models.Index(
                fields=["-win_rate"],
                name="meta_win_rate_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="metatracker",
            index=models.Index(
                fields=["-usage_count"],
                name="meta_usage_count_idx",
            ),
        ),
        # ── Step 9: Add Unique Constraints ────────────────────────────────────
        migrations.AlterUniqueTogether(
            name="playerposition",
            unique_together={("formation", "display_order")},
        ),
        migrations.AlterUniqueTogether(
            name="countertactic",
            unique_together={("formation", "countered_by")},
        ),
        # ── Step 10: Add DB Check Constraints ─────────────────────────────────
        migrations.AddConstraint(
            model_name="formation",
            constraint=models.CheckConstraint(
                check=models.Q(attacking_rating__gte=1)
                & models.Q(attacking_rating__lte=10),
                name="formation_attacking_rating_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="formation",
            constraint=models.CheckConstraint(
                check=models.Q(defensive_rating__gte=1)
                & models.Q(defensive_rating__lte=10),
                name="formation_defensive_rating_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="formation",
            constraint=models.CheckConstraint(
                check=models.Q(possession_rating__gte=1)
                & models.Q(possession_rating__lte=10),
                name="formation_possession_rating_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="formation",
            constraint=models.CheckConstraint(
                check=models.Q(pressing_rating__gte=1)
                & models.Q(pressing_rating__lte=10),
                name="formation_pressing_rating_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="formation",
            constraint=models.CheckConstraint(
                check=models.Q(width_rating__gte=1)
                & models.Q(width_rating__lte=10),
                name="formation_width_rating_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="formation",
            constraint=models.CheckConstraint(
                check=models.Q(tempo_rating__gte=1)
                & models.Q(tempo_rating__lte=10),
                name="formation_tempo_rating_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="playerposition",
            constraint=models.CheckConstraint(
                check=models.Q(x_coordinate__gte=0.0)
                & models.Q(x_coordinate__lte=100.0),
                name="position_x_coordinate_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="playerposition",
            constraint=models.CheckConstraint(
                check=models.Q(y_coordinate__gte=0.0)
                & models.Q(y_coordinate__lte=100.0),
                name="position_y_coordinate_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="countertactic",
            constraint=models.CheckConstraint(
                check=models.Q(effectiveness_rating__gte=1)
                & models.Q(effectiveness_rating__lte=10),
                name="counter_effectiveness_rating_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="metatracker",
            constraint=models.CheckConstraint(
                check=models.Q(win_rate__gte=0) & models.Q(win_rate__lte=100),
                name="meta_tracker_win_rate_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="metatracker",
            constraint=models.CheckConstraint(
                check=models.Q(average_goals_scored__gte=0),
                name="meta_tracker_goals_scored_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="metatracker",
            constraint=models.CheckConstraint(
                check=models.Q(average_goals_conceded__gte=0),
                name="meta_tracker_goals_conceded_positive",
            ),
        ),
    ]