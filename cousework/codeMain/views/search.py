import requests
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User
from games.aut.models import Profile

RAWG_API_KEY = "52cb9ffb113b485299bb0625e7c9b503"  # заміни на свій!


# Загальний пошук: користувачі + ігри через RAWG API
def search(request):
    # Отримуємо пошуковий запит з GET-параметра
    query = request.GET.get('q', '').strip()

    games_results = []
    users_results = []

    if query:
        # Пошук користувачів за частиною імені (username)
        users_results = User.objects.filter(
            Q(username__icontains=query)
        ).select_related('profile')[:12]

        # Пошук ігор через RAWG API
        try:
            url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={query}&page_size=20"
            resp = requests.get(url, timeout=8)

            if resp.status_code == 200:
                data = resp.json()
                # Беремо тільки перші 12 результатів
                games_results = data.get('results', [])[:12]
            else:
                print(f"RAWG повернув статус {resp.status_code} для запиту '{query}'")

        except requests.exceptions.RequestException as e:
            print(f"Мережева помилка RAWG при пошуку '{query}': {e}")
        except ValueError as e:
            print(f"Помилка парсингу JSON від RAWG для '{query}': {e}")
        except Exception as e:
            print(f"Несподівана помилка RAWG при пошуку '{query}': {e}")

    context = {
        'query': query,
        'games_results': games_results,
        'users_results': users_results,
        'has_results': bool(games_results or users_results),
    }

    return render(request, 'search.html', context)