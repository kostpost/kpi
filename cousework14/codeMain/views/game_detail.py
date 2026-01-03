from datetime import datetime
import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from games.aut.models import UserGame
from games.aut.models import UserList


STEAM_API_KEY = "27947505395A6AA7FDAB420DCF4A4C52"


def get_steamid(user):
    """Повертає SteamID користувача з соціальної авторизації"""
    if user.is_authenticated:
        try:
            return user.social_auth.get(provider='steam').uid
        except Exception:
            return None
    return None


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def delete_game_status(request, appid):
    if request.method == 'POST':
        UserGame.objects.filter(user=request.user, appid=appid).delete()
    return redirect('game_detail', appid=appid)


# games/views.py

@login_required
def update_game_status(request, appid):
    if request.method == 'POST':
        # Отримуємо всі можливі поля
        status = request.POST.get('status')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        list_id = request.POST.get('list_id')
        new_list_name = request.POST.get('new_list')

        # Знаходимо або створюємо запис
        user_game, created = UserGame.objects.get_or_create(
            user=request.user,
            appid=appid
        )

        # Оновлюємо ТІЛЬКИ ті поля, які прийшли
        update_fields = {}
        if status is not None:
            update_fields['status'] = status if status and status != 'not_played' else None
        if rating is not None:
            update_fields['rating'] = int(rating) if rating and status != 'planned' else None
        if comment:
            update_fields['comment'] = comment

        if update_fields:
            for field, value in update_fields.items():
                setattr(user_game, field, value)
            user_game.save(update_fields=update_fields.keys())

        # Обробка списків (незалежно від відгуку)
        if list_id:
            try:
                user_list = UserList.objects.get(id=list_id, user=request.user)
                user_game.lists.add(user_list)
            except UserList.DoesNotExist:
                pass

        elif new_list_name:
            new_list_name = new_list_name.strip()
            if new_list_name:
                user_list, _ = UserList.objects.get_or_create(
                    user=request.user,
                    name=new_list_name
                )
                user_game.lists.add(user_list)

        return redirect('game_detail', appid=appid)

    return redirect('home')


# Новий view — для додавання/видалення гри зі списку (якщо потрібно)
@login_required
def manage_game_in_list(request, appid, list_id):
    if request.method == 'POST':
        action = request.POST.get('action')  # 'add' або 'remove'
        user_game = get_object_or_404(UserGame, user=request.user, appid=appid)
        user_list = get_object_or_404(UserList, id=list_id, user=request.user)

        if action == 'add':
            user_game.lists.add(user_list)
        elif action == 'remove':
            user_game.lists.remove(user_list)

    return redirect('game_detail', appid=appid)


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
        user_game = UserGame.objects.filter(user=request.user, appid=appid).first()
        has_review = bool(user_game and (
                user_game.rating is not None or
                user_game.comment.strip() or
                (user_game.status and user_game.status != 'not_played')
        ))

    friends_reviews = []

    if request.user.is_authenticated:
        try:
            # Друзі поточного користувача
            friends = request.user.profile.friends.values_list('user__id', flat=True)

            # Відгуки друзів про цю гру (якщо є)
            friends_reviews = UserGame.objects.filter(
                user__id__in=friends,
                appid=appid,
            ).exclude(
                comment__isnull=True,
                rating__isnull=True,
                status='not_played'
            ).select_related('user').order_by('-updated_at')[:10]  # обмежимо 10 останніми
        except Exception as e:
            print(f"Помилка завантаження відгуків друзів для {appid}: {e}")


    return render(request, 'game_detail.html', {
        'game': game,
        'user_game': user_game or None,
        'status_choices': status_choices,
        'chart_data': chart_data,
        'has_review': has_review,
        'friends_reviews': friends_reviews,
    })