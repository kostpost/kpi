// === Завдання 2 ===
document.addEventListener('DOMContentLoaded', function() {
    const input1 = document.getElementById('input1');
    const input2 = document.getElementById('input2');
    const swapBtn = document.getElementById('swapBtn');

    swapBtn.addEventListener('click', function() {
        const temp = input1.value;
        input1.value = input2.value;
        input2.value = temp;
    });
});


// === Завдання 4 ===
document.addEventListener('DOMContentLoaded', function() {
    const square = document.getElementById('square');
    const decreaseBtn = document.getElementById('decreaseBtn');
    const increaseBtn = document.getElementById('increaseBtn');

    let size = 100;

    decreaseBtn.addEventListener('click', function() {
        if (size > 30) {
            size -= 15;
            square.style.width = size + 'px';
            square.style.height = size + 'px';
        }
    });

    increaseBtn.addEventListener('click', function() {
        size += 15;
        square.style.width = size + 'px';
        square.style.height = size + 'px';
    });
});



// === Завдання 6 ===
document.addEventListener('DOMContentLoaded', function() {
    const listItems = document.querySelectorAll('#numberList li');
    const doubleBtn = document.getElementById('doubleBtn');

    doubleBtn.addEventListener('click', function() {
        listItems.forEach(item => {
            let value = parseInt(item.textContent);
            value *= 2;
            item.textContent = value;
        });
    });
});




// === Завдання 7 ===
document.addEventListener('DOMContentLoaded', function() {
    const categoriesList = document.getElementById('categories');

    // Перевірка: чи існує елемент
    if (!categoriesList) {
        console.error('Елемент з id="categories" не знайдено на сторінці!');
        return;
    }

    const items = categoriesList.querySelectorAll('li.item');

    console.log(`Number of categories: ${items.length}`);

    items.forEach(item => {
        const title = item.querySelector('h2').textContent.trim();
        const elementsCount = item.querySelectorAll('ul li').length;

        console.log(`Category: ${title}`);
        console.log(`Elements: ${elementsCount}`);
    });
});



// === Завдання 8 ===
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const emailInput = loginForm.elements.email;
        const passwordInput = loginForm.elements.password;

        const emailValue = emailInput.value.trim();
        const passwordValue = passwordInput.value.trim();

        if (emailValue === '' || passwordValue === '') {
            alert('All form fields must be filled in');
            return;
        }

        const formData = {
            email: emailValue,
            password: passwordValue
        };

        console.log(formData);

        loginForm.reset();
    });
});



// === Завдання 9 ===
document.addEventListener('DOMContentLoaded', function() {
    const changeColorBtn = document.querySelector('.change-color');
    const colorSpan = document.querySelector('.color');

    function getRandomHexColor() {
        return `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
    }

    changeColorBtn.addEventListener('click', function() {
        const newColor = getRandomHexColor();

        // Змінюємо фон body через інлайн-стиль
        document.body.style.backgroundColor = newColor;

        // Оновлюємо текст у спані
        colorSpan.textContent = newColor;
    });
});







// === Завдання 10 ===
document.addEventListener('DOMContentLoaded', function() {
    const controls = document.getElementById('controls');
    const input = controls.querySelector('input');
    const createBtn = controls.querySelector('[data-create]');
    const destroyBtn = controls.querySelector('[data-destroy]');
    const boxesContainer = document.getElementById('boxes');

    function getRandomHexColor() {
        return `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
    }

    function createBoxes(amount) {
        boxesContainer.innerHTML = '';

        if (amount < 1 || amount > 100) {
            return;
        }

        const fragment = document.createDocumentFragment();
        let size = 30;

        for (let i = 0; i < amount; i++) {
            const div = document.createElement('div');
            div.style.width = `${size}px`;
            div.style.height = `${size}px`;
            div.style.backgroundColor = getRandomHexColor();
            div.style.border = '1px solid #000';
            fragment.appendChild(div);
            size += 10;
        }

        boxesContainer.appendChild(fragment);
    }

    createBtn.addEventListener('click', function() {
        const amount = Number(input.value);

        if (amount >= 1 && amount <= 100) {
            createBoxes(amount);
            input.value = '';
        } else {
            alert('Please enter a number between 1 and 100');
        }
    });

    destroyBtn.addEventListener('click', function() {
        boxesContainer.innerHTML = '';
        input.value = '';
    });
});