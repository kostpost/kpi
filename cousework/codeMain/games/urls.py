from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from views import home
from views import game_detail
from views import logout
from views import profile

urlpatterns = [
    path('', home.home, name='home'),  # ← головна сторінка
    path('game/<str:appid>/', game_detail.game_detail, name='game_detail'),  # Новий маршрут
    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout/', logout.logout_view, name='logout'),

    # path('profile/', profile.profile, name='profile'),
    path('profile/<str:steamid>/', profile.profile, name='profile'),

    path('game/<str:appid>/update/', game_detail.update_game_status, name='update_game_status'),

    path('game/<int:appid>/delete/', game_detail.delete_game_status, name='delete_game_status'),
]


