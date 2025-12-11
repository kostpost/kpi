import requests
from django.shortcuts import render

STEAM_API_KEY = "27947505395A6AA7FDAB420DCF4A4C52"


def game_detail(request, appid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    game = {
        'appid': appid,
        'name': 'Завантаження...',
        'header_image': 'https://via.placeholder.com/460x215?text=Loading...',
        'developer': 'Невідомо',
        'publisher': 'Невідомо',
        'platforms': 'Невідомо',
        'release_date': 'Невідомо',
        'current': 0,
        'review_count': 0,
        'review_percentage': None,  # None = немає даних
        'genres': 'Невідомо',
    }

    try:
        # 1. Основні деталі гри
        response = requests.get(
            f"https://store.steampowered.com/api/appdetails?appids={appid}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json().get(str(appid), {}).get('data', {})
            if data:
                game.update({
                    'name': data.get('name', 'Невідома гра'),
                    'header_image': data.get('header_image'),
                    'developer': ', '.join(data.get('developers', ['Невідомо'])),
                    'publisher': ', '.join(data.get('publishers', ['Невідомо'])),
                    'release_date': data.get('release_date', {}).get('date', 'Невідомо'),
                    'genres': ', '.join([g['description'] for g in data.get('genres', [])]) or 'Невідомо',
                })

                # Платформи
                plats = data.get('platforms', {})
                plat_list = []
                if plats.get('windows'): plat_list.append('Windows')
                if plats.get('mac'): plat_list.append('Mac')
                if plats.get('linux'): plat_list.append('Linux')
                game['platforms'] = ', '.join(plat_list) or 'Невідомо'

                # Відгуки — спроба взяти з appdetails (часто є!)
                if 'steam_appid' in data:
                    # Деякі ігри мають review_summary в самому appdetails
                    if data.get('review_type'):
                        # Іноді є прямі поля (нестандартно, але буває)
                        pass
                    # Але найчастіше — потрібно окремий запит

                last_update = 'Unknown'
                if 'last_modified' in data:
                    import time
                    last_update = time.strftime('%d.%m.%Y', time.localtime(data['last_modified']))
                game['last_update'] = last_update

                # Technologies (визначаємо за категоріями, двигунами тощо)
                tech_list = []
                categories = data.get('categories', [])
                for cat in categories:
                    desc = cat.get('description', '').lower()
                    if 'source' in desc: tech_list.append('Source Engine')
                    if 'unreal' in desc: tech_list.append('Unreal Engine')
                    if 'unity' in desc: tech_list.append('Unity')
                    if 'vr ' in desc or 'steamvr' in data: tech_list.append('VR Support')
                    if 'controller' in desc: tech_list.append('Controller Support')
                    if 'workshop' in desc: tech_list.append('Steam Workshop')

                # Якщо нічого не знайшли — шукаємо в metacritic або описі (не завжди)
                if not tech_list:
                    if data.get('metacritic'):
                        tech_list.append('Metacritic Integration')
                    if data.get('dlc'):
                        tech_list.append('DLC Support')

                game['technologies'] = ', '.join(tech_list) if tech_list else 'Not specified'

        # 2. Окремий запит на відгуки (Steam Storefront API — працює без ключа!)
        review_url = f"https://store.steampowered.com/appreviews/{appid}"
        params = {
            'json': 1,
            'language': 'all',
            'review_type': 'all',
            'purchase_type': 'all',
            'filter': 'summary',
            'day_range': 0,  # всі відгуки
        }
        review_resp = requests.get(review_url, headers=headers, params=params, timeout=10)
        if review_resp.status_code == 200:
            review_data = review_resp.json()
            summary = review_data.get('query_summary', {})
            total_reviews = summary.get('total_reviews', 0)
            positive_reviews = summary.get('total_positive', 0)

            if total_reviews > 0:
                percentage = round((positive_reviews / total_reviews) * 100)
                game['review_count'] = total_reviews
                game['review_percentage'] = percentage
            # Якщо 0 — залишаємо None

        # 3. Актуальний онлайн
        players_resp = requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={STEAM_API_KEY}&appid={appid}",
            headers=headers,
            timeout=10
        )
        if players_resp.status_code == 200:
            game['current'] = players_resp.json().get('response', {}).get('player_count', 0)

    except Exception as e:
        print("Помилка в game_detail:", e)

    # ... попередній код ...

    # Після отримання актуального онлайну додай:
    try:
        # 24h peak та all-time peak з SteamCharts API (публічний, без ключа)
        charts_url = f"https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
        charts_resp = requests.get(charts_url, headers=headers, timeout=10)
        if charts_resp.status_code == 200:
            ranks = charts_resp.json().get('response', {}).get('ranks', [])
            for entry in ranks:
                if entry['appid'] == int(appid):
                    game['peak_24h'] = entry.get('peak_in_game', 0)
                    break

        # All-time peak з steamcharts.com (парсимо простий JSON)
        steamcharts_resp = requests.get(f"https://steamcharts.com/app/{appid}/chart-data.json", timeout=10)
        if steamcharts_resp.status_code == 200:
            chart_data = steamcharts_resp.json()
            if chart_data:
                # Останній елемент — це all-time peak
                peaks = [point[1] for point in chart_data]
                max_peak = max(peaks)
                max_index = peaks.index(max_peak)
                timestamp = chart_data[max_index][0] / 1000  # ms → sec
                from datetime import datetime
                peak_date = datetime.utcfromtimestamp(timestamp).strftime('%d.%m.%Y')
                game['all_time_peak'] = max_peak
                game['all_time_peak_date'] = peak_date

    except Exception as e:
        print("Помилка отримання піків:", e)

    return render(request, 'game_detail.html', {'game': game})