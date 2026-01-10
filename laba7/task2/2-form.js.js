
const form = document.querySelector('.feedback-form');
const LOCALSTORAGE_KEY = 'feedback-form-state';

let formData = { email: '', message: '' };

function populateForm() {
    const savedData = localStorage.getItem(LOCALSTORAGE_KEY);
    if (savedData) {
        formData = JSON.parse(savedData);
        form.elements.email.value = formData.email;
        form.elements.message.value = formData.message;
    }
}

populateForm();

form.addEventListener('input', (event) => {
    formData[event.target.name] = event.target.value.trim();

    localStorage.setItem(LOCALSTORAGE_KEY, JSON.stringify(formData));
});

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const { email, message } = formData;

    if (!email.trim() || !message.trim()) {
        alert('Fill please all fields');
        return;
    }

    console.log('Відправляємо:', formData);

    localStorage.removeItem(LOCALSTORAGE_KEY);
    formData = { email: '', message: '' };
    form.reset();
});