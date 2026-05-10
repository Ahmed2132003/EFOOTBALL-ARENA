from django.contrib import admin
from .models import Formation, TacticCard


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display   = ("name", "created_at")
    search_fields  = ("name",)
    readonly_fields = ("created_at",)


@admin.register(TacticCard)
class TacticCardAdmin(admin.ModelAdmin):
    list_display   = ("title", "owner", "formation", "style", "is_public", "likes", "created_at")
    list_filter    = ("style", "is_public", "formation")
    search_fields  = ("title", "owner__username")
    readonly_fields = ("likes", "created_at", "updated_at")
    raw_id_fields  = ("owner",)