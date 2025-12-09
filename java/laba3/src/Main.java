import java.util.Arrays;
import java.util.Comparator;

/**
 * Лабораторна робота: створення та обробка масиву об’єктів класу «Одяг».
 * Варіант — клас Одяг (Clothes).
 *
 * @author Ткаченко Костянтин
 */
public class Main {
    public static void main(String[] args) {
        Clothes[] wardrobe = {
                new Clothes("Футболка Nike",     "M",  "білий",   799.99,  "бавовна"),
                new Clothes("Джинси Levi’s",     "32", "синій",  2499.00,  "денім"),
                new Clothes("Куртка шкіряна",    "L",  "чорний", 5999.00,  "шкіра"),
                new Clothes("Светр кашеміровий", "S",  "сірий",  3499.50,  "кашемір"),
                new Clothes("Шорти спортивні",   "XL", "чорний",  899.00,  "поліестер"),
                new Clothes("Сукня вечірня",     "M",  "червоний",4299.00, "шовк"),
                new Clothes("Худі Adidas",       "L",  "сірий",  2199.99,  "бавовна"),
                new Clothes("Штани карго",       "34", "зелений",1899.00, "бавовна")
        };

        System.out.println("Початковий масив:");
        printArray(wardrobe);

        Arrays.sort(wardrobe, Comparator.comparingDouble(Clothes::getPrice));
        System.out.println("\nВідсортовано за ціною (за зростанням):");
        printArray(wardrobe);

        // (лексикографічно)
        Arrays.sort(wardrobe, Comparator.comparing(Clothes::getColor, Comparator.reverseOrder()));
        System.out.println("\nВідсортовано за кольором (за спаданням):");
        printArray(wardrobe);

       Clothes target = new Clothes("Худі Adidas", "L", "сірий", 2199.99, "бавовна");

        int index = Arrays.binarySearch(wardrobe, target,
                Comparator.comparing(Clothes::getName)
                        .thenComparing(Clothes::getSize)
                        .thenComparing(Clothes::getColor)
                        .thenComparingDouble(Clothes::getPrice)
                        .thenComparing(Clothes::getMaterial));

        System.out.println("\nПошук об’єкта:");
        System.out.println(target);

        if (index >= 0) {
            System.out.println("Знайдено на позиції: " + index);
            System.out.println("Знайдений: " + wardrobe[index]);
        } else {
            System.out.println("Не знайдено в масиві");
        }
    }


    private static void printArray(Clothes[] array) {
        for (int i = 0; i < array.length; i++) {
            System.out.printf("%2d. %s%n", i + 1, array[i]);
        }
    }

    public static class Clothes {

        public String Name;
        public String Size;
        public String Color;
        public double Price;
        public String material;

        public Clothes(String name, String size, String color, double price, String material) {
            Name = name;
            Size = size;
            Color = color;
            Price = price;
            this.material = material;
        }

        @Override
        public String toString() {
            return String.format("%-20s | розмір: %-4s | колір: %-10s | ціна: %8.2f грн | матеріал: %s",
                    Name, Size, Color, Price, material);
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Clothes)) return false;
            Clothes that = (Clothes) o;
            return Double.compare(that.Price, Price) == 0 &&
                    Name.equals(that.Name) &&
                    Size.equals(that.Size) &&
                    Color.equals(that.Color) &&
                    material.equals(that.material);
        }

        @Override
        public int hashCode() {
            int result = Name.hashCode();
            result = 31 * result + Size.hashCode();
            result = 31 * result + Color.hashCode();
            result = 31 * result + Double.hashCode(Price);
            result = 31 * result + material.hashCode();
            return result;
        }

        public String getMaterial() {
            return material;
        }

        public void setMaterial(String material) {
            this.material = material;
        }

        public double getPrice() {
            return Price;
        }

        public void setPrice(double price) {
            Price = price;
        }

        public String getColor() {
            return Color;
        }

        public void setColor(String color) {
            Color = color;
        }

        public String getSize() {
            return Size;
        }

        public void setSize(String size) {
            Size = size;
        }

        public String getName() {
            return Name;
        }

        public void setName(String name) {
            Name = name;
        }

    }
}

