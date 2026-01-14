import java.util.Arrays;
import java.util.Random;

/**
 * C5 = 1, C7 = 2, C11 = 5
 * Дія з матрицею(ями) =  C = aB , де a — константа
 * Тип елементів матриці = short
 * Дія з матрицею С = Обчислити суму найбільших елементів в стовпцях матриці з непарними номерами та найменших елементів в стовпцях матриці з парними номерами
 * Лабораторна робота №1. Тема: Масиви в мові програмування Java
 * Група: ІП-з31к
 * Виконав: Ткаченко Костянтин
 */
public class Main {

    private static final int SIZE = 6;
    private static final short MIN_VALUE = -100;
    private static final short MAX_VALUE = 99;
    private static final short constant = -3;

    public static void main(String[] args) {
        Random random = new Random();

        // матрицю A
        short[][] A = generateRandomMatrix(random);
        printMatrix("Початкова матриця A:", A);

        //  матрицю B = Aᵀ
        short[][] B = transpose(A);
        printMatrix("Транспонована матриця B = Aᵀ:", B);

        //  C = a · B
        short[][] C;
        try {
            C = multiplyByScalar(B);
            printMatrix("Результуюча матриця C = " + constant + " · B:", C);
        } catch (ArithmeticException e) {
            System.err.println("Помилка переповнення при множенні на скаляр: " + e.getMessage());
            return;
        }

        //  Обчислюємо потрібну суму по стовпцях матриці C
        try {
            long sumOfExtremes = computeColumnExtremesSum(C);
            System.out.println("─".repeat(50));
            System.out.printf("Сума екстремумів по стовпцях матриці C:%n" +
                    "  • парні стовпці (0,2,4)   → мінімум%n" +
                    "  • непарні стовпці (1,3,5) → максимум%n" +
                    "Результат: %,d%n", sumOfExtremes);
        } catch (Exception e) {
            System.err.println("Помилка під час обчислення суми екстремумів: " + e.getMessage());
        }
    }

    /**
     * Генерує квадратну матрицю SIZE×SIZE з випадковими значеннями [MIN_VALUE..MAX_VALUE]
     */
    private static short[][] generateRandomMatrix(Random random) {
        short[][] matrix = new short[SIZE][SIZE];
        int range = MAX_VALUE - MIN_VALUE + 1;

        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                matrix[i][j] = (short) (random.nextInt(range) + MIN_VALUE);
            }
        }
        return matrix;
    }

    /**
     * Транспонує матрицю
     */
    private static short[][] transpose(short[][] matrix) {
        if (matrix == null || matrix.length == 0 || matrix.length != matrix[0].length) {
            throw new IllegalArgumentException("Матриця повинна бути квадратною та не null");
        }

        short[][] result = new short[SIZE][SIZE];
        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                result[i][j] = matrix[j][i];
            }
        }
        return result;
    }

    /**
     * Множить матрицю на скаляр (з перевіркою переповнення)
     */
    private static short[][] multiplyByScalar(short[][] matrix) {
        if (matrix == null || matrix.length == 0) {
            throw new IllegalArgumentException("Матриця не може бути null або порожньою");
        }

        short[][] result = new short[SIZE][SIZE];

        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                long temp = (long) matrix[i][j] * Main.constant;  // запобігаємо переповненню
                if (temp < Short.MIN_VALUE || temp > Short.MAX_VALUE) {
                    throw new ArithmeticException(
                            String.format("Переповнення short: %d * %d = %d (виходить за межі [%d..%d])",
                                    matrix[i][j], Main.constant, temp, Short.MIN_VALUE, Short.MAX_VALUE));
                }
                result[i][j] = (short) temp;
            }
        }
        return result;
    }

    /**
     * Обчислює суму: min(парні стовпці) + max(непарні стовпці) матриці
     */
    private static long computeColumnExtremesSum(short[][] matrix) {
        if (matrix == null || matrix.length != SIZE || matrix[0].length != SIZE) {
            throw new IllegalArgumentException("Матриця повинна бути " + SIZE + "×" + SIZE);
        }

        long sum = 0;

        System.out.println("Екстремуми по стовпцях матриці C:");
        for (int col = 0; col < SIZE; col++) {
            short extreme = matrix[0][col];

            if (col % 2 == 0) {
                // парний стовпець → мінімум
                for (int row = 1; row < SIZE; row++) {
                    if (matrix[row][col] < extreme) {
                        extreme = matrix[row][col];
                    }
                }
                System.out.printf("Стовпець %d (парний)  → min = %4d%n", col, extreme);
            } else {
                // непарний стовпець → максимум
                for (int row = 1; row < SIZE; row++) {
                    if (matrix[row][col] > extreme) {
                        extreme = matrix[row][col];
                    }
                }
                System.out.printf("Стовпець %d (непарний) → max = %4d%n", col, extreme);
            }
            sum += extreme;
        }
        return sum;
    }

    /**
     * Виводить матрицю з підписом
     */
    private static void printMatrix(String title, short[][] matrix) {
        System.out.println(title);
        for (short[] row : matrix) {
            System.out.println(Arrays.toString(row));
        }
        System.out.println();
    }
}