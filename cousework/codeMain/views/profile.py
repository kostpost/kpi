

from django.shortcuts import render
from django.http import Http404
import requests
from datetime import datetime
from games import steam_utils  # твоя функція для фону
from codeMain import settings

STEAM_API_KEY = getattr(settings, 'SOCIAL_AUTH_STEAM_API_KEY', None)

status_order = {'completed': 0, 'playing': 1, 'dropped': 2}  # 0 — найвище

def sort_key(game):
    status = game.get('status', 'not_played')
    return status_order.get(status, 3), game['name'].lower()  # 3 — найнижче

def profile(request, steamid: str):
    if not steamid:
        raise Http404("SteamID не вказано")

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
            'stats': {},
        })

    # 1. Базова інформація
    summary_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steamid}"
    try:
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
            # Роки в Steam
            timecreated = player.get('timecreated')
            if timecreated:
                profile_data['years_in_steam'] = datetime.now().year - datetime.fromtimestamp(timecreated).year
    except Exception as e:
        print(f"Steam API error (GetPlayerSummaries): {e}")

    is_public = profile_data['communityvisibilitystate'] == 3

    # 2. Рівень Steam
    if is_public:
        level_url = f"http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM_API_KEY}&steamid={steamid}"
        try:
            level_response = requests.get(level_url, timeout=10).json()
            level = level_response.get('response', {}).get('player_level')
            if level is not None:
                profile_data['steam_level'] = str(level)
        except Exception as e:
            print(f"Steam API error (GetSteamLevel): {e}")

    # 3. Фон
    if is_public:
        profile_data['profile_background'] = steam_utils.get_steam_profile_background_url(steamid)

    # 4. Бібліотека ігор (тільки якщо публічна)
    games = []
    stats = {
        'total_games': 0,
        'total_hours': 0,
        'completed_percentage': 0,
        'total_achievements': 0,
    }

    if is_public:
        # GetOwnedGames — список ігор + години
        owned_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steamid}&include_appinfo=true&include_played_free_games=true"
        try:
            owned_response = requests.get(owned_url, timeout=10).json()
            game_list = owned_response.get('response', {}).get('games', [])
            stats['total_games'] = len(game_list)

            for game in game_list:
                appid = game['appid']
                name = game.get('name', 'Unknown')
                playtime = game.get('playtime_forever', 0) / 60  # години
                stats['total_hours'] += playtime

                # Обкладинка
                header_image = f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg"

                # Досягнення (відсоток)
                achievements = 0
                total_achievements = 0
                try:
                    ach_url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?key={STEAM_API_KEY}&steamid={steamid}&appid={appid}"
                    ach_response = requests.get(ach_url, timeout=15).json()
                    achs = ach_response.get('playerstats', {}).get('achievements', [])
                    total_achievements = len(achs)
                    achievements = sum(1 for a in achs if a.get('achieved') == 1)
                except:
                    pass

                stats['total_achievements'] += achievements

                # Статус проходження (простий алгоритм)
                status = 'Не грав'
                if playtime > 0:
                    status = 'Граю'
                if achievements > 0 and achievements / max(total_achievements, 1) > 0.9:
                    status = 'Пройдено'

                games.append({
                    'appid': appid,
                    'name': name,
                    'header_image': header_image,
                    'playtime_forever': round(playtime, 1),
                    'achievements': achievements,
                    'total_achievements': total_achievements,
                    'status': status.lower().replace(' ', '_'),  # для класу в шаблоні
                    'user_rating': 5,  # Заглушка, можна зберігати в БД
                })

            # % пройдених ігор (якщо є досягнення)
            if stats['total_games'] > 0:
                stats['completed_percentage'] = round((sum(1 for g in games if g['status'] == 'completed') / stats['total_games']) * 100)

        except Exception as e:
            print(f"Steam API error (GetOwnedGames): {e}")

    # Округлюємо години
    stats['total_hours'] = round(stats['total_hours'], 1)

    games.sort(key=sort_key)

    return render(request, 'profile.html', {
        'profile_data': profile_data,
        'is_private': not is_public,
        'games': games,
        'stats': stats,
    })