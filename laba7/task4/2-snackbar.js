const form = document.querySelector('.form');

form.addEventListener('submit', (e) => {
    e.preventDefault();

    const delay = Number(form.delay.value);
    const state = form.state.value;

    // Створюємо проміс
    const promise = new Promise((resolve, reject) => {
        setTimeout(() => {
            if (state === 'fulfilled') {
                resolve(delay);
            } else {
                reject(delay);
            }
        }, delay);
    });

    promise
        .then((delay) => {
            iziToast.success({
                message: `Fulfilled promise in ${delay}ms`,
                position: 'topRight',
                timeout: 3000
            });
        })
        .catch((delay) => {
            iziToast.error({
                message: `Rejected promise in ${delay}ms`,
                position: 'topRight',
                timeout: 3000
            });
        });
});