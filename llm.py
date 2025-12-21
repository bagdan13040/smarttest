import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def generate_quiz(topic, difficulty="средний"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        return generate_mock_quiz(topic, difficulty)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Промпт для генерации JSON
    prompt = (
        f"Тема: '{topic}'. Сложность: '{difficulty}'. "
        "1. Напиши ОБШИРНЫЙ и ПОДРОБНЫЙ теоретический материал. "
        "Раздели текст на логические блоки с заголовками. "
        "Текст должен содержать ВСЮ информацию, необходимую для ответов на вопросы ниже. "
        "Используй переносы строк \\n для форматирования. "
        "2. Сгенерируй 10 вопросов с 4 вариантами ответов. "
        "Верни ТОЛЬКО JSON объект. "
        "Структура: {\"theory\": \"Текст теории...\", \"questions\": [{\"question\": \"...\", \"options\": [\"...\", ...], \"answer\": 0}]}"
    )

    data = {
        "model": "deepseek/deepseek-v3.2",
        "messages": [
            {
                "role": "system",
                "content": "Ты — API, возвращающий только сырой JSON. Никогда не используй markdown блоки. Никогда не пиши вступлений."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            
            # Очистка от возможных markdown-тегов, если модель их все-таки добавит
            content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                response_data = json.loads(content)
                
                # Валидация структуры
                if not isinstance(response_data, dict) or 'theory' not in response_data or 'questions' not in response_data:
                    print("Ошибка: неверная структура JSON")
                    return generate_mock_quiz(topic, difficulty)
                
                quiz_data = response_data['questions']
                if not isinstance(quiz_data, list):
                    print("Ошибка: questions не список")
                    return generate_mock_quiz(topic, difficulty)
                
                valid_quiz = []
                for item in quiz_data:
                    if (isinstance(item, dict) and 
                        'question' in item and isinstance(item['question'], str) and
                        'options' in item and isinstance(item['options'], list) and len(item['options']) == 4 and
                        'answer' in item and isinstance(item['answer'], int) and 0 <= item['answer'] <= 3):
                        valid_quiz.append(item)
                
                if not valid_quiz:
                    print("Ошибка: нет валидных вопросов")
                    return generate_mock_quiz(topic, difficulty)

                # Собираем meta, если модель вернула дополнительные данные
                meta = response_data.get('meta', {}) if isinstance(response_data, dict) else {}
                # Ensure topic and difficulty are returned for UI
                try:
                    meta['topic'] = topic
                    meta['difficulty'] = difficulty
                except Exception:
                    pass

                return {'theory': response_data['theory'], 'questions': valid_quiz, 'meta': meta}
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
                print(f"Полученный контент: {content}")
                return generate_mock_quiz(topic, difficulty)
        else:
            print("Некорректный ответ от API")
            print(result)
            return generate_mock_quiz(topic, difficulty)
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return generate_mock_quiz(topic, difficulty)

def generate_mock_quiz(topic, difficulty):
    print("Generating mock quiz due to API failure...")
    return {
        "theory": f"### Оффлайн режим\\n\\nК сожалению, сервис генерации временно недоступен. Вот пример того, как это должно выглядеть для темы **{topic}**.\\n\\n#### 1. Введение\\nЗдесь обычно располагается теоретический материал, который генерирует нейросеть. Он разбит на логические блоки и содержит всю необходимую информацию.\\n\\n#### 2. Основные понятия\\n* **Тема**: {topic}\\n* **Сложность**: {difficulty}\\n\\nПопробуйте повторить запрос позже, когда API снова заработает.",
        "questions": [
            {
                "question": f"Это тестовый вопрос по теме {topic}?",
                "options": ["Да", "Нет", "Возможно", "Не знаю"],
                "answer": 0
            },
            {
                "question": "Сколько бит в байте?",
                "options": ["4", "8", "16", "32"],
                "answer": 1
            },
            {
                "question": "Столица Франции?",
                "options": ["Лондон", "Берлин", "Париж", "Мадрид"],
                "answer": 2
            }
        ],
        "meta": {
            "topic": topic,
            "difficulty": difficulty
        }
    }

if __name__ == "__main__":
    # Пример использования
    test_topic = "иррациональные уравнения"
    print(f"Генерируем тест на тему: {test_topic}...")
    
    quiz = generate_quiz(test_topic)
    
    if quiz:
        print("\nУспешно сгенерирован тест:")
        print(json.dumps(quiz, indent=4, ensure_ascii=False))
        
        # Проверка структуры
        questions = quiz.get('questions', [])
        print(f"\nКоличество вопросов: {len(questions)}")
        if len(questions) > 0:
            print(f"Первый вопрос: {questions[0].get('question')}")
            print(f"Варианты: {questions[0].get('options')}")
            print(f"Правильный ответ (индекс): {questions[0].get('answer')}")
    else:
        print("Не удалось получить тест.")