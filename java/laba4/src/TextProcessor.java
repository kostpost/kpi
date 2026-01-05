import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

/**
 * Лабораторна робота №X
 * Тема: Відношення між класами в мові програмування Java
 * Мета: Ознайомлення з відношеннями між класами в мові програмування Java.
 *       Здобуття навичок у використанні відношень між класами в мові програмування Java.
 *
 * Завдання:
 * - Використовуючи класи Letter, Word, Sentence, Text, Punctuation
 * - У кожному слові видалити всі попередні входження останньої літери
 * - Забезпечити нормалізацію пробілів
 * - Коректно обробляти знаки пунктуації
 *
 * Демонструються відношення:
 * - Композиція (Text → Sentence → Word → Letter, Sentence → Punctuation)
 * - Агрегація (List як контейнер)
 * - Використання допоміжних класів
 *
 * @author Ткаченко Костянтин
 * @group ІП-з31к
 */
public class TextProcessor {

    public static void main(String[] args) {
        // Усі основні змінні оголошуються та ініціалізуються у виконавчому методі

        String inputText;
        Text textObject;
        String processingResult;
        try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {

            System.out.println("Введіть текст:");
            inputText = scanner.nextLine();

            // Створення та обробка об'єкта Text
            textObject = Text.fromString(inputText);
            processingResult = textObject.processAndToString();

            System.out.println("\nРезультат обробки:");
            System.out.println(processingResult.isEmpty()
                    ? "(порожній рядок)"
                    : processingResult);

        } catch (Exception e) {
            System.err.println("Помилка: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

/** Клас, що представляє одну літеру (найнижчий рівень ієрархії). */
class Letter {
    private final char value;

    public Letter(char value) {
        this.value = value;
    }

    public char getValue() {
        return value;
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }
}

/** Клас, що представляє слово — композиція з об'єктів Letter. */
class Word {
    private final List<Letter> letters = new ArrayList<>();

    public Word(String str) {
        for (char c : str.toCharArray()) {
            letters.add(new Letter(c));
        }
    }

    private Word(List<Letter> transformedLetters) {
        this.letters.addAll(transformedLetters);
    }

    /**
     * Виконує перетворення слова за завданням лабораторної
     */
    public Word transform() {
        if (letters.size() <= 1) {
            return this;
        }

        char lastChar = letters.getLast().getValue();
        List<Letter> transformed = new ArrayList<>();

        for (int i = 0; i < letters.size() - 1; i++) {
            if (letters.get(i).getValue() != lastChar) {
                transformed.add(letters.get(i));
            }
        }
        transformed.add(letters.getLast());

        return new Word(transformed);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (Letter letter : letters) {
            sb.append(letter.getValue());
        }
        return sb.toString();
    }
}

/** Клас, що представляє знак пунктуації. */
class Punctuation {
    private final char sign;

    public Punctuation(char sign) {
        this.sign = sign;
    }

    @Override
    public String toString() {
        return String.valueOf(sign);
    }
}

/** Клас, що представляє речення — композиція з Word та Punctuation. */
class Sentence {
    public final List<Object> elements = new ArrayList<>();  // Word або Punctuation

    public void addWord(Word word) {
        elements.add(word.transform());
    }

    public void addPunctuation(char sign) {
        elements.add(new Punctuation(sign));
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < elements.size(); i++) {
            Object current = elements.get(i);
            sb.append(current);

            // Логіка пробілів: після слова + перед словом (крім після пунктуації)
            if (i < elements.size() - 1) {
                Object next = elements.get(i + 1);
                if (current instanceof Word || next instanceof Word) {
                    sb.append(' ');
                }
            }
        }
        return sb.toString();
    }
}

/** Клас, що представляє текст — композиція з об'єктів Sentence. */
class Text {
    private final List<Sentence> sentences = new ArrayList<>();

    private Text() {
    }

    public static Text fromString(String input) {
        Text text = new Text();
        String normalized = input.replaceAll("\\s+", " ").trim();

        Sentence currentSentence = new Sentence();
        StringBuilder wordBuffer = new StringBuilder();

        for (int i = 0; i < normalized.length(); i++) {
            char c = normalized.charAt(i);

            if (c == ' ') {
                if (!wordBuffer.isEmpty()) {
                    currentSentence.addWord(new Word(wordBuffer.toString()));
                    wordBuffer.setLength(0);
                }
                continue;
            }

            if (isPunctuation(c)) {
                if (!wordBuffer.isEmpty()) {
                    currentSentence.addWord(new Word(wordBuffer.toString()));
                    wordBuffer.setLength(0);
                }
                currentSentence.addPunctuation(c);

                // Визначення кінця речення
                boolean isSentenceEnd = (c == '.' || c == '!' || c == '?')
                        && (i + 1 >= normalized.length() || Character.isWhitespace(normalized.charAt(i + 1)));

                if (isSentenceEnd && !currentSentence.elements.isEmpty()) {
                    text.sentences.add(currentSentence);
                    currentSentence = new Sentence();
                }
            } else {
                wordBuffer.append(c);
            }
        }

        // Останнє слово та останнє речення
        if (!wordBuffer.isEmpty()) {
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

    public String processAndToString() {
        if (sentences.isEmpty()) {
            return "";
        }

        StringBuilder result = new StringBuilder();
        for (int i = 0; i < sentences.size(); i++) {
            if (i > 0) {
                result.append(' ');
            }
            result.append(sentences.get(i));
        }
        return result.toString();
    }
}