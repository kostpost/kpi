from datetime import datetime
import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from games.aut.models import UserGame
from games.aut.models import UserList

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"


def game_detail(request, rawg_id):  # ← параметр тепер rawg_id (int)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    game = {
        'rawg_id': rawg_id,
        'name': 'Завантаження...',
        'background_image': 'https://via.placeholder.com/460x215?text=Loading...',
        'description': 'Опис завантажується...',
        'developer': 'Невідомо',
        'publisher': 'Невідомо',
        'platforms': 'Невідомо',
        'released': 'Невідомо',
        'genres': 'Невідомо',
        'rating': None,
        'metacritic': None,
        'website': None,
    }

    try:
        url = f"https://api.rawg.io/api/games/{rawg_id}?key={RAWG_API_KEY}"
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            if data:
                game.update({
                    'name': data.get('name', 'Невідома гра'),
                    'background_image': data.get('background_image'),
                    'description': data.get('description_raw') or data.get('description', ''),
                    'developer': ', '.join(d.get('name', '') for d in data.get('developers', [])) or 'Невідомо',
                    'publisher': ', '.join(p.get('name', '') for p in data.get('publishers', [])) or 'Невідомо',
                    'released': data.get('released', 'Невідомо'),
                    'genres': ', '.join(g.get('name', '') for g in data.get('genres', [])) or 'Невідомо',
                    'platforms': ', '.join(p['platform'].get('name', '') for p in data.get('parent_platforms', [])) or 'Невідомо',
                    'rating': data.get('rating'),           # 0–5
                    'metacritic': data.get('metacritic'),   # 0–100, може бути None
                    'website': data.get('website'),
                })
        else:
            print(f"RAWG API error {resp.status_code} для гри ID {rawg_id}")

    except Exception as e:
        print(f"Помилка завантаження даних RAWG для ID {rawg_id}: {e}")

    # Статуси та відгуки — фільтруємо по rawg_id
    status_choices = [
        ('playing', 'Граю'),
        ('completed', 'Пройдено'),
        ('planned', 'У планах'),
        ('dropped', 'Відкладено'),
    ]

    user_game = None
    has_review = False

    if request.user.is_authenticated:
        user_game = UserGame.objects.filter(user=request.user, rawg_id=rawg_id).first()
        has_review = bool(user_game and (
            user_game.rating is not None or
            (user_game.comment or '').strip() or
            (user_game.status and user_game.status != 'not_played')
        ))

    friends_reviews = []

    if request.user.is_authenticated:
        try:
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













@login_required
def delete_game_status(request, rawg_id):
    if request.method == 'POST':
        UserGame.objects.filter(user=request.user, rawg_id=rawg_id).delete()
    return redirect('game_detail', rawg_id=rawg_id)  # ← змінили параметр


@login_required
def update_game_status(request, rawg_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        list_id = request.POST.get('list_id')
        new_list_name = request.POST.get('new_list')

        user_game, created = UserGame.objects.get_or_create(
            user=request.user,
            rawg_id=rawg_id  # ← змінили!
        )

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

        # Обробка списків
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

        return redirect('game_detail', rawg_id=rawg_id)

    return redirect('home')




