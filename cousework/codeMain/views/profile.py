from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from games.aut.models import UserGame, UserList


# Списки бачать усі, але редагувати/видаляти/створювати — тільки власник
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    is_own_profile = request.user.is_authenticated and request.user == profile_user

    # Завантажуємо списки
    if is_own_profile:
        user_lists = profile_user.lists.all()
    else:
        # Інші користувачі бачать тільки публічні списки
        user_lists = profile_user.lists.filter(is_private=False)

    # Ігри бібліотеки (можна залишити як є, або теж зробити вибірковою видимістю)
    games = []
    stats = {'total_games': 0}

    try:
        user_games = UserGame.objects.filter(user=profile_user)
        for ug in user_games:
            name = f"Гра {ug.appid}"
            header_image = f"https://steamcdn-a.akamaihd.net/steam/apps/{ug.appid}/header.jpg"

            games.append({
                'appid': ug.appid,
                'name': name,
                'header_image': header_image,
                'status': ug.status or 'not_played',
                'user_rating': ug.rating or 0,
            })
        games.sort(key=lambda g: (
            {'completed': 0, 'playing': 1, 'planned': 2, 'dropped': 3, 'not_played': 4}.get(g['status'], 5),
            -g['user_rating'],
            g['name'].lower()
        ))
        stats['total_games'] = len(games)
    except Exception as e:
        print(f"Помилка завантаження бібліотеки для {username}: {e}")

    context = {
        'profile_user': profile_user,
        'games': games,
        'stats': stats,
        'user_lists': user_lists,  # змінено з user.lists → user_lists
        'is_own_profile': is_own_profile,
        'can_see_library': True,
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

    # Перевірка доступу
    if lst.is_private and request.user != lst.user:
        # можна зробити 403 або перенаправити
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Цей список приватний")

    games = lst.games.all()

    return render(request, 'list_detail.html', {
        'list': lst,
        'games': games,
        'profile_user': lst.user,
    })