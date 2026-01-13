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

# list_detail — доступний усім, але з перевіркою видимості
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

@login_required
def toggle_list_privacy(request, list_id):
    if request.method == 'POST':
        lst = get_object_or_404(UserList, id=list_id, user=request.user)

        lst.is_private = not lst.is_private
        lst.save()



    # Повертаємось на профіль
    return redirect('profile_by_username', username=request.user.username)


@login_required
def add_friend(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)

        if target_user == request.user:
            # Не можна додати себе
            return redirect('profile_by_username', username=username)

        # Отримуємо профілі
        current_profile = request.user.profile
        target_profile = target_user.profile

        if not current_profile.is_friend(target_profile):
            current_profile.add_friend(target_profile)
            # messages.success(request, f"Ви додали {target_user.username} в друзі!")

        return redirect('profile_by_username', username=username)

    return redirect('profile_by_username', username=username)


@login_required
def remove_friend(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)

        try:
            current_profile = request.user.profile
            target_profile = target_user.profile
            if current_profile.friends.filter(pk=target_profile.pk).exists():
                current_profile.friends.remove(target_profile)
                target_profile.friends.remove(current_profile)
                # Очищаємо будь-які запити між ними
                FriendRequest.objects.filter(
                    sender__in=[request.user, target_user],
                    receiver__in=[request.user, target_user]
                ).delete()
                messages.success(request, f"{target_user.username} видалений з друзів")
            else:
                messages.info(request, "Цей користувач не у ваших друзях")
        except Profile.DoesNotExist:
            messages.error(request, "Профіль не знайдено")

    return redirect('profile_by_username', username=request.user.username)


@login_required
def send_friend_request(request, username):
    if request.method != 'POST':
        return redirect('profile_by_username', username=username)

    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        messages.error(request, "Неможливо надіслати запит собі")
        return redirect('profile_by_username', username=username)

    current_profile = request.user.profile
    target_profile = target_user.profile

    # 1. Вже друзі?
    if current_profile.is_friend(target_profile):
        messages.info(request, f"Ви вже в друзях з {target_user.username}")
        return redirect('profile_by_username', username=username)

    # 2. Спробуємо знайти або створити запит
    try:
        friend_request, created = FriendRequest.objects.get_or_create(
            sender=request.user,
            receiver=target_user,
            defaults={'status': 'pending'}
        )

        if not created:
            # Запит вже існує
            if friend_request.status == 'pending':
                messages.info(request, "Запит вже відправлено раніше")
            elif friend_request.status == 'accepted':
                messages.info(request, "Ви вже в друзях (запит був прийнятий)")
            elif friend_request.status == 'rejected':
                # Дозволяємо повторну відправку, оновлюючи статус
                friend_request.status = 'pending'
                friend_request.save()
                messages.success(request, f"Запит у друзі відправлено повторно до {target_user.username}!")
            return redirect('profile_by_username', username=username)

        # Новий запит створено успішно
        messages.success(request, f"Запит у друзі успішно відправлено до {target_user.username}!")

    except IntegrityError:
        messages.info(request, "Запит вже існує (можливо, відправлено паралельно)")

    return redirect('profile_by_username', username=username)


@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
        friend_request.accept()
        messages.success(request, f"Ви прийняли запит від {friend_request.sender.username}")
        return redirect('profile_by_username', username=request.user.username)

    return redirect('profile_by_username', username=request.user.username)


@login_required
def reject_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
        friend_request.reject()
        messages.success(request, f"Запит від {friend_request.sender.username} відхилено")
        return redirect('profile_by_username', username=request.user.username)

    return redirect('profile_by_username', username=request.user.username)
