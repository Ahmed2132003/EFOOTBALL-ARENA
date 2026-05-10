from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ("username", "email", "rank_level", "rating", "country",
                     "is_verified", "is_active", "date_joined")
    list_filter   = ("rank_level", "is_verified", "is_active", "is_staff", "country")
    search_fields = ("username", "email", "first_name", "last_name", "country")
    readonly_fields = ("date_joined", "last_login", "created_at", "updated_at")

    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {
            "fields": ("bio", "avatar", "rating", "rank_level",
                       "country", "is_verified", "created_at", "updated_at")
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {
            "fields": ("bio", "avatar", "rating", "rank_level", "country", "is_verified")
        }),
    )