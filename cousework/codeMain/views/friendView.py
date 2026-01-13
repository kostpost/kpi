from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from games.aut.models import Profile, FriendRequest


# Додає користувача до списку друзів (якщо ще не друзі)
@login_required
def add_friend(request, username):
    if request.method != 'POST':
        return redirect('profile_by_username', username=username)

    target_user = get_object_or_404(User, username=username)

    # Сам себе додавати не можна
    if target_user == request.user:
        return redirect('profile_by_username', username=username)

    current_profile = request.user.profile
    target_profile = target_user.profile

    if not current_profile.is_friend(target_profile):
        current_profile.add_friend(target_profile)

    return redirect('profile_by_username', username=username)


# Видаляє користувача з друзів та очищає пов’язані запити
@login_required
def remove_friend(request, username):
    if request.method != 'POST':
        return redirect('profile_by_username', username=request.user.username)

    target_user = get_object_or_404(User, username=username)

    current_profile = request.user.profile
    target_profile = target_user.profile

    if current_profile.friends.filter(pk=target_profile.pk).exists():
        current_profile.friends.remove(target_profile)
        target_profile.friends.remove(current_profile)
        # Видаляємо всі запити дружби між цими двома користувачами
        FriendRequest.objects.filter(
            sender__in=[request.user, target_user],
            receiver__in=[request.user, target_user]
        ).delete()
        messages.success(request, f"{target_user.username} видалений з друзів")
    else:
        messages.info(request, "Цей користувач не у ваших друзях")

    return redirect('profile_by_username', username=request.user.username)


# Надсилає запит у друзі або повторно надсилає, якщо попередній був відхилений
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

    if current_profile.is_friend(target_profile):
        messages.info(request, f"Ви вже в друзях з {target_user.username}")
        return redirect('profile_by_username', username=username)

    friend_request, created = FriendRequest.objects.get_or_create(
        sender=request.user,
        receiver=target_user,
        defaults={'status': 'pending'}
    )

    if not created:
        if friend_request.status == 'pending':
            messages.info(request, "Запит вже відправлено")
        elif friend_request.status == 'accepted':
            messages.info(request, "Ви вже в друзях")
        elif friend_request.status == 'rejected':
            friend_request.status = 'pending'
            friend_request.save()
            messages.success(request, f"Повторний запит надіслано до {target_user.username}")
    else:
        messages.success(request, f"Запит надіслано до {target_user.username}")

    return redirect('profile_by_username', username=username)


# Приймає вхідний запит у друзі
@login_required
def accept_friend_request(request, request_id):
    if request.method != 'POST':
        return redirect('profile_by_username', username=request.user.username)

    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
        status='pending'
    )

    friend_request.accept()
    messages.success(request, f"Запит від {friend_request.sender.username} прийнято")

    return redirect('profile_by_username', username=request.user.username)


# Відхиляє вхідний запит у друзі
@login_required
def reject_friend_request(request, request_id):
    if request.method != 'POST':
        return redirect('profile_by_username', username=request.user.username)

    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
        status='pending'
    )

    friend_request.reject()
    messages.success(request, f"Запит від {friend_request.sender.username} відхилено")

    return redirect('profile_by_username', username=request.user.username)