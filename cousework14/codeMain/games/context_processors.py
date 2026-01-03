# games/context_processors.py  (або де в тебе лежить цей файл)

from .steam_utils import get_steam_profile_data  # якщо steam_utils.py в тій самій папці


def steam_user_data(request):
    """
    Контекст-процесор, який додає в кожен шаблон змінну steam_profile
    з актуальними даними Steam (нік, аватарка тощо) для авторизованого користувача.
    """
    if request.user.is_authenticated and hasattr(request.user, 'social_auth') and request.user.social_auth.exists():
        social = request.user.social_auth.first()
        steamid = social.uid
        profile_data = get_steam_profile_data(steamid)
        return {'steam_profile': profile_data}

    return {'steam_profile': None}