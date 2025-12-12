# steam_utils.py
import akamai
import requests
from django.conf import settings
from typing import Dict, Optional

# Ключ API можна винести в settings.py
STEAM_API_KEY = getattr(settings, 'SOCIAL_AUTH_STEAM_API_KEY', None)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_current_players(appid: int) -> int:
    """Повертає поточну кількість гравців"""
    try:
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={STEAM_API_KEY}&appid={appid}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('response', {}).get('player_count', 0)
    except Exception as e:
        print(f"Помилка отримання поточного онлайну для {appid}: {e}")
    return 0


def get_peak_24h(appid: int) -> int:
    """Повертає пік за 24 години з офіційного API (як у home view)"""
    try:
        url = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            ranks = resp.json().get('response', {}).get('ranks', [])
            for entry in ranks:
                if entry['appid'] == appid:
                    return entry.get('peak_in_game', 0)
    except Exception as e:
        print(f"Помилка отримання 24h peak для {appid}: {e}")
    return 0


def get_all_time_peak_and_chart(appid: int) -> Tuple[int, Dict[str, List]]:
    """
    Повертає:
    - all_time_peak (int)
    - chart_data = {'labels': [...], 'data': [...]}
    """
    all_time_peak = 0
    chart_data = {'labels': [], 'data': []}

    try:
        charts_url = f"https://steamcharts.com/app/{appid}"
        resp = requests.get(charts_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            text = resp.text

            # All-time peak: число перед "all-time peak"
            match = re.search(r'([\d,]+)\s+all-time peak', text, re.IGNORECASE)
            if match:
                all_time_peak = int(re.sub(r'[^\d]', '', match.group(1)))

            # Графік за 30 днів з JSON
            json_url = f"https://steamcharts.com/app/{appid}/chart-data.json"
            json_resp = requests.get(json_url, headers=HEADERS, timeout=10)
            if json_resp.status_code == 200:
                chart_json = json_resp.json()
                if chart_json:
                    for point in chart_json[-30:]:
                        ts = point[0] / 1000
                        date_str = datetime.utcfromtimestamp(ts).strftime('%d.%m')
                        chart_data['labels'].append(date_str)
                        chart_data['data'].append(point[1])

    except Exception as e:
        print(f"Помилка отримання all-time peak або графіка для {appid}: {e}")

    return all_time_peak, chart_data

def get_steam_profile_data(steamid: str) -> Dict[str, Optional[str]]:
    """
    Повертає актуальні дані профілю Steam за steamid.

    Повертає словник з ключами:
        - personaname
        - avatarfull (повнорозмірна аватарка)
        - profileurl
        - steam_level (або '—' якщо приватний або помилка)
        - communityvisibilitystate (1 або 3)

    Якщо API ключ не налаштований або сталася помилка — повертає базові дані.
    """
    if not STEAM_API_KEY:
        return {
            'personaname': 'Невідомий користувач',
            'avatarfull': None,
            'profileurl': f"https://steamcommunity.com/profiles/{steamid}",
            'steam_level': '—',
            'communityvisibilitystate': 1,
        }

    profile_data = {
        'personaname': 'Невідомий користувач',
        'avatarfull': None,
        'profileurl': f"https://steamcommunity.com/profiles/{steamid}",
        'steam_level': '—',
        'communityvisibilitystate': 1,
    }

    # 1. GetPlayerSummaries — базова інформація + аватарка + visibility
    summary_url = (
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={STEAM_API_KEY}&steamids={steamid}"
    )

    try:
        response = requests.get(summary_url, timeout=10).json()
        players = response.get('response', {}).get('players', [])
        if players:
            player = players[0]
            profile_data.update({
                'personaname': player.get('personaname', profile_data['personaname']),
                'avatarfull': player.get('avatarfull'),
                'profileurl': player.get('profileurl', profile_data['profileurl']),
                'communityvisibilitystate': player.get('communityvisibilitystate', 1),
            })
        else:
            return profile_data  # Профіль не знайдено
    except Exception as e:
        print(f"Steam API error (GetPlayerSummaries): {e}")
        return profile_data

    # Якщо профіль приватний — не запитуємо рівень
    if profile_data['communityvisibilitystate'] != 3:
        return profile_data

    # 2. GetSteamLevel — тільки для публічних профілів
    level_url = (
        f"http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/"
        f"?key={STEAM_API_KEY}&steamid={steamid}"
    )
    try:
        level_response = requests.get(level_url, timeout=10).json()
        level = level_response.get('response', {}).get('player_level')
        if level is not None:
            profile_data['steam_level'] = str(level)
    except Exception as e:
        print(f"Steam API error (GetSteamLevel): {e}")

    return profile_data


import re
import requests
from typing import Optional

def get_steam_profile_background_url(steamid: str) -> Optional[str]:
    """
    Витягує URL статичного jpg-постера кастомного фону профілю Steam.
    Для відео-фонів використовує атрибут poster з <video> (офіційний постер Steam).
    Працює тільки для публічних профілів.
    """
    profile_url = f"https://steamcommunity.com/profiles/{steamid}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }
        response = requests.get(profile_url, headers=headers, timeout=10)
        response.raise_for_status()

        text = response.text

        poster_pattern = r'<video[^>]*poster=["\']([^"\']+\.jpg)["\']'
        poster_match = re.search(poster_pattern, text)
        if poster_match:
            jpg_url = poster_match.group(1)
            jpg_url = re.sub(r'\?.*$', '', jpg_url)  # Очищаємо параметри
            print(f"DEBUG: Знайдено poster jpg: {jpg_url}")
            return jpg_url

        video_pattern = r'<source\s+src="([^"]+\.(?:webm|mp4))"'
        video_match = re.search(video_pattern, text)
        if video_match:
            video_url = video_match.group(1)
            video_url = re.sub(r'\?.*$', '', video_url)
            # Замінюємо розширення на .jpg (працює для багатьох анімованих фонів)
            jpg_url = video_url.rsplit('.', 1)[0] + '.jpg'
            print(f"DEBUG: Відео знайдено {video_url}, fallback jpg: {jpg_url}")
            return jpg_url

        img_pattern = r'background-image\s*:\s*url\(["\']?(https?://[^"\')]+\.(?:jpg|png))["\']?\)'
        img_match = re.search(img_pattern, text)
        if img_match:
            jpg_url = img_match.group(1)
            jpg_url = re.sub(r'\?.*$', '', jpg_url)
            print(f"DEBUG: Знайдено статичний фон: {jpg_url}")
            return jpg_url

    except requests.RequestException as e:
        print(f"Помилка запиту до Steam профілю {steamid}: {e}")
    except Exception as e:
        print(f"Помилка парсингу фону для {steamid}: {e}")

    print(f"DEBUG: Фон не знайдено для {steamid}")
    return None