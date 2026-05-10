from django.db import models
from django.conf import settings


class Account(models.Model):
    class PlatformChoices(models.TextChoices):
        PC      = "PC",      "PC"
        PS4     = "PS4",     "PS4"
        PS5     = "PS5",     "PS5"
        XBOX    = "Xbox",    "Xbox"
        MOBILE  = "Mobile",  "Mobile"

    owner       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="game_accounts"
    )
    platform    = models.CharField(
        max_length=20, choices=PlatformChoices.choices
    )
    level       = models.PositiveIntegerField(default=1)
    rating      = models.PositiveIntegerField(default=1000)
    coin_balance = models.PositiveBigIntegerField(default=0)
    description  = models.TextField(blank=True)
    screenshot   = models.ImageField(upload_to="marketplace/screenshots/", blank=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rating"]
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return f"{self.platform} Lv.{self.level} — {self.owner.username}"


class Listing(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE    = "Active",    "Active"
        SOLD      = "Sold",      "Sold"
        EXPIRED   = "Expired",   "Expired"
        CANCELLED = "Cancelled", "Cancelled"

    account     = models.OneToOneField(
        Account, on_delete=models.CASCADE, related_name="listing"
    )
    seller      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="listings"
    )
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    currency    = models.CharField(max_length=10, default="USD")
    status      = models.CharField(
        max_length=20, choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    views       = models.PositiveIntegerField(default=0)
    expires_at  = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Listing"
        verbose_name_plural = "Listings"

    def __str__(self):
        return f"{self.account} — {self.price} {self.currency} [{self.status}]"


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING   = "Pending",   "Pending"
        PAID      = "Paid",      "Paid"
        DELIVERED = "Delivered", "Delivered"
        REFUNDED  = "Refunded",  "Refunded"
        DISPUTED  = "Disputed",  "Disputed"

    listing     = models.ForeignKey(
        Listing, on_delete=models.PROTECT, related_name="orders"
    )
    buyer       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="orders"
    )
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    currency    = models.CharField(max_length=10, default="USD")
    status      = models.CharField(
        max_length=20, choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.pk} — {self.buyer.username} — {self.status}"