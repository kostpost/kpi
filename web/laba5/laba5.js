// === Завдання 1.2 ===
const products = [
    { id: 1, name: "Ноутбук", price: 25000 },
    { id: 2, name: "Смартфон", price: 15000 },
    { id: 3, name: "Планшет", price: 10000 }
];

function getProductDetails(productId, successCallback, errorCallback) {
    setTimeout(() => {
        const product = products.find(p => p.id === productId);
        if (product) {
            successCallback(product);
        } else {
            errorCallback(`Товар з ID ${productId} не знайдено.`);
        }
    }, 1000);
}

const task1Result = document.getElementById('task1-result');
task1Result.innerHTML = '<p><em>Завантаження даних про товари...</em></p>';

getProductDetails(1, (product) => {
    task1Result.innerHTML += `<p class="success">Знайдено: ${product.name}, ціна: ${product.price} грн.</p>`;
}, (error) => {
    task1Result.innerHTML += `<p class="error">${error}</p>`;
});

getProductDetails(4, (product) => {
    task1Result.innerHTML += `<p class="success">Знайдено: ${product.name}, ціна: ${product.price} грн.</p>`;
}, (error) => {
    task1Result.innerHTML += `<p class="error">${error}</p>`;
});

// === Завдання 1.4 ===
const concerts = {
    Київ: new Date("2020-04-01"),
    Умань: new Date("2025-07-02"),
    Вінниця: new Date("2020-04-21"),
    Одеса: new Date("2025-03-15"),
    Хмельницький: new Date("2020-04-18"),
    Харків: new Date("2025-07-10"),
};

const now = new Date("2025-05-02");

const upcomingCities = Object.keys(concerts)
    .filter(city => concerts[city] > now)
    .sort((a, b) => concerts[a] - concerts[b]);

const task2Result = document.getElementById('task2-result');
if (upcomingCities.length > 0) {
    task2Result.innerHTML = `<p><strong>Майбутні концерти:</strong> ${upcomingCities.join(', ')}</p>`;
} else {
    task2Result.innerHTML = `<p><strong>Майбутні концерти:</strong> Немає концертів після ${now.toLocaleDateString('uk-UA')}.</p>`;
}

// === Завдання 1.6 ===
const medicines = [
    { name: "Noshpa", price: 170 },
    { name: "Analgin", price: 55 },
    { name: "Quanil", price: 310 },
    { name: "Alphacholine", price: 390 },
];

function applyDiscountAndAddId(meds) {
    return meds.map((med, index) => {
        const newPrice = med.price > 300 ? Math.round(med.price * 0.7 * 100) / 100 : med.price;
        return {
            id: index + 1,
            name: med.name,
            originalPrice: med.price,
            price: newPrice,
            hasDiscount: med.price > 300
        };
    });
}

const discountedMedicines = applyDiscountAndAddId(medicines);

const task3Result = document.getElementById('task3-result');
let tableHTML = `
<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Назва</th>
            <th>Початкова ціна</th>
            <th>Ціна зі знижкою</th>
            <th>Знижка</th>
        </tr>
    </thead>
    <tbody>`;

discountedMedicines.forEach(med => {
    const priceDisplay = med.hasDiscount
        ? `<span class="original">${med.originalPrice} грн</span> → <strong class="discount">${med.price} грн</strong>`
        : `${med.price} грн`;

    const discountText = med.hasDiscount ? 'Так (-30%)' : 'Ні';

    tableHTML += `
        <tr>
            <td>${med.id}</td>
            <td>${med.name}</td>
            <td>${med.originalPrice} грн</td>
            <td>${priceDisplay}</td>
            <td>${discountText}</td>
        </tr>`;
});

tableHTML += `</tbody></table>`;
task3Result.innerHTML = tableHTML;

// === Завдання 1.8 ===
function Storage(initialItems = []) {
    this.items = initialItems.slice();
}

Storage.prototype.getItems = function() {
    return this.items.slice();
};

Storage.prototype.addItem = function(item) {
    this.items.push(item);
};

Storage.prototype.removeItem = function(item) {
    const index = this.items.indexOf(item);
    if (index !== -1) {
        this.items.splice(index, 1);
    }
};

const arr = ["apple", "banana", "mango"];
const storage = new Storage(arr);

const task4Output = document.getElementById('task4-output');

let outputText = "";
outputText += "Початкові товари: " + storage.getItems().join(", ") + "\n";
storage.addItem("orange");
outputText += "Після додавання 'orange': " + storage.getItems().join(", ") + "\n";
storage.removeItem("banana");
outputText += "Після видалення 'banana': " + storage.getItems().join(", ") + "\n";
storage.removeItem("grape");
outputText += "Після спроби видалити 'grape' (немає): " + storage.getItems().join(", ") + "\n";

task4Output.textContent = outputText;

// === Завдання 1.10 ===
function checkBrackets(str) {
    const stack = [];
    const pairs = {
        ')': '(',
        '}': '{',
        ']': '['
    };
    const openBrackets = new Set(['(', '{', '[']);

    for (let char of str) {
        if (openBrackets.has(char)) {
            stack.push(char);
        } else if (char in pairs) {
            if (stack.length === 0) {
                return false;
            }
            const lastOpen = stack.pop();
            if (lastOpen !== pairs[char]) {
                return false;
            }
        }
    }
    return stack.length === 0;
}

document.addEventListener('DOMContentLoaded', function() {
    const testCases = [
        "function someFn(a, b) { return [a + b]; }",
        "(function() { console.log({key: [1, 2]}); })",
        "if (x > 0) { arr.push(y); } else { return; }",
        "({[]})",
        "(]",
        "({)}",
        "((())",
        "function(a { return b; }",
        ""
    ];

    const results = testCases.map(code => ({
        code,
        valid: checkBrackets(code)
    }));

    const task5Result = document.getElementById('task5-result');
    if (!task5Result) {
        console.error("Елемент #task5-result не знайдено!");
        return;
    }

    let tableHTML = `
    <table>
        <thead>
            <tr>
                <th>Код</th>
                <th>Результат</th>
            </tr>
        </thead>
        <tbody>`;

    results.forEach(item => {
        const status = item.valid
            ? '<span class="success">true (правильно)</span>'
            : '<span class="error">false (помилка)</span>';

        const displayCode = item.code || '(порожній рядок)';

        tableHTML += `
            <tr>
                <td><code>${displayCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></td>
                <td>${status}</td>
            </tr>`;
    });

    tableHTML += `</tbody></table>`;
    task5Result.innerHTML = tableHTML;
});

// === Завдання 2.2 ===
document.addEventListener('DOMContentLoaded', function() {
    const people = [
        { name: 'John', age: 27 },
        { name: 'Jane', age: 31 },
        { name: 'Bob', age: 19 },
    ];

    const hasYoungPerson = people.some(person => person.age < 20);

    const task6Result = document.getElementById('task6-result');

    if (hasYoungPerson) {
        task6Result.innerHTML = `
            <p class="success">Є хоча б одна людина молодше 20 років.</p>
            <p><strong>Результат:</strong> <code>true</code></p>
            <p><small>Знайдено: ${people.find(p => p.age < 20).name} (вік ${people.find(p => p.age < 20).age})</small></p>
        `;
    } else {
        task6Result.innerHTML = `
            <p class="error">Усі люди старше або дорівнюють 20 рокам.</p>
            <p><strong>Результат:</strong> <code>false</code></p>
        `;
    }
});

// === Завдання 2.4 ===
document.addEventListener('DOMContentLoaded', function() {
    const numbers = [1, 2, 3, 4, 5];

    const squaredNumbers = numbers.map(num => num * num);

    const task7Result = document.getElementById('task7-result');

    task7Result.innerHTML = `
        <p><strong>Вхідний масив:</strong> [${numbers.join(', ')}]</p>
        <p><strong>Масив квадратів:</strong> [${squaredNumbers.join(', ')}]</p>
        <p class="success">Результат отримано правильно!</p>
    `;
});

// === Завдання 2.6 ===
document.addEventListener('DOMContentLoaded', function() {
    const users = [
        { name: 'John', age: 27 },
        { name: 'Jane', age: 31 },
        { name: 'Bob', age: 19 },
    ];

    const sortedUsers = [...users].sort((a, b) => a.age - b.age);

    const task8Result = document.getElementById('task8-result');

    let outputHTML = `
        <p><strong>Початковий масив:</strong></p>
        <ul>`;
    users.forEach(user => {
        outputHTML += `<li>{ name: "${user.name}", age: ${user.age} }</li>`;
    });
    outputHTML += `</ul>

        <p><strong>Відсортований за віком (зростання):</strong></p>
        <ul>`;
    sortedUsers.forEach(user => {
        outputHTML += `<li>{ name: "${user.name}", age: ${user.age} }</li>`;
    });
    outputHTML += `</ul>

        <p class="success">Масив успішно відсортований!</p>
    `;

    task8Result.innerHTML = outputHTML;
});

// === Завдання 2.8 ===
document.addEventListener('DOMContentLoaded', function() {
    class Calculator {
        constructor() {
            this.result = 0;
        }

        number(value) {
            this.result = value;
            return this;
        }

        add(value) {
            this.result += value;
            return this;
        }

        subtract(value) {
            this.result -= value;
            return this;
        }

        multiply(value) {
            this.result *= value;
            return this;
        }

        divide(value) {
            if (value === 0) {
                throw new Error("Помилка: ділення на нуль неможливе!");
            }
            this.result /= value;
            return this;
        }

        getResult() {
            return this.result;
        }
    }

    let calcResult;
    let outputText = "";

    try {
        const calc = new Calculator();

        calcResult = calc
            .number(10)
            .add(5)
            .subtract(3)
            .multiply(4)
            .divide(2)
            .getResult();

        outputText += `<p class="success">Розрахунок виконано успішно!</p>`;
        outputText += `<p><strong>Результат ланцюжка:</strong> <code>24</code></p>`;
        outputText += `<p><em>Отримано: ${calcResult}</em></p>`;

        outputText += `<hr>`;
        try {
            new Calculator()
                .number(10)
                .divide(0);
            outputText += `<p>Ділення на 0 пройшло (це помилка)</p>`;
        } catch (error) {
            outputText += `<p class="error">${error.message}</p>`;
        }
    } catch (error) {
        outputText += `<p class="error">Помилка при виконанні: ${error.message}</p>`;
    }

    const task9Result = document.getElementById('task9-result');
    task9Result.innerHTML = outputText;
});