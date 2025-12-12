from datetime import datetime

import ch
import requests
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from games.aut.models import UserGame
import re
import time

STEAM_API_KEY = "27947505395A6AA7FDAB420DCF4A4C52"


def get_steamid(user):
    """Повертає SteamID користувача з соціальної авторизації"""
    if user.is_authenticated:
        try:
            return user.social_auth.get(provider='steam').uid
        except Exception:
            return None
    return None


@login_required
def delete_game_status(request, appid):
    """Видаляє запис UserGame для даної гри (відгук, статус, оцінка тощо)"""
    if request.method == 'POST':
        steamid = get_steamid(request.user)
        if steamid:
            UserGame.objects.filter(user=request.user, appid=appid).delete()
    return redirect('game_detail', appid=appid)


@login_required
def update_game_status(request, appid):
    """Оновлює або створює запис про гру в бібліотеці користувача"""
    if request.method == 'POST':
        status = request.POST.get('status')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        steamid = get_steamid(request.user)
        if not steamid:
            return redirect('home')

        UserGame.objects.update_or_create(
            user=request.user,
            steamid=steamid,
            appid=appid,
            defaults={
                'status': status if status and status != 'not_played' else None,
                'rating': int(rating) if rating else None,
                'comment': comment if comment else '',
            }
        )
        return redirect('game_detail', appid=appid)

    return redirect('home')


def game_detail(request, appid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        'genres': 'Невідомо',
        'technologies': 'Not specified',
        'peak_24h': 0,
        'all_time_peak': 0,
        'all_time_peak_date': 'Unknown',
    }

    chart_data = {'labels': [], 'data': []}

    try:
        # 1. Дані з Steam Store API
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

                # Технології
                tech_list = []
                for cat in data.get('categories', []):
                    desc = cat.get('description', '').lower()
                    if 'source' in desc: tech_list.append('Source Engine')
                    if 'unreal' in desc: tech_list.append('Unreal Engine')
                    if 'unity' in desc: tech_list.append('Unity')
                    if 'vr ' in desc: tech_list.append('VR Support')
                    if 'controller' in desc: tech_list.append('Controller Support')
                    if 'workshop' in desc: tech_list.append('Steam Workshop')
                game['technologies'] = ', '.join(tech_list) if tech_list else 'Not specified'

        # 2. Відгуки Steam
        review_resp = requests.get(
            f"https://store.steampowered.com/appreviews/{appid}",
            headers=headers,
            params={'json': 1, 'language': 'all', 'filter': 'summary'},
            timeout=10
        )
        if review_resp.status_code == 200:
            summary = review_resp.json().get('query_summary', {})
            total = summary.get('total_reviews', 0)
            positive = summary.get('total_positive', 0)
            if total > 0:
                game['review_percentage'] = round((positive / total) * 100)

        # 3. Поточний онлайн
        players_resp = requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={STEAM_API_KEY}&appid={appid}",
            headers=headers,
            timeout=10
        )
        if players_resp.status_code == 200:
            game['current'] = players_resp.json().get('response', {}).get('player_count', 0)

        # 4. Піки онлайн: 24h peak — як у home, all-time peak з SteamCharts
        try:
            # ───── 24h peak — точно як у твоєму home (з офіційного API) ─────
            most_played_resp = requests.get(
                "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/",
                headers=headers,
                timeout=10
            )
            if most_played_resp.status_code == 200:
                ranks = most_played_resp.json().get('response', {}).get('ranks', [])
                for entry in ranks:
                    if entry['appid'] == int(appid):
                        game['peak_24h'] = entry.get('peak_in_game', game['current'])
                        break  # знайшли — виходимо

            # ───── All-time peak + графік з SteamCharts ─────
            charts_url = f"https://steamcharts.com/app/{appid}"
            charts_resp = requests.get(charts_url, headers=headers, timeout=10)
            if charts_resp.status_code == 200:
                text = charts_resp.text

                # All-time peak: число ПЕРЕД фразою "all-time peak" (наприклад: "1,818,368 all-time peak")
                all_time_match = re.search(r'([\d,]+)\s+all-time peak', text, re.IGNORECASE)
                if all_time_match:
                    game['all_time_peak'] = int(re.sub(r'[^\d]', '', all_time_match.group(1)))

                # Графік за 30 днів (JSON — найнадійніше)
                json_url = f"https://steamcharts.com/app/{appid}/chart-data.json"
                json_resp = requests.get(json_url, headers=headers, timeout=10)
                if json_resp.status_code == 200:
                    chart_json = json_resp.json()
                    if chart_json:
                        chart_data['labels'] = []
                        chart_data['data'] = []
                        for point in chart_json[-30:]:
                            ts = point[0] / 1000
                            date_str = datetime.utcfromtimestamp(ts).strftime('%d.%m')
                            chart_data['labels'].append(date_str)
                            chart_data['data'].append(point[1])

        except Exception as e:
            print(f"Помилка при отриманні піків для appid {appid}: {e}")

        # Fallback: якщо нічого не знайшли — показуємо поточний онлайн
        if game['peak_24h'] == 0:
            game['peak_24h'] = game['current']
        if game['all_time_peak'] == 0:
            game['all_time_peak'] = game['current']

        # Якщо дати немає — залишаємо "Unknown" (як у твоєму початковому словнику)
        # game['all_time_peak_date'] залишається 'Unknown'

        # if not chart_data['labels']:  # fallback
        #     chart_data['labels'] = ['Сьогодні', 'Вчора', 'Тиждень тому']
        #     chart_data['data'] = [game['current'], game['peak_24h'] or 0, game['all_time_peak'] or 0]

    except Exception as e:
        print(f"Помилка в game_detail: {e}")

    # --- Персональні дані користувача ---
    status_choices = [
        ('completed', 'Пройдено'),
        ('playing', 'Граю'),
        ('dropped', 'Відкладено'),  # або 'Покинуто' — як у тебе в шаблоні
        ('not_played', 'Не грав'),
    ]

    user_game = None
    has_review = False

    if request.user.is_authenticated:
        steamid = get_steamid(request.user)
        if steamid:
            user_game = UserGame.objects.filter(user=request.user, appid=appid).first()

            # Тепер безпечно перевіряємо, чи є реальний відгук
            if user_game:
                if (user_game.rating is not None or
                    user_game.comment.strip() or
                    (user_game.status and user_game.status != 'not_played')):
                    has_review = True

    return render(request, 'game_detail.html', {
        'game': game,
        'user_game': user_game,  # може бути None — шаблон це обробляє
        'status_choices': status_choices,
        'chart_data': chart_data,
        'has_review': has_review,
    })



























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