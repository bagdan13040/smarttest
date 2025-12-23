import requests
import json
import os
import sys
import socket
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Explicitly load .env from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"[LLM] .env loaded from: {env_path}, exists: {env_path.exists()}")
except Exception as e:
    print(f"[LLM] Warning: Could not load dotenv: {e}")
    # On Android, dotenv might not work properly, but we can still use os.environ

def check_internet_connection():
    """Check if device has internet connectivity by trying to connect to Google DNS"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def resolve_dns(hostname):
    """Manually resolve DNS using socket.getaddrinfo"""
    try:
        result = socket.getaddrinfo(hostname, 443, socket.AF_INET, socket.SOCK_STREAM)
        ip = result[0][4][0]
        print(f"[LLM] Resolved {hostname} to {ip}")
        return ip
    except Exception as e:
        print(f"[LLM] DNS resolution failed: {e}")
        return None

def generate_quiz(topic, difficulty="средний", api_key=None, server_url=None):
    print(f"[LLM] Generating quiz for topic: {topic}, difficulty: {difficulty}")
    print(f"[LLM] Platform: {sys.platform}")
    
    # Check internet connection first
    if not check_internet_connection():
        msg = "Нет подключения к интернету. Проверьте WiFi или мобильные данные."
        print(f"[LLM] {msg}")
        return generate_mock_quiz(topic, difficulty, error=msg)
    else:
        print("[LLM] Internet connection: OK")
    
    # Determine URL and headers based on whether we use a proxy server or direct API
    if server_url:
        url = f"{server_url}/generate_quiz"
        print(f"[LLM] Using custom server: {url}")
        headers = {"Content-Type": "application/json"}
    else:
        url = "https://openrouter.ai/api/v1/chat/completions"
        # Priority: 1. Passed argument (from settings), 2. Environment variable
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
        
        if api_key:
            print(f"[LLM] API Key found: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else '***'}")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "SmartTest/1.0 (Android)",
                "HTTP-Referer": "https://github.com/bagdan13040/smarttest",
                "X-Title": "SmartTest"
            }
        else:
            msg = "Error: OPENROUTER_API_KEY not found in environment variables or settings"
            print(f"[LLM] {msg}")
            env_path = Path(__file__).parent / '.env'
            print(f"[LLM] Checked .env at: {env_path}, exists: {env_path.exists()}")
            print(f"[LLM] Current working directory: {os.getcwd()}")
            print(f"[LLM] __file__ location: {__file__}")
            return generate_mock_quiz(topic, difficulty, error=msg)

    # Промпт для генерации JSON
    prompt = (
        f"Тема: '{topic}'. Сложность: '{difficulty}'. "
        "1. Напиши ОБШИРНЫЙ и ПОДРОБНЫЙ теоретический материал. "
        "Раздели текст на логические блоки с заголовками. "
        "Текст должен содержать ВСЮ информацию, необходимую для ответов на вопросы ниже. "
        "Используй теги [b]...[/b] для жирного шрифта и переносы строк \\n для форматирования. НЕ используй Markdown (**, ##). "
        "2. Сгенерируй 10 вопросов с 4 вариантами ответов. "
        "Верни ТОЛЬКО JSON объект. "
        "Структура: {\"theory\": \"Текст теории...\", \"questions\": [{\"question\": \"...\", \"options\": [\"...\", ...], \"answer\": 0}]}"
    )

    data = {
        "model": "xiaomi/mimo-v2-flash:free",
        "messages": [
            {
                "role": "system",
                "content": "Ты — API, возвращающий только сырой JSON. Используй Kivy markup ([b], [i], [color]) вместо Markdown. Никогда не пиши вступлений."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        print(f"[LLM] Sending request to {url}...")
        print(f"[LLM] Headers: {dict((k, '***' if k == 'Authorization' else v) for k, v in headers.items())}")
        
        # On Android, try to resolve DNS manually first
        if sys.platform.startswith('linux') and 'ANDROID' in os.environ.get('PYTHONPATH', '').upper():
            print("[LLM] Detected Android, attempting manual DNS resolution...")
            hostname = url.split('//')[1].split('/')[0]
            ip = resolve_dns(hostname)
            if not ip:
                msg = f"Не удалось разрешить DNS для {hostname}. Попробуйте перезапустить приложение."
                print(f"[LLM] {msg}")
                return generate_mock_quiz(topic, difficulty, error=msg)
        
        # Try with SSL verification first
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
            print(f"[LLM] Request successful with SSL verification")
        except requests.exceptions.SSLError as ssl_err:
            print(f"[LLM] SSLError: {ssl_err}, retrying with verify=False...")
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30, verify=False)
            print(f"[LLM] Request successful without SSL verification")
            
        print(f"[LLM] Response status: {response.status_code}")
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
                    msg = "Ошибка: неверная структура JSON от API"
                    print(msg)
                    return generate_mock_quiz(topic, difficulty, error=msg)
                
                quiz_data = response_data['questions']
                if not isinstance(quiz_data, list):
                    msg = "Ошибка: questions не список"
                    print(msg)
                    return generate_mock_quiz(topic, difficulty, error=msg)
                
                valid_quiz = []
                for item in quiz_data:
                    if (isinstance(item, dict) and 
                        'question' in item and isinstance(item['question'], str) and
                        'options' in item and isinstance(item['options'], list) and len(item['options']) == 4 and
                        'answer' in item and isinstance(item['answer'], int) and 0 <= item['answer'] <= 3):
                        valid_quiz.append(item)
                
                if not valid_quiz:
                    msg = "Ошибка: нет валидных вопросов в ответе API"
                    print(msg)
                    return generate_mock_quiz(topic, difficulty, error=msg)

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
                msg = f"Ошибка парсинга JSON: {e}"
                print(msg)
                print(f"Полученный контент: {content}")
                return generate_mock_quiz(topic, difficulty, error=msg)
        else:
            msg = f"Некорректный ответ от API: {result}"
            print(msg)
            return generate_mock_quiz(topic, difficulty, error=msg)
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return generate_mock_quiz(topic, difficulty, error=str(e))

def generate_mock_quiz(topic, difficulty, error=None):
    print("[LLM] Generating mock quiz due to API failure...")
    print(f"[LLM] Error details: {error}")
    theory_intro = f"[b]Оффлайн режим[/b]\n\n"
    if error:
        theory_intro += f"[color=ff0000]Ошибка: {error}[/color]\n\n"
        if "Failed to resolve" in error or "No address associated" in error:
            theory_intro += "[color=ff6600]Возможные причины:[/color]\n"
            theory_intro += "1. Нет подключения к интернету\n"
            theory_intro += "2. DNS не настроен (для эмулятора)\n"
            theory_intro += "3. Проверьте браузер в эмуляторе\n\n"
    
    theory_intro += f"К сожалению, сервис генерации временно недоступен. Вот пример того, как это должно выглядеть для темы [b]{topic}[/b].\n\n[b]1. Введение[/b]\nЗдесь обычно располагается теоретический материал, который генерирует нейросеть. Он разбит на логические блоки и содержит всю необходимую информацию.\n\n[b]2. Основные понятия[/b]\n• [b]Тема[/b]: {topic}\n• [b]Сложность[/b]: {difficulty}\n\nПопробуйте повторить запрос позже, когда API снова заработает."

    return {
        "theory": theory_intro,
        "error": error, # Return error for logging
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