// let input = "14:25";
//
// input = input.trim();
//
// const timeRegex = /^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$/;
//
// if (!timeRegex.test(input)) {
//     console.log("ПОМИЛКА: Неправильний формат часу! Має бути год:хв (наприклад, 09:45 або 23:59)");
// } else {
//     console.log(`Введений час: ${input}`);
//
//     const [hours, minutes] = input.split(":").map(Number);
//
//     let quarter;
//     if (minutes <= 15) {
//         quarter = "Перша чверть години";
//     } else if (minutes <= 30) {
//         quarter = "Друга чверть години";
//     } else if (minutes <= 45) {
//         quarter = "Третя чверть години";
//     } else {
//         quarter = "Четверта чверть години";
//     }
//
//     console.log(quarter);
//     console.log(`---------`);
// }
//
//
//
//
//
//
// let day = prompt("Введіть номер дня тижня (від 1 до 7)");
//
// if (day === null || day.trim() === "") {
//     alert("Ви не ввели значення або скасували введення.");
//     console.log("ПОМИЛКА: Користувач не ввів значення.");
// } else {
//     day = day.trim();
//
//     const dayRegex = /^[1-7]$/;
//
//     if (!dayRegex.test(day)) {
//         alert("Некоректне значення! Введіть число від 1 до 7.");
//         console.log("ПОМИЛКА: Некоректне значення – " + day);
//     } else {
//         let finish;
//
//         switch (day) {
//             case "1":
//                 finish = "понеділок";
//                 break;
//             case "2":
//                 finish = "вівторок";
//                 break;
//             case "3":
//                 finish = "середа";
//                 break;
//             case "4":
//                 finish = "четвер";
//                 break;
//             case "5":
//                 finish = "п'ятниця";
//                 break;
//             case "6":
//                 finish = "субота";
//                 break;
//             case "7":
//                 finish = "неділя";
//                 break;
//         }
//
//         console.log(`Введене значення: ${day}`);
//         console.log(`День тижня: ${finish}`);
//         alert(finish);
//         console.log(`---------`);
//
//     }
// }
//
//
//
//
//
//
//
//
//
// const users = {
//     "user1": "1",
//     "user2": "2",
//     "user3": "3"
// };
//
// function askLogin() {
//     let login = prompt("Введіть логін:");
//
//     if (login === null || login.trim() === "") {
//         console.log("Користувач скасував введення або залишив поле порожнім");
//         alert("Ви нічого не ввели. Спробуйте ще раз.");
//         askLogin();
//         return;
//     }
//
//     login = login.trim();
//
//     console.log(`Введений логін: ${login}`);
//
//     if (users[login]) {
//         let password = prompt(`Введіть пароль для ${login}:`);
//
//         if (password === null || password.trim() === "") {
//             console.log(`Користувач ${login} скасував введення пароля`);
//             alert("Пароль не введено. Спробуйте ще раз.");
//             askLogin();
//             return;
//         }
//
//         password = password.trim();
//
//         if (password === users[login]) {
//             console.log(`Успішна авторизація для ${login}`);
//             alert(`Hello, ${login}`);
//         } else {
//             console.log(`Неправильний пароль для ${login}`);
//             alert("Неправильний пароль!");
//             askLogin();
//         }
//     } else {
//         console.log(`Невідомий користувач: ${login}`);
//         alert("I don't know you");
//         askLogin();
//     }
// }
// askLogin();
// console.log(`---------`);










function getShippingMessage(country, price, deliveryFee) {
    const totalPrice = price + deliveryFee;
    return `Shipping to ${country} will cost ${totalPrice} credits`;
}
console.log(getShippingMessage("Germany", 80, 20));






function makeTransaction(quantity, pricePerDroid, customerCredits) {
    const totalPrice = quantity * pricePerDroid;

    if (totalPrice > customerCredits) {
        return "Insufficient funds!";
    } else {
        return `You ordered ${quantity} droids worth ${totalPrice} credits!`;
    }
}
console.log(makeTransaction(5, 3000, 1));
console.log(makeTransaction(3, 1000, 15000));






function makeArray(firstArray, secondArray, maxLength) {
    const newArray = firstArray.concat(secondArray);

    if (newArray.length > maxLength) {
        return newArray.slice(0, maxLength);
    } else {
        return newArray;
    }
}

console.log(makeArray(["Mango", "Plum"], ["Apple", "Orange"], 4));
console.log(makeArray(["Earth", "Jupiter"], ["Neptune", "Uranus"], 3));





const rows = 5;
const cols = 5;
const matrix = [];

for (let i = 0; i < rows; i++) {
    matrix[i] = [];
    for (let j = 0; j < cols; j++) {
        matrix[i][j] = Math.floor(Math.random() * 101) - 50;
    }
}

console.log("Початковий двовимірний масив:");
console.table(matrix);

const firstElement = matrix[0][0];
const lastElement = matrix[rows - 1][cols - 1];

console.log(`Перший елемент: ${firstElement}`);
console.log(`Останній елемент: ${lastElement}`);

matrix[0].splice(2, 0, 25);

console.log("Масив після вставки 25 після другого елемента:");
console.table(matrix);



