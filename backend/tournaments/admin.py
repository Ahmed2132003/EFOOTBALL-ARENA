from django.contrib import admin
from .models import Tournament, Match, Ranking


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display   = ("title", "organizer", "format", "status",
                      "max_players", "prize_pool", "start_date")
    list_filter    = ("status", "format")
    search_fields  = ("title", "organizer__username")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields  = ("organizer",)
    filter_horizontal = ("participants",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display   = ("tournament", "round_number", "home_player", "home_score",
                      "away_score", "away_player", "result", "scheduled_at")
    list_filter    = ("result", "tournament")
    search_fields  = ("home_player__username", "away_player__username",
                      "tournament__title")
    readonly_fields = ("created_at",)


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display   = ("tournament", "position", "player", "points",
                      "wins", "draws", "losses", "goals_for", "goals_against")
    list_filter    = ("tournament",)
    search_fields  = ("player__username", "tournament__title")
    readonly_fields = ("updated_at",)