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

# Правильний URL для деталей ігор (НЕ потребує ключа!)
STEAM_APPDETAILS_URL = "https://store.steampowered.com/api/appdetails"
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == profile_user

    # Списки — без змін
    if is_own_profile:
        user_lists = profile_user.lists.all()
    else:
        user_lists = profile_user.lists.filter(is_private=False)

    # Ігри бібліотеки
    games = []
    stats = {'total_games': 0}

    try:
        user_games = UserGame.objects.filter(user=profile_user)

        for ug in user_games:
            appid = str(ug.appid)
            name = f"Гра {appid}"  # запасний варіант
            header_image = f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg"

            try:
                # Запит по одній грі — як у твоєму game_detail
                resp = requests.get(
                    f"{STEAM_APPDETAILS_URL}?appids={appid}",
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
                    timeout=6
                )

                if resp.status_code == 200:
                    data = resp.json().get(appid, {})
                    if data.get('success'):
                        details = data.get('data', {})
                        if details:
                            name = details.get('name', name)
                            header_image = details.get('header_image', header_image)

                else:
                    print(f"Steam API status {resp.status_code} для appid {appid} у профілі {username}")

            except Exception as e:
                print(f"Помилка Steam API для appid {appid} у профілі {username}: {e}")

            games.append({
                'appid': ug.appid,
                'name': name,
                'header_image': header_image,
                'status': ug.status or 'not_played',
                'user_rating': ug.rating or 0,
            })

        # Сортування — без змін
        games.sort(key=lambda g: (
            {'completed': 0, 'playing': 1, 'planned': 2, 'dropped': 3, 'not_played': 4}.get(g['status'], 5),
            -g['user_rating'],
            g['name'].lower()
        ))

        stats['total_games'] = len(games)

    except Exception as e:
        print(f"Критична помилка завантаження бібліотеки для {username}: {e}")

    # Додаткові дані для соціальної взаємодії
    is_already_friend = False
    pending_sent_request = False
    incoming_requests = []

    if request.user.is_authenticated:
        try:
            # Чи вже друзі
            is_already_friend = profile_user.profile.friends.filter(user=request.user).exists()

            # Чи відправлений запит від мене до нього
            pending_sent_request = FriendRequest.objects.filter(
                sender=request.user,
                receiver=profile_user,
                status='pending'
            ).exists()

            # Вхідні запити (тільки для власного профілю)
            if is_own_profile:
                incoming_requests = FriendRequest.objects.filter(
                    receiver=request.user,
                    status='pending'
                ).select_related('sender').order_by('-created_at')

            friends_list = profile_user.profile.friends.select_related('user').all()[
                :12]  # обмежимо перші 12 для швидкості

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


# list_detail — доступний усім, але з перевіркою видимості
def list_detail(request, list_id):
    lst = get_object_or_404(UserList, id=list_id)

    # Перевірка доступу до приватного списку
    if lst.is_private and request.user != lst.user:
        return HttpResponseForbidden("Цей список приватний")

    games = []

    try:
        user_games = lst.games.all()

        for ug in user_games:
            appid = str(ug.appid)
            name = f"Гра {appid}"  # запасний варіант
            header_image = f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg"

            try:
                # ТОЧНО ТАКИЙ ЖЕ запит, як у game_detail
                resp = requests.get(
                    f"{STEAM_APPDETAILS_URL}?appids={appid}",
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    timeout=6
                )

                if resp.status_code == 200:
                    data = resp.json().get(appid, {})
                    if data.get('success'):
                        details = data.get('data', {})
                        if details:
                            name = details.get('name', name)
                            header_image = details.get('header_image', header_image)

                else:
                    print(f"Steam API status {resp.status_code} для appid {appid} у списку {list_id}")

            except Exception as e:
                print(f"Помилка Steam API для appid {appid} у списку {list_id}: {e}")

            games.append({
                'appid': ug.appid,
                'name': name,
                'header_image': header_image,
                'status': ug.status,
                'rating': ug.rating,
                'comment': ug.comment,
                'get_status_display': ug.get_status_display(),
            })

    except Exception as e:
        print(f"Загальна помилка обробки списку {list_id}: {e}")

    return render(request, 'list_detail.html', {
        'list': lst,
        'games': games,
        'profile_user': lst.user,
    })


@login_required
def toggle_list_privacy(request, list_id):
    if request.method == 'POST':
        lst = get_object_or_404(UserList, id=list_id, user=request.user)

        # Інвертуємо поточний статус приватності
        lst.is_private = not lst.is_private
        lst.save()

        # Можна додати повідомлення, якщо хочеш
        # from django.contrib import messages
        # messages.success(request, f"Список «{lst.name}» тепер {'приватний' if lst.is_private else 'публічний'}")

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

        if target_user == request.user:
            return redirect('profile_by_username', username=username)

        current_profile = request.user.profile
        target_profile = target_user.profile

        if current_profile.is_friend(target_profile):
            current_profile.remove_friend(target_profile)
            # messages.success(request, f"Ви видалили {target_user.username} з друзів")

        return redirect('profile_by_username', username=username)

    return redirect('profile_by_username', username=username)


@login_required
def send_friend_request(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)

        if target_user == request.user:
            messages.error(request, "Неможливо додати себе в друзі")
            return redirect('profile_by_username', username=username)

        # Перевіряємо, чи немає вже запиту або дружби
        if FriendRequest.objects.filter(sender=request.user, receiver=target_user).exists():
            messages.info(request, "Запит вже відправлено")
        elif request.user.profile.friends.filter(user=target_user).exists():
            messages.info(request, "Ви вже друзі")
        else:
            FriendRequest.objects.create(sender=request.user, receiver=target_user)
            messages.success(request, f"Запит у друзі відправлено до {target_user.username}")

        return redirect('profile_by_username', username=username)

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


@login_required
def remove_friend(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)

        try:
            current_profile = request.user.profile
            target_profile = target_user.profile
            if current_profile.friends.filter(user=target_user).exists():
                current_profile.friends.remove(target_profile)
                target_profile.friends.remove(current_profile)  # симетрично
                messages.success(request, f"{target_user.username} видалений з друзів")
            else:
                messages.info(request, "Цей користувач не у ваших друзях")
        except Profile.DoesNotExist:
            messages.error(request, "Профіль не знайдено")

    return redirect('profile_by_username', username=request.user.username)