from datetime import datetime
import requests
import re
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
    """Видаляє запис UserGame для даної гри"""
    if request.method == 'POST':
        steamid = get_steamid(request.user)
        if steamid:
            UserGame.objects.filter(user=request.user, appid=appid).delete()
    return redirect('game_detail', appid=appid)


@login_required
def update_game_status(request, appid):
    """Оновлює або створює статус, оцінку та коментар для гри"""
    if request.method == 'POST':
        status = request.POST.get('status')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        steamid = get_steamid(request.user)
        if not steamid:
            return redirect('home')

        # Якщо статус "У планах" — оцінка не дозволена
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
        # 1. Основні дані гри з Steam Store API
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
                game['technologies'] = ', '.join(tech_list) if tech_list else 'Не вказано'

        # 2. Поточний онлайн
        try:
            players_resp = requests.get(
                f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={STEAM_API_KEY}&appid={appid}",
                headers=headers,
                timeout=10
            )
            if players_resp.status_code == 200:
                game['current'] = players_resp.json().get('response', {}).get('player_count', 0)
        except Exception as e:
            print(f"Помилка отримання поточного онлайну: {e}")

        # 3. Піки + графік з SteamCharts (найнадійніше джерело)
        try:
            charts_url = f"https://steamcharts.com/app/{appid}"
            charts_resp = requests.get(charts_url, headers=headers, timeout=10)
            if charts_resp.status_code == 200:
                text = charts_resp.text

                # 24-hour peak
                peak_24h_match = re.search(r'([\d,]+)\s+24-hour peak', text, re.IGNORECASE)
                if peak_24h_match:
                    game['peak_24h'] = int(re.sub(r'[^\d]', '', peak_24h_match.group(1)))

                # All-time peak
                all_time_match = re.search(r'([\d,]+)\s+all-time peak', text, re.IGNORECASE)
                if all_time_match:
                    game['all_time_peak'] = int(re.sub(r'[^\d]', '', all_time_match.group(1)))

                # Графік за 30 днів
                json_url = f"https://steamcharts.com/app/{appid}/chart-data.json"
                json_resp = requests.get(json_url, headers=headers, timeout=10)
                if json_resp.status_code == 200:
                    chart_json = json_resp.json()
                    if chart_json:
                        for point in chart_json[-30:]:
                            ts = point[0] / 1000
                            date_str = datetime.utcfromtimestamp(ts).strftime('%d.%m')
                            chart_data['labels'].append(date_str)
                            chart_data['data'].append(point[1])

        except Exception as e:
            print(f"Помилка SteamCharts для {appid}: {e}")

        # Fallback на поточний онлайн
        if game['peak_24h'] == 0:
            game['peak_24h'] = game['current']

    except Exception as e:
        print(f"Помилка в game_detail: {e}")

    # Статуси для форми
    status_choices = [
        ('playing', 'Граю'),
        ('completed', 'Пройдено'),
        ('planned', 'У планах'),
        ('dropped', 'Відкладено'),
    ]

    # Персональні дані користувача
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