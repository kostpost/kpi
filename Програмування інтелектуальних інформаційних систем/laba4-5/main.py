from openai import OpenAI

GROQ_API_KEY = "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"
MODEL = "llama-3.3-70b-versatile"


def create_groq_client():
    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


def ask_groq(client, system_prompt, user_prompt, temperature=0.6, max_tokens=1500):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("\nпомилка при запиті")
        print(f"деталі: {e}")

        error_str = str(e).lower()
        if "authentication" in error_str:
            print("ключ проблема")
        elif "rate limit" in error_str or "429" in error_str:
            print("вичерпано ліміт ")
        elif "network" in error_str or "connection" in error_str:
            print("проблеми з інтеренотом")
        else:
            print("невідома помилка")

        return None


def print_separator(title):
    print("\n" + "=" * 70)
    print(f" {title} ")
    print("=" * 70 + "\n")


def main():
    client = create_groq_client()

    # Відстань Левенштейна
    print_separator("Відстань Левенштейна")
    levenshtein_prompt = (
        "Напиши функцію на Python для обчислення відстані Левенштейна (Levenshtein distance) "
        "між двома рядками за допомогою динамічного програмування. "
        "Функція повинна повертати тільки число — відстань. "
        "Додай 3 приклади тестування з print."
    )
    result = ask_groq(client, "Ти експерт з алгоритмів на Python. Пиши чистий, ефективний код.", levenshtein_prompt)
    if result:
        print(result)

    # Алгоритм Евкліда
    print_separator("Алгоритм Евкліда")
    euclid_prompt = (
        "Напиши на Python функцію для обчислення НСД (GCD) за алгоритмом Евкліда "
        "(iterative версія з while). "
        "Додай 3-4 приклади тестування з виводом, дай саме відповіді у кінці"

    )
    result = ask_groq(client, "Ти експерт з алгоритмів. Пиши чистий код на Python.", euclid_prompt)
    if result:
        print(result)

    # Фібоначчі
    print_separator(" Фібоначчі ")
    fib_prompt_simple = (
        "Напиши на Python функцію для обчислення n-го числа Фібоначчі з мемоїзацією.\n"
        "F(0) = 0, F(1) = 1\n"
        "Додай коментарі українською.\n"
        "Виведи приклади: F(0), F(5), F(10), F(20), дай саме відповіді у кінці"
    )
    result = ask_groq(client, "Ти експерт з алгоритмів на Python. Пиши чистий код з коментарями українською.",
                      fib_prompt_simple)
    if result:
        print(result)

    print("\n" + "=" * 70)
    print("РОБОТА ЗАВЕРШЕНА")
    print("=" * 70)


if __name__ == "__main__":
    main()