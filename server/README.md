# SmartTest Backend Server

Централизованный API сервер для обработки LLM запросов SmartTest приложения.

## 🚀 Быстрый Старт

### 1. Установка зависимостей

```bash
# Перейти в папку сервера
cd server

# Создать виртуальное окружение (опционально)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка API ключа

```bash
# Скопировать пример конфигурации
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Открыть .env и вставить свой OpenRouter API ключ
notepad .env  # или любой другой редактор
```

Содержимое `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-ваш-реальный-ключ-здесь
PORT=8000
```

**Как получить API ключ:**
1. Перейти на https://openrouter.ai/
2. Зарегистрироваться/войти
3. Перейти в Keys → Create Key
4. Пополнить баланс ($5 хватит на старт)

### 3. Запуск сервера

```bash
# Локальный запуск
python main.py

# Или через uvicorn напрямую
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: **http://localhost:8000**

### 4. Проверка работоспособности

Открыть в браузере:
- http://localhost:8000/ — главная страница
- http://localhost:8000/health — проверка здоровья
- http://localhost:8000/docs — Swagger документация (интерактивная)

## 📡 API Endpoints

### `POST /api/v1/generate-quiz`
Генерация урока с теорией и тестами

**Request Body:**
```json
{
  "topic": "Python Functions",
  "level": "Intermediate",
  "user_interests": "game development",
  "device_id": "unique-device-id-123"
}
```

### `POST /api/v1/generate-roadmap`
Создание дорожной карты обучения

**Request Body:**
```json
{
  "topic": "Machine Learning",
  "goal": "Become ML Engineer",
  "level": "Beginner",
  "user_interests": "finance",
  "device_id": "unique-device-id-123"
}
```

### `POST /api/v1/generate-questions`
Генерация открытых вопросов

### `POST /api/v1/evaluate-answer`
Оценка ответа пользователя

### `POST /api/v1/chat-with-image`
Анализ изображения через Vision модель

## 🔒 Безопасность

### Rate Limiting
- **20 запросов/час** на device_id
- **5 запросов/минуту** на device_id

### CORS
В production измените `allow_origins` в `main.py`:
```python
allow_origins=["https://your-app-domain.com"]  # Вместо "*"
```

## 🌐 Деплой на Production

### Вариант 1: Railway.app (Рекомендуется)

1. Создать аккаунт на https://railway.app/
2. New Project → Deploy from GitHub
3. Подключить репозиторий
4. Добавить переменные окружения:
   - `OPENROUTER_API_KEY` = ваш ключ
   - `PORT` = 8000
5. Railway автоматически деплоит при каждом push

**Стоимость:** $5/месяц (Hobby план)

### Вариант 2: Render.com

1. Создать аккаунт на https://render.com/
2. New → Web Service
3. Подключить GitHub репозиторий
4. Build Command: `pip install -r server/requirements.txt`
5. Start Command: `cd server && python main.py`
6. Добавить Environment Variables
7. Deploy

**Стоимость:** Бесплатно (с ограничениями) или $7/месяц

### Вариант 3: Fly.io

1. Установить CLI: `curl -L https://fly.io/install.sh | sh`
2. `fly launch` в папке server/
3. `fly secrets set OPENROUTER_API_KEY=ваш-ключ`
4. `fly deploy`

**Стоимость:** ~$3/месяц

## 🐳 Docker (Опционально)

```dockerfile
# Dockerfile уже включён в проект
docker build -t smarttest-backend .
docker run -p 8000:8000 -e OPENROUTER_API_KEY=ваш-ключ smarttest-backend
```

## 📊 Мониторинг

### Просмотр логов
```bash
# В Railway/Render можно смотреть логи в веб-интерфейсе
# Локально:
tail -f logs.txt  # если настроен file logging
```

### Метрики
- Количество запросов: логируется каждый вызов
- Время ответа: в логах
- Ошибки: уровень ERROR в логах

## 🔧 Troubleshooting

### Проблема: "Все модели LLM недоступны"
**Решение:** 
1. Проверьте баланс на OpenRouter
2. Проверьте правильность API ключа
3. Попробуйте другую модель в коде

### Проблема: 429 Too Many Requests
**Решение:** Увеличьте лимиты в `main.py`:
```python
MAX_REQUESTS_PER_HOUR = 50  # было 20
```

### Проблема: Медленные ответы
**Решение:**
1. Используйте более быструю модель
2. Уменьшите `max_tokens`
3. Добавьте Redis для кеширования

## 📈 Масштабирование

### Для большой нагрузки:
1. Добавить Redis для rate limiting
2. Использовать PostgreSQL для статистики
3. Настроить load balancer (Nginx)
4. Horizontal scaling (несколько инстансов)

### Оптимизация расходов:
1. Кешировать популярные запросы
2. Использовать более дешёвые модели для простых задач
3. Сжимать промпты (убрать лишние слова)

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи сервера
2. Проверьте `/health` endpoint
3. Убедитесь что API ключ валиден
4. Проверьте баланс OpenRouter

## 🔄 Обновления

Для обновления сервера:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
# Restart server
```

---

**Версия:** 1.0.0  
**Дата:** 2026-02-02  
**Лицензия:** MIT
