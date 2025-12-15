

from django.shortcuts import render
from django.http import Http404
import requests
from datetime import datetime
from games import steam_utils  # твоя функція для фону
from codeMain import settings
from games.aut.models import UserGame
from views.game_detail import get_steamid

STEAM_API_KEY = getattr(settings, 'SOCIAL_AUTH_STEAM_API_KEY', None)

# Єдиний порядок статусів для сортування
STATUS_PRIORITY = {
    'completed': 0,
    'playing': 1,
    'planned': 2,
    'dropped': 3,
    'not_played': 4,
}

def sort_games(game):
    """Сортування ігор: статус → оцінка (від високої) → назва"""
    status = game.get('status', 'not_played')
    rating = game.get('user_rating', 0) or 0
    name = game.get('name', '').lower()
    return (STATUS_PRIORITY.get(status, 5), -rating, name)

def profile(request, steamid: str):
    if not steamid:
        raise Http404("SteamID не вказано")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
            'is_private': True,
            'games': [],
            'stats': {'total_games': 0, 'total_hours': 0, 'completed_percentage': 0, 'total_achievements': 0},
            'friends': [],
        })

    # 1. Базова інформація профілю
    try:
        summary_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steamid}"
        response = requests.get(summary_url, timeout=10).json()
        players = response.get('response', {}).get('players', [])
        if players:
            player = players[0]
            profile_data.update({
                'personaname': player.get('personaname', profile_data['personaname']),
                'avatar': player.get('avatarfull'),
                'profileurl': player.get('profileurl', profile_data['profileurl']),
                'communityvisibilitystate': player.get('communityvisibilitystate', 1),
            })
            timecreated = player.get('timecreated')
            if timecreated:
                profile_data['years_in_steam'] = datetime.now().year - datetime.fromtimestamp(timecreated).year
    except Exception as e:
        print(f"Steam API error (GetPlayerSummaries): {e}")

    is_public = profile_data['communityvisibilitystate'] == 3

    # 2. Рівень Steam
    if is_public:
        try:
            level_url = f"http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM_API_KEY}&steamid={steamid}"
            level_response = requests.get(level_url, timeout=10).json()
            level = level_response.get('response', {}).get('player_level')
            if level is not None:
                profile_data['steam_level'] = str(level)
        except Exception as e:
            print(f"Steam API error (GetSteamLevel): {e}")

    # 3. Фон профілю
    if is_public:
        profile_data['profile_background'] = steam_utils.get_steam_profile_background_url(steamid)

    # 4. Бібліотека ігор — ТІЛЬКИ оцінені в GamingLibrary
    games = []
    stats = {
        'total_games': 0,
        'total_hours': 0.0,
        'completed_percentage': 0,
        'total_achievements': 0,
    }

    current_user_steamid = get_steamid(request.user) if request.user.is_authenticated else None

    if request.user.is_authenticated and current_user_steamid == steamid:
        try:
            user_games = UserGame.objects.filter(user=request.user)

            for ug in user_games:
                # Показуємо гру ТІЛЬКИ якщо є оцінка, статус (не not_played) або коментар
                if (ug.rating is None and
                    (ug.status is None or ug.status == 'not_played') and
                    not ug.comment.strip()):
                    continue

                # Дані гри з Steam API
                try:
                    details_resp = requests.get(
                        f"https://store.steampowered.com/api/appdetails?appids={ug.appid}",
                        headers=headers,
                        timeout=10
                    )
                    if details_resp.status_code == 200:
                        data = details_resp.json().get(str(ug.appid), {}).get('data', {})
                        name = data.get('name', f"Гра {ug.appid}")
                        header_image = data.get('header_image') or f"https://steamcdn-a.akamaihd.net/steam/apps/{ug.appid}/header.jpg"
                    else:
                        name = f"Гра {ug.appid}"
                        header_image = f"https://steamcdn-a.akamaihd.net/steam/apps/{ug.appid}/header.jpg"
                except Exception:
                    name = f"Гра {ug.appid}"
                    header_image = f"https://steamcdn-a.akamaihd.net/steam/apps/{ug.appid}/header.jpg"

                games.append({
                    'appid': ug.appid,
                    'name': name,
                    'header_image': header_image,
                    'playtime_forever': 0.0,
                    'achievements': 0,
                    'total_achievements': 0,
                    'status': ug.status or 'not_played',
                    'user_rating': ug.rating or 0,
                })

            # Сортування ігор
            games.sort(key=sort_games)

            stats['total_games'] = len(games)

        except Exception as e:
            print(f"Помилка отримання бібліотеки: {e}")

    # 5. Друзі з Steam
    friends = []
    if is_public and request.user.is_authenticated and current_user_steamid == steamid:
        try:
            friends_url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={STEAM_API_KEY}&steamid={steamid}&relationship=friend"
            friends_resp = requests.get(friends_url, timeout=10).json()
            friend_list = friends_resp.get('friendslist', {}).get('friends', [])

            if friend_list:
                friend_ids = ','.join([f['steamid'] for f in friend_list[:50]])

                summaries_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={friend_ids}"
                summaries_resp = requests.get(summaries_url, timeout=10).json()
                players = summaries_resp.get('response', {}).get('players', [])

                for player in players:
                    state = "Оффлайн"
                    persona_state = player.get('personastate', 0)
                    if persona_state == 1:
                        state = "Онлайн"
                    elif persona_state in [2, 3]:
                        state = "В грі"
                    elif persona_state == 5:
                        state = "Хоче обмінятись"
                    elif persona_state == 6:
                        state = "Хоче грати"

                    friends.append({
                        'steamid': player['steamid'],
                        'personaname': player.get('personaname', 'Невідомий'),
                        'avatar': player.get('avatarfull'),
                        'profileurl': player.get('profileurl'),
                        'state': state,
                    })

        except Exception as e:
            print(f"Помилка отримання друзів Steam: {e}")

    return render(request, 'profile.html', {
        'profile_data': profile_data,
        'is_private': not is_public,
        'games': games,
        'stats': stats,
        'friends': friends,
    })