import requests
from django.shortcuts import render
from django.views.decorators.cache import cache_page

@cache_page(60 * 60)  # кеш на 1 годину
def home(request):
    top_games = []
    try:
        response = requests.get("https://steamspy.com/api.php?request=top100in2weeks")
        if response.status_code == 200:
            data = response.json()
            top_games = sorted(data.items(), key=lambda x: x[1].get('ccu', 0), reverse=True)[:10]
            top_games = [{"name": game_data.get('name', 'Unknown')} for appid, game_data in top_games]
    except:
        pass

    context = {
        'most_played': top_games,
        'trending': [],
        'popular_releases': [],
        'hot_releases': [],
    }
    return render(request, 'home.html', context)
