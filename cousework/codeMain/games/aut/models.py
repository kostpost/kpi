# models.py (в твоєму app, наприклад games/models.py)

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserGame(models.Model):
    """
    Model for storing user's personal data about a Steam game:
    - Completion status
    - Rating (1-5 stars)
    - Comment
    """
    STATUS_CHOICES = [
        ('completed', 'Пройдено'),
        ('playing', 'Граю'),
        ('planned', 'У планах'),  # Новий статус
        ('dropped', 'Відкладено'),
        ('not_played', 'Не грав'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_games',
        help_text="The authenticated user who owns this record"
    )

    steamid = models.CharField(
        max_length=17,
        help_text="SteamID64 of the user (for additional safety and queries)"
    )

    appid = models.PositiveIntegerField(
        help_text="Steam AppID of the game"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        blank=True,
        null=True,
        help_text="User-defined completion status"
    )

    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User rating from 1 to 5 stars"
    )

    comment = models.TextField(
        blank=True,
        help_text="User's personal comment or review about the game"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )

    class Meta:
        unique_together = ('user', 'appid')  # One record per user per game
        verbose_name = "User Game"
        verbose_name_plural = "User Games"
        ordering = ['-updated_at']

    def __str__(self):
        status_display = self.get_status_display() if self.status else "No status"
        return f"{self.user.username} - {self.appid} - {status_display}"

    def get_status_color(self):
        colors = {
            'completed': 'bg-green-600',
            'playing': 'bg-blue-600',
            'dropped': 'bg-red-600',
            'not_played': 'bg-gray-600',
        }
        return colors.get(self.status or 'not_played', 'bg-gray-600')