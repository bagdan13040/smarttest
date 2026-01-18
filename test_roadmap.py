"""
Тестирование функции генерации дорожной карты обучения
"""
import os
import json
from llm import generate_learning_roadmap

# Получаем API ключ из переменных окружения или вводим вручную
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    api_key = input("Введите API ключ OpenRouter: ")

# Тестовая тема
topic = "Python программирование"
goal = "стать веб-разработчиком"
level = "начинающий"

print(f"\n{'='*60}")
print(f"Генерация дорожной карты обучения")
print(f"{'='*60}")
print(f"Тема: {topic}")
print(f"Цель: {goal}")
print(f"Уровень: {level}")
print(f"{'='*60}\n")

# Генерируем дорожную карту
result = generate_learning_roadmap(
    topic=topic,
    goal=goal,
    level=level,
    api_key=api_key
)

# Выводим результат
if 'error' in result:
    print(f"❌ ОШИБКА: {result['error']}")
else:
    print(f"✅ Дорожная карта успешно сгенерирована!\n")
    print(f"📚 Название: {result.get('title', 'Без названия')}")
    print(f"📝 Описание: {result.get('description', 'Нет описания')}")
    print(f"⏱ Время: {result.get('estimated_time', 'Не указано')}")
    print(f"\nМодули ({len(result.get('modules', []))}):\n")
    
    for module in result.get('modules', []):
        print(f"\n{module.get('order')}. {module.get('title', 'Без названия')}")
        print(f"   🎯 Сложность: {module.get('difficulty', 'средний')}")
        print(f"   ⏱ Часов: {module.get('estimated_hours', 0)}")
        print(f"   📌 Зависит от: {', '.join(module.get('prerequisites', [])) or 'Нет'}")
        print(f"   📝 Темы:")
        for topic_name in module.get('topics', []):
            print(f"      • {topic_name}")
    
    # Сохраняем в файл для просмотра
    with open('test_roadmap_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Результат сохранён в test_roadmap_result.json")
