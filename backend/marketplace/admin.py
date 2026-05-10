from django.contrib import admin
from .models import Account, Listing, Order


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display   = ("owner", "platform", "level", "rating", "coin_balance", "is_active")
    list_filter    = ("platform", "is_active")
    search_fields  = ("owner__username", "description")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields  = ("owner",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display   = ("account", "seller", "price", "currency", "status", "views", "created_at")
    list_filter    = ("status", "currency")
    search_fields  = ("seller__username", "account__owner__username")
    readonly_fields = ("views", "created_at", "updated_at")
    raw_id_fields  = ("seller", "account")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ("id", "buyer", "listing", "amount", "currency", "status", "created_at")
    list_filter    = ("status", "currency")
    search_fields  = ("buyer__username",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields  = ("buyer", "listing")