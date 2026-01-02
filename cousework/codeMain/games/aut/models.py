# games/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserList(models.Model):
    """Списки ігор користувача (наприклад: Улюблене, Хочу пройти тощо)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=100, verbose_name="Назва списку")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)  # За замовчуванням публічні

    class Meta:
        unique_together = ('user', 'name')  # Один список з такою назвою на користувача
        verbose_name = "Список ігор"
        verbose_name_plural = "Списки ігор"
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} — {self.name}"


class UserGame(models.Model):
    STATUS_CHOICES = [
        ('playing', 'Граю'),
        ('completed', 'Пройдено'),
        ('planned', 'У планах'),
        ('dropped', 'Відкладено'),
        ('not_played', 'Не грав'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_games')
    appid = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Зв'язок з списками — багато-до-багатьох
    lists = models.ManyToManyField(UserList, related_name='games', blank=True, verbose_name="Списки")

    class Meta:
        unique_together = ('user', 'appid')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} — AppID {self.appid}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Не вказано')