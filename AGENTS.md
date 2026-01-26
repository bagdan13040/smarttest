# AGENTS.md - Документация для AI Агентов

## 📋 Обзор Проекта

**SmartTest** - мобильное приложение на Kivy для адаптивного обучения с использованием LLM (Language Model).

### Основная концепция
Приложение генерирует персонализированные учебные материалы и тесты по любой теме, оценивает ответы пользователя через LLM, и адаптирует сложность на основе результатов. Поддерживает как одиночные уроки, так и полноценные "Дорожные карты" (Roadmaps).

### Технологический стек
- **Framework**: Kivy 2.3.1 (Python GUI) + KivyMD
- **Language**: Python 3.10+
- **LLM Integration**: Пользовательский модуль `llm.py` (OpenRouter API)
- **Storage**: JSON-based (JsonStore, `courses.json`, `roadmaps.json`)
- **Target Platform**: Android (с поддержкой Desktop)

---

## 🏗️ Архитектура Приложения

### Структура файлов
```
main.py               # Основной файл приложения (~5850 строк)
llm.py               # LLM интеграция (1400+ строк)
courses.json         # Хранилище курсов
roadmaps.json        # Хранилище дорожных карт
settings.json        # Настройки пользователя
open_questions_cache.json  # Кеш развёрнутых вопросов
course_topics.json   # История тем
assets/              # Иконки и ресурсы
```

### Основные компоненты

#### 1. Экраны (Screens)
```
MainScreen           → Главный экран с тремя табами
├── SavedScreen      → Список сохранённых курсов и дорожных карт
├── SearchScreen     → Поиск и создание (Урок / Дорожная карта)
└── SettingsScreen   → Настройки API и системы

LoadingScreen        → Экран загрузки с фактами
TheoryScreen         → Отображение теории
QuizScreen           → MC тест (множественный выбор)
OpenAnswerScreen     → Развёрнутые ответы
RoadmapScreen        → Визуализация программы обучения (Grafo-подобная сетка)
FinalScreen          → Финальный отчёт с ошибками
```

#### 2. Хранилища данных

**CourseStorage** (`courses.json`): Хранит отдельные уроки.
**RoadmapStorage** (`roadmaps.json`): Хранит дорожные карты и прогресс по модулям.

**Кеш открытых вопросов** (`open_questions_cache.json`):
```python
{
  "тема|сложность": [вопросы...]
}
```

#### 3. LLM Модуль (llm.py)

**Ключевые функции**:
- `generate_quiz(topic, difficulty, api_key, interests)` - генерация урока (теория + MC)
- `generate_learning_roadmap(topic, goal, level, api_key)` - генерация программы из модулей
- `generate_open_questions(topic, n, difficulty, api_key)` - открытые вопросы
- `evaluate_answer(question, answer, notes, api_key)` - оценка ответа
- `chat_with_image(message, image_path, api_key)` - Vision-поддержка (Gemini 2.0 Flash)

---

## 🔄 Потоки Данных

### 1. Создание нового курса/карты
```
SearchScreen.start_new_quiz() / start_roadmap_generation()
    ↓
MyApp.generate_quiz_thread() / generate_roadmap_thread()
    ↓
llm.generate_quiz() / llm.generate_learning_roadmap()
    ↓
MyApp.on_generation_complete()
    ↓
TheoryScreen (для урока) или RoadmapScreen (для программы)
```

### 2. Система дорожных карт (Roadmaps)
1. Генератор создает список модулей с зависимостями (`prerequisites`).
2. `RoadmapScreen` отрисовывает их узлами.
3. Клик на узел открывает детали модуля.
4. "Начать изучение" модуля запускает стандартный поток урока для темы модуля.

### 3. Предзагрузка открытых вопросов
Запускается в фоне на `QuizScreen`, чтобы к моменту окончания MC-теста вопросы уже были готовы (из кеша или сгенерированы).

---

## ⚡ Ключевые Особенности Реализации

### 1. Мульти-модельный Fallback (llm.py)
Если основная модель (`xiaomi/mimo-v2-flash:free`) недоступна, система автоматически пробует альтернативы:
- `google/gemini-2.0-flash-exp:free`
- `meta-llama/llama-3.1-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

### 2. Поддержка Vision (Зрение)
Интеграция функции `chat_with_image` позволяет анализировать скриншоты или фото учебников для генерации вопросов или пояснений (используется в Vision-тестах).

### 3. Адаптивная сложность и Контекст интересов
При генерации курса можно передать `interests` пользователя. LLM адаптирует примеры в теории под эти интересы (например, объясняет физику через футбол).

---

## 🎨 UI/UX Паттерны

### Roadmap Visualization
- Модули отображаются в сетке.
- Связи отрисовываются линиями (Canvas `Line`).
- Цвета: Серый (не начато), Синий (в процессе), Зеленый (пройдено).

### Асинхронность
Все запросы к API идут через `threading`, чтобы не фризить UI. Обратный вызов в GUI через `Clock.schedule_once`.

---

## 🔧 Типичные Проблемы и Решения

- **Таймауты**: Увеличены до 120 секунд для стабильности на плохом соединении.
- **Unicode-символы**: Используется `sanitize_unicode` в `llm.py` для замены спецсимволов на понятные Kivy ASCII/простые UTF.
- **Android Settings**: На Android рекомендуется вводить API ключ через UI (SettingsScreen), так как `.env` часто не подхватывается.

---

**Версия документа**: 1.1 (Roadmap & Vision Update)  
**Дата**: 2026-01-26  
**Размер кодовой базы**: ~5850 строк (main.py) + 1400+ (llm.py)
