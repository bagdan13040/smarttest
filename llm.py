"""LLM module for quiz generation using OpenRouter API.
Uses kivy.network.urlrequest for Android compatibility.
Falls back to urllib for desktop.
"""
import json
import os
import sys
import traceback
import socket
import http.client
from pathlib import Path

# Detailed logging
def log(msg):
    """Print log message with prefix"""
    print(f"[LLM] {msg}")
    # Also try to write to file for Android debugging
    try:
        log_path = Path(__file__).parent / 'llm_debug.log'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{msg}\n")
    except:
        pass

log(f"=== LLM Module Loading ===")
log(f"Python version: {sys.version}")
log(f"Platform: {sys.platform}")
log(f"Current directory: {os.getcwd()}")
log(f"__file__: {__file__}")

# Try to load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    log(f".env loaded from: {env_path}, exists: {env_path.exists()}")
except Exception as e:
    log(f"Warning: Could not load dotenv: {e}")

# Check if running on Android
IS_ANDROID = False
try:
    import android
    IS_ANDROID = True
    log("Android module imported - running on Android")
except ImportError:
    log("Not running on Android (android module not found)")

# Global variable to store async result
_async_result = None
_async_error = None
_async_done = False

# Fallback IPs for openrouter.ai (to bypass DNS issues on some networks)
FALLBACK_OPENROUTER_IPS = [
    "104.21.74.91",
    "172.67.213.90",
]


def get_course_topics(memory_file='course_topics.json'):
    """Загрузить список тем курса из памяти (файла)."""
    path = Path(memory_file)
    if not path.exists():
        return []
    try:
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception as e:
        log(f"Не удалось прочитать память тем: {e}")
    return []


def save_course_topic(topic, memory_file='course_topics.json'):
    """Сохранить новую тему в память курса (файл)."""
    if not topic or not isinstance(topic, str):
        return
    normalized = topic.strip()
    if not normalized:
        return
    path = Path(memory_file)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log(f"Не удалось создать директорию памяти тем: {e}")
    topics = get_course_topics(memory_file)
    if normalized not in topics:
        topics.append(normalized)
        try:
            with path.open('w', encoding='utf-8') as f:
                json.dump(topics, f, ensure_ascii=False, indent=2)
            log(f"Тема сохранена в памяти: {normalized}")
        except Exception as e:
            log(f"Не удалось сохранить память тем: {e}")


def generate_next_topics(prev_material, n=5, api_key=None, memory_file='course_topics.json'):
    """Генерировать новые темы для изучения на основе предыдущего материала и сохранить их в память."""
    if not prev_material:
        prev_material = "Ранее изученный материал недоступен."
    material_snippet = prev_material[:1500]
    log(f"=== generate_next_topics() starting ===")
    log(f"  Material snippet length: {len(material_snippet)}")
    log(f"  API key provided: {api_key is not None}")
    url = "https://openrouter.ai/api/v1/chat/completions"
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
        log(f"API key from env: {api_key is not None}")
    if not api_key:
        log("API ключ не найден. Генерация тем пропущена.")
        return []
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "SmartTest/1.0",
        "HTTP-Referer": "https://github.com/bagdan13040/smarttest",
        "X-Title": "SmartTest"
    }
    prompt = (
        f"На основе следующего учебного материала предложи {n} новых тем для дальнейшего изучения. "
        "Верни только JSON массив строк, где каждая строка — это краткое название темы. "
        "Материал:\n" + material_snippet
    )
    data = {
        "model": "xiaomi/mimo-v2-flash:free",
        "messages": [
            {"role": "system", "content": "Ты — API, возвращающий только сырой JSON массив строк (тем)."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        log(f"Sending request to OpenRouter for next topics...")
        result = make_request(url, headers, data, timeout=60)
        log(f"Got response from OpenRouter (next topics)")
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            log(f"Content preview: {content[:200]}...")
            content = content.replace('```json', '').replace('```', '').strip()
            try:
                topics_raw = json.loads(content)
                if isinstance(topics_raw, list):
                    topics = []
                    for item in topics_raw:
                        topic_name = str(item).strip()
                        if topic_name and topic_name not in topics:
                            topics.append(topic_name)
                            save_course_topic(topic_name, memory_file)
                    log(f"Saved {len(topics)} topics to memory.")
                    return topics
                else:
                    log("Ответ не является списком тем.")
                    return []
            except json.JSONDecodeError as e:
                log(f"Ошибка парсинга JSON тем: {e}")
                return []
        else:
            log(f"Некорректный ответ API (next topics): {result}")
            return []
    except Exception as e:
        log(f"Exception in generate_next_topics: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        return []


def make_request_java(url, headers, data, timeout=60):
    """Make HTTP request using Java HttpURLConnection (Android native, best compatibility)."""
    if not IS_ANDROID:
        raise ImportError("Java HTTP client only available on Android")
    
    log("make_request_java() starting...")
    log(f"  URL: {url}")
    
    try:
        from jnius import autoclass, cast
        log("jnius imported successfully")
    except ImportError as e:
        log(f"Failed to import jnius: {e}")
        raise
    
    URL = autoclass('java.net.URL')
    HttpURLConnection = autoclass('java.net.HttpURLConnection')
    BufferedReader = autoclass('java.io.BufferedReader')
    InputStreamReader = autoclass('java.io.InputStreamReader')
    DataOutputStream = autoclass('java.io.DataOutputStream')
    
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    log(f"Request body prepared, length: {len(body)}")
    
    try:
        url_obj = URL(url)
        # openConnection() returns URLConnection, need to cast to HttpURLConnection
        url_connection = url_obj.openConnection()
        conn = cast('java.net.HttpURLConnection', url_connection)
        log("Connection cast to HttpURLConnection successfully")
        
        conn.setRequestMethod("POST")
        conn.setDoOutput(True)
        conn.setDoInput(True)
        conn.setConnectTimeout(timeout * 1000)
        conn.setReadTimeout(timeout * 1000)
        
        # Set headers
        for key, value in headers.items():
            conn.setRequestProperty(key, value)
        
        log("Sending request via Java HttpURLConnection...")
        
        # Write body
        out_stream = DataOutputStream(conn.getOutputStream())
        out_stream.write(body)
        out_stream.flush()
        out_stream.close()
        
        # Read response
        response_code = conn.getResponseCode()
        log(f"Java response code: {response_code}")
        
        if response_code >= 400:
            # Read error stream
            error_stream = conn.getErrorStream()
            if error_stream:
                reader = BufferedReader(InputStreamReader(error_stream, "UTF-8"))
                response_text = ""
                line = reader.readLine()
                while line is not None:
                    response_text += line
                    line = reader.readLine()
                reader.close()
                raise Exception(f"HTTP {response_code}: {response_text[:500]}")
            else:
                raise Exception(f"HTTP {response_code}")
        
        # Read success stream
        reader = BufferedReader(InputStreamReader(conn.getInputStream(), "UTF-8"))
        response_text = ""
        line = reader.readLine()
        while line is not None:
            response_text += line
            line = reader.readLine()
        reader.close()
        conn.disconnect()
        
        log(f"Java response length: {len(response_text)}")
        return json.loads(response_text)
        
    except Exception as e:
        log(f"Java HTTP request failed: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        raise

def _on_success(req, result):
    """Callback for successful UrlRequest"""
    global _async_result, _async_done
    log(f"UrlRequest SUCCESS!")
    log(f"  Status: {req.resp_status}")
    log(f"  Headers: {req.resp_headers}")
    log(f"  Result type: {type(result)}")
    log(f"  Result preview: {str(result)[:500]}")
    _async_result = result
    _async_done = True

def _on_failure(req, result):
    """Callback for failed UrlRequest"""
    global _async_error, _async_done
    log(f"UrlRequest FAILURE!")
    log(f"  Status: {req.resp_status}")
    log(f"  Result: {result}")
    _async_error = f"HTTP {req.resp_status}: {result}"
    _async_done = True

def _on_error(req, error):
    """Callback for UrlRequest error"""
    global _async_error, _async_done
    log(f"UrlRequest ERROR!")
    log(f"  Error type: {type(error)}")
    log(f"  Error: {error}")
    log(f"  Traceback: {traceback.format_exc()}")
    _async_error = str(error)
    _async_done = True

def _on_progress(req, current, total):
    """Callback for UrlRequest progress"""
    if total > 0:
        log(f"Progress: {current}/{total} bytes ({100*current//total}%)")
    else:
        log(f"Progress: {current} bytes (total unknown)")

def make_request_kivy(url, headers, data, timeout=60):
    """Make HTTP request using Kivy's UrlRequest (Android compatible)"""
    global _async_result, _async_error, _async_done
    _async_result = None
    _async_error = None
    _async_done = False
    
    log(f"make_request_kivy() starting...")
    log(f"  URL: {url}")
    log(f"  Timeout: {timeout}")
    log(f"  Data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
    
    try:
        from kivy.network.urlrequest import UrlRequest
        log("UrlRequest imported successfully")
    except Exception as e:
        log(f"Failed to import UrlRequest: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        raise
    
    import time
    
    try:
        # Ensure UTF-8 encoding for body with non-ASCII characters
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        log(f"Request body prepared, length: {len(body)}")
    except Exception as e:
        log(f"Failed to serialize data: {e}")
        raise
    
    # Force Content-Type with charset for proper encoding
    headers_copy = dict(headers)
    headers_copy['Content-Type'] = 'application/json; charset=utf-8'
    
    log("Creating UrlRequest...")
    try:
        req = UrlRequest(
            url,
            req_body=body,
            req_headers=headers_copy,
            on_success=_on_success,
            on_failure=_on_failure,
            on_error=_on_error,
            on_progress=_on_progress,
            timeout=timeout,
            method='POST'
        )
        log(f"UrlRequest created: {req}")
    except Exception as e:
        log(f"Failed to create UrlRequest: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        raise
    
    # Wait for request to complete (with timeout)
    log("Waiting for request to complete...")
    start_time = time.time()
    check_count = 0
    while not _async_done:
        time.sleep(0.1)
        check_count += 1
        elapsed = time.time() - start_time
        if check_count % 50 == 0:  # Log every 5 seconds
            log(f"  Still waiting... {elapsed:.1f}s elapsed")
        if elapsed > timeout:
            log(f"Request timeout after {elapsed:.1f}s")
            _async_error = "Request timeout"
            break
    
    log(f"Request completed in {time.time() - start_time:.1f}s")
    
    if _async_error:
        log(f"Request failed with error: {_async_error}")
        raise Exception(_async_error)
    
    log(f"Returning result: {type(_async_result)}")
    return _async_result

def make_request_urllib(url, headers, data, timeout=60):
    """Make HTTP request using urllib (standard library fallback)"""
    log(f"make_request_urllib() starting...")
    log(f"  URL: {url}")
    
    try:
        import urllib.request
        import ssl
        log("urllib.request and ssl imported")
    except Exception as e:
        log(f"Failed to import urllib/ssl: {e}")
        raise
    
    # Create SSL context that doesn't verify certificates (for Android compatibility)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    log("SSL context created (no verification)")
    
    try:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        log(f"Request body prepared, length: {len(body)}")
    except Exception as e:
        log(f"Failed to serialize data: {e}")
        raise
    
    # Force Content-Type with charset
    headers_copy = dict(headers)
    headers_copy['Content-Type'] = 'application/json; charset=utf-8'
    
    try:
        req = urllib.request.Request(
            url,
            data=body,
            headers=headers_copy,
            method='POST'
        )
        log("urllib.request.Request created")
    except Exception as e:
        log(f"Failed to create Request: {e}")
        raise
    
    try:
        log("Opening URL...")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            log(f"Response received, status: {response.status}")
            result = json.loads(response.read().decode('utf-8'))
            log(f"Response parsed successfully")
            return result
    except Exception as e:
        log(f"urlopen failed: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        raise


def make_request_urllib_ip(url, headers, data, timeout, ip_override):
    """Attempt urllib request using a direct IP with Host header for openrouter.ai"""
    import urllib.request
    import ssl

    log(f"make_request_urllib_ip() starting with IP {ip_override}...")

    # Clone headers and force Host
    headers_ip = dict(headers)
    headers_ip["Host"] = "openrouter.ai"

    # Build URL with IP
    request_url = url.replace("https://openrouter.ai", f"https://{ip_override}")
    log(f"  Request URL: {request_url}")

    # SSL context without verification (SNI will be IP, so we must disable checks)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    headers_ip["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(
        request_url,
        data=body,
        headers=headers_ip,
        method='POST'
    )

    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
        log(f"Response via IP {ip_override}, status: {response.status}")
        return json.loads(response.read().decode('utf-8'))


def make_request_socket_ip(url, headers, data, timeout, ip_override):
    """Direct socket HTTPS request to IP with SNI set to openrouter.ai (bypasses DNS)."""
    import ssl as ssl_module
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = "openrouter.ai"
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    body = json.dumps(data, ensure_ascii=False).encode("utf-8")

    ctx = ssl_module.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl_module.CERT_NONE

    log(f"make_request_socket_ip() connecting to {ip_override}:{parsed.port or 443} with SNI={host}")

    sock = socket.create_connection((ip_override, parsed.port or 443), timeout=timeout)
    ssl_sock = ctx.wrap_socket(sock, server_hostname=host)

    # Build HTTP/1.1 request manually
    request_headers = {
        "Host": host,
        "User-Agent": headers.get("User-Agent", "SmartTest/1.0"),
        "Content-Type": headers.get("Content-Type", "application/json; charset=utf-8"),
        "Authorization": headers.get("Authorization", ""),
        "HTTP-Referer": headers.get("HTTP-Referer", ""),
        "X-Title": headers.get("X-Title", ""),
        "Accept": "application/json",
        "Content-Length": str(len(body)),
        "Connection": "close",
    }

    header_lines = "\r\n".join([f"{k}: {v}" for k, v in request_headers.items() if v])
    request_bytes = f"POST {path} HTTP/1.1\r\n{header_lines}\r\n\r\n".encode("utf-8") + body

    ssl_sock.sendall(request_bytes)

    response = http.client.HTTPResponse(ssl_sock)
    response.begin()
    status = response.status
    raw = response.read()
    log(f"Response via socket IP {ip_override}, status: {status}, len={len(raw)}")

    if status >= 400:
        raise Exception(f"HTTP {status}: {raw[:200]}")

    return json.loads(raw.decode("utf-8"))

def make_request(url, headers, data, timeout=60):
    """
    Make HTTP request using the best available method.
    Priority on Android: Java HttpURLConnection -> Kivy UrlRequest -> urllib -> IP fallbacks
    """
    log(f"make_request() starting...")
    errors = []
    
    # On Android, try Java HttpURLConnection FIRST (uses native Android network stack)
    if IS_ANDROID:
        log("Attempting Java HttpURLConnection (Android native)...")
        try:
            return make_request_java(url, headers, data, timeout)
        except ImportError as e:
            log(f"Java HTTP not available: {e}")
        except Exception as e:
            errors.append(f"Java: {e}")
            log(f"Java HTTP failed: {e}")
            log(f"Traceback: {traceback.format_exc()}")
    
    # Try Kivy UrlRequest
    log("Attempting Kivy UrlRequest...")
    try:
        return make_request_kivy(url, headers, data, timeout)
    except ImportError as e:
        log(f"Kivy UrlRequest not available: {e}")
    except Exception as e:
        errors.append(f"Kivy: {e}")
        log(f"Kivy UrlRequest failed: {e}")
        log(f"Traceback: {traceback.format_exc()}")
    
    # Try urllib (standard library, should always work)
    log("Attempting urllib...")
    try:
        return make_request_urllib(url, headers, data, timeout)
    except Exception as e:
        errors.append(f"urllib: {e}")
        log(f"urllib failed: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        # If DNS resolution failed, try direct IP fallbacks
        reason = getattr(e, "reason", None)
        reason_msg = str(reason) if reason else ""
        is_dns_error = (
            isinstance(e, socket.gaierror)
            or isinstance(reason, socket.gaierror)
            or "No address associated with hostname" in str(e)
            or "No address associated with hostname" in reason_msg
        )
        if reason:
            log(f"urllib error reason: {reason} ({type(reason)})")
        if is_dns_error:
            log("Detected DNS error, trying direct IP fallbacks for openrouter.ai ...")
            for ip in FALLBACK_OPENROUTER_IPS:
                try:
                    return make_request_urllib_ip(url, headers, data, timeout, ip_override=ip)
                except Exception as ip_err:
                    errors.append(f"ip {ip}: {ip_err}")
                    log(f"Fallback via {ip} failed: {ip_err}")
                    log(f"Traceback: {traceback.format_exc()}")
                try:
                    return make_request_socket_ip(url, headers, data, timeout, ip_override=ip)
                except Exception as ip_err:
                    errors.append(f"socket {ip}: {ip_err}")
                    log(f"Socket fallback via {ip} failed: {ip_err}")
                    log(f"Traceback: {traceback.format_exc()}")
    
    # All methods failed
    error_msg = f"Все методы HTTP не сработали: {'; '.join(errors)}"
    log(error_msg)
    raise Exception(error_msg)

def generate_quiz(topic, difficulty="средний", api_key=None):
    """Generate a quiz using OpenRouter API"""
    log(f"=== generate_quiz() starting ===")
    log(f"  Topic: {topic}")
    log(f"  Difficulty: {difficulty}")
    log(f"  API key provided: {api_key is not None}")
    log(f"  Platform: {sys.platform}")
    log(f"  IS_ANDROID: {IS_ANDROID}")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Get API key
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
        log(f"API key from env: {api_key is not None}")
    
    if not api_key:
        msg = "API ключ не найден. Введите ключ в настройках."
        log(msg)
        return generate_mock_quiz(topic, difficulty, error=msg)
    
    log(f"Using API Key: {api_key[:10]}...{api_key[-5:]}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "SmartTest/1.0",
        "HTTP-Referer": "https://github.com/bagdan13040/smarttest",
        "X-Title": "SmartTest"
    }
    log(f"Headers prepared: {list(headers.keys())}")
    
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
        "model": "xiaomi/mimo-v2-flash:free",
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
    log(f"Model: {data['model']}")
    
    try:
        log(f"Sending request to OpenRouter...")
        result = make_request(url, headers, data, timeout=60)
        log(f"Got response from OpenRouter")
        log(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            log(f"Content length: {len(content)}")
            log(f"Content preview: {content[:200]}...")
            content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                log("Parsing JSON response...")
                response_data = json.loads(content)
                
                if not isinstance(response_data, dict) or 'theory' not in response_data or 'questions' not in response_data:
                    log(f"Invalid response structure: {list(response_data.keys()) if isinstance(response_data, dict) else 'not a dict'}")
                    return generate_mock_quiz(topic, difficulty, error="Неверная структура ответа API")
                
                quiz_data = response_data['questions']
                log(f"Quiz has {len(quiz_data) if isinstance(quiz_data, list) else 0} questions")
                if not isinstance(quiz_data, list):
                    log(f"questions is not a list: {type(quiz_data)}")
                    return generate_mock_quiz(topic, difficulty, error="questions не список")
                
                valid_quiz = []
                for item in quiz_data:
                    if (isinstance(item, dict) and 
                        'question' in item and isinstance(item['question'], str) and
                        'options' in item and isinstance(item['options'], list) and len(item['options']) == 4 and
                        'answer' in item and isinstance(item['answer'], int) and 0 <= item['answer'] <= 3):
                        valid_quiz.append(item)
                
                if not valid_quiz:
                    log("No valid questions found after validation")
                    return generate_mock_quiz(topic, difficulty, error="Нет валидных вопросов")
                
                log(f"Validated {len(valid_quiz)} questions")
                meta = response_data.get('meta', {})
                meta['topic'] = topic
                meta['difficulty'] = difficulty
                
                log("Quiz generated successfully!")
                return {'theory': response_data['theory'], 'questions': valid_quiz, 'meta': meta}
                
            except json.JSONDecodeError as e:
                log(f"JSON parse error: {e}")
                log(f"Content was: {content[:500]}...")
                return generate_mock_quiz(topic, difficulty, error=f"Ошибка парсинга JSON: {e}")
        else:
            log(f"No choices in response: {result}")
            return generate_mock_quiz(topic, difficulty, error=f"Некорректный ответ API")
            
    except Exception as e:
        log(f"Exception in generate_quiz: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        return generate_mock_quiz(topic, difficulty, error=str(e))

def generate_mock_quiz(topic, difficulty, error=None):
    """Generate a mock quiz when API is unavailable"""
    log(f"generate_mock_quiz() called")
    log(f"  Error: {error}")
    
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
