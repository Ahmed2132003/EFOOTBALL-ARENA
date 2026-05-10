from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class RankLevel(models.TextChoices):
        BRONZE   = "Bronze",   "Bronze"
        SILVER   = "Silver",   "Silver"
        GOLD     = "Gold",     "Gold"
        PLATINUM = "Platinum", "Platinum"
        DIAMOND  = "Diamond",  "Diamond"
        LEGEND   = "Legend",   "Legend"

    bio        = models.TextField(blank=True)
    avatar     = models.ImageField(upload_to="avatars/", blank=True)
    rating     = models.FloatField(default=1000.0)
    rank_level = models.CharField(
        max_length=20,
        choices=RankLevel.choices,
        default=RankLevel.BRONZE,
    )
    country     = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.rank_level})"