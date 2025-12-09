import java.util.Arrays;
import java.util.Random;


public class Main {

    private static final int Size = 6;
    private static final Random RANDOM = new Random();

    public static void main(String[] args) {
        try {
            short[][] aMatrix = createMatrix();
            System.out.println("Матриця B (" + Size + "×" + Size + "):");
            printMatrix(aMatrix);

            short[][] bMatrix = transpose(aMatrix);
            System.out.println("\nРезультат першої дії (C = B^Т):");
            printMatrix(bMatrix);

            calculateSum(bMatrix);


        } catch (NegativeArraySizeException e) {
            System.err.println("Розмір має бути >0\"");
        } catch (Exception e) {
            System.err.println("Невідома помилка: " + e.getMessage());
            e.printStackTrace();
        }
    }


    private static short[][] createMatrix() {
        if (Size <= 0) {
            throw new NegativeArraySizeException("Розмір має бути >0");
        }

        short[][] matrix = new short[Size][Size];
        for (int i = 0; i < Size; i++) {
            for (int j = 0; j < Size; j++) {
                matrix[i][j] = (short) (RANDOM.nextInt(200) - 100);
            }
        }
        return matrix;
    }


    private static short[][] transpose(short[][] original) {
        int n = original.length;
        short[][] transposed = new short[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                transposed[i][j] = original[j][i];
            }
        }
        return transposed;
    }


    private static void calculateSum(short[][] matrix) {
        int n = matrix.length;
        long sum = 0;


        for (int i = 0; i < n; i++) {
            short extreme = matrix[i][0];

            if (i % 2 == 0) {
                for (int j = 1; j < n; j++) {
                    if (matrix[i][j] < extreme) {
                        extreme = matrix[i][j];
                    }
                }
                System.out.println("рядок " + i + " парний -> найменший елемент = " + extreme);
            } else {
                for (int j = 1; j < n; j++) {
                    if (matrix[i][j] > extreme) {
                        extreme = matrix[i][j];
                    }
                }
                System.out.println("рядок " + i + " непарний -> найбільший елемент = " + extreme);
            }

            sum += extreme;
        }

        System.out.println("\nЗагальна сума = " + sum);
    }

    private static void printMatrix(short[][] matrix) {
        for (short[] row : matrix) {
            System.out.println(Arrays.toString(row));
        }
    }
}