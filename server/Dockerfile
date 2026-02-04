# SmartTest Backend Dockerfile
FROM python:3.10-slim

# Установка рабочей директории
WORKDIR /app

# Копирование requirements
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY main.py .

# Порт который будет использоваться
EXPOSE 8000

# Переменные окружения по умолчанию
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Запуск сервера
CMD ["python", "main.py"]
