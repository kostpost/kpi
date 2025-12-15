// function createArray() {
//     const n = Number(prompt("Введіть кількість елементів масиву:"));
//     if (isNaN(n) || n <= 0) {
//         console.log("Некоректне значення кількості елементів");
//         return null;
//     }
//
//     const arr = [];
//     for (let i = 0; i < n; i++) {
//         const value = Number(prompt(`Введіть елемент ${i + 1} з ${n}:`));
//         if (isNaN(value)) {
//             console.log("Некоректне значення елемента");
//             return null;
//         }
//         arr.push(value);
//     }
//     return arr;
// }
//
// function findMinMaxIndices(arr) {
//     let minIndex = 0;
//     let maxIndex = 0;
//     for (let i = 1; i < arr.length; i++) {
//         if (arr[i] < arr[minIndex]) minIndex = i;
//         if (arr[i] > arr[maxIndex]) maxIndex = i;
//     }
//     return { minIndex, maxIndex };
// }
//
// function sumBetweenMinAndMax(arr) {
//     if (arr.length < 2) return 0;
//
//     const { minIndex, maxIndex } = findMinMaxIndices(arr);
//     const start = Math.min(minIndex, maxIndex) + 1;
//     const end = Math.max(minIndex, maxIndex);
//
//     let sum = 0;
//     for (let i = start; i < end; i++) {
//         sum += arr[i];
//     }
//     return sum;
// }
//
// function partition(arr, low, high) {
//     const pivot = arr[high];
//     let i = low - 1;
//
//     for (let j = low; j < high; j++) {
//         if (arr[j] < pivot) {
//             i++;
//             [arr[i], arr[j]] = [arr[j], arr[i]];
//         }
//     }
//     [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
//     return i + 1;
// }
//
// function quickSort(arr, low = 0, high = arr.length - 1) {
//     if (low < high) {
//         const pi = partition(arr, low, high);
//         quickSort(arr, low, pi - 1);
//         quickSort(arr, pi + 1, high);
//     }
//     return arr;
// }
//
// const originalArray = createArray();
//
// if (originalArray) {
//     console.log("Вхідний масив:", [...originalArray]);
//
//     const sum = sumBetweenMinAndMax(originalArray);
//     console.log("Сума елементів між мінімальним та максимальним:", sum);
//
//     const sortedArray = [...originalArray];
//     quickSort(sortedArray);
//     console.log("Відсортований масив (швидке сортування):", sortedArray);
// }