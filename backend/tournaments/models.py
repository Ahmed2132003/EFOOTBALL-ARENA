from django.db import models
from django.conf import settings


class Tournament(models.Model):
    class StatusChoices(models.TextChoices):
        UPCOMING  = "Upcoming",   "Upcoming"
        ONGOING   = "Ongoing",    "Ongoing"
        COMPLETED = "Completed",  "Completed"
        CANCELLED = "Cancelled",  "Cancelled"

    class FormatChoices(models.TextChoices):
        SINGLE_ELIM = "Single Elimination", "Single Elimination"
        DOUBLE_ELIM = "Double Elimination", "Double Elimination"
        ROUND_ROBIN = "Round Robin",         "Round Robin"
        LEAGUE      = "League",              "League"

    title        = models.CharField(max_length=200)
    organizer    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="organized_tournaments"
    )
    format       = models.CharField(
        max_length=30, choices=FormatChoices.choices,
        default=FormatChoices.ROUND_ROBIN
    )
    status       = models.CharField(
        max_length=20, choices=StatusChoices.choices,
        default=StatusChoices.UPCOMING
    )
    max_players   = models.PositiveIntegerField(default=16)
    prize_pool    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date    = models.DateTimeField()
    end_date      = models.DateTimeField(null=True, blank=True)
    description   = models.TextField(blank=True)
    banner        = models.ImageField(upload_to="tournaments/banners/", blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    participants  = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="tournaments",
        blank=True
    )

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Tournament"
        verbose_name_plural = "Tournaments"

    def __str__(self):
        return f"{self.title} [{self.status}]"


class Match(models.Model):
    class ResultChoices(models.TextChoices):
        PENDING    = "Pending",    "Pending"
        HOME_WIN   = "Home Win",   "Home Win"
        AWAY_WIN   = "Away Win",   "Away Win"
        DRAW       = "Draw",       "Draw"
        CANCELLED  = "Cancelled",  "Cancelled"

    tournament  = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="matches"
    )
    home_player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="home_matches"
    )
    away_player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="away_matches"
    )
    home_score  = models.PositiveSmallIntegerField(default=0)
    away_score  = models.PositiveSmallIntegerField(default=0)
    result      = models.CharField(
        max_length=20, choices=ResultChoices.choices,
        default=ResultChoices.PENDING
    )
    round_number = models.PositiveIntegerField(default=1)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    played_at    = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["round_number", "scheduled_at"]
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __str__(self):
        return (f"{self.tournament.title} | R{self.round_number} | "
                f"{self.home_player} vs {self.away_player}")


class Ranking(models.Model):
    tournament  = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="rankings"
    )
    player      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="rankings"
    )
    position    = models.PositiveIntegerField()
    points      = models.IntegerField(default=0)
    wins        = models.PositiveIntegerField(default=0)
    draws       = models.PositiveIntegerField(default=0)
    losses      = models.PositiveIntegerField(default=0)
    goals_for   = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        unique_together = ("tournament", "player")
        verbose_name = "Ranking"
        verbose_name_plural = "Rankings"

    def __str__(self):
        return f"{self.tournament.title} — #{self.position} {self.player}"