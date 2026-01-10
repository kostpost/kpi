# main.py
from openai import OpenAI

client = OpenAI(api_key="sk-твій_новий_ключ")  # обов'язково новий ключ!

response = client.chat.completions.create(
    model="gpt-4o-mini",  # або gpt-3.5-turbo, gpt-4o
    messages=[
        {"role": "system", "content": "Ти корисний асистент."},
        {"role": "user", "content": "Привіт! Напиши функцію для LCS на Python"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)