from django.db import models
from django.conf import settings


class Formation(models.Model):
    FORMATION_CHOICES = [
        ("4-3-3",   "4-3-3"),
        ("4-4-2",   "4-4-2"),
        ("4-2-3-1", "4-2-3-1"),
        ("3-5-2",   "3-5-2"),
        ("5-3-2",   "5-3-2"),
        ("3-4-3",   "3-4-3"),
        ("4-1-4-1", "4-1-4-1"),
    ]

    name        = models.CharField(max_length=20, choices=FORMATION_CHOICES, unique=True)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to="formations/", blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Formation"
        verbose_name_plural = "Formations"

    def __str__(self):
        return self.name


class TacticCard(models.Model):
    class StyleChoices(models.TextChoices):
        ATTACKING = "Attacking", "Attacking"
        DEFENSIVE = "Defensive", "Defensive"
        BALANCED  = "Balanced",  "Balanced"
        COUNTER   = "Counter",   "Counter"

    owner      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="tactic_cards"
    )
    formation  = models.ForeignKey(
        Formation, on_delete=models.SET_NULL,
        null=True, related_name="tactic_cards"
    )
    title       = models.CharField(max_length=120)
    style       = models.CharField(
        max_length=20, choices=StyleChoices.choices,
        default=StyleChoices.BALANCED
    )
    description = models.TextField(blank=True)
    is_public   = models.BooleanField(default=False)
    likes       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tactic Card"
        verbose_name_plural = "Tactic Cards"

    def __str__(self):
        return f"{self.title} — {self.owner.username}"