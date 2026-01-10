const images = [
    {
        preview: 'https://images.unsplash.com/photo-1767173760312-d6fa1304c3a3?q=80&w=1036&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D?w=300',
        original: 'https://images.unsplash.com/photo-1767173760312-d6fa1304c3a3?q=80&w=1036&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',

        description: 'Зимні гори',
    },
    {
        preview: 'https://images.unsplash.com/photo-1765871321198-30fffc41e605?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D?w=300',
        original: 'https://images.unsplash.com/photo-1765871321198-30fffc41e605?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        description: 'Водоспад у горах',
    },
    {
        preview: 'https://images.unsplash.com/photo-1766488742306-506acfc8682e?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D?w=300',
        original: 'https://images.unsplash.com/photo-1766488742306-506acfc8682e?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        description: 'Пустиня',
    },
];






const galleryContainer = document.querySelector('.gallery');
const galleryMarkup = images
    .map(({ preview, original, description }) => `
    <li class="gallery-item">
      <a class="gallery-link" href="${original}">
        <img
          class="gallery-image"
          src="${preview}"
          data-source="${original}"
          alt="${description}"
        />
      </a>
    </li>
  `)
    .join('');
galleryContainer.innerHTML = galleryMarkup;







galleryContainer.addEventListener('click', onGalleryClick);

function onGalleryClick(event) {
    event.preventDefault();

    if (event.target.nodeName !== 'IMG') {
        return;
    }

    const largeImageUrl = event.target.dataset.source;

    const instance = basicLightbox.create(`
    <img src="${largeImageUrl}" alt="Велике зображення" width="1400" height="900">
  `);

    instance.show();

    const closeOnEsc = (e) => {
        if (e.code === 'Escape') {
            instance.close();
            window.removeEventListener('keydown', closeOnEsc);
        }
    };

    window.addEventListener('keydown', closeOnEsc);
}