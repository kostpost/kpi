import requests
from datetime import datetime, timedelta
from django.shortcuts import render
from games.aut.models import UserGame

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"

def home(request):
    context = {}

    def fetch_games(params):
        try:
            resp = requests.get("https://api.rawg.io/api/games", params={'key': RAWG_API_KEY, **params}, timeout=10)
            if resp.status_code == 200:
                return resp.json().get('results', [])
        except Exception as e:
            print(f"RAWG error: {e}")
        return []

    sections = [
        {
            'title': 'Топ ігор 2025 року',
            'games': fetch_games({
                'dates': '2025-01-01,2025-12-31',
                'ordering': '-ratings_count',
                'page_size': 12
            }),
            'empty_text': 'Поки що немає популярних ігор 2025 року в базі...'
        },
        {
            'title': 'Топ ігор за весь час',
            'games': fetch_games({'ordering': '-rating', 'metacritic': '85,100', 'page_size': 12}),
            'empty_text': 'Немає вічних класиків? Дивно...'
        },
        {
            'title': 'Гарячі новинки',
            'games': fetch_games({'dates': f"{(datetime.now().date() - timedelta(days=45))},{datetime.now().date()}", 'ordering': '-released,-added', 'page_size': 12}),
            'empty_text': 'Нові релізи ще не з\'явилися...'
        },
        {
            'title': 'Очікувані релізи 2026',
            'games': fetch_games({'dates': '2026-01-01,2026-12-31', 'ordering': '-added', 'page_size': 12}),
            'empty_text': 'Скоро буде гаряче!'
        }
    ]

    context['sections'] = sections

    return render(request, 'home.html', context)