"""
LLM module for quiz generation using OpenRouter API.
Uses kivy.network.urlrequest for Android compatibility.
Falls back to urllib for desktop.
"""
import json
import os
import sys
from pathlib import Path

# Try to load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"[LLM] .env loaded from: {env_path}, exists: {env_path.exists()}")
except Exception as e:
    print(f"[LLM] Warning: Could not load dotenv: {e}")

# Global variable to store async result
_async_result = None
_async_error = None
_async_done = False

def _on_success(req, result):
    """Callback for successful UrlRequest"""
    global _async_result, _async_done
    print(f"[LLM] UrlRequest success, status: {req.resp_status}")
    _async_result = result
    _async_done = True

def _on_failure(req, result):
    """Callback for failed UrlRequest"""
    global _async_error, _async_done
    print(f"[LLM] UrlRequest failure: {result}")
    _async_error = f"Request failed: {result}"
    _async_done = True

def _on_error(req, error):
    """Callback for UrlRequest error"""
    global _async_error, _async_done
    print(f"[LLM] UrlRequest error: {error}")
    _async_error = str(error)
    _async_done = True

def _on_progress(req, current, total):
    """Callback for UrlRequest progress"""
    if total > 0:
        print(f"[LLM] Progress: {current}/{total} bytes")

def make_request_kivy(url, headers, data, timeout=60):
    """Make HTTP request using Kivy's UrlRequest (Android compatible)"""
    global _async_result, _async_error, _async_done
    _async_result = None
    _async_error = None
    _async_done = False
    
    from kivy.network.urlrequest import UrlRequest
    import time
    
    print(f"[LLM] Using Kivy UrlRequest for: {url}")
    
    req = UrlRequest(
        url,
        req_body=json.dumps(data),
        req_headers=headers,
        on_success=_on_success,
        on_failure=_on_failure,
        on_error=_on_error,
        on_progress=_on_progress,
        timeout=timeout,
        method='POST'
    )
    
    # Wait for request to complete (with timeout)
    start_time = time.time()
    while not _async_done:
        time.sleep(0.1)
        if time.time() - start_time > timeout:
            _async_error = "Request timeout"
            break
    
    if _async_error:
        raise Exception(_async_error)
    
    return _async_result

def make_request_urllib(url, headers, data, timeout=60):
    """Make HTTP request using urllib (standard library fallback)"""
    import urllib.request
    import ssl
    
    print(f"[LLM] Using urllib for: {url}")
    
    # Create SSL context that doesn't verify certificates (for Android compatibility)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
        return json.loads(response.read().decode('utf-8'))

def make_request(url, headers, data, timeout=60):
    """
    Make HTTP request using the best available method.
    Priority: Kivy UrlRequest (Android) -> urllib (fallback)
    """
    errors = []
    
    # Try Kivy UrlRequest first (best for Android)
    try:
        return make_request_kivy(url, headers, data, timeout)
    except ImportError:
        print("[LLM] Kivy UrlRequest not available")
    except Exception as e:
        errors.append(f"Kivy: {e}")
        print(f"[LLM] Kivy UrlRequest failed: {e}")
    
    # Try urllib (standard library, should always work)
    try:
        return make_request_urllib(url, headers, data, timeout)
    except Exception as e:
        errors.append(f"urllib: {e}")
        print(f"[LLM] urllib failed: {e}")
    
    # All methods failed
    raise Exception(f"Все методы HTTP не сработали: {'; '.join(errors)}")

def generate_quiz(topic, difficulty="средний", api_key=None):
    """Generate a quiz using OpenRouter API"""
    print(f"[LLM] Generating quiz for topic: {topic}, difficulty: {difficulty}")
    print(f"[LLM] Platform: {sys.platform}")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Get API key
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        msg = "API ключ не найден. Введите ключ в настройках."
        print(f"[LLM] {msg}")
        return generate_mock_quiz(topic, difficulty, error=msg)
    
    print(f"[LLM] API Key: {api_key[:10]}...{api_key[-5:]}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "SmartTest/1.0",
        "HTTP-Referer": "https://github.com/bagdan13040/smarttest",
        "X-Title": "SmartTest"
    }
    
    prompt = (
        f"Тема: '{topic}'. Сложность: '{difficulty}'. "
        "1. Напиши ОБШИРНЫЙ и ПОДРОБНЫЙ теоретический материал. "
        "Раздели текст на логические блоки с заголовками. "
        "Используй теги [b]...[/b] для жирного шрифта и переносы строк \\n для форматирования. "
        "НЕ используй Markdown (**, ##). "
        "2. Сгенерируй 10 вопросов с 4 вариантами ответов. "
        "Верни ТОЛЬКО JSON объект. "
        "Структура: {\"theory\": \"Текст теории...\", \"questions\": [{\"question\": \"...\", \"options\": [\"...\", ...], \"answer\": 0}]}"
    )
    
    data = {
        "model": "google/gemma-3-1b-it:free",
        "messages": [
            {
                "role": "system",
                "content": "Ты — API, возвращающий только сырой JSON. Используй Kivy markup ([b], [i], [color]) вместо Markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        print(f"[LLM] Sending request...")
        result = make_request(url, headers, data, timeout=60)
        print(f"[LLM] Got response")
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                response_data = json.loads(content)
                
                if not isinstance(response_data, dict) or 'theory' not in response_data or 'questions' not in response_data:
                    return generate_mock_quiz(topic, difficulty, error="Неверная структура ответа API")
                
                quiz_data = response_data['questions']
                if not isinstance(quiz_data, list):
                    return generate_mock_quiz(topic, difficulty, error="questions не список")
                
                valid_quiz = []
                for item in quiz_data:
                    if (isinstance(item, dict) and 
                        'question' in item and isinstance(item['question'], str) and
                        'options' in item and isinstance(item['options'], list) and len(item['options']) == 4 and
                        'answer' in item and isinstance(item['answer'], int) and 0 <= item['answer'] <= 3):
                        valid_quiz.append(item)
                
                if not valid_quiz:
                    return generate_mock_quiz(topic, difficulty, error="Нет валидных вопросов")
                
                meta = response_data.get('meta', {})
                meta['topic'] = topic
                meta['difficulty'] = difficulty
                
                return {'theory': response_data['theory'], 'questions': valid_quiz, 'meta': meta}
                
            except json.JSONDecodeError as e:
                return generate_mock_quiz(topic, difficulty, error=f"Ошибка парсинга JSON: {e}")
        else:
            return generate_mock_quiz(topic, difficulty, error=f"Некорректный ответ API")
            
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return generate_mock_quiz(topic, difficulty, error=str(e))

def generate_mock_quiz(topic, difficulty, error=None):
    """Generate a mock quiz when API is unavailable"""
    print(f"[LLM] Generating mock quiz. Error: {error}")
    
    theory = f"[b]Оффлайн режим[/b]\n\n"
    if error:
        theory += f"[color=ff0000]Ошибка: {error}[/color]\n\n"
    
    theory += f"К сожалению, сервис генерации временно недоступен.\n\n"
    theory += f"[b]Тема:[/b] {topic}\n"
    theory += f"[b]Сложность:[/b] {difficulty}\n\n"
    theory += "Попробуйте повторить запрос позже."
    
    return {
        "theory": theory,
        "error": error,
        "questions": [
            {"question": f"Тестовый вопрос по теме {topic}?", "options": ["Да", "Нет", "Возможно", "Не знаю"], "answer": 0},
            {"question": "Сколько бит в байте?", "options": ["4", "8", "16", "32"], "answer": 1},
            {"question": "Столица Франции?", "options": ["Лондон", "Берлин", "Париж", "Мадрид"], "answer": 2}
        ],
        "meta": {"topic": topic, "difficulty": difficulty}
    }

if __name__ == "__main__":
    test_topic = "Python программирование"
    print(f"Тестируем генерацию для темы: {test_topic}")
    quiz = generate_quiz(test_topic)
    print(json.dumps(quiz, indent=2, ensure_ascii=False))
