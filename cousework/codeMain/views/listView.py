from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from games.aut.models import UserGame, UserList, FriendRequest, Profile

import requests

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"
RAWG_GAME_DETAIL_URL = "https://api.rawg.io/api/games/"


# Створює новий список ігор користувача
@login_required
def create_list(request):
    if request.method == 'POST':
        name = request.POST.get('list_name', '').strip()
        is_private = request.POST.get('is_private') == 'on'

        if name:
            UserList.objects.create(
                user=request.user,
                name=name,
                is_private=is_private
            )

    return redirect('profile_by_username', username=request.user.username)


# Видаляє список ігор (тільки власник)
@login_required
def delete_list(request, list_id):
    if request.method == 'POST':
        lst = get_object_or_404(UserList, id=list_id, user=request.user)
        lst.delete()

    return redirect('profile_by_username', username=request.user.username)


# Перейменовує існуючий список
@login_required
def rename_list(request, list_id):
    if request.method == 'POST':
        new_name = request.POST.get('new_name', '').strip()
        if new_name:
            lst = get_object_or_404(UserList, id=list_id, user=request.user)
            lst.name = new_name
            lst.save()

    return redirect('profile_by_username', username=request.user.username)


# Видаляє гру зі списку (тільки власник списку)
@login_required
def remove_from_list(request, list_id, rawg_id):
    if request.method == 'POST':
        user_list = get_object_or_404(UserList, id=list_id, user=request.user)
        user_game = get_object_or_404(UserGame, rawg_id=rawg_id, user=request.user)

        user_game.lists.remove(user_list)

    return redirect('list_detail', list_id=list_id)


# Показує детальну сторінку списку з іграми та даними з RAWG
def list_detail(request, list_id):
    lst = get_object_or_404(UserList, id=list_id)

    # Перевірка доступу до приватного списку
    if lst.is_private and request.user != lst.user:
        return HttpResponseForbidden("Цей список приватний")

    games = []

    try:
        user_games = lst.games.all()

        for ug in user_games:
            game_id = str(ug.rawg_id)
            name = f"Гра ID {game_id}"
            background_image = "/static/images/placeholder_game.jpg"

            try:
                resp = requests.get(
                    f"{RAWG_GAME_DETAIL_URL}{game_id}",
                    params={'key': RAWG_API_KEY},
                    headers={'User-Agent': 'GameLibraryApp/1.0'},
                    timeout=8
                )

                if resp.status_code == 200:
                    details = resp.json()
                    if details:
                        name = details.get('name', name)
                        background_image = details.get('background_image') or background_image

                else:
                    print(f"RAWG API status {resp.status_code} для гри {game_id} у списку {list_id}")

            except requests.exceptions.RequestException as e:
                print(f"Помилка запиту RAWG для гри {game_id}: {e}")
            except ValueError as e:
                print(f"Помилка парсингу JSON для гри {game_id}: {e}")

            games.append({
                'rawg_id': ug.rawg_id,
                'name': name,
                'header_image': background_image,  # використовується в шаблоні
                'status': ug.status,
                'rating': ug.rating,
                'comment': ug.comment,
                'get_status_display': ug.get_status_display(),
            })

    except Exception as e:
        print(f"Критична помилка при обробці списку {list_id}: {e}")

    return render(request, 'list_detail.html', {
        'list': lst,
        'games': games,
        'profile_user': lst.user,
    })