

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=100, verbose_name="Назва списку")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'name')
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

    rawg_id = models.PositiveIntegerField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_games')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    lists = models.ManyToManyField(UserList, related_name='games', blank=True, verbose_name="Списки")

    class Meta:
        unique_together = ('user', 'rawg_id')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} — AppID {self.rawg_id}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Не вказано')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    friends = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True,
        related_name='friend_of'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name="Аватар"
    )

    @property
    def is_friend_with_current_user(self):
        if not hasattr(self, '_request_user'):
            return False
        try:
            current_user_profile = self._request_user.profile
            return self.friends.filter(pk=current_user_profile.pk).exists()
        except:
            return False

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def __str__(self):
        return f"Профіль {self.user.username}"

    def add_friend(self, other_profile):
        self.friends.add(other_profile)

    def remove_friend(self, other_profile):
        self.friends.remove(other_profile)

    def is_friend(self, other_profile):
        return self.friends.filter(user=other_profile.user).exists()

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()




class FriendRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В очікуванні'),
        ('accepted', 'Прийнято'),
        ('rejected', 'Відхилено'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"

    def accept(self):
        self.status = 'accepted'
        self.save()
        sender_profile = self.sender.profile
        receiver_profile = self.receiver.profile
        sender_profile.friends.add(receiver_profile)
        receiver_profile.friends.add(sender_profile)

    def reject(self):
        self.status = 'rejected'
        self.save()