from datetime import datetime
import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from games.aut.models import UserGame, UserList

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"


# Детальна сторінка гри з даними з RAWG + статус користувача + відгуки друзів
def game_detail(request, rawg_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    # Початковий шаблон даних гри (показується під час завантаження)
    game = {
        'rawg_id': rawg_id,
        'name': 'Завантаження...',
        'background_image': None,
        'description': 'Опис завантажується...',
        'developer': 'Невідомо',
        'publisher': 'Невідомо',
        'platforms': 'Невідомо',
        'released': 'Невідомо',
        'genres': 'Невідомо',
        'rating': None,
        'metacritic': None,
        'website': None,
        'screenshots': [],
        'trailers': [],
    }

    try:
        # Основна інформація про гру
        url = f"https://api.rawg.io/api/games/{rawg_id}?key={RAWG_API_KEY}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            game.update({
                'name': data.get('name', 'Невідома гра'),
                'background_image': data.get('background_image'),
                'description': data.get('description_raw') or data.get('description', ''),
                'developer': ', '.join(d.get('name', '') for d in data.get('developers', [])) or 'Невідомо',
                'publisher': ', '.join(p.get('name', '') for p in data.get('publishers', [])) or 'Невідомо',
                'released': data.get('released', 'Невідомо'),
                'genres': ', '.join(g.get('name', '') for g in data.get('genres', [])) or 'Невідомо',
                'platforms': ', '.join(p['platform'].get('name', '') for p in data.get('parent_platforms', [])) or 'Невідомо',
                'rating': data.get('rating'),
                'metacritic': data.get('metacritic'),
                'website': data.get('website'),
            })

        # Завантаження скріншотів (максимум 6)
        ss_url = f"https://api.rawg.io/api/games/{rawg_id}/screenshots?key={RAWG_API_KEY}"
        ss_resp = requests.get(ss_url, headers=headers, timeout=5)
        if ss_resp.status_code == 200:
            game['screenshots'] = [item['image'] for item in ss_resp.json().get('results', [])[:6]]

        # Завантаження трейлерів (максимум 3)
        movies_url = f"https://api.rawg.io/api/games/{rawg_id}/movies?key={RAWG_API_KEY}"
        movies_resp = requests.get(movies_url, headers=headers, timeout=5)
        if movies_resp.status_code == 200:
            game['trailers'] = movies_resp.json().get('results', [])[:3]

    except Exception as e:
        print(f"Помилка завантаження даних RAWG для ID {rawg_id}: {e}")

    # Варіанти статусів для вибору
    status_choices = [
        ('playing', 'Граю'),
        ('completed', 'Пройдено'),
        ('planned', 'У планах'),
        ('dropped', 'Відкладено'),
    ]

    user_game = None
    has_review = False

    if request.user.is_authenticated:
        # Статус та відгук поточного користувача
        user_game = UserGame.objects.filter(user=request.user, rawg_id=rawg_id).first()
        has_review = bool(user_game and (
            user_game.rating is not None or
            (user_game.comment or '').strip() or
            (user_game.status and user_game.status != 'not_played')
        ))

    friends_reviews = []

    if request.user.is_authenticated:
        try:
            # Відгуки друзів (останні 10, з виключенням порожніх)
            friends_ids = request.user.profile.friends.values_list('user__id', flat=True)
            friends_reviews = UserGame.objects.filter(
                user__id__in=friends_ids,
                rawg_id=rawg_id,
            ).exclude(
                Q(comment__isnull=True) | Q(comment=''),
                rating__isnull=True,
                status='not_played'
            ).select_related('user').order_by('-updated_at')[:10]
        except Exception as e:
            print(f"Помилка завантаження відгуків друзів для {rawg_id}: {e}")

    return render(request, 'game_detail.html', {
        'game': game,
        'user_game': user_game,
        'status_choices': status_choices,
        'has_review': has_review,
        'friends_reviews': friends_reviews,
    })


# Видаляє запис про гру у користувача (статус, оцінку, коментар)
@login_required
def delete_game_status(request, rawg_id):
    if request.method == 'POST':
        UserGame.objects.filter(user=request.user, rawg_id=rawg_id).delete()
    return redirect('game_detail', rawg_id=rawg_id)


# Оновлює статус гри, оцінку, коментар та додає до списку(ів)
@login_required
def update_game_status(request, rawg_id):
    if request.method != 'POST':
        return redirect('home')

    status = request.POST.get('status')
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()
    list_id = request.POST.get('list_id')
    new_list_name = request.POST.get('new_list')

    # Отримуємо або створюємо запис
    user_game, _ = UserGame.objects.get_or_create(
        user=request.user,
        rawg_id=rawg_id
    )

    update_fields = []

    # Оновлення статусу
    if status is not None:
        new_status = status if status and status != 'not_played' else None
        if user_game.status != new_status:
            user_game.status = new_status
            update_fields.append('status')

    # Оновлення оцінки (1–10)
    if rating is not None:
        try:
            new_rating = int(rating)
            if 1 <= new_rating <= 10:
                if user_game.rating != new_rating:
                    user_game.rating = new_rating
                    update_fields.append('rating')
        except (ValueError, TypeError):
            pass

    # Оновлення коментаря
    if comment != user_game.comment:
        user_game.comment = comment
        update_fields.append('comment')

    # Зберігаємо тільки змінені поля
    if update_fields:
        user_game.save(update_fields=update_fields)

    # Додавання до існуючого списку
    if list_id:
        try:
            user_list = UserList.objects.get(id=list_id, user=request.user)
            user_game.lists.add(user_list)
        except UserList.DoesNotExist:
            pass

    # Створення та додавання нового списку
    elif new_list_name:
        new_list_name = new_list_name.strip()
        if new_list_name:
            user_list, _ = UserList.objects.get_or_create(
                user=request.user,
                name=new_list_name
            )
            user_game.lists.add(user_list)

    return redirect('game_detail', rawg_id=rawg_id)