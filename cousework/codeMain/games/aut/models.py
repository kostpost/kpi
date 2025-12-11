# models.py
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    steam_id = models.CharField(max_length=50, blank=True)
    steam_personaname = models.CharField(max_length=100, blank=True)
    steam_avatar = models.URLField(blank=True)

    def __str__(self):
        return self.steam_personaname or self.user.username