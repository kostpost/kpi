import java.util.Arrays;
import java.util.Comparator;

/**
 * Лабораторна робота
 * Тема: Класи в мові програмування Java
 * Мета: Ознайомлення з класами. Використання існуючих та створення власних класів в мові Java.
 *
 * Завдання:
 * - Створити клас «Одяг» (Clothes)
 * - Створити масив об’єктів цього класу
 * - Відсортувати масив за різними критеріями
 * - Виконати бінарний пошук елемента
 *
 * Виконав: Ткаченко Костянтин
 * Група: ІП-з31к
 */
public class Main {

    public static void main(String[] args) {
        // Усі основні змінні оголошуються та ініціалізуються тут
        Clothes[] wardrobe;
        Clothes target;
        int foundIndex;
        Comparator<Clothes> priceComparator;
        Comparator<Clothes> colorComparator;
        Comparator<Clothes> fullSearchComparator;

        wardrobe = new Clothes[]{
                new Clothes("Футболка Nike",     "M",  "білий",   799.99,  "бавовна"),
                new Clothes("Джинси Levi’s",     "32", "синій",  2499.00,  "денім"),
                new Clothes("Куртка шкіряна",    "L",  "чорний", 5999.00,  "шкіра"),
                new Clothes("Светр кашеміровий", "S",  "сірий",  3499.50,  "кашемір"),
                new Clothes("Шорти спортивні",   "XL", "чорний",  899.00,  "поліестер"),
                new Clothes("Сукня вечірня",     "M",  "червоний",4299.00, "шовк"),
                new Clothes("Худі Adidas",       "L",  "сірий",  2199.99,  "бавовна"),
                new Clothes("Штани карго",       "34", "зелений",1899.00, "бавовна")
        };

        System.out.println("Початковий масив одягу:");
        printArray(wardrobe);

        // Сортування за ціною (зростання)
        priceComparator = Comparator.comparingDouble(Clothes::getPrice);
        Arrays.sort(wardrobe, priceComparator);
        System.out.println("\nВідсортовано за ціною (за зростанням):");
        printArray(wardrobe);

        // Сортування за кольором (спадання)
        colorComparator = Comparator.comparing(Clothes::getColor, Comparator.reverseOrder());
        Arrays.sort(wardrobe, colorComparator);
        System.out.println("\nВідсортовано за кольором (за спаданням):");
        printArray(wardrobe);

        // Об’єкт для пошуку
        target = new Clothes("Худі Adidas", "L", "сірий", 2199.99, "бавовна");

        // Компаратор для бінарного пошуку (повний збіг за всіма полями)
        fullSearchComparator = Comparator.comparing(Clothes::getName)
                .thenComparing(Clothes::getSize)
                .thenComparing(Clothes::getColor)
                .thenComparingDouble(Clothes::getPrice)
                .thenComparing(Clothes::getMaterial);

        foundIndex = Arrays.binarySearch(wardrobe, target, fullSearchComparator);

        System.out.println("\nПошук об’єкта:");
        System.out.println("Шукаємо: " + target);

        if (foundIndex >= 0) {
            System.out.println("Знайдено на позиції: " + (foundIndex + 1));
            System.out.println("Знайдений елемент: " + wardrobe[foundIndex]);
        } else {
            System.out.println("Об’єкт не знайдено в масиві");
        }
    }

    /**
     * Виводить масив одягу з нумерацією
     */
    private static void printArray(Clothes[] array) {
        for (int i = 0; i < array.length; i++) {
            System.out.printf("%2d. %s%n", i + 1, array[i]);
        }
    }

    public static class Clothes {
        private String name;
        private String size;
        private String color;
        private double price;
        private String material;

        public Clothes(String name, String size, String color, double price, String material) {
            this.name = name;
            this.size = size;
            this.color = color;
            this.price = price;
            this.material = material;
        }

        @Override
        public String toString() {
            return String.format("%-20s | розмір: %-4s | колір: %-10s | ціна: %8.2f грн | матеріал: %s",
                    name, size, color, price, material);
        }

        // Геттери (всі поля приватні → потрібні для компараторів)
        public String getName() {
            return name;
        }

        public String getSize() {
            return size;
        }

        public String getColor() {
            return color;
        }

        public double getPrice() {
            return price;
        }

        public String getMaterial() {
            return material;
        }

        // equals та hashCode (за бажанням викладача можна залишити або прибрати)
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Clothes that)) return false;
            return Double.compare(that.price, price) == 0 &&
                    name.equals(that.name) &&
                    size.equals(that.size) &&
                    color.equals(that.color) &&
                    material.equals(that.material);
        }

        @Override
        public int hashCode() {
            int result = name.hashCode();
            result = 31 * result + size.hashCode();
            result = 31 * result + color.hashCode();
            result = 31 * result + Double.hashCode(price);
            result = 31 * result + material.hashCode();
            return result;
        }
    }
}