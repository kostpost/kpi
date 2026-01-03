import requests
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User
from games.aut.models import Profile  # якщо використовуєш Profile

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"  # заміни на свій!

def search(request):
    query = request.GET.get('q', '').strip()

    games_results = []
    users_results = []

    if query:
        # 1. Пошук користувачів (за username)
        users_results = User.objects.filter(
            Q(username__icontains=query)
        ).select_related('profile')[:12]

        # 2. Пошук ігор через RAWG API (повнотекстовий, точний і швидкий)
        try:
            url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={query}&page_size=20"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                games_results = data.get('results', [])[:12]  # обмежуємо 12 результатів
        except Exception as e:
            print(f"Помилка RAWG API при пошуку '{query}': {e}")

    context = {
        'query': query,
        'games_results': games_results,
        'users_results': users_results,
        'has_results': bool(games_results or users_results),
    }

    return render(request, 'search.html', context)