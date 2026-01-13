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



def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == profile_user

    if is_own_profile:
        user_lists = profile_user.lists.all()
    else:
        user_lists = profile_user.lists.filter(is_private=False)

    games = []
    stats = {'total_games': 0}

    try:
        user_games = UserGame.objects.filter(user=profile_user, rating__gt=0).order_by('-updated_at')[:6]

        for ug in user_games:
            game_id = str(ug.rawg_id)  # ← ЗМІНИЛИ appid → rawg_id
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
                        background_image = details.get('background_image', background_image) or background_image
                else:
                    print(f"RAWG API status {resp.status_code} для game_id {game_id} у профілі {username}")

            except requests.exceptions.RequestException as e:
                print(f"Помилка RAWG API для game_id {game_id} у профілі {username}: {e}")
            except ValueError:
                print(f"Неможливо розпарсити JSON від RAWG для game_id {game_id}")

            games.append({
                'rawg_id': ug.rawg_id,
                # ← ЗМІНИЛИ appid → rawg_id (і в шаблоні profile.html теж змініть {{ game.appid }} на {{ game.rawg_id }} в посиланнях)
                'name': name,
                'header_image': background_image,
                'status': ug.status or 'not_played',
                'user_rating': ug.rating or 0,
            })

        stats['total_games'] = len(games)

    except Exception as e:
        print(f"Критична помилка завантаження бібліотеки для {username}: {e}")

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
                sender=request.user,
                receiver=profile_user,
                status='pending'
            ).exists()

            if is_own_profile:
                incoming_requests = FriendRequest.objects.filter(
                    receiver=request.user,
                    status='pending'
                ).select_related('sender').order_by('-created_at')

            can_see_friends = is_own_profile or is_already_friend

            if can_see_friends:
                friends_list = profile_user.profile.friends.select_related('user').all()[:12]

        except Exception as e:
            print(f"Помилка соціальної взаємодії для {username}: {e}")

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




def is_friend(self, other_profile):
    return self.friends.filter(pk=other_profile.pk).exists()

def user_friends_all(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user == profile_user

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

def user_lists_all(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == profile_user

    if is_own_profile:
        user_lists = profile_user.lists.all().order_by('-created_at')
    else:
        user_lists = profile_user.lists.filter(is_private=False).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'user_lists': user_lists,
        'total_lists': user_lists.count(),
        'is_own_profile': is_own_profile,
    }
    return render(request, 'user_lists_all.html', context)

def user_library(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == profile_user

    games = []
    try:
        # Беремо ВСІ ігри користувача (можна сортувати як хочете)
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
                print(f"Помилка завантаження гри {game_id}: {e}")

            games.append({
                'rawg_id': ug.rawg_id,
                'name': name,
                'header_image': background_image,
                'status': ug.status or 'not_played',
                'user_rating': ug.rating or 0,
                # можна додати 'comment': ug.comment, якщо хочете показувати
            })

    except Exception as e:
        print(f"Помилка в user_library для {username}: {e}")

    context = {
        'profile_user': profile_user,
        'games': games,
        'total_games': len(games),
        'is_own_profile': is_own_profile,
        # можна передати інші дані, наприклад friends_list, якщо потрібно
    }

    return render(request, 'user_library.html', context)







@login_required
def toggle_list_privacy(request, list_id):
    if request.method == 'POST':
        lst = get_object_or_404(UserList, id=list_id, user=request.user)

        lst.is_private = not lst.is_private
        lst.save()



    # Повертаємось на профіль
    return redirect('profile_by_username', username=request.user.username)



