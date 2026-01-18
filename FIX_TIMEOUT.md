## Что исправлено

### Проблема
- Запросы к OpenRouter API истекали по timeout (60 секунд)
- На Windows Kivy UrlRequest оказался нестабильнее, чем стандартная urllib

### Решение

#### 1. Увеличен timeout
- Изменено с 60 на 120 секунд в `generate_quiz()`
- Дает больше времени на медленный интернет и большие генерации

#### 2. Переупорядочена приоритизация методов
```
На Desktop (Windows/Linux/Mac):
1. urllib (стандартная библиотека, самая стабильная)
2. Kivy UrlRequest (fallback)
3. IP fallbacks для DNS ошибок

На Android:
1. Java HttpURLConnection (нативный стек)
2. urllib (стандартная)
3. Kivy UrlRequest
4. IP fallbacks
```

#### 3. Улучшены логи
- Добавлено `timeout={timeout}s` в логи make_request
- Логирование каждого этапа попыток подключения

### Что проверено
✓ OpenRouter API доступен (HTTP 204 на OPTIONS)
✓ DNS разрешается правильно (openrouter.ai → 104.18.3.115)
✓ Синтаксис llm.py исправлен

### Как тестировать

1. Установить API ключ (в PowerShell):
```powershell
$env:OPENROUTER_API_KEY = "your-api-key-here"
```

2. Запустить тест:
```bash
python test_generation.py
```

3. Если работает - запустить приложение:
```bash
python main.py
```

### Что дальше

Если генерация всё ещё не работает:
1. Проверить логи в `llm_debug.log`
2. Убедиться, что API ключ валиден
3. Проверить, есть ли в аккаунте kredits/баланс
4. Посмотреть разделы с `[LLM]` префиксом в логах
