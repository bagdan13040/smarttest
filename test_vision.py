"""
Тестовый модуль для работы с Vision моделями через OpenRouter API.

Поддерживает отправку изображений (URL или base64) вместе с текстовым запросом.
"""

import requests
import base64
import os
from pathlib import Path


def encode_image_to_base64(image_path: str) -> str:
    """
    Кодирует изображение в base64 строку.
    
    Args:
        image_path: Путь к файлу изображения
        
    Returns:
        str: Base64-encoded строка изображения с префиксом data URL
    """
    with open(image_path, 'rb') as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        # Определяем MIME тип по расширению
        extension = Path(image_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(extension, 'image/jpeg')
        return f"data:{mime_type};base64,{encoded}"


def ask_ai_about_image(
    image_input: str,
    question: str,
    api_key: str = None,
    model: str = "openai/gpt-4o",
    detail: str = "auto"
) -> dict:
    """
    Отправляет изображение и текстовый запрос в Vision модель через OpenRouter API.
    
    Args:
        image_input: Путь к локальному файлу или URL изображения
        question: Текстовый вопрос об изображении
        api_key: API ключ OpenRouter (если None, берется из переменной окружения)
        model: Идентификатор модели (по умолчанию gpt-4o)
        detail: Уровень детализации анализа ("auto", "low", "high")
        
    Returns:
        dict: Ответ от API с результатом анализа
        
    Raises:
        ValueError: Если API ключ не предоставлен
        requests.exceptions.RequestException: При ошибках сетевого запроса
    """
    # Получаем API ключ
    if api_key is None:
        api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        raise ValueError(
            "API ключ не предоставлен. Передайте параметр api_key или "
            "установите переменную окружения OPENROUTER_API_KEY"
        )
    
    # Определяем, это URL или локальный файл
    if image_input.startswith(('http://', 'https://')):
        image_url = image_input
    else:
        # Кодируем локальный файл в base64
        image_url = encode_image_to_base64(image_input)
    
    # Формируем запрос согласно документации OpenRouter
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/bagdan13040/smarttest",  # Для статистики
        "X-Title": "SmartTest Vision Test"  # Название приложения
    }
    
    # Структура сообщения с изображением
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": detail  # "auto", "low", или "high"
                        }
                    }
                ]
            }
        ]
    }
    
    # Отправляем запрос
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Вызовет исключение при ошибке HTTP
    
    return response.json()


def extract_answer(response: dict) -> str:
    """
    Извлекает текстовый ответ из JSON ответа API.
    
    Args:
        response: JSON ответ от OpenRouter API
        
    Returns:
        str: Текст ответа модели
    """
    try:
        return response['choices'][0]['message']['content']
    except (KeyError, IndexError) as e:
        return f"Ошибка при извлечении ответа: {e}\nПолный ответ: {response}"


# Пример использования
if __name__ == "__main__":
    # Пример 1: Использование с URL изображения
    print("=" * 60)
    print("ТЕСТ 1: Анализ изображения по URL")
    print("=" * 60)
    
    try:
        # Тестовое изображение (котик)
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
        
        response = ask_ai_about_image(
            image_input=test_image_url,
            question="Что изображено на этой картинке? Опиши детально на русском языке.",
            model="openai/gpt-4o"
        )
        
        answer = extract_answer(response)
        print(f"\n✅ Ответ модели:\n{answer}\n")
        
        # Показываем использование токенов
        if 'usage' in response:
            usage = response['usage']
            print(f"📊 Статистика:")
            print(f"   - Токенов в запросе: {usage.get('prompt_tokens', 'N/A')}")
            print(f"   - Токенов в ответе: {usage.get('completion_tokens', 'N/A')}")
            print(f"   - Всего токенов: {usage.get('total_tokens', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Анализ локального файла (если есть)")
    print("=" * 60)
    
    # Пример 2: Использование с локальным файлом
    # Раскомментируйте, если у вас есть локальное изображение
    """
    try:
        local_image_path = "path/to/your/image.jpg"
        
        response = ask_ai_about_image(
            image_input=local_image_path,
            question="Что ты видишь на этом изображении?",
            model="google/gemini-2.0-flash-exp:free"  # Бесплатная модель
        )
        
        answer = extract_answer(response)
        print(f"\n✅ Ответ модели:\n{answer}\n")
        
    except FileNotFoundError:
        print(f"⚠️  Файл не найден: {local_image_path}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    """
    
    print("\n" + "=" * 60)
    print("ИНФОРМАЦИЯ О ПОДДЕРЖИВАЕМЫХ МОДЕЛЯХ")
    print("=" * 60)
    print("""
    Vision-модели, доступные через OpenRouter:
    
    - openai/gpt-4o              - Самая мощная модель от OpenAI
    - openai/gpt-4o-mini         - Более быстрая и дешевая версия
    - anthropic/claude-3.5-sonnet - Отличная модель от Anthropic
    - google/gemini-2.0-flash-exp:free - БЕСПЛАТНАЯ модель Google
    - google/gemini-pro-vision   - Vision версия Gemini
    
    Больше моделей: https://openrouter.ai/models?supported_parameters=vision
    """)
    
    print("\n" + "=" * 60)
    print("ПРИМЕРЫ ВОПРОСОВ")
    print("=" * 60)
    print("""
    - "Что изображено на этой картинке?"
    - "Опиши все объекты, которые ты видишь"
    - "Какие цвета преобладают на изображении?"
    - "Есть ли на картинке текст? Если да, прочитай его"
    - "Какие эмоции вызывает это изображение?"
    - "Посчитай количество людей на фотографии"
    - "Определи стиль этой иллюстрации"
    """)
