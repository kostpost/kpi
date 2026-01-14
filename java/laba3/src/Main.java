import java.util.Arrays;
import java.util.Comparator;

/**
 * Лабораторна робота
 * С11 = 5,
 * Варіант завдання = Визначити клас косметика, який складається як мінімум з 5-и полів.
 * Виконав: Ткаченко Костянтин
 * Група: ІП-з31к
 */
public class Main {

    public static void main(String[] args) {

        Cosmetic[] products = {
                new Cosmetic("Тональний крем",     "Maybelline", "матовий",  649.50,  30, "рідкий"),
                new Cosmetic("Помада",             "MAC",       "глянцева", 1249.00,  3.5, "стійка"),
                new Cosmetic("Туш для вій",        "L'Oréal",   "об'ємна",  549.99,  8.0, "водостійка"),
                new Cosmetic("Палетка тіней",      "Anastasia", "матова",  2899.00, 15.0, "суха"),
                new Cosmetic("Хайлайтер",          "Rare Beauty","сяючий",  1799.50,  8.0, "кремовий"),
                new Cosmetic("Олівець для брів",   "NYX",       "матовий",  399.00,  1.2, "олівець"),
                new Cosmetic("Бронзер",            "Fenty",     "матовий",  2100.00, 12.0, "пудра"),
                new Cosmetic("Фіксатор макіяжу",   "Urban Decay","прозорий", 899.00, 100.0, "спрей")
        };

        System.out.println("Початковий масив косметики:");
        printArray(products);

        // Сортування за ціною — за зростанням
        Comparator<Cosmetic> byPriceAsc = Comparator.comparingDouble(Cosmetic::getPrice);
        Arrays.sort(products, byPriceAsc);

        System.out.println("\nВідсортовано за ціною (за зростанням):");
        printArray(products);

        // Сортування за об'ємом/вагою — за спаданням
        Comparator<Cosmetic> byVolumeDesc = Comparator.comparingDouble(Cosmetic::getVolume).reversed();
        Arrays.sort(products, byVolumeDesc);

        System.out.println("\nВідсортовано за об'ємом (за спаданням):");
        printArray(products);

        // Створення об'єкта для пошуку та пошук
        Cosmetic target = new Cosmetic("Туш для вій", "L'Oréal", "об'ємна", 549.99, 8.0, "водостійка");

        // Компаратор для повного порівняння (binarySearch)
        Comparator<Cosmetic> fullComparator = Comparator
                .comparing(Cosmetic::getName)
                .thenComparing(Cosmetic::getBrand)
                .thenComparing(Cosmetic::getFinish)
                .thenComparingDouble(Cosmetic::getPrice)
                .thenComparingDouble(Cosmetic::getVolume)
                .thenComparing(Cosmetic::getType);

        int index = Arrays.binarySearch(products, target, fullComparator);

        System.out.println("\nПошук об'єкта: " + target);
        if (index >= 0) {
            System.out.println("Знайдено на позиції: " + (index + 1));
            System.out.println("Знайдений елемент: " + products[index]);
        } else {
            System.out.printf("Об'єкт НЕ знайдено (вставка на позицію %d)%n", -(index + 1));
        }
    }

    /**
     * Виводить масив косметичних засобів з нумерацією
     * @param array масив об'єктів Cosmetic
     */
    private static void printArray(Cosmetic[] array) {
        for (int i = 0; i < array.length; i++) {
            System.out.printf("%2d. %s%n", i + 1, array[i]);
        }
    }


    public static class Cosmetic {

        private final String name;
        private final String brand;
        private final String finish;
        private final double price;
        private final double volume;
        private final String type;      //


        public Cosmetic(String name, String brand, String finish,
                        double price, double volume, String type) {
            this.name    = name;
            this.brand   = brand;
            this.finish  = finish;
            this.price   = price;
            this.volume  = volume;
            this.type    = type;
        }

        @Override
        public String toString() {
            return String.format("%-22s %-12s %-10s %8.2f грн  %5.1f мл/г  %s",
                    name, brand, finish, price, volume, type);
        }

        public String  getName()    { return name;    }
        public String  getBrand()   { return brand;   }
        public String  getFinish()  { return finish;  }
        public double  getPrice()   { return price;   }
        public double  getVolume()  { return volume;  }
        public String  getType()    { return type;    }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;

            Cosmetic that = (Cosmetic) o;
            return Double.compare(that.price, price) == 0 &&
                    Double.compare(that.volume, volume) == 0 &&
                    name.equals(that.name) &&
                    brand.equals(that.brand) &&
                    finish.equals(that.finish) &&
                    type.equals(that.type);
        }

        @Override
        public int hashCode() {
            int result = name.hashCode();
            result = 31 * result + brand.hashCode();
            result = 31 * result + finish.hashCode();
            result = 31 * result + Double.hashCode(price);
            result = 31 * result + Double.hashCode(volume);
            result = 31 * result + type.hashCode();
            return result;
        }
    }
}