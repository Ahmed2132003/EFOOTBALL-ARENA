from django.db import models
from django.conf import settings


class Notification(models.Model):
    class TypeChoices(models.TextChoices):
        MATCH       = "match",        "Match"
        TOURNAMENT  = "tournament",   "Tournament"
        MARKETPLACE = "marketplace",  "Marketplace"
        SYSTEM      = "system",       "System"
        RANK_UP     = "rank_up",      "Rank Up"
        MESSAGE     = "message",      "Message"

    recipient   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="notifications"
    )
    sender      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="sent_notifications"
    )
    type        = models.CharField(
        max_length=30, choices=TypeChoices.choices,
        default=TypeChoices.SYSTEM
    )
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    data        = models.JSONField(default=dict, blank=True)  # extra payload
    created_at  = models.DateTimeField(auto_now_add=True)
    read_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["recipient", "is_read"]),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"[{self.type}] → {self.recipient.username}: {self.title}"