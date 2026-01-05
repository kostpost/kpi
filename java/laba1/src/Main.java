import java.util.Arrays;
import java.util.Random;

/**
 * Лабораторна робота №X. Тема: Масиви в мові програмування Java
 * Група: ІП-з31к
 * Виконав: Ткаченко Костянтин
 *
 * Завдання:
 * 1. Сформувати квадратну матрицю 6×6 з випадковими цілими числами [-100..99]
 * 2. Вивести початкову матрицю
 * 3. Побудувати транспоновану матрицю
 * 4. Вивести транспоновану матрицю
 * 5. Для кожного рядка транспонованої матриці:
 *    - якщо номер рядка парний → знайти найменший елемент рядка
 *    - якщо номер рядка непарний → знайти найбільший елемент рядка
 * 6. Вивести знайдені екстремуми та їх суму
 */
public class Main {

    private static final int SIZE = 6;
    private static final int MIN_VALUE = -100;
    private static final int MAX_VALUE = 99;
    private static final int RANGE = MAX_VALUE - MIN_VALUE + 1;

    public static void main(String[] args) {
        Random random = new Random();

        // створення матриці
        short[][] matrix = new short[SIZE][SIZE];

        System.out.println("Початкова матриця A (" + SIZE + "×" + SIZE + "):");
        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                matrix[i][j] = (short) (random.nextInt(RANGE) + MIN_VALUE);
            }
            System.out.println(Arrays.toString(matrix[i]));
        }
        System.out.println();

        short[][] transposed = new short[SIZE][SIZE];
        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                transposed[i][j] = matrix[j][i];
            }
        }

        System.out.println("Транспонована матриця B = Aᵀ:");
        for (short[] row : transposed) {
            System.out.println(Arrays.toString(row));
        }
        System.out.println();

        // обробка рядків та підрахунок суми екстремумів
        long sumOfExtremes = 0;

        System.out.println("Екстремуми по рядках транспонованої матриці:");
        for (int i = 0; i < SIZE; i++) {
            short extreme;
            String description;

            if (i % 2 == 0) {
                // парний рядок / найменший елемент
                extreme = transposed[i][0];
                for (int j = 1; j < SIZE; j++) {
                    if (transposed[i][j] < extreme) {
                        extreme = transposed[i][j];
                    }
                }
                description = "найменший";
            } else {
                // непарний рядок / найбільший елемент
                extreme = transposed[i][0];
                for (int j = 1; j < SIZE; j++) {
                    if (transposed[i][j] > extreme) {
                        extreme = transposed[i][j];
                    }
                }
                description = "найбільший";
            }

            System.out.printf("Рядок %d (%s) → %s елемент = %3d%n",
                    i, (i % 2 == 0) ? "парний " : "непарний", description, extreme);

            sumOfExtremes += extreme;
        }

        System.out.println("─".repeat(45));
        System.out.println("Сума всіх знайдених екстремумів: " + sumOfExtremes);
    }
}