//import java.nio.charset.StandardCharsets;
//import java.util.ArrayList;
//import java.util.List;
//import java.util.Scanner;
//
//public class Task1 {
//
//    public static void main(String[] args) {
//        new Task1().Start();
//    }
//
//    public void Start() {
//        try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
//            System.out.println("Введіть текст:");
//            String input = scanner.nextLine();
//
//            Text text = Text.fromString(input);
//            String result = text.processAndToString();
//
//            System.out.println("Результат:");
//            System.out.println(result.isEmpty() ? "(порожній рядок)" : result);
//
//        } catch (Exception e) {
//            System.err.println("Помилка: " + e.getMessage());
//            e.printStackTrace();
//        }
//    }
//}
//
//class Letter {
//    private final char value;
//    Letter(char value) { this.value = value; }
//    char getValue() { return value; }
//    @Override public String toString() { return String.valueOf(value); }
//}
//
//class Punctuation {
//    private final char sign;
//    Punctuation(char sign) { this.sign = sign; }
//    @Override public String toString() { return String.valueOf(sign); }
//}
//
//class Word {
//    private final List<Letter> letters = new ArrayList<>();
//
//    Word(String str) {
//        for (char c : str.toCharArray()) {
//            letters.add(new Letter(c));
//        }
//    }
//
//    Word transform() {
//        if (letters.size() <= 1) return this;
//
//        char lastChar = letters.get(letters.size() - 1).getValue();
//        List<Letter> newLetters = new ArrayList<>();
//
//        for (int i = 0; i < letters.size() - 1; i++) {
//            if (letters.get(i).getValue() != lastChar) {
//                newLetters.add(letters.get(i));
//            }
//        }
//        newLetters.add(letters.get(letters.size() - 1));
//
//        Word transformed = new Word("");
//        transformed.letters.addAll(newLetters);
//        return transformed;
//    }
//
//    @Override
//    public String toString() {
//        StringBuilder sb = new StringBuilder();
//        for (Letter l : letters) sb.append(l.getValue());
//        return sb.toString();
//    }
//}
//
//class Sentence {
//    final List<Object> elements = new ArrayList<>(); // Word или Punctuation
//
//    void addWord(Word word) { elements.add(word.transform()); }
//    void addPunctuation(char sign) { elements.add(new Punctuation(sign)); }
//
//    @Override
//    public String toString() {
//        StringBuilder sb = new StringBuilder();
//        for (int i = 0; i < elements.size(); i++) {
//            Object current = elements.get(i);
//            sb.append(current.toString());
//
//            // Ставим пробел ТОЛЬКО после слова или после знака, если дальше слово
//            if (i < elements.size() - 1) {
//                Object next = elements.get(i + 1);
//                if (current instanceof Word || next instanceof Word) {
//                    sb.append(" ");
//                }
//            }
//        }
//        return sb.toString();
//    }
//}
//
//class Text {
//    private final List<Sentence> sentences = new ArrayList<>();
//
//    private Text() {}
//
//    public static Text fromString(String input) {
//        Text text = new Text();
//        String normalized = input.replaceAll("\\s+", " ").trim();
//
//        Sentence sentence = new Sentence();
//        StringBuilder wordBuf = new StringBuilder();
//
//        for (int i = 0; i < normalized.length(); i++) {
//            char c = normalized.charAt(i);
//
//            if (c == ' ') {
//                if (wordBuf.length() > 0) {
//                    sentence.addWord(new Word(wordBuf.toString()));
//                    wordBuf.setLength(0);
//                }
//                continue;
//            }
//
//            if (isPunctuation(c)) {
//                if (wordBuf.length() > 0) {
//                    sentence.addWord(new Word(wordBuf.toString()));
//                    wordBuf.setLength(0);
//                }
//                sentence.addPunctuation(c);
//
//                // Конец предложения — только после . ! ? и если это последний знак в последовательности
//                boolean isSentenceEnd = (c == '.' || c == '!' || c == '?') &&
//                        (i + 1 >= normalized.length() || !isPunctuation(normalized.charAt(i + 1)));
//
//                if (isSentenceEnd && !sentence.elements.isEmpty()) {
//                    text.sentences.add(sentence);
//                    sentence = new Sentence();
//                }
//            } else {
//                wordBuf.append(c);
//            }
//        }
//
//        // Последнее слово
//        if (wordBuf.length() > 0) {
//            sentence.addWord(new Word(wordBuf.toString()));
//        }
//        if (!sentence.elements.isEmpty()) {
//            text.sentences.add(sentence);
//        }
//
//        return text;
//    }
//
//    private static boolean isPunctuation(char c) {
//        return ",.!?;:-–—\"'()[]{}".indexOf(c) != -1;
//    }
//
//    public String processAndToString() {
//        StringBuilder result = new StringBuilder();
//        for (int i = 0; i < sentences.size(); i++) {
//            if (i > 0) result.append(" ");
//            result.append(sentences.get(i));
//        }
//        return result.toString();
//    }
//}