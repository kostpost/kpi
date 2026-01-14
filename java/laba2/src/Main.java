import java.nio.charset.StandardCharsets;
import java.util.Scanner;

/**
 * Лабораторна робота
 * c3 = 1, c17 - 16
 *  Тип = String
 *  Дія з текстом =  В кожному слові заданого тексту, видалити всі попередні входження останньої літери цього слова.
 * Виконав: Ткаченко Костянтин
 * Група: ІП-з31к
 */
public class Main {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Введіть текст: ");
        String inputText = scanner.nextLine().trim();

        if (inputText.isEmpty()) {
            System.out.println("порожній рядок");
            scanner.close();
            return;
        }

        String result = "";
        String currentWord = "";

        for (int i = 0; i < inputText.length(); i++) {
            char ch = inputText.charAt(i);

            if (Character.isWhitespace(ch)) {
                if (!currentWord.isEmpty()) {
                    result += processWord(currentWord);
                    currentWord = "";
                }
                result += ch;
            } else {
                currentWord += ch;
            }
        }

        // останнє слово
        if (!currentWord.isEmpty()) {
            result += processWord(currentWord);
        }

        System.out.println("Результат:");
        System.out.println(result);

        scanner.close();
    }

    /**
     * Перетворює одне слово за правилом:
     * залишає останній символ,
     * видаляє всі попередні входження цього ж символу
     */
    private static String processWord(String word) {
        if (word.length() <= 1) {
            return word;
        }

        char lastChar = word.charAt(word.length() - 1);
        String processed = "";

        for (int i = 0; i < word.length() - 1; i++) {
            char current = word.charAt(i);
            if (current != lastChar) {
                processed += current;
            }
        }

        processed += lastChar;  //  останній символ

        return processed;
    }
}