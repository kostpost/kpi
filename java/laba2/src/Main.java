import java.nio.charset.StandardCharsets;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
            System.out.println("введіть текст:");
            String input = scanner.nextLine().trim();

            String result = processText(input);
            System.out.println("результат:");
            System.out.println(result.isEmpty() ? "(порожній рядок)" : result);

        } catch (Exception e) {
            System.err.println("Помилка: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static String processText(String text) {
        if (text.isEmpty()) return "";

        StringBuilder result = new StringBuilder();
        StringBuilder word = new StringBuilder();

        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);

            if (Character.isWhitespace(c)) {
                if (!word.isEmpty()) {
                    result.append(transformWord(word));
                    word.setLength(0);
                }
                result.append(c);
            } else {
                word.append(c);
            }
        }

        if (!word.isEmpty()) {
            result.append(transformWord(word));
        }

        return result.toString();
    }

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