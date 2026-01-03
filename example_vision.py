"""
Простой пример использования test_vision.py

Запустите этот файл, чтобы протестировать Vision API с вашим ключом.
"""

from test_vision import ask_ai_about_image, extract_answer

# Вставьте ваш API ключ OpenRouter здесь
API_KEY = "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"  # Или оставьте None для использования .env

# Пример 1: Анализ изображения по URL
print("Анализ изображения кота...\n")

image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
question = "Что изображено на этой картинке? Опиши подробно."

try:
    # Отправляем запрос
    response = ask_ai_about_image(
        image_input=image_url,
        question=question,
        api_key=API_KEY if API_KEY != "YOUR_API_KEY_HERE" else None,
        model="google/gemini-2.0-flash-exp:free"  # Бесплатная модель Gemini с поддержкой изображений
    )
    
    # Получаем ответ
    answer = extract_answer(response)
    print(f"✅ Ответ AI:\n{answer}\n")
    
    # Показываем статистику
    if 'usage' in response:
        usage = response['usage']
        print(f"\n📊 Использовано токенов:")
        print(f"   Запрос: {usage.get('prompt_tokens', 'N/A')}")
        print(f"   Ответ: {usage.get('completion_tokens', 'N/A')}")
        print(f"   Всего: {usage.get('total_tokens', 'N/A')}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    if "429" in str(e):
        print("\n⏳ Лимит запросов исчерпан. Подождите немного и попробуйте снова.")
    elif "401" in str(e):
        print("\n🔑 Проверьте правильность API ключа")
    else:
        print("\nУкажите ваш OpenRouter API ключ в переменной API_KEY")
        print("Или установите переменную окружения OPENROUTER_API_KEY")
