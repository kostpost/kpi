# from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required
# from django.urls import path, include
# from views import home
# from views import game_detail
# from views import logout
# from views import profile
#
# urlpatterns = [
#     path('', home.home, name='home'),  # ← головна сторінка
#     path('game/<str:appid>/', game_detail.game_detail, name='game_detail'),  # Новий маршрут
#     path('oauth/', include('social_django.urls', namespace='social')),
#
#     # path('profile/', profile.profile, name='profile'),
#     path('profile/<str:steamid>/', profile.profile, name='profile'),
#
#     path('game/<str:appid>/update/', game_detail.update_game_status, name='update_game_status'),
#
#     path('game/<int:appid>/delete/', game_detail.delete_game_status, name='delete_game_status'),
#
#     path('register/', game_views.register, name='register'),
#     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
# ]


from django.urls import path
from django.contrib.auth import views as auth_views  # ← це обов'язково!

# Імпортуємо всі потрібні функції-представлення
# (припускаю, що вони знаходяться в games/views.py)
from views import (
    home,                    # головна сторінка
    game_detail,             # деталі гри
    profile,                 # профіль
    aut,
    search,
)

urlpatterns = [
    # Головна сторінка
    path('', home.home, name='home'),
    path('search/',search.search , name='search'),

    # Деталі гри
    path('game/<str:appid>/', game_detail.game_detail, name='game_detail'),

    # Оновлення статусу гри (POST)
    path('game/<str:appid>/update/', game_detail.update_game_status, name='update_game_status'),

    # Видалення статусу гри (POST)
    path('game/<str:appid>/delete/', game_detail.delete_game_status, name='delete_game_status'),

    # Профіль користувача
    # (якщо профіль тепер не залежить від steamid, можна спростити до path('profile/', profile, name='profile'))
    # але поки залишив твою версію
    path('profile/<str:username>/', profile.profile, name='profile_by_username'),    # Реєстрація
    path('register/', aut.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # Вихід (перенаправлення на головну)
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # urls.py
    path('list/create/', profile.create_list, name='create_list'),
    path('list/<int:list_id>/delete/', profile.delete_list, name='delete_list'),
path('list/<int:list_id>/', profile.list_detail, name='list_detail'),

path('list/<int:list_id>/rename/', profile.rename_list, name='rename_list'),

path('list/<int:list_id>/toggle-privacy/', profile.toggle_list_privacy, name='toggle_list_privacy'),




path('profile/<str:username>/add-friend/', profile.add_friend, name='add_friend'),
path('profile/<str:username>/remove-friend/', profile.remove_friend, name='remove_friend'),

path('profile/<str:username>/send-request/', profile.send_friend_request, name='send_friend_request'),
path('friend-request/<int:request_id>/accept/', profile.accept_friend_request, name='accept_friend_request'),
path('friend-request/<int:request_id>/reject/', profile.reject_friend_request, name='reject_friend_request'),



]