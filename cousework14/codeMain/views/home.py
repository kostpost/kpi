import requests
from django.shortcuts import render
from django.views.decorators.cache import cache_page

STEAM_API_KEY = "27947505395A6AA7FDAB420DCF4A4C52"

def home(request):
    most_played = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(
            "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            ranks = data.get('response', {}).get('ranks', [])

            # Сортуємо за піком за 24 години і беремо топ-10
            sorted_games = sorted(ranks, key=lambda x: x.get('peak_in_game', 0), reverse=True)[:10]

            for game in sorted_games:
                appid = str(game['appid'])

                # Назва гри
                details_response = requests.get(
                    f"https://store.steampowered.com/api/appdetails?appids={appid}",
                    headers=headers,
                    timeout=10
                )
                name = 'Unknown Game'
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    game_details = details_data.get(appid, {}).get('data', {})
                    name = game_details.get('name', 'Unknown Game')

                # Актуальний онлайн
                current = game.get('concurrent_in_game', 0)
                players_response = requests.get(
                    f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={STEAM_API_KEY}&appid={appid}",
                    headers=headers,
                    timeout=10
                )
                if players_response.status_code == 200:
                    players_data = players_response.json()
                    fetched_current = players_data.get('response', {}).get('player_count', 0)
                    if fetched_current > 0:
                        current = fetched_current

                most_played.append({
                    'name': name,
                    'current': current,
                    'peak': game.get('peak_in_game', 0),
                    'appid': appid,
                    'image': f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg",
                })

    except Exception as e:
        print("Помилка запиту:", str(e))

    context = {
        'most_played': most_played,
        'trending': [],
        'popular_releases': [],
        'hot_releases': [],
    }
    return render(request, 'home.html', context)
