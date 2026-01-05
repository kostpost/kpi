import java.nio.charset.StandardCharsets;
import java.util.Scanner;

/**
 * Лабораторна робота
 * Тема: Рядки в мові програмування Java
 * Мета: Ознайомлення з рядками та використання основних методів їх обробки
 *       в мові програмування Java. Здобуття навичок у використанні рядків
 *       в мові програмування Java.
 *
 * Завдання:
 * - Зчитати текст з клавіатури
 * - У кожному слові залишити останній символ без змін,
 *   а всі попередні символи, що дорівнюють останньому — видалити
 *
 * Виконав: Ткаченко Костянтин
 * Група: ІП-з31к
 */
public class Main {

    public static void main(String[] args) {
        Scanner scanner = null;
        String inputText;
        String finalResult;
        StringBuilder resultBuilder;
        StringBuilder currentWord;
        char currentSymbol;
        int index;

        try {
            scanner = new Scanner(System.in, StandardCharsets.UTF_8);

            System.out.println("введіть текст:");
            inputText = scanner.nextLine().trim();

            // Обробка введеного тексту
            if (inputText.isEmpty()) {
                finalResult = "";
            } else {
                resultBuilder = new StringBuilder();
                currentWord = new StringBuilder();

                for (index = 0; index < inputText.length(); index++) {
                    currentSymbol = inputText.charAt(index);

                    if (Character.isWhitespace(currentSymbol)) {
                        if (!currentWord.isEmpty()) {
                            resultBuilder.append(transformWord(currentWord));
                            currentWord.setLength(0);
                        }
                        resultBuilder.append(currentSymbol);
                    } else {
                        currentWord.append(currentSymbol);
                    }
                }

                // Обробка останнього слова (якщо є)
                if (!currentWord.isEmpty()) {
                    resultBuilder.append(transformWord(currentWord));
                }

                finalResult = resultBuilder.toString();
            }

            System.out.println("результат:");
            System.out.println(finalResult.isEmpty() ? "(порожній рядок)" : finalResult);

        } catch (Exception e) {
            System.err.println("Помилка: " + e.getMessage());
        } finally {
            if (scanner != null) {
                scanner.close();
            }
        }
    }

    /**
     * Перетворює одне слово за правилом:
     * залишає останній символ,
     * видаляє всі попередні входження цього ж символу
     */
    private static StringBuilder transformWord(StringBuilder word) {
        if (word.length() <= 1) {
            return new StringBuilder(word);
        }

        char lastChar = word.charAt(word.length() - 1);
        StringBuilder transformed = new StringBuilder();

        for (int i = 0; i < word.length() - 1; i++) {
            if (word.charAt(i) != lastChar) {
                transformed.append(word.charAt(i));
            }
        }

        transformed.append(lastChar);
        return transformed;
    }
}