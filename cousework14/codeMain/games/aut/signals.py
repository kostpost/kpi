# signals.py
from django.dispatch import receiver
from social_core.pipeline.user import get_username
from .models import UserProfile

@receiver('social_core.pipeline.user.create_user')
def create_user_profile(sender, user, social, **kwargs):
    if social.provider == 'steam':
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.steam_id = social.uid
        profile.steam_personaname = social.extra_data.get('player', {}).get('personaname')
        profile.steam_avatar = social.extra_data.get('player', {}).get('avatarfull')
        profile.save()