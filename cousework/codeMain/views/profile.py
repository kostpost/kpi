from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from games.aut.models import UserGame, UserList, FriendRequest, Profile

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

import requests

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"
RAWG_GAME_DETAIL_URL = "https://api.rawg.io/api/games/"


# Профіль користувача: ігри, списки, друзі, запити в друзі
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == profile_user

    # Списки: свої — всі, чужі — тільки публічні
    user_lists = profile_user.lists.all() if is_own_profile else profile_user.lists.filter(is_private=False)

    games = []
    stats = {'total_games': 0}

    try:
        # Останні 6 оціненних ігор для відображення в профілі
        user_games = UserGame.objects.filter(user=profile_user, rating__gt=0).order_by('-updated_at')[:6]

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
            except Exception as e:
                print(f"Помилка RAWG для гри {game_id} у профілі {username}: {e}")

            games.append({
                'rawg_id': ug.rawg_id,
                'name': name,
                'header_image': background_image,
                'status': ug.status or 'not_played',
                'user_rating': ug.rating or 0,
            })

        stats['total_games'] = len(games)

    except Exception as e:
        print(f"Критична помилка профілю {username}: {e}")

    is_already_friend = False
    pending_sent_request = False
    incoming_requests = []
    friends_list = []

    if request.user.is_authenticated:
        try:
            current_profile = request.user.profile
            target_profile = profile_user.profile

            is_already_friend = target_profile.friends.filter(user=request.user).exists()
            pending_sent_request = FriendRequest.objects.filter(
                sender=request.user, receiver=profile_user, status='pending'
            ).exists()

            if is_own_profile:
                incoming_requests = FriendRequest.objects.filter(
                    receiver=request.user, status='pending'
                ).select_related('sender').order_by('-created_at')

            can_see_friends = is_own_profile or is_already_friend
            if can_see_friends:
                friends_list = profile_user.profile.friends.select_related('user').all()[:12]

        except Exception as e:
            print(f"Помилка соціальної частини профілю {username}: {e}")

    context = {
        'profile_user': profile_user,
        'games': games,
        'stats': stats,
        'user_lists': user_lists,
        'is_own_profile': is_own_profile,
        'can_see_library': True,
        'is_already_friend': is_already_friend,
        'pending_sent_request': pending_sent_request,
        'incoming_requests': incoming_requests,
        'friends_list': friends_list,
    }

    return render(request, 'profile.html', context)


# Перевірка, чи є два профілі в друзях
def is_friend(self, other_profile):
    return self.friends.filter(pk=other_profile.pk).exists()


# Сторінка зі списком усіх друзів користувача
def user_friends_all(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user == profile_user

    # Доступ: свої друзі або друзі один одного
    if is_own_profile or profile_user.profile in request.user.profile.friends.all():
        friends = profile_user.profile.friends.select_related('user').order_by('user__username')
    else:
        friends = profile_user.profile.friends.none()

    context = {
        'profile_user': profile_user,
        'friends': friends,
        'total_friends': friends.count(),
        'is_own_profile': is_own_profile,
    }
    return render(request, 'user_friends_all.html', context)


# Сторінка зі списком усіх списків користувача
def user_lists_all(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == profile_user

    user_lists = profile_user.lists.all().order_by('-created_at') if is_own_profile \
        else profile_user.lists.filter(is_private=False).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'user_lists': user_lists,
        'total_lists': user_lists.count(),
        'is_own_profile': is_own_profile,
    }
    return render(request, 'user_lists_all.html', context)


# Повна бібліотека ігор користувача
def user_library(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == profile_user

    games = []
    try:
        user_games = UserGame.objects.filter(user=profile_user).order_by('-updated_at')

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
                    name = details.get('name', name)
                    background_image = details.get('background_image') or background_image
            except Exception as e:
                print(f"Помилка завантаження гри {game_id} у бібліотеці {username}: {e}")

            games.append({
                'rawg_id': ug.rawg_id,
                'name': name,
                'header_image': background_image,
                'status': ug.status or 'not_played',
                'user_rating': ug.rating or 0,
            })

    except Exception as e:
        print(f"Помилка завантаження бібліотеки {username}: {e}")

    context = {
        'profile_user': profile_user,
        'games': games,
        'total_games': len(games),
        'is_own_profile': is_own_profile,
    }

    return render(request, 'user_library.html', context)


@login_required
def upload_avatar(request):
    if request.method == 'POST' and 'avatar' in request.FILES:
        profile = request.user.profile
        profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Аватар успішно оновлено!')
    else:
        messages.error(request, 'Не вдалося завантажити аватар. Спробуйте ще раз.')

    return redirect('profile_by_username', username=request.user.username)



# Перемикання приватності списку
@login_required
def toggle_list_privacy(request, list_id):
    if request.method == 'POST':
        lst = get_object_or_404(UserList, id=list_id, user=request.user)
        lst.is_private = not lst.is_private
        lst.save()

    return redirect('profile_by_username', username=request.user.username)