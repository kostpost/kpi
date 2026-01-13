from django.urls import path
from django.contrib.auth import views as auth_views  # ← це обов'язково!

# Імпортуємо всі потрібні функції-представлення
# (припускаю, що вони знаходяться в games/views.py)
from views import (
    home,  # головна сторінка
    game_detail,  # деталі гри
    profile,  # профіль
    aut,
    search,  # реєстрація (твоя функція)
)

urlpatterns = [
    path('', home.home, name='home'),
    path('search/', search.search, name='search'),

    path('game/<str:rawg_id>/', game_detail.game_detail, name='game_detail'),
    path('game/<int:rawg_id>/', game_detail.game_detail, name='game_detail'),

    path('game/<str:rawg_id>/update/', game_detail.update_game_status, name='update_game_status'),

    path('game/<str:rawg_id>/delete/', game_detail.delete_game_status, name='delete_game_status'),

    path('profile/<str:username>/', profile.profile, name='profile_by_username'),  # Реєстрація
    path('profile/<str:username>/library/', profile.user_library, name='user_library'),
    path('profile/<str:username>/lists/', profile.user_lists_all, name='user_lists_all'),
path('profile/<str:username>/friends/', profile.user_friends_all, name='user_friends_all'),


    path('register/', aut.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('list/create/', profile.create_list, name='create_list'),
    path('list/<int:list_id>/delete/', profile.delete_list, name='delete_list'),
    path('list/<int:list_id>/', profile.list_detail, name='list_detail'),
    path('list/<int:list_id>/remove/<int:rawg_id>/', profile.remove_from_list, name='remove_from_list'),

    path('list/<int:list_id>/rename/', profile.rename_list, name='rename_list'),

    path('list/<int:list_id>/toggle-privacy/', profile.toggle_list_privacy, name='toggle_list_privacy'),

    path('profile/<str:username>/add-friend/', profile.add_friend, name='add_friend'),
    path('profile/<str:username>/remove-friend/', profile.remove_friend, name='remove_friend'),
    path('profile/<str:username>/send-request/', profile.send_friend_request, name='send_friend_request'),
    path('friend-request/<int:request_id>/accept/', profile.accept_friend_request, name='accept_friend_request'),
    path('friend-request/<int:request_id>/reject/', profile.reject_friend_request, name='reject_friend_request'),

]
