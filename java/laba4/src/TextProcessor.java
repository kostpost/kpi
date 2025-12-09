import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

/**
 * Лабораторна робота №3
 * <p>
 * Мета: Використовуючи класи з лабораторної №2 (Letter, Word, Sentence, Text, Punctuation),
 * виконати завдання: у кожному слові видалити всі попередні входження останньої літери.
 * <p>
 * Вимоги:
 * - Використовувати створені класи
 * - Нормалізація пробілів
 * - Коректна обробка знаків пунктуації
 * - Код відповідає Google Java Style Guide
 * - Повна Javadoc-документація
 *
 * @author Твоє ім'я
 */
public class TextProcessor {

    /** Точка входу в програму. */


    /** Виконавчий метод — містить усю логіку програми. */
    public void run() {
        try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
            System.out.println("Введіть текст:");
            String input = scanner.nextLine();

            Text text = Text.fromString(input);
            String result = text.processAndToString();

            System.out.println("Результат:");
            System.out.println(result.isEmpty() ? "(порожній рядок)" : result);

        } catch (Exception e) {
            System.err.println("Помилка: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

/** Клас, що представляє одну літеру. */
class Letter {
    private final char value;

    Letter(char value) {
        this.value = value;
    }

    char getValue() {
        return value;
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }
}

/** Клас, що представляє слово — масив літер. */
class Word {
    private final List<Letter> letters = new ArrayList<>();

    Word(String str) {
        for (char c : str.toCharArray()) {
            letters.add(new Letter(c));
        }
    }

    /** Видаляє всі попередні входження останньої літери (завдання). */
    Word transform() {
        if (letters.size() <= 1) {
            return this;
        }
        char lastChar = letters.get(letters.size() - 1).getValue();

        List<Letter> transformed = new ArrayList<>();
        for (int i = 0; i < letters.size() - 1; i++) {
            if (letters.get(i).getValue() != lastChar) {
                transformed.add(letters.get(i));
            }
        }
        transformed.add(letters.get(letters.size() - 1));

        return new Word(transformed);
    }

    private Word(List<Letter> list) {
        letters.addAll(list);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (Letter l : letters) sb.append(l.getValue());
        return sb.toString();
    }
}

/** Клас, що представляє розділовий знак. */
class Punctuation {
    private final char sign;

    Punctuation(char sign) {
        this.sign = sign;
    }

    @Override
    public String toString() {
        return String.valueOf(sign);
    }
}

/** Клас, що представляє речення — послідовність слів і знаків пунктуації. */
class Sentence {
    final List<Object> elements = new ArrayList<>(); // Word або Punctuation

    void addWord(Word word) {
        elements.add(word.transform());
    }

    void addPunctuation(char sign) {
        elements.add(new Punctuation(sign));
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < elements.size(); i++) {
            Object el = elements.get(i);
            sb.append(el instanceof Word w ? w.toString() : ((Punctuation) el).toString());

            if (i < elements.size() - 1) {
                Object next = elements.get(i + 1);
                boolean needSpace = (el instanceof Word) || (next instanceof Word);
                if (needSpace) {
                    sb.append(' ');
                }
            }
        }
        return sb.toString();
    }
}

/** Клас, що представляє текст — масив речень. */
class Text {
    private final List<Sentence> sentences = new ArrayList<>();

    private Text() {}

    /**
     * Створює об'єкт Text з рядка.
     *
     * @param input вхідний текст
     * @return оброблений об'єкт Text
     */
    public static Text fromString(String input) {
        Text text = new Text();
        String normalized = input.replaceAll("\\s+", " ").trim();

        Sentence currentSentence = new Sentence();
        StringBuilder wordBuffer = new StringBuilder();

        for (int i = 0; i < normalized.length(); i++) {
            char c = normalized.charAt(i);

            if (c == ' ') {
                if (wordBuffer.length() > 0) {
                    currentSentence.addWord(new Word(wordBuffer.toString()));
                    wordBuffer.setLength(0);
                }
                continue;
            }

            if (isPunctuation(c)) {
                if (wordBuffer.length() > 0) {
                    currentSentence.addWord(new Word(wordBuffer.toString()));
                    wordBuffer.setLength(0);
                }
                currentSentence.addPunctuation(c);

                boolean isSentenceEnd = (c == '.' || c == '!' || c == '?') &&
                        (i + 1 >= normalized.length() || !isPunctuation(normalized.charAt(i + 1)));

                if (isSentenceEnd && !currentSentence.elements.isEmpty()) {
                    text.sentences.add(currentSentence);
                    currentSentence = new Sentence();
                }
            } else {
                wordBuffer.append(c);
            }
        }

        if (wordBuffer.length() > 0) {
            currentSentence.addWord(new Word(wordBuffer.toString()));
        }
        if (!currentSentence.elements.isEmpty()) {
            text.sentences.add(currentSentence);
        }

        return text;
    }

    private static boolean isPunctuation(char c) {
        return ",.!?;:-–—\"'()[]{}".indexOf(c) != -1;
    }

    /**
     * Повертає оброблений текст як рядок.
     *
     * @return оброблений текст
     */
    public String processAndToString() {
        if (sentences.isEmpty()) return "";
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < sentences.size(); i++) {
            if (i > 0) result.append(' ');
            result.append(sentences.get(i));
        }
        return result.toString();
    }
}