import requests
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User
from math import ceil
from datetime import datetime

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"
GAMES_PER_PAGE = 20

GENRES_CHOICES = [
    ('4', 'Action'), ('51', 'Indie'), ('3', 'Adventure'), ('5', 'RPG'),
    ('10', 'Strategy'), ('2', 'Shooter'), ('40', 'Casual'), ('14', 'Simulation'),
    ('7', 'Puzzle'), ('11', 'Arcade'), ('83', 'Platformer'), ('59', 'Massively Multiplayer'),
    ('1', 'Racing'), ('15', 'Sports'), ('6', 'Fighting'), ('19', 'Family'),
    ('28', 'Board Games'), ('17', 'Card'), ('34', 'Educational'),
]

def search(request):
    q = request.GET.get('q', '').strip()
    genres = request.GET.getlist('genres')
    year_from = request.GET.get('year_from', '').strip()
    year_to = request.GET.get('year_to', '').strip()
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1

    games_results = []
    users_results = []
    total_pages = 1
    has_next = False
    has_prev = False
    error_message = None

    current_year = datetime.now().year

    if q:
        users_results = User.objects.filter(
            Q(username__icontains=q)
        ).select_related('profile').order_by('username')[:15]

    try:
        params = {
            'key': RAWG_API_KEY,
            'page': page,
            'page_size': GAMES_PER_PAGE,
            'ordering': '-added',
        }

        if q:
            params['search'] = q

        if genres and any(genres):
            params['genres'] = ','.join([g for g in genres if g.strip()])

        dates_param = None
        if year_from.isdigit() or year_to.isdigit():
            start_year = int(year_from) if year_from.isdigit() else 1980
            end_year = int(year_to) if year_to.isdigit() else current_year + 1

            if start_year > end_year:
                start_year, end_year = end_year, start_year  # міняємо місцями

            from_date = f"{start_year}-01-01"
            to_date = f"{end_year}-12-31"

            dates_param = f"{from_date},{to_date}"
            params['dates'] = dates_param

        print("DEBUG: year_from =", year_from, "year_to =", year_to)
        print("DEBUG: dates_param =", dates_param if dates_param else "не вказано")
        print("DEBUG: params =", params)

        url = "https://api.rawg.io/api/games"
        resp = requests.get(url, params=params, timeout=10, headers={'User-Agent': 'GameLibraryApp/1.0'})

        print("DEBUG: full URL =", resp.url)

        if resp.status_code == 200:
            data = resp.json()
            games_results = data.get('results', [])

            count = data.get('count', 0)
            total_pages = ceil(count / GAMES_PER_PAGE) if count else 1
            has_next = bool(data.get('next'))
            has_prev = bool(data.get('previous'))

            print("DEBUG: знайдено ігор =", len(games_results), "загальна кількість =", count)
        else:
            error_message = f"RAWG помилка {resp.status_code}: {resp.text[:200]}"
            print(error_message)

    except Exception as e:
        error_message = "Помилка завантаження ігор"
        print(f"RAWG error: {e}")

    context = {
        'query': q,
        'genres_list': genres,
        'year_from': year_from,
        'year_to': year_to,
        'genres_choices': GENRES_CHOICES,
        'games_results': games_results,
        'users_results': users_results,
        'has_results': bool(games_results or users_results),
        'error_message': error_message,
        'page': page,
        'total_pages': total_pages,
        'has_next': has_next,
        'has_prev': has_prev,
        'current_year': current_year,
    }

    return render(request, 'search.html', context)