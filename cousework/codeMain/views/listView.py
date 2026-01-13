import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from games.aut.models import UserGame, UserList, FriendRequest, Profile

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from games.aut.models import UserGame, UserList


RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"
RAWG_GAME_DETAIL_URL = "https://api.rawg.io/api/games/"


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


@login_required
def delete_list(request, list_id):
    if request.method == 'POST':
        lst = get_object_or_404(UserList, id=list_id, user=request.user)
        lst.delete()
    return redirect('profile_by_username', username=request.user.username)


@login_required
def rename_list(request, list_id):
    if request.method == 'POST':
        new_name = request.POST.get('new_name', '').strip()
        if new_name:
            lst = get_object_or_404(UserList, id=list_id, user=request.user)
            lst.name = new_name
            lst.save()
    return redirect('profile_by_username', username=request.user.username)


@login_required
def remove_from_list(request, list_id, rawg_id):
    if request.method == 'POST':
        user_list = get_object_or_404(UserList, id=list_id, user=request.user)  # тільки власник може видаляти
        user_game = get_object_or_404(UserGame, rawg_id=rawg_id, user=request.user)

        user_game.lists.remove(user_list)


    return redirect('list_detail', list_id=list_id)

def list_detail(request, list_id):
    lst = get_object_or_404(UserList, id=list_id)

    if lst.is_private and request.user != lst.user:
        return HttpResponseForbidden("Цей список приватний")

    games = []

    try:
        user_games = lst.games.all()

        for ug in user_games:
            game_id = str(ug.rawg_id)  # Має бути валідний RAWG ID (наприклад 3498)
            name = f"Гра ID {game_id}"
            background_image = "/static/images/placeholder_game.jpg"  # Твій плейсхолдер

            try:
                resp = requests.get(
                    f"{RAWG_GAME_DETAIL_URL}{game_id}",
                    params={'key': RAWG_API_KEY},
                    headers={'User-Agent': 'GameLibraryApp/1.0'},
                    timeout=8
                )

                if resp.status_code == 200:
                    details = resp.json()
                    if details:  # ← Важливо: перевіряємо, чи є дані
                        name = details.get('name', name)
                        # Ось ключовий рядок, як у profile:
                        background_image = details.get('background_image', background_image) or background_image
                else:
                    print(f"RAWG API status {resp.status_code} для game_id {game_id} у списку {list_id}")

            except requests.exceptions.RequestException as e:
                print(f"Помилка RAWG API (мережа/таймаут) для game_id {game_id} у списку {list_id}: {e}")
            except ValueError as e:
                print(f"Неможливо розпарсити JSON від RAWG для game_id {game_id}: {e}")

            games.append({
                'rawg_id': ug.rawg_id,          # ← Змінили на rawg_id (для посилань у шаблоні)
                'name': name,
                'header_image': background_image,  # Це поле використовується в шаблоні
                'status': ug.status,
                'rating': ug.rating,
                'comment': ug.comment,
                'get_status_display': ug.get_status_display(),
            })

    except Exception as e:
        print(f"Критична помилка обробки списку {list_id}: {e}")

    return render(request, 'list_detail.html', {
        'list': lst,
        'games': games,
        'profile_user': lst.user,
    })
