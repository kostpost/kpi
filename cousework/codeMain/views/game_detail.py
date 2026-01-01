from datetime import datetime
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from games.aut.models import UserGame

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
    if request.method == 'POST':
        steamid = get_steamid(request.user)
        if steamid:
            UserGame.objects.filter(user=request.user, appid=appid).delete()
    return redirect('game_detail', appid=appid)


@login_required
def update_game_status(request, appid):
    if request.method == 'POST':
        status = request.POST.get('status')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        steamid = get_steamid(request.user)
        if not steamid:
            return redirect('home')

        if status == 'planned':
            rating = None

        UserGame.objects.update_or_create(
            user=request.user,
            steamid=steamid,
            appid=appid,
            defaults={
                'status': status if status and status != 'not_played' else None,
                'rating': int(rating) if rating and status != 'planned' else None,
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
        'technologies': 'Не вказано',
        'peak_24h': 0,
        'all_time_peak': 0,
    }

    chart_data = {'labels': [], 'data': []}

    try:
        # 1. Основні дані гри
        resp = requests.get(
            f"https://store.steampowered.com/api/appdetails?appids={appid}",
            headers=headers, timeout=10
        )
        if resp.status_code == 200:
            data = resp.json().get(str(appid), {}).get('data', {})
            if data:
                game.update({
                    'name': data.get('name', 'Невідома гра'),
                    'header_image': data.get('header_image'),
                    'developer': ', '.join(data.get('developers', ['Невідомо'])),
                    'publisher': ', '.join(data.get('publishers', ['Невідомо'])),
                    'release_date': data.get('release_date', {}).get('date', 'Невідомо'),
                    'genres': ', '.join(g['description'] for g in data.get('genres', [])) or 'Невідомо',
                })

                plats = data.get('platforms', {})
                game['platforms'] = ', '.join(p for p in ['Windows', 'Mac', 'Linux'] if plats.get(p.lower())) or 'Невідомо'

                tech_list = []
                for cat in data.get('categories', []):
                    desc = cat.get('description', '').lower()
                    if 'source' in desc: tech_list.append('Source Engine')
                    if 'unreal' in desc: tech_list.append('Unreal Engine')
                    if 'unity' in desc: tech_list.append('Unity')
                    if 'vr ' in desc: tech_list.append('VR Support')
                    if 'controller' in desc: tech_list.append('Controller Support')
                    if 'workshop' in desc: tech_list.append('Steam Workshop')
                game['technologies'] = ', '.join(tech_list) if tech_list else 'Не вказано'

        # 2. Поточний онлайн + пік 24h — з того ж API, що й на головній
        try:
            most_played_resp = requests.get(
                "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/",
                headers=headers, timeout=8
            )
            if most_played_resp.status_code == 200:
                ranks = most_played_resp.json().get('response', {}).get('ranks', [])
                for rank in ranks:
                    if str(rank.get('appid')) == appid:
                        game['current'] = rank.get('concurrent_in_game', 0)
                        game['peak_24h'] = rank.get('peak_in_game', 0)
                        break

            # Якщо не знайшли в топі → fallback на класичний ендпоінт
            if game['current'] == 0:
                players_resp = requests.get(
                    f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={STEAM_API_KEY}&appid={appid}",
                    headers=headers, timeout=8
                )
                if players_resp.status_code == 200:
                    game['current'] = players_resp.json().get('response', {}).get('player_count', 0)

            # Якщо пік все ще 0 → використовуємо поточний онлайн
            if game['peak_24h'] == 0:
                game['peak_24h'] = game['current']

        except Exception as e:
            print(f"Помилка SteamChartsService для {appid}: {e}")
            game['current'] = 0
            game['peak_24h'] = 0

        # 3. Графік (залишаємо спробу, але з надійними перевірками)
        try:
            json_url = f"https://steamcharts.com/app/{appid}/chart-data.json"
            json_resp = requests.get(json_url, headers=headers, timeout=12)
            if json_resp.status_code == 200:
                chart_json = json_resp.json()
                if isinstance(chart_json, list) and len(chart_json) > 0:
                    for point in chart_json[-30:]:
                        ts = point[0] / 1000
                        date_str = datetime.utcfromtimestamp(ts).strftime('%d.%m')
                        chart_data['labels'].append(date_str)
                        chart_data['data'].append(point[1])
        except Exception as e:
            print(f"Помилка графіка SteamCharts {appid}: {e}")

    except Exception as e:
        print(f"Загальна помилка game_detail {appid}: {e}")

    # Статуси для форми
    status_choices = [
        ('playing', 'Граю'),
        ('completed', 'Пройдено'),
        ('planned', 'У планах'),
        ('dropped', 'Відкладено'),
    ]

    user_game = None
    has_review = False

    if request.user.is_authenticated:
        steamid = get_steamid(request.user)
        if steamid:
            user_game = UserGame.objects.filter(user=request.user, appid=appid).first()
            if user_game:
                if (user_game.rating is not None or
                    user_game.comment.strip() or
                    (user_game.status and user_game.status != 'not_played')):
                    has_review = True

    return render(request, 'game_detail.html', {
        'game': game,
        'user_game': user_game or None,
        'status_choices': status_choices,
        'chart_data': chart_data,
        'has_review': has_review,
    })