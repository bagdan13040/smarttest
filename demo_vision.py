"""
Демонстрация работы Vision API без реальных запросов.
Показывает структуру запроса и ожидаемого ответа.
"""

from test_vision import encode_image_to_base64
import json

print("=" * 70)
print("ДЕМОНСТРАЦИЯ: Как работает Vision API")
print("=" * 70)

# Пример 1: Структура запроса с URL изображения
print("\n1️⃣  СТРУКТУРА ЗАПРОСА С URL ИЗОБРАЖЕНИЯ\n")

request_with_url = {
    "model": "google/gemini-2.0-flash-exp:free",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Что изображено на этой картинке?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg",
                        "detail": "auto"
                    }
                }
            ]
        }
    ]
}

print(json.dumps(request_with_url, indent=2, ensure_ascii=False))

# Пример 2: Структура с base64
print("\n" + "=" * 70)
print("\n2️⃣  СТРУКТУРА ЗАПРОСА С BASE64 ИЗОБРАЖЕНИЕМ\n")

request_with_base64 = {
    "model": "openai/gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Опиши это изображение подробно"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                        "detail": "high"
                    }
                }
            ]
        }
    ]
}

print(json.dumps(request_with_base64, indent=2, ensure_ascii=False))

# Пример 3: Типичный ответ от API
print("\n" + "=" * 70)
print("\n3️⃣  ПРИМЕР ОТВЕТА ОТ API\n")

example_response = {
    "id": "gen-1234567890",
    "model": "google/gemini-2.0-flash-exp:free",
    "object": "chat.completion",
    "created": 1704326400,
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "На изображении представлен рыжий кот с зелёными глазами. Кот сидит на зелёной траве и смотрит прямо в камеру. Шерсть кота выглядит мягкой и пушистой. Освещение естественное, вероятно дневное."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 1250,
        "completion_tokens": 85,
        "total_tokens": 1335
    }
}

print(json.dumps(example_response, indent=2, ensure_ascii=False))

# Извлечение ответа
answer = example_response['choices'][0]['message']['content']
print("\n" + "=" * 70)
print("\n4️⃣  ИЗВЛЕЧЁННЫЙ ОТВЕТ\n")
print(f"📝 {answer}")

# Статистика
usage = example_response['usage']
print("\n" + "=" * 70)
print("\n5️⃣  СТАТИСТИКА ИСПОЛЬЗОВАНИЯ\n")
print(f"📊 Токены в запросе (включая изображение): {usage['prompt_tokens']}")
print(f"📊 Токены в ответе: {usage['completion_tokens']}")
print(f"📊 Всего токенов: {usage['total_tokens']}")

# Примеры использования
print("\n" + "=" * 70)
print("\n6️⃣  ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ В КОДЕ\n")

example_code = """
# Вариант 1: С URL изображения
from test_vision import ask_ai_about_image, extract_answer

response = ask_ai_about_image(
    image_input="https://example.com/cat.jpg",
    question="Что на картинке?",
    api_key="your-api-key",
    model="google/gemini-2.0-flash-exp:free"
)

answer = extract_answer(response)
print(answer)

# Вариант 2: С локальным файлом
response = ask_ai_about_image(
    image_input="./my_photo.jpg",
    question="Опиши эту фотографию",
    api_key="your-api-key"
)

answer = extract_answer(response)
print(answer)

# Вариант 3: Высокая детализация для сложных изображений
response = ask_ai_about_image(
    image_input="diagram.png",
    question="Объясни, что показано на этой диаграмме",
    api_key="your-api-key",
    detail="high"  # Более детальный анализ
)
"""

print(example_code)

print("\n" + "=" * 70)
print("\n✅ ФУНКЦИЯ ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
print("\nДля реального запроса:")
print("1. Убедитесь, что на счету OpenRouter есть кредиты")
print("2. Используйте бесплатные модели (gemini-2.0-flash-exp:free)")
print("3. Или пополните баланс для использования платных моделей")
print("\n" + "=" * 70)
