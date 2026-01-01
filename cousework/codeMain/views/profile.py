from django.shortcuts import render
from django.http import Http404
import requests
from datetime import datetime
from games import steam_utils
from codeMain import settings
from games.aut.models import UserGame
from views.game_detail import get_steamid

STEAM_API_KEY = getattr(settings, 'SOCIAL_AUTH_STEAM_API_KEY', None)

STATUS_PRIORITY = {
    'completed': 0,
    'playing': 1,
    'planned': 2,
    'dropped': 3,
    'not_played': 4,
}

def sort_games(game):
    status = game.get('status', 'not_played')
    rating = game.get('user_rating', 0) or 0
    name = game.get('name', '').lower()
    return (STATUS_PRIORITY.get(status, 5), -rating, name)

def profile(request, steamid: str):
    if not steamid:
        raise Http404("SteamID не вказано")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    profile_data = {
        'personaname': 'Невідомий користувач',
        'steamid': steamid,
        'profileurl': f"https://steamcommunity.com/profiles/{steamid}",
        'avatar': None,
        'profile_background': None,
        'steam_level': '—',
        'years_in_steam': None,
        'communityvisibilitystate': 1,
    }

    if not STEAM_API_KEY:
        return render(request, 'profile.html', {
            'profile_data': profile_data,
            'games': [],
            'stats': {'total_games': 0},
            'friends': [],
        })

    # 1. Інформація про профіль
    try:
        summary_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steamid}"
        response = requests.get(summary_url, timeout=10).json()
        players = response.get('response', {}).get('players', [])
        if players:
            player = players[0]
            profile_data.update({
                'personaname': player.get('personaname', profile_data['personaname']),
                'avatar': player.get('avatarfull'),
                'profileurl': player.get('profileurl'),
                'communityvisibilitystate': player.get('communityvisibilitystate', 1),
            })
            if timecreated := player.get('timecreated'):
                profile_data['years_in_steam'] = datetime.now().year - datetime.fromtimestamp(timecreated).year
    except Exception as e:
        print(f"GetPlayerSummaries error: {e}")

    is_public = profile_data['communityvisibilitystate'] == 3

    # Рівень
    if is_public:
        try:
            level_url = f"http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM_API_KEY}&steamid={steamid}"
            level = requests.get(level_url, timeout=10).json()['response'].get('player_level')
            if level is not None:
                profile_data['steam_level'] = str(level)
        except Exception:
            pass

    # Фон
    if is_public:
        profile_data['profile_background'] = steam_utils.get_steam_profile_background_url(steamid)

    # 4. Бібліотека ігор — завжди завантажуємо, якщо є хоч один запис
    games = []
    stats = {'total_games': 0}

    try:
        # Завантажуємо ВСІ записи для цього steamid
        user_games = UserGame.objects.filter(steamid=steamid)

        for ug in user_games:
            try:
                resp = requests.get(
                    f"https://store.steampowered.com/api/appdetails?appids={ug.appid}",
                    headers=headers, timeout=8
                )
                data = resp.json().get(str(ug.appid), {}).get('data', {})
                name = data.get('name', f"Гра {ug.appid}")
                header = data.get('header_image') or f"https://steamcdn-a.akamaihd.net/steam/apps/{ug.appid}/header.jpg"
            except Exception:
                name = f"Гра {ug.appid}"
                header = f"https://steamcdn-a.akamaihd.net/steam/apps/{ug.appid}/header.jpg"

            games.append({
                'appid': ug.appid,
                'name': name,
                'header_image': header,
                'playtime_forever': 0.0,
                'achievements': 0,
                'total_achievements': 0,
                'status': ug.status or 'not_played',
                'user_rating': ug.rating or 0,
                # Додаємо поле для шаблону, щоб було гарніше
                'has_content': bool(ug.rating or ug.comment.strip() or ug.status != 'not_played')
            })

        games.sort(key=sort_games)
        stats['total_games'] = len(games)

    except Exception as e:
        print(f"Помилка завантаження бібліотеки {steamid}: {e}")

    # 5. Друзі (залишаємо як було — тільки для власника)
    friends = []
    current_user_steamid = get_steamid(request.user) if request.user.is_authenticated else None
    if is_public and request.user.is_authenticated and current_user_steamid == steamid:
        # ... (твій код отримання друзів без змін)
        pass  # залиш свій код друзів тут

    return render(request, 'profile.html', {
        'profile_data': profile_data,
        'games': games,
        'stats': stats,
        'friends': friends,
        'can_see_library': True,           # завжди показуємо
        'current_user_steamid': current_user_steamid,
    })