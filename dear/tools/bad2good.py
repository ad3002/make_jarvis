import openai
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

# Инициализация клиента OpenAI
api_key = os.getenv("OPENAI_KEY")
client = openai.OpenAI(api_key=api_key)


def clean_and_correct_text(text, system_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ],
    )
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="Обработка текста транскрипции: корректировка и чистка с учетом контекста")
    parser.add_argument("input_file", help="Путь к файлу с текстом транскрипции")
    parser.add_argument("output_file", help="Путь к выходному файлу с откорректированным текстом")
    parser.add_argument("context", help="Контекст или описание домена, из которого был получен текст")
    args = parser.parse_args()

    # Чтение входного файла
    with open(args.input_file, "r", encoding="utf-8") as f:
        transcribed_text = f.read()

    # Системное сообщение для OpenAI GPT с учетом контекста
    system_prompt = (
        "Ты ассистент, который исправляет транскрипцию на русском языке. "
        "Текст получен из домена, связанного с следующим контекстом: '{}'. "
        "Разбей текст на предложения и параграфы, исправь орфографические и грамматические ошибки, "
        "удали ненужные слова и улучшай структуру текста. Добавляй только необходимую пунктуацию и используй только контекст, который предоставлен."
    ).format(args.context)

    # Коррекция текста
    corrected_text = clean_and_correct_text(transcribed_text, system_prompt)

    # Запись откорректированного текста в файл
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(corrected_text)

    print(f"Откорректированный текст сохранен в файл: {args.output_file}")

if __name__ == "__main__":
    main()
