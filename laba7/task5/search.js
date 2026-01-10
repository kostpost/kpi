const API_KEY = '54117029-0d3ad1dc2964c162212ff1bde';

const form = document.querySelector('.search-form');
const gallery = document.querySelector('.gallery');
const loader = document.querySelector('.loader');

const lightbox = new SimpleLightbox('.gallery a', {
    captionsData: 'alt',
    captionDelay: 250,
});

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const query = form.elements.query.value.trim();

    if (!query) {
        iziToast.warning({
            message: 'Введіть запит для пошуку!',
            position: 'topRight',
        });
        return;
    }

    loader.style.display = 'block';
    gallery.innerHTML = '';

    try {
        const url = `https://pixabay.com/api/?key=${API_KEY}&q=${encodeURIComponent(query)}&image_type=photo&orientation=horizontal&safesearch=true`;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Помилка сервера: ${response.status}`);
        }

        const data = await response.json();

        if (!data.hits || data.hits.length === 0) {
            iziToast.info({
                message: 'Sorry, there are no images matching your search query. Please try again!',
                position: 'topRight',
            });
            return;
        }

        const markup = data.hits.map((img) => `
      <a href="${img.largeImageURL}" class="gallery-link">
        <img 
          src="${img.webformatURL}" 
          alt="${img.tags || 'Зображення з Pixabay'}" 
          loading="lazy"
        >
        <div class="info">
          <p>Likes: ${img.likes}</p>
          <p>Views: ${img.views}</p>
          <p>Comments: ${img.comments}</p>
          <p>Downloads: ${img.downloads}</p>
        </div>
      </a>
    `).join('');

        gallery.innerHTML = markup;

        lightbox.refresh();

    } catch (error) {
        iziToast.error({
            message: 'Щось пішло не так! Спробуйте пізніше.',
            position: 'topRight',
        });
        console.error('Помилка запиту:', error);
    } finally {
        loader.style.display = 'none';
        form.reset();
    }
});