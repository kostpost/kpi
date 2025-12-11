from django.urls import path, include
from views import home
from views import game_detail

urlpatterns = [
    path('', home.home, name='home'),  # ← головна сторінка
    path('game/<str:appid>/', game_detail.game_detail, name='game_detail'),  # Новий маршрут
    path('oauth/', include('social_django.urls', namespace='social')),
]