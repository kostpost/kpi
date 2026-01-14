// js/script.js

const searchForm = document.getElementById('search-form');
const cityInput = document.getElementById('city-input');
const currentWeatherDiv = document.getElementById('current-weather');
const forecastGrid = document.getElementById('forecast');
const favoritesDiv = document.getElementById('favorites-buttons');
const burgerBtn = document.getElementById('burger-btn');
const navMenu = document.querySelector('.nav-menu');

const API_GEOCODE = 'https://geocoding-api.open-meteo.com/v1/search';
const API_FORECAST = 'https://api.open-meteo.com/v1/forecast';

// Відкриває/закриває бургер-меню на мобільних пристроях
burgerBtn.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});

// Отримує список улюблених міст з localStorage
function getFavorites() {
    return JSON.parse(localStorage.getItem('favorites')) || [];
}

// Зберігає список улюблених міст у localStorage
function saveFavorites(favs) {
    localStorage.setItem('favorites', JSON.stringify(favs));
}

// Відображає кнопки улюблених міст
function renderFavorites() {
    favoritesDiv.innerHTML = '';
    const favs = getFavorites();
    favs.forEach(city => {
        const btn = document.createElement('button');
        btn.textContent = city;
        btn.classList.add('fav-btn');
        btn.addEventListener('click', () => loadWeather(city));

        const removeBtn = document.createElement('span');
        removeBtn.textContent = '×';
        removeBtn.classList.add('remove-fav');
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const updated = favs.filter(c => c !== city);
            saveFavorites(updated);
            renderFavorites();
        });

        btn.appendChild(removeBtn);
        favoritesDiv.appendChild(btn);
    });
}

// Завантажує погоду за назвою міста (основна функція)
async function loadWeather(cityName) {
    if (!cityName.trim()) return;

    // Очищення назви від зайвого (наприклад, з хешу)
    cityName = cityName.trim().replace(/-ukraina$/, '').replace(/-ukraine$/, '').replace(/,.*$/, '').trim();

    showLoading(true);
    hideResults();

    try {
        // Геокодинг: перетворення назви міста в координати
        const geoRes = await fetch(`${API_GEOCODE}?name=${encodeURIComponent(cityName)}&count=1&language=uk&format=json`);
        const geoData = await geoRes.json();

        if (!geoData.results || geoData.results.length === 0) {
            throw new Error('Місто не знайдено. Спробуйте іншу назву.');
        }

        const { latitude, longitude, name, country } = geoData.results[0];
        const displayName = `${name}${country ? ', ' + country : ''}`.trim();

        // Отримання поточної погоди та прогнозу
        const forecastRes = await fetch(
            `${API_FORECAST}?latitude=${latitude}&longitude=${longitude}` +
            `&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m` +
            `&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum` +
            `&timezone=auto&forecast_days=5`
        );

        const data = await forecastRes.json();

        if (data.error) {
            throw new Error(data.reason || 'Помилка отримання даних про погоду');
        }

        renderCurrentWeather(data.current, displayName);
        renderForecast(data.daily);

        currentWeatherDiv.classList.remove('hidden');
        forecastGrid.classList.remove('hidden');

        // Оновлення URL-хешу (тільки назва міста)
        const slug = toUrlSlug(name);
        history.replaceState(null, '', '#' + slug);

    } catch (err) {
        showError(err.message);
    } finally {
        showLoading(false);
    }
}

// Відображає блок поточної погоди + кнопку "Додати в улюблені"
function renderCurrentWeather(current, cityName) {
    const weatherCode = current.weather_code;
    const icon = getWeatherIcon(weatherCode);
    const description = getWeatherDescription(weatherCode);

    currentWeatherDiv.innerHTML = `
    <h2>${cityName}</h2>
    <div class="current-main">
      <img src="https://openweathermap.org/img/wn/${icon}@2x.png" alt="${description}" width="100">
      <div>
        <p class="temp">${Math.round(current.temperature_2m)}°C</p>
        <p>Відчувається: ${Math.round(current.apparent_temperature)}°C</p>
      </div>
    </div>
    <p class="desc">${description}</p>
    <div class="details">
      <p>Вологість: ${current.relative_humidity_2m}%</p>
      <p>Вітер: ${Math.round(current.wind_speed_10m)} км/год</p>
      <p>Опади: ${current.precipitation} мм</p>
    </div>
  `;

    // Кнопка "Додати в улюблені" (додається тільки вручну)
    const favs = getFavorites();
    const isFavorite = favs.includes(cityName);

    const favBtn = document.createElement('button');
    favBtn.textContent = isFavorite ? 'Вже в улюблених' : 'Додати в улюблені';
    favBtn.className = 'add-fav-btn';
    favBtn.disabled = isFavorite;

    if (!isFavorite) {
        favBtn.addEventListener('click', () => {
            favs.push(cityName);
            saveFavorites(favs);
            renderFavorites();
            favBtn.textContent = 'Вже в улюблених';
            favBtn.disabled = true;
        });
    }

    currentWeatherDiv.appendChild(favBtn);
}

// Відображає прогноз на 5 днів
function renderForecast(daily) {
    forecastGrid.innerHTML = '';

    for (let i = 0; i < daily.time.length; i++) {
        const date = new Date(daily.time[i]).toLocaleDateString('uk-UA', { weekday: 'short', day: 'numeric', month: 'short' });
        const icon = getWeatherIcon(daily.weather_code[i]);
        const desc = getWeatherDescription(daily.weather_code[i]);

        const card = document.createElement('div');
        card.classList.add('forecast-card');
        card.innerHTML = `
      <p class="date">${date}</p>
      <img src="https://openweathermap.org/img/wn/${icon}@2x.png" alt="${desc}" width="60">
      <p class="temp-range">${Math.round(daily.temperature_2m_min[i])}° / ${Math.round(daily.temperature_2m_max[i])}°</p>
      <p>${desc}</p>
      <p>Опади: ${daily.precipitation_sum[i]} мм</p>
    `;
        forecastGrid.appendChild(card);
    }
}

// Повертає код іконки погоди (сумісний з OpenWeatherMap)
function getWeatherIcon(code) {
    const map = {
        0: '01d', 1: '02d', 2: '03d', 3: '04d',
        45: '50d', 48: '50d',
        51: '09d', 53: '09d', 55: '09d',
        61: '10d', 63: '10d', 65: '10d',
        71: '13d', 73: '13d', 75: '13d',
        80: '09d', 81: '09d', 82: '09d',
        95: '11d', 96: '11d', 99: '11d'
    };
    return map[code] || '01d';
}

// Повертає текстове описання погоди українською
function getWeatherDescription(code) {
    const desc = {
        0: 'Ясно',
        1: 'Мало хмар',
        2: 'Розсіяні хмари',
        3: 'Хмарно',
        45: 'Туман',
        51: 'Легкий дощ',
        61: 'Дощ',
        71: 'Сніг',
        80: 'Злива',
        95: 'Гроза'
    };
    return desc[code] || 'Невідомо';
}

// Перетворює назву міста в чистий slug для URL-хешу
function toUrlSlug(str) {
    if (!str) return '';

    str = str.split(',')[0].trim();  // тільки назва міста без країни

    const translitMap = {
        'а':'a', 'б':'b', 'в':'v', 'г':'h', 'ґ':'g', 'д':'d', 'е':'e', 'є':'ie', 'ж':'zh',
        'з':'z', 'и':'y', 'і':'i', 'ї':'i', 'й':'i', 'к':'k', 'л':'l', 'м':'m', 'н':'n',
        'о':'o', 'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'kh', 'ц':'ts',
        'ч':'ch', 'ш':'sh', 'щ':'shch', 'ь':'', 'ю':'iu', 'я':'ia',
        'А':'A', 'Б':'B', 'В':'V', 'Г':'H', 'Ґ':'G', 'Д':'D', 'Е':'E', 'Є':'Ie', 'Ж':'Zh',
        'З':'Z', 'И':'Y', 'І':'I', 'Ї':'I', 'Й':'I', 'К':'K', 'Л':'L', 'М':'M', 'Н':'N',
        'О':'O', 'П':'P', 'Р':'R', 'С':'S', 'Т':'T', 'У':'U', 'Ф':'F', 'Х':'Kh', 'Ц':'Ts',
        'Ч':'Ch', 'Ш':'Sh', 'Щ':'Shch', 'Ю':'Iu', 'Я':'Ia'
    };

    return str.split('').map(char => translitMap[char] || char).join('')
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
}

// Показує індикатор завантаження
function showLoading(show) {
    document.body.style.cursor = show ? 'wait' : 'default';
}

// Показує повідомлення про помилку
function showError(msg) {
    currentWeatherDiv.innerHTML = `<p class="error">${msg}</p>`;
    currentWeatherDiv.classList.remove('hidden');
    forecastGrid.classList.add('hidden');
}

// Ховає блоки з погодою
function hideResults() {
    currentWeatherDiv.classList.add('hidden');
    forecastGrid.classList.add('hidden');
}

// Обробка форми пошуку
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const city = cityInput.value.trim();
    if (city) {
        loadWeather(city);
        cityInput.value = '';
    }
});

// Початкове завантаження сторінки
window.addEventListener('load', () => {
    renderFavorites();

    // Завантажуємо місто тільки якщо є хеш у URL
    if (location.hash) {
        let initialCity = location.hash.substring(1).replace(/-/g, ' ').trim();

        // Очищення від зайвого
        if (initialCity.toLowerCase().includes('ukraina') || initialCity.toLowerCase().includes('ukraine')) {
            initialCity = initialCity.split(' ')[0].trim();
        }

        if (initialCity) {
            loadWeather(initialCity);
            cityInput.value = initialCity.charAt(0).toUpperCase() + initialCity.slice(1);
        }
    }
    // Якщо хешу немає — показуємо тільки початковий екран
});