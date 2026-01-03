"""
SmartTest - Приложение для интеллектуального тестирования с AI
Автоматическая генерация теории, тестов и открытых вопросов на основе LLM.

Основные функции:
- Генерация образовательного контента по любой теме
- MC (Multiple Choice) тесты с автоматической проверкой
- Открытые вопросы с AI-оценкой ответов
- Адаптивная сложность на основе результатов
- Кеширование вопросов для быстрого доступа
- Полный отчёт с работой над ошибками
"""

print("[MAIN] === Application Starting ===")
import sys
import traceback as tb_module
print(f"[MAIN] Python version: {sys.version}")
print(f"[MAIN] Platform: {sys.platform}")

# ========================================
# ПРОВЕРКА ПЛАТФОРМЫ
# ========================================
# Определяем, запущено ли приложение на Android
# (в будущем можно добавить специфичную логику для мобильной версии)
IS_ANDROID = False
try:
    from android.permissions import request_permissions, Permission
    IS_ANDROID = True
    print("[MAIN] Running on Android")
except ImportError:
    print("[MAIN] Running on Desktop")

# ========================================
# ИМПОРТЫ KIVY
# ========================================
# Импортируем все необходимые компоненты Kivy для построения UI
try:
    print("[MAIN] UI widgets imported")
    from kivy.app import App  # Основной класс приложения
    from kivy.lang import Builder  # Парсер KV языка для описания UI
    from kivy.core.window import Window  # Управление окном приложения
    from kivy.uix.screenmanager import ScreenManager, Screen  # Менеджер экранов
    from kivy.uix.boxlayout import BoxLayout  # Линейный layout
    from kivy.uix.anchorlayout import AnchorLayout  # Layout для центрирования
    from kivy.uix.gridlayout import GridLayout  # Табличный layout
    from kivy.uix.label import Label  # Текстовые метки
    from kivy.uix.image import Image  # Изображения
    from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior  # Поведение кнопок
    from kivy.uix.button import Button  # Стандартные кнопки
    from kivy.uix.togglebutton import ToggleButton  # Переключаемые кнопки
    from kivy.uix.scrollview import ScrollView  # Прокручиваемые области
    from kivy.uix.textinput import TextInput  # Поля ввода текста
    from kivy.uix.widget import Widget  # Базовый виджет
    from kivy.metrics import dp  # Density-independent pixels для кросс-платформенности
    from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty  # Реактивные свойства

    print("[MAIN] graphics imported")
    from kivy.graphics import Color, RoundedRectangle, Rectangle  # Графические примитивы
    print("[MAIN] Clock imported")
    from kivy.clock import Clock  # Планировщик событий
    print("[MAIN] metrics imported")
except Exception as e:
    print(f"[MAIN] ERROR importing kivy: {e}")
    print(f"[MAIN] Traceback: {tb_module.format_exc()}")
    raise

# ========================================
# СТАНДАРТНЫЕ БИБЛИОТЕКИ
# ========================================
print("[MAIN] Importing standard modules...")
from datetime import datetime  # Работа с датой и временем
import threading  # Многопоточность для асинхронных операций
import random  # Генерация случайных чисел
import json  # Работа с JSON
import os  # Работа с файловой системой
import uuid  # Генерация уникальных идентификаторов
print("[MAIN] Standard modules imported")

# ========================================
# ИМПОРТ LLM МОДУЛЯ
# ========================================
# Модуль llm.py содержит функции для работы с AI:
# - generate_quiz: генерация теории и MC вопросов
# - generate_open_questions: генерация открытых вопросов
# - evaluate_answer: оценка развёрнутых ответов
# - generate_next_topics: предложение тем для углубления
print("[MAIN] Importing llm module...")
try:
    from llm import generate_quiz, generate_next_topics, get_course_topics, generate_open_questions, evaluate_answer, chat_with_image
    print("[MAIN] llm module imported successfully")
except Exception as e:
    print(f"[MAIN] Error importing llm: {e}")
    print(f"[MAIN] Traceback: {tb_module.format_exc()}")
    # Fallback функции если LLM модуль не загружен
    def chat_with_image(message, image_path=None, history=None, api_key=None, model="google/gemini-2.0-flash-exp:free"):
        return {"content": "Ошибка: модуль LLM не загружен.", "role": "assistant"}

    def generate_quiz(topic, difficulty):
        return {
            "theory": f"Ошибка загрузки модуля LLM: {e}. Проверьте логи.",
            "questions": [
                {"question": "Ошибка", "options": ["Ок", "Ок", "Ок", "Ок"], "answer": 0}
            ]
        }
    def generate_next_topics(prev_material, n=5, api_key=None, memory_file='course_topics.json'):
        return []

    def get_course_topics(memory_file='course_topics.json'):
        return []

# ========================================
# НАСТРОЙКА ОКНА
# ========================================
# Устанавливаем тёплый светлый фон для всего приложения
Window.clearcolor = (0.95, 0.93, 0.90, 1)
# Window.size закомментирован для корректного масштабирования на Android

# ========================================
# ОБРАЗОВАТЕЛЬНЫЙ КОНТЕНТ
# ========================================
# Интересные факты, показываемые на экране загрузки
# для развлечения пользователя во время генерации контента
INTERESTING_FACTS = [
    "Первый компьютерный баг был настоящим мотыльком, застрявшим в реле.",
    "Сердце синего кита весит столько же, сколько автомобиль.",
    "Мёд — единственный продукт, который никогда не портится. Его находили в гробницах фараонов.",
    "Венера — единственная планета Солнечной системы, вращающаяся по часовой стрелке.",
    "Осьминоги имеют три сердца и голубую кровь.",
    "Бананы с ботанической точки зрения являются ягодами, а клубника — нет.",
    "В теле человека достаточно железа, чтобы сделать гвоздь длиной 7 см.",
    "Колибри — единственная птица, способная летать назад.",
    "Самая короткая война в истории длилась 38 минут (между Британией и Занзибаром)",
    "В Австралии кроликов больше, чем людей в Китае.",
    "Алмазы могут гореть, если их нагреть до 720-800 градусов Цельсия.",
    "Вода в горячем состоянии замерзает быстрее, чем в холодном (эффект Мпембы).",
    "У жирафа такой же длинный язык, что он может чистить им свои уши.",
    "В космосе полная тишина, так как там нет воздуха для распространения звука.",
    "Самое глубокое место на Земле — Марианская впадина (около 11 км).",
    "Бамбук может расти со скоростью до 91 см в день.",
    "В теле взрослого человека 206 костей, а у ребенка — около 300.",
    "Самая большая пустыня в мире — Антарктическая (полярная пустыня).",
    "Свет от Солнца доходит до Земли за 8 минут и 20 секунд.",
    "Python назван в честь комедийной группы 'Монти Пайтон', а не змеи.",
    "Первая веб-камера была создана, чтобы проверять кофейник в Кембридже.",
    "Символ @ использовался еще в средние века для обозначения меры веса.",
    "Самый популярный пароль в мире — '123456'. Не используйте его!",
    "Первый домен .com был зарегистрирован 15 марта 1985 года (symbolics.com).",
    "В 1956 году жесткий диск на 5 МБ весил около тонны.",
    "Google обрабатывает более 3.5 миллиардов поисковых запросов в день.",
    "Первая мышь была сделана из дерева.",
    "Код запуска ядерных ракет США долгое время был '00000000'.",
    "В среднем программист делает от 10 до 50 ошибок на каждые 1000 строк кода.",
    "Linux используется на всех суперкомпьютерах из топ-500 мира.",
    "Первая SMS была отправлена в 1992 году с текстом 'Merry Christmas'.",
    "QWERTY-раскладка была создана, чтобы замедлить машинисток и избежать залипания клавиш.",
    "В Японии есть роботы, которые могут готовить суши.",
    "Первый логотип Apple изображал Исаака Ньютона под яблоней.",
    "Wi-Fi не имеет расшифровки, это просто маркетинговое название.",
    "Каждую минуту на YouTube загружается более 500 часов видео.",
    "Первый твит был опубликован Джеком Дорси в 2006 году: 'just setting up my twttr'.",
    "В 1999 году NASA потеряло спутник из-за путаницы между метрической и дюймовой системами.",
    "Самый дорогой домен в истории — cars.com (872 млн долларов).",
    "В Норвегии доступ к интернету является правом человека.",
    "Первый смайлик :-) был предложен профессором Скоттом Фалманом в 1982 году.",
    "Каждый день отправляется более 300 миллиардов электронных писем.",
    "В Китае есть лагеря для лечения интернет-зависимости.",
    "Первая компьютерная игра Spacewar! была создана в 1962 году.",
    "Билл Гейтс написал свою первую программу в 13 лет (крестики-нолики).",
    "В 2012 году Facebook купил Instagram за 1 миллиард долларов.",
    "Первый iPhone был представлен Стивом Джобсом в 2007 году.",
    "В Антарктиде есть банкомат.",
    "Самая популярная операционная система в мире — Android.",
    "В 1980-х годах 1 ГБ памяти стоил около 100 000 долларов.",
    "Первый вирус Creeper просто выводил сообщение: 'Я Creeper, поймай меня, если сможешь'.",
    "В Финляндии доступ к широкополосному интернету гарантирован законом.",
    "Каждый день в мире взламывают около 30 000 сайтов.",
    "Первый баннер в интернете появился в 1994 году.",
    "В 2000 году флешка на 8 МБ стоила около 50 долларов.",
    "Самый быстрый суперкомпьютер Frontier выполняет 1.1 квинтиллиона операций в секунду.",
    "В 1971 году было отправлено первое электронное письмо.",
    "В мире больше мобильных телефонов, чем людей.",
    "Первый браузер назывался WorldWideWeb (позже переименован в Nexus).",
    "В 1995 году доменное имя было бесплатным.",
    "В среднем человек проверяет телефон 58 раз в день.",
    "Первый жесткий диск IBM 305 RAMAC (1956) вмещал 5 МБ данных.",
    "В 2005 году YouTube был сайтом знакомств.",
    "В 2010 году биткоин стоил меньше цента.",
    "Первый смартфон IBM Simon появился в 1992 году.",
    "В 1998 году Google хранился на 10 жестких дисках по 4 ГБ.",
    "В 2004 году Gmail был запущен 1 апреля, и многие думали, что это шутка.",
    "В 2009 году был добыт первый блок биткоина (Genesis Block)."
]

from kivy.storage.jsonstore import JsonStore

class CourseStorage:
    """
    Класс для управления хранилищем курсов и тестов.
    
    Хранит все пройденные курсы в JSON файле, включая:
    - Мета-информацию (тема, сложность, дата)
    - Сгенерированную теорию
    - Вопросы для тестирования
    - Историю прохождения
    - Краткие заметки
    
    Файл: courses.json в директории пользовательских данных приложения
    """
    
    def __init__(self, filename='courses.json'):
        """
        Инициализация хранилища.
        
        Args:
            filename: Путь к JSON файлу для хранения курсов
        """
        self.filename = filename
        self.courses = self.load()  # Загружаем существующие курсы

    def load(self):
        """
        Загружает курсы из JSON файла.
        
        Returns:
            list: Список курсов или пустой список если файл не существует
        """
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save(self, course):
        """
        Сохраняет курс в хранилище.
        
        Если курс с такой же темой и сложностью уже существует - обновляет его.
        Иначе добавляет новый курс. Перемещает курс в начало списка.
        
        Args:
            course: Словарь с данными курса, должен содержать ключ 'meta' с 'topic' и 'difficulty'
        """
        topic = course.get('meta', {}).get('topic', '')
        difficulty = course.get('meta', {}).get('difficulty', '')
        
        # Ищем существующий курс с такими же параметрами
        for idx, c in enumerate(self.courses):
            if c.get('meta', {}).get('topic') == topic and \
               c.get('meta', {}).get('difficulty') == difficulty:
                # Обновляем существующий курс и перемещаем в начало списка
                self.courses[idx] = course
                self.courses.insert(0, self.courses.pop(idx))
                self._write()
                return

        # Если курс не найден, добавляем новый в начало списка
        self.courses.insert(0, course)
        self._write()

    def find(self, topic, difficulty):
        """
        Ищет курс по теме и сложности.
        
        Args:
            topic: Название темы курса
            difficulty: Уровень сложности ('easy', 'medium', 'hard')
            
        Returns:
            dict|None: Найденный курс или None если курс не найден
        """
        for c in self.courses:
            meta = c.get('meta', {})
            if meta.get('topic') == topic and meta.get('difficulty') == difficulty:
                return c
        return None

    def update_entry(self, topic, difficulty, updater):
        """
        Обновляет существующий курс с помощью функции-обновителя.
        
        Args:
            topic: Название темы курса
            difficulty: Уровень сложности
            updater: Функция, принимающая словарь курса и модифицирующая его
            
        Returns:
            dict|None: Обновленный курс или None если курс не найден
        """
        for idx, c in enumerate(self.courses):
            meta = c.get('meta', {})
            if meta.get('topic') == topic and meta.get('difficulty') == difficulty:
                updater(c)  # Вызываем функцию обновления
                # Перемещаем обновленный курс в начало списка
                self.courses.insert(0, self.courses.pop(idx))
                self._write()
                return c
        return None

    def delete(self, topic, difficulty):
        """
        Удаляет курс из хранилища.
        
        Args:
            topic: Название темы курса
            difficulty: Уровень сложности
            
        Returns:
            bool: True если курс был удален, False если курс не найден
        """
        removed = False
        for idx, c in enumerate(self.courses):
            meta = c.get('meta', {})
            if meta.get('topic') == topic and meta.get('difficulty') == difficulty:
                self.courses.pop(idx)
                removed = True
                break
        if removed:
            self._write()
        return removed

    def _write(self):
        """
        Записывает текущий список курсов в JSON файл.
        
        Внутренний метод для сохранения состояния хранилища на диск.
        """
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)
            
    def get_all(self):
        """
        Возвращает список всех курсов.
        
        Returns:
            list: Список всех сохраненных курсов
        """
        return self.courses


# ============================================================================
# KV MARKUP LANGUAGE - ДЕКЛАРАТИВНОЕ ОПИСАНИЕ ИНТЕРФЕЙСА
# ============================================================================
# Kivy использует язык KV для описания UI компонентов
# Формат: ClassName: с отступами для вложенных элементов
# Свойства: property: value
# Привязки: self.property для реактивных обновлений

KV = """
#:import dp kivy.metrics.dp

# Главный менеджер экранов - переключает между основными экранами приложения
ScreenManager:
    MainScreen:
    LoadingScreen:
    TheoryScreen:
    QuizScreen:
    OpenAnswerScreen:
    ChatScreen:
    FinalScreen:

# NavButton - Кнопка нижней навигации (табы)
# Унаследована от ToggleButton для поддержки выбора активного таба
<NavButton@ToggleButton>:
    background_normal: ''  # Отключаем стандартный фон
    background_down: ''
    background_color: 0, 0, 0, 0  # Прозрачный фон
    group: 'nav'  # Группа для взаимоисключающего выбора
    allow_no_selection: False  # Всегда должна быть выбрана одна кнопка
    # Цвет текста: серый если не активна, синий если активна
    color: (0.5, 0.5, 0.5, 1) if self.state == 'normal' else (0.15, 0.55, 0.9, 1)
    bold: True if self.state == 'down' else False
    font_size: '16sp'
    halign: 'center'
    valign: 'middle'
    text_size: self.size
    canvas.before:
        Color:
            # Синяя линия сверху для активной кнопки
            rgba: (0.15, 0.55, 0.9, 1) if self.state == 'down' else (0, 0, 0, 0)
        Line:
            # Рисуем горизонтальную линию сверху кнопки
            points: [self.x + self.width * 0.2, self.y + self.height - 2, self.x + self.width * 0.8, self.y + self.height - 2]
            width: 2 if self.state == 'down' else 0.001

# MainScreen - Главный экран приложения с тремя табами
<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        size_hint: (1, 1)
        padding: [0, dp(30), 0, 0]  # Отступ сверху для статус-бара Android
        
        # Хедер с логотипом и статусом сети
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            padding: [dp(16), 0]
            
            Label:
                text: 'SmartTest'
                font_size: '18sp'
                bold: True
                color: 0.15, 0.55, 0.9, 1  # Основной синий цвет
                halign: 'left'
                text_size: self.size
                valign: 'middle'
            
            Button:
                text: 'AI'
                size_hint: None, None
                size: dp(30), dp(30)
                background_normal: ''
                background_color: 0.15, 0.55, 0.9, 1
                color: 1, 1, 1, 1
                bold: True
                on_release: app.root.current = 'chat'

            Label:
                id: network_status
                text: '⚡'  # Иконка статуса подключения
                font_size: '18sp'
                color: 0.5, 0.5, 0.5, 1
                halign: 'right'
                text_size: self.size
                valign: 'middle'

        # Менеджер табов - переключает между сохраненными, поиском, настройками
        ScreenManager:
            id: tab_manager
            size_hint: (1, 1)
            SavedScreen:
                name: 'saved'
            SearchScreen:
                name: 'search'
            SettingsScreen:
                name: 'settings'
                
        # Нижняя навигация - фиксированная панель с кнопками табов
        BoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: [dp(12), dp(8), dp(12), dp(8)]
            spacing: dp(32)
            canvas.before:
                Color:
                    rgba: 0, 0, 0, 0
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 0.92, 0.92, 0.92, 1
                Line:
                    points: [self.x, self.y + self.height, self.x + self.width, self.y + self.height]
                    width: 1

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    id: nav_saved
                    size: dp(34), dp(34)
                    icon_source: 'assets/icons/free-icon-font-home-3917033.png'
                    target_screen: 'saved'
                    group: 'main_nav'

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    id: nav_search
                    size: dp(34), dp(34)
                    icon_source: 'assets/icons/free-icon-font-search-3917132.png'
                    target_screen: 'search'
                    group: 'main_nav'

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    id: nav_settings
                    size: dp(34), dp(34)
                    icon_source: 'assets/icons/free-icon-font-settings-sliders-3917103.png'
                    target_screen: 'settings'
                    group: 'main_nav'

<SavedScreen>:
    on_enter: app.load_saved_courses_ui()
    BoxLayout:
        orientation: 'vertical'
        padding: [16, 16]
        spacing: 10
        
        Label:
            text: 'Сохраненные курсы'
            color: 0.15, 0.55, 0.9, 1
            font_size: '22sp'
            bold: True
            size_hint_y: None
            height: 40
            halign: 'left'
            text_size: (self.width, None)

        ScrollView:
            GridLayout:
                id: courses_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 10

<SearchScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(12), dp(8), dp(12), dp(8)]
        spacing: dp(8)

        BoxLayout:
            padding: [dp(16), dp(8), dp(16), dp(16)]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: (0.95, 0.93, 0.90, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(20)]
            orientation: 'vertical'
            size_hint_y: None
            height: dp(320)
            Label:
                text: 'Добро пожаловать! Введите тему для теста:'
                color: 0.15, 0.55, 0.9, 1
                font_size: '18sp'
                halign: 'center'
                valign: 'middle'
                text_size: self.width - dp(24), None
                size_hint_y: None
                height: dp(60)

            TextInput:
                id: topic_input
                hint_text: 'Например: Космос'
                multiline: False
                size_hint_y: None
                height: dp(50)
                font_size: '18sp'
                padding: [dp(10), dp(12)]
                background_normal: ''
                background_active: ''
                background_color: 1, 1, 1, 1
                foreground_color: 0, 0, 0, 1
                cursor_color: 0.15, 0.55, 0.9, 1
                halign: 'center'

            Label:
                text: 'Сложность:'
                color: 0.5, 0.5, 0.5, 1
                font_size: '14sp'
                size_hint_y: None
                height: dp(20)

            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(10)
                DifficultyButton:
                    text: 'Легкий'
                    state: 'down'
                    on_release: app.set_difficulty('легкий')
                DifficultyButton:
                    text: 'Средний'
                    on_release: app.set_difficulty('средний')
                DifficultyButton:
                    text: 'Эксперт'
                    on_release: app.set_difficulty('эксперт')

            Widget:
                size_hint_y: None
                height: dp(10)

            RoundedButton:
                text: 'НАЧАТЬ ТЕСТ'
                font_size: '20sp'
                bold: True
                size_hint: None, None
                size: dp(280), dp(60)
                pos_hint: {'center_x': 0.5}
                on_release: app.start_generation()

        Widget:

<SettingsScreen>:
    on_enter: app.load_settings_ui()
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(16), dp(16)]
        spacing: dp(12)
        
        Label:
            text: 'Настройки'
            color: 0.15, 0.55, 0.9, 1
            font_size: '22sp'
            bold: True
            size_hint_y: None
            height: dp(40)
            halign: 'left'
            text_size: (self.width, None)

        Label:
            text: 'API Ключ OpenRouter:'
            color: 0.4, 0.4, 0.4, 1
            font_size: '16sp'
            size_hint_y: None
            height: dp(25)
            halign: 'left'
            text_size: (self.width, None)

        TextInput:
            id: api_key_input
            hint_text: 'sk-or-...'
            multiline: False
            size_hint_y: None
            height: dp(45)
            font_size: '16sp'
            padding: [dp(10), dp(10)]
            background_normal: ''
            background_active: ''
            background_color: 1, 1, 1, 1
            foreground_color: 0, 0, 0, 1
            cursor_color: 0.15, 0.55, 0.9, 1

        RoundedButton:
            text: 'СОХРАНИТЬ'
            font_size: '18sp'
            bold: True
            size_hint: None, None
            size: dp(280), dp(45)
            pos_hint: {'center_x': 0.5}
            bg_color: (0.15, 0.55, 0.9, 1)
            color: 1, 1, 1, 1
            on_release: app.save_settings()

        Label:
            id: status_label
            text: ''
            color: 0.3, 0.8, 0.4, 1
            font_size: '14sp'
            halign: 'center'
            size_hint_y: None
            height: dp(25)

        Label:
            text: 'Лог ошибок:'
            color: 0.5, 0.5, 0.5, 1
            font_size: '14sp'
            size_hint_y: None
            height: dp(18)

        ScrollView:
            size_hint_y: None
            height: dp(80)
            canvas.before:
                Color:
                    rgba: 0.9, 0.9, 0.9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: debug_log
                text: 'Ожидание событий...'
                color: 0, 0, 0, 1
                font_size: '10sp'
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'left'
                valign: 'top'
                padding: [dp(5), dp(5)]

        Widget:


<TheoryScreen>:
    name: 'theory'
    BoxLayout:
        orientation: 'vertical'
        padding: 16
        spacing: 12

        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            
            IconButton:
                size_hint: None, None
                size: dp(36), dp(36)
                default_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                pressed_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                on_release: app.root.current = 'main'
                canvas.before:
                    Color:
                        rgba: (0.9, 0.9, 0.9, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]

            Label:
                text: 'Теория'
                color: 0.15, 0.55, 0.9, 1
                font_size: '24sp'
                bold: True
                halign: 'center'
                text_size: self.size
                valign: 'middle'

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)
            Label:
                text: root.meta_title
                color: 0.2, 0.2, 0.2, 1
                font_size: '14sp'
                halign: 'left'
            Label:
                text: root.meta_sub
                color: 0.45, 0.45, 0.45, 1
                font_size: '14sp'
                halign: 'right'

        ScrollView:
            Label:
                id: theory_text
                text: root.theory_content
                color: 0.2, 0.2, 0.2, 1
                font_size: '16sp'
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'left'
                valign: 'top'
                padding: [dp(10), dp(10)]
                markup: True

        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(10)
            padding: [0, 0, 0, 0]
            Widget:
            RoundedButton:
                text: 'ПЕРЕЙТИ К ТЕСТУ'
                font_size: '18sp'
                bold: True
                size_hint: None, None
                size: dp(280), dp(50)
                bg_color: (0.15, 0.55, 0.9, 1)
                color: 1, 1, 1, 1
                on_release: app.start_quiz_from_theory()
            Widget:

<LoadingScreen>:
    name: 'loading'
    on_enter: root.start_fact_cycle()
    on_leave: root.stop_fact_cycle()
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(12)
        Widget:
            size_hint_y: 0.3
        DotSpinner:
            size_hint_y: None
            height: dp(40)
            pos_hint: {'center_x': 0.5}
        Label:
            text: 'Генерация курса'
            color: 0.5, 0.5, 0.5, 1
            font_size: '16sp'
            halign: 'center'
            size_hint_y: None
            height: dp(30)
        
        Widget:
            size_hint_y: 0.1
            
        Label:
            id: fact_label
            text: ''
            color: 0.4, 0.4, 0.4, 1
            font_size: '14sp'
            halign: 'center'
            valign: 'top'
            text_size: self.width, None
            size_hint_y: None
            height: dp(80)
            italic: True

        Widget:
            size_hint_y: 0.3



<QuizScreen>:
    name: 'quiz'
    question_index: 0
    score: 0
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            IconButton:
                size_hint: None, None
                size: dp(36), dp(36)
                default_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                pressed_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                on_release: app.root.current = 'main'
                canvas.before:
                    Color:
                        rgba: (0.9, 0.9, 0.9, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]

            Widget:

        Label:
            id: question_label
            text: root.current_question_text
            color: 0.15, 0.55, 0.9, 1
            font_size: '22sp'
            bold: True
            text_size: self.width - dp(30), None
            halign: 'center'
            valign: 'middle'
            size_hint_y: 0.35

        Label:
            text: str(root.question_index + 1) + '/' + str(len(root.questions))
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: dp(30)
            halign: 'center'
            font_size: '16sp'

        GridLayout:
            id: options_box
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(12)

        Label:
            id: result_label
            text: root.result_text
            size_hint_y: None
            height: self.texture_size[1]
            color: 0.25, 0.25, 0.25, 1
            font_size: '16sp'
        
        Widget:

<OpenAnswerScreen>:
    name: 'open_answer'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            IconButton:
                size_hint: None, None
                size: dp(36), dp(36)
                default_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                pressed_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                on_release: app.root.current = 'main'
                canvas.before:
                    Color:
                        rgba: (0.9, 0.9, 0.9, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]

            Widget:

        Label:
            id: progress_label
            text: 'Вопрос 1/3'
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: dp(30)
            halign: 'center'
            font_size: '16sp'

        ScrollView:
            size_hint_y: None
            height: dp(180)
            do_scroll_x: False
            Label:
                id: question_label
                text: ''
                color: 0.12, 0.45, 0.85, 1
                font_size: '20sp'
                bold: True
                text_size: self.parent.width - dp(30), None
                halign: 'left'
                valign: 'top'
                size_hint_y: None
                height: max(dp(100), self.texture_size[1])

        Widget:
            size_hint_y: None
            height: dp(12)

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.5
            spacing: dp(8)

            Label:
                text: 'Ваш развёрнутый ответ:'
                color: 0.4, 0.4, 0.45, 1
                font_size: '15sp'
                halign: 'left'
                size_hint_y: None
                height: dp(28)
                text_size: self.width, None

            BoxLayout:
                size_hint_y: 1
                canvas.before:
                    Color:
                        rgba: 0.7, 0.7, 0.8, 0.1
                    RoundedRectangle:
                        pos: self.x + dp(1), self.y - dp(2)
                        size: self.width, self.height
                        radius: [dp(16)]
                    Color:
                        rgba: 0.96, 0.97, 0.99, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(16)]
                TextInput:
                    id: answer_input
                    hint_text: '💭 Введите ваш ответ здесь...'
                    multiline: True
                    font_size: '16sp'
                    padding: [dp(16), dp(12)]
                    background_normal: ''
                    background_active: ''
                    background_color: 0, 0, 0, 0
                    foreground_color: 0.15, 0.15, 0.2, 1
                    cursor_color: 0.12, 0.45, 0.85, 1

            ScrollView:
                size_hint_y: 0.4
                Label:
                    id: feedback_label
                    text: ''
                    markup: True
                    color: 0.3, 0.3, 0.3, 1
                    font_size: '15sp'
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.parent.width - dp(20), None
                    padding: [dp(10), dp(10)]

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)

            RoundedButton:
                id: skip_button
                text: 'ПРОПУСТИТЬ'
                bg_color: (0.6, 0.6, 0.65, 1)
                font_size: '16sp'
                size_hint_x: 0.35
                on_release: app.skip_open_question()

            RoundedButton:
                id: action_button
                text: 'ОТПРАВИТЬ ✓'
                font_size: '17sp'
                bold: True
                size_hint_x: 0.65
                bg_color: (0.15, 0.55, 0.9, 1)
                color: 1, 1, 1, 1
                on_release: app.handle_open_answer_action()

        Widget:
            size_hint_y: None
            height: dp(10)

<ChatScreen>:
    name: 'chat'
    BoxLayout:
        orientation: 'vertical'
        padding: [0, 0, 0, dp(10)]
        
        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            padding: [dp(10), 0]
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            IconButton:
                size_hint: None, None
                size: dp(36), dp(36)
                default_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                pressed_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                on_release: app.root.current = 'main'
            
            Label:
                text: 'AI Чат (Vision)'
                color: 0.15, 0.55, 0.9, 1
                font_size: '18sp'
                bold: True
                halign: 'center'
                valign: 'middle'
                text_size: self.size

        # Chat History
        ScrollView:
            id: chat_scroll
            BoxLayout:
                id: chat_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(10), dp(10)]
                spacing: dp(10)

        # Input Area
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(10), dp(5)]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 0.95, 0.95, 0.95, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                id: attach_btn
                text: '📎'
                font_size: '20sp'
                size_hint: None, None
                size: dp(45), dp(40)
                pos_hint: {'center_y': 0.5}
                background_normal: ''
                background_color: 0.15, 0.55, 0.9, 1
                color: 1, 1, 1, 1
                on_release: root.show_image_chooser()

            TextInput:
                id: message_input
                hint_text: 'Сообщение...'
                multiline: False
                size_hint_y: None
                height: dp(40)
                pos_hint: {'center_y': 0.5}
                background_color: 1, 1, 1, 1
                padding: [dp(10), dp(10)]

            Button:
                text: '->'
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': 0.5}
                on_release: root.send_message()

<FinalScreen>:
    name: 'final'
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(16), dp(12), dp(16), dp(16)]
        spacing: dp(0)

        ScrollView:
            id: final_scroll
            size_hint_y: 1
            bar_width: 0
            do_scroll_x: False
            GridLayout:
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)
                padding: [0, dp(12), 0, dp(120)]

                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    padding: [0, 0, 0, 0]
                    IconButton:
                        size_hint: None, None
                        size: dp(36), dp(36)
                        pos_hint: {'center_y': 0.5}
                        default_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                        pressed_source: 'assets/icons/free-icon-font-arrow-small-left-3916837(1).png'
                        on_release: app.exit_to_main()
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 0.9
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(22)]
                    Widget:

                Widget:
                    size_hint_y: None
                    height: dp(8)

                Label:
                    text: 'Результат'
                    color: 0.15, 0.55, 0.9, 1
                    font_size: '32sp'
                    bold: True
                    size_hint_y: None
                    height: dp(56)

                Label:
                    id: score_label
                    text: root.score_text
                    color: 0.2, 0.2, 0.2, 1
                    font_size: '24sp'
                    halign: 'center'
                    valign: 'top'
                    size_hint_y: None
                    height: self.texture_size[1] + dp(20)
                    text_size: self.width, None

                Widget:
                    size_hint_y: None
                    height: dp(8)

                Label:
                    id: note_label
                    text: root.note_text
                    color: 0.35, 0.35, 0.35, 1
                    font_size: '14sp'
                    halign: 'left'
                    valign: 'top'
                    size_hint_y: None
                    height: self.texture_size[1] + dp(16)
                    text_size: self.width, None

                Widget:
                    size_hint_y: None
                    height: dp(16)

                Label:
                    text: 'Работа над ошибками'
                    color: 0.3, 0.3, 0.3, 1
                    font_size: '18sp'
                    bold: True
                    halign: 'left'
                    size_hint_y: None
                    height: dp(32)
                    text_size: self.width, None

                GridLayout:
                    id: error_explanations_box
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(10)
                    padding: [0, 0]

                Widget:
                    size_hint_y: None
                    height: dp(16)

                Label:
                    text: 'Темы для углубления'
                    color: 0.3, 0.3, 0.3, 1
                    font_size: '18sp'
                    bold: True
                    halign: 'left'
                    size_hint_y: None
                    height: dp(32)
                    text_size: self.width, None

                GridLayout:
                    id: followup_topics_box
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)
                    padding: [0, 0]

        BoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: [dp(12), dp(8), dp(12), dp(8)]
            spacing: dp(32)
            canvas.before:
                Color:
                    rgba: 0, 0, 0, 0
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 0.92, 0.92, 0.92, 1
                Line:
                    points: [self.x, self.y + self.height, self.x + self.width, self.y + self.height]
                    width: 1

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    size: dp(34), dp(34)
                    icon_source: 'assets/icons/free-icon-font-home-3917033.png'
                    target_screen: 'saved'
                    group: 'final_nav'
                    on_release: app.exit_to_main()

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    size: dp(34), dp(34)
                    icon_source: 'assets/icons/free-icon-font-search-3917132.png'
                    target_screen: 'search'
                    group: 'final_nav'
                    on_release: app.goto_search_tab()

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    size: dp(34), dp(34)
                    icon_source: 'assets/icons/free-icon-font-settings-sliders-3917103.png'
                    target_screen: 'settings'
                    group: 'final_nav'
                    on_release: app.return_to_theory()
"""


# ============================================================================
# ПОЛЬЗОВАТЕЛЬСКИЕ ВИДЖЕТЫ - ПЕРЕИСПОЛЬЗУЕМЫЕ UI КОМПОНЕНТЫ
# ============================================================================

class CourseCard(ButtonBehavior, BoxLayout):
    """
    Карточка курса для отображения в списке сохранённых курсов.
    
    Показывает название темы, уровень сложности и кнопку удаления.
    Кликабельная - при нажатии открывает курс для прохождения.
    
    Атрибуты:
        topic: Название темы курса
        difficulty: Уровень сложности ('легкий', 'средний', 'эксперт')
        bg_color: Цвет фона карточки
    """
    bg_color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, topic, difficulty, **kwargs):
        super().__init__(**kwargs)
        self.topic = topic
        self.difficulty = difficulty
        self.orientation = 'vertical'
        self.padding = [dp(16), dp(12)]
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(110)
        
        with self.canvas.before:
            self._rect_color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        top_row = BoxLayout(size_hint_y=None, height=dp(32))
        topic_label = Label(
            text=topic,
            color=(0.2, 0.2, 0.2, 1),
            font_size='18sp',
            bold=True,
            halign='left',
            valign='middle',
            text_size=(self.width, None),
        )
        topic_label.bind(size=lambda inst, size: setattr(inst, 'text_size', (size[0], None)))
        topic_label.size_hint_x = 0.85
        top_row.add_widget(topic_label)
        delete_btn = IconButton(
            size_hint=(None, None),
            size=(dp(26), dp(26)),
            default_source='assets/icons/free-icon-font-trash-3917242(1).png',
            pressed_source='assets/icons/free-icon-font-trash-3917242(1).png'
        )
        delete_btn.bind(on_release=lambda inst, t=topic, d=difficulty: App.get_running_app().delete_saved_course(t, d))
        top_row.add_widget(delete_btn)
        self.add_widget(top_row)
        
        diff_color = (0.3, 0.7, 0.3, 1) if 'легкий' in difficulty.lower() else \
                     (0.9, 0.6, 0.2, 1) if 'средний' in difficulty.lower() else \
                     (0.9, 0.3, 0.3, 1)
                     
        self.add_widget(Label(
            text=difficulty,
            color=diff_color,
            font_size='14sp',
            halign='left',
            valign='middle',
            text_size=(self.width, None),
            size_hint_y=None,
            height=dp(20)
        ))

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        for child in self.children:
            child.text_size = (self.width - dp(32), None)


class RoundedButton(Button):
    """
    Кнопка со скруглёнными углами и настраиваемым цветом фона.
    
    Используется для основных действий в приложении.
    Поддерживает динамическое изменение цвета через bg_color.
    
    Атрибуты:
        bg_color: Цвет фона кнопки в формате [R, G, B, A]
    """
    bg_color = ListProperty([0.15, 0.55, 0.9, 1])

    def __init__(self, **kwargs):
        """Инициализация кнопки с прозрачным стандартным фоном"""
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)  # Прозрачный - рисуем свой фон
        self.halign = 'center'
        self.valign = 'middle'
        with self.canvas.before:
            self._rect_color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(bg_color=self._update_color)

    def _update_rect(self, *args):
        """Обновляет позицию и размер фона при изменении кнопки"""
        self._rect.pos = self.pos
        self._rect.size = self.size
        self.text_size = (self.width, None)

    def _update_color(self, *args):
        """Обновляет цвет фона при изменении bg_color"""
        self._rect_color.rgba = self.bg_color


class GradientButton(Button):
    """
    Современная кнопка с градиентным эффектом и тенью.
    
    ПРИМЕЧАНИЕ: В текущей версии не используется, оставлена для будущих обновлений.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.halign = 'center'
        self.valign = 'middle'
        
        with self.canvas.before:
            # Тень под кнопкой
            self._shadow_color = Color(rgba=(0.1, 0.3, 0.6, 0.25))
            self._shadow = RoundedRectangle(pos=(self.x, self.y - dp(4)), size=self.size, radius=[dp(20)])
            # Градиент (симуляция двумя прямоугольниками)
            self._grad1_color = Color(rgba=(0.1, 0.4, 0.9, 1))
            self._grad1 = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)])
            self._grad2_color = Color(rgba=(0.15, 0.5, 0.95, 0.8))
            self._grad2 = RoundedRectangle(pos=(self.x, self.y + self.height * 0.5), 
                                          size=(self.width, self.height * 0.5), 
                                          radius=[0, 0, dp(20), dp(20)])
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        self.bind(state=self._on_state)
    
    def _update_graphics(self, *args):
        """Обновляет графические элементы при изменении размера/позиции"""
        self._shadow.pos = (self.x, self.y - dp(4))
        self._shadow.size = self.size
        self._grad1.pos = self.pos
        self._grad1.size = self.size
        self._grad2.pos = (self.x, self.y + self.height * 0.5)
        self._grad2.size = (self.width, self.height * 0.5)
        self.text_size = (self.width, None)
    
    def _on_state(self, instance, state):
        """Анимация нажатия - поднимает/опускает тень"""
        if state == 'down':
            self._shadow.pos = (self.x, self.y - dp(1))
            self._grad1_color.rgba = (0.08, 0.35, 0.8, 1)
        else:
            self._shadow.pos = (self.x, self.y - dp(4))
            self._grad1_color.rgba = (0.1, 0.4, 0.9, 1)


class IconButton(ButtonBehavior, Image):
    """
    Кнопка-иконка с поддержкой смены изображения при нажатии.
    
    Используется для небольших действий типа удаления, закрытия и т.д.
    
    Атрибуты:
        default_source: Путь к изображению в нормальном состоянии
        pressed_source: Путь к изображению при нажатии
    """
    default_source = StringProperty('')
    pressed_source = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True
        self.size_hint = (None, None)
        self.bind(state=self._update_source)
        self._update_source(self, getattr(self, 'state', 'normal'))

    def on_default_source(self, instance, value):
        """Устанавливает изображение по умолчанию"""
        if self.state != 'down' and value:
            self.source = value

    def _update_source(self, instance, state):
        """Меняет изображение в зависимости от состояния кнопки"""
        if state == 'down' and self.pressed_source:
            self.source = self.pressed_source
        elif self.default_source:
            self.source = self.default_source


class IconToggleButton(ToggleButtonBehavior, Image):
    """
    Кнопка-иконка с поддержкой переключения (toggle).
    
    Используется в нижней навигации для переключения между табами.
    Меняет цвет при активации.
    
    Атрибуты:
        icon_source: Путь к файлу иконки
        target_screen: Имя целевого экрана для переключения
        active_color: Цвет иконки в активном состоянии (синий)
        inactive_color: Цвет иконки в неактивном состоянии (серый)
    """
    icon_source = StringProperty('')
    target_screen = StringProperty('')
    active_color = ListProperty([0.15, 0.55, 0.9, 1])
    inactive_color = ListProperty([0.5, 0.5, 0.5, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True
        self.size_hint = (None, None)
        self.bind(state=self._update_style)
        self._update_style(self, getattr(self, 'state', 'normal'))
        if self.icon_source:
            self.source = self.icon_source

    def on_icon_source(self, instance, value):
        """Устанавливает иконку"""
        if value:
            self.source = value

    def _update_style(self, instance, state):
        """Меняет цвет иконки в зависимости от состояния"""
        if state == 'down':
            self.color = self.active_color  # Синий когда активна
        else:
            self.color = self.inactive_color  # Серый когда неактивна

    def on_release(self):
        """Переключает экран при нажатии"""
        super().on_release()
        if self.target_screen:
            app = App.get_running_app()
            if app and getattr(app.root, 'get_screen', None):
                try:
                    main_screen = app.root.get_screen('main')
                    main_screen.ids.tab_manager.current = self.target_screen
                except Exception:
                    pass


class SectionDivider(Widget):
    """
    Визуальный разделитель между секциями на финальном экране.
    
    Рисует толстую синюю горизонтальную линию для разделения
    MC теста и развёрнутых ответов в финальном отчёте.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._line_color = Color(rgba=(0.15, 0.55, 0.9, 1))  # Основной синий цвет
            # Линия толщиной 3dp для хорошей видимости
            self._line = Rectangle(pos=(self.x + dp(8), self.y + self.height / 2 - dp(1)), size=(self.width - dp(16), dp(3)))
        self.bind(pos=self._update_line, size=self._update_line)

    def _update_line(self, *args):
        """Обновляет позицию и размер линии при изменении виджета"""
        self._line.pos = (self.x + dp(8), self.y + self.height / 2 - dp(1))
        self._line.size = (self.width - dp(16), dp(3))


class DifficultyButton(ToggleButton):
    bg_color = ListProperty([0.9, 0.9, 0.9, 1])
    selected_color = ListProperty([0.15, 0.55, 0.9, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (0.2, 0.2, 0.2, 1)
        self.group = 'difficulty'
        with self.canvas.before:
            self._rect_color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(state=self._update_state)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _update_state(self, *args):
        if self.state == 'down':
            self._rect_color.rgba = self.selected_color
            self.color = (1, 1, 1, 1)
        else:
            self._rect_color.rgba = self.bg_color
            self.color = (0.2, 0.2, 0.2, 1)


class OptionButton(Button):
    default_color = (0.85, 0.85, 0.85, 1)
    selected_color = (0.3, 0.8, 0.4, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1)  # default text color black
        self.halign = 'center'
        self.valign = 'middle'
        with self.canvas.before:
            self._bg_color = Color(*self.default_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(texture_size=self._update_height)

    def _update_rect(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self.text_size = (self.width - dp(20), None)

    def _update_height(self, *args):
        self.height = max(dp(60), self.texture_size[1] + dp(30))

    def set_selected(self, selected: bool):
        """Устанавливает выбранное состояние кнопки"""
        self._bg_color.rgba = self.selected_color if selected else self.default_color
        self.color = (1, 1, 1, 1) if selected else (0, 0, 0, 1)


# ============================================================================
# КЛАССЫ ЭКРАНОВ - ОСНОВНЫЕ СТРАНИЦЫ ПРИЛОЖЕНИЯ
# ============================================================================

class MainScreen(Screen):
    """
    Главный экран приложения с тремя табами.
    
    Содержит:
    - SavedScreen: Список сохранённых курсов
    - SearchScreen: Поиск и создание новых курсов
    - SettingsScreen: Настройки приложения
    
    Функции:
    - Проверка подключения к сети каждые 30 секунд
    - Синхронизация состояния навигации с текущим табом
    """
    
    def on_enter(self):
        """Запускается при входе на экран"""
        self.check_network()
        # Повторяем проверку каждые 30 секунд
        self._network_check = Clock.schedule_interval(lambda dt: self.check_network(), 30)
    
    def on_leave(self):
        """Останавливаем проверку при уходе с экрана"""
        if hasattr(self, '_network_check'):
            self._network_check.cancel()
    
    def check_network(self):
        """
        Быстрая проверка подключения к интернету.
        
        Проверяет доступность DNS Google (8.8.8.8:53) с таймаутом 2 секунды.
        Обновляет иконку статуса в UI.
        """
        def _check():
            try:
                import socket
                # Проверяем доступность DNS Google (быстро и надёжно)
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                Clock.schedule_once(lambda dt: self._update_network_status(True))
            except:
                Clock.schedule_once(lambda dt: self._update_network_status(False))
        
        import threading
        threading.Thread(target=_check, daemon=True).start()
    
    def _update_network_status(self, is_online):
        """Обновляет иконку статуса сети в UI"""
        if is_online:
            self.ids.network_status.text = '🌐'  # Онлайн
            self.ids.network_status.color = (0.3, 0.7, 0.3, 1)  # Зелёный
        else:
            self.ids.network_status.text = '📵'  # Оффлайн
            self.ids.network_status.color = (0.9, 0.3, 0.3, 1)  # Красный

    def on_kv_post(self, base_widget):
        """Инициализация после создания UI из KV"""
        super().on_kv_post(base_widget)
        try:
            # Собираем кнопки навигации для синхронизации
            self._nav_buttons = [
                self.ids.nav_saved,
                self.ids.nav_search,
                self.ids.nav_settings
            ]
            tab_manager = self.ids.tab_manager
            # Синхронизируем состояние кнопок при переключении табов
            tab_manager.bind(current=self._sync_nav_icons)
            self._sync_nav_icons(tab_manager, tab_manager.current)
        except Exception:
            self._nav_buttons = []

    def _sync_nav_icons(self, tab_manager, current):
        """Синхронизирует состояние кнопок навигации с текущим табом"""
        for btn in getattr(self, '_nav_buttons', []):
            btn.state = 'down' if getattr(btn, 'target_screen', None) == current else 'normal'


class SavedScreen(Screen):
    """Экран со списком сохранённых курсов"""
    pass


class SearchScreen(Screen):
    """Экран поиска и создания новых курсов"""
    pass


class SettingsScreen(Screen):
    """Экран настроек приложения"""
    pass


class LoadingScreen(Screen):
    """
    Экран загрузки с анимацией и интересными фактами.
    
    Показывается во время генерации курсов, тестов и оценки ответов.
    Меняет интересный факт каждые 7 секунд.
    """
    
    def start_fact_cycle(self):
        """Запускает цикл смены интересных фактов"""
        self.update_fact()
        self._fact_event = Clock.schedule_interval(self.update_fact, 7)

    def stop_fact_cycle(self):
        """Останавливает цикл смены фактов"""
        if hasattr(self, '_fact_event'):
            self._fact_event.cancel()

    def update_fact(self, dt=None):
        """Обновляет текст интересного факта"""
        fact = random.choice(INTERESTING_FACTS)
        self.ids.fact_label.text = f"Интересный факт:\n{fact}"


class TheoryScreen(Screen):
    """
    Экран отображения теоретического материала.
    
    Показывает сгенерированную теорию перед началом теста.
    Пользователь может изучить материал перед тестированием.
    
    Атрибуты:
        theory_content: Текст теории (HTML разметка поддерживается)
        meta_title: Название темы
        meta_sub: Уровень сложности
    """
    theory_content = StringProperty('')
    meta_title = StringProperty('')
    meta_sub = StringProperty('')


class DotSpinner(BoxLayout):
    """
    Анимированный индикатор загрузки из трёх точек.
    
    Точки последовательно подсвечиваются синим цветом,
    создавая эффект пульсации.
    """
    
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(8), size_hint=(None, None), **kwargs)
        self.size = (dp(120), dp(40))
        self.dots = [Label(text='•', font_size='28sp', color=(0.6,0.6,0.6,1)) for _ in range(3)]
        for d in self.dots:
            self.add_widget(d)
        self._idx = 0
        self._event = Clock.schedule_interval(self._pulse, 0.4)

    def _pulse(self, dt):
        """Анимация пульсации - подсвечивает текущую точку"""
        for i, d in enumerate(self.dots):
            if i == self._idx:
                d.color = (0.15, 0.55, 0.9, 1)  # Синий - активная точка
            else:
                d.color = (0.6,0.6,0.6,1)  # Серый - неактивные
        self._idx = (self._idx + 1) % len(self.dots)

    def on_parent(self, widget, parent):
        """Останавливает анимацию при удалении виджета"""
        if parent is None and getattr(self, '_event', None):
            self._event.cancel()


class QuizScreen(Screen):
    """
    Экран множественного выбора (MC тест).
    
    Показывает вопросы с 4 вариантами ответов.
    Сохраняет историю ошибок для финального отчёта.
    Запускает предзагрузку открытых вопросов в фоне.
    
    Атрибуты:
        question_index: Индекс текущего вопроса
        score: Количество правильных ответов
        result_text: Текст результата после ответа
        current_question_text: Текст текущего вопроса
        wrong_explanations: Список ошибок для финального экрана
    """
    question_index = NumericProperty(0)
    score = NumericProperty(0)
    result_text = StringProperty('')
    current_question_text = StringProperty('')
    wrong_explanations = []

    questions = [
        {"question": "Какого цвета небо?",
         "options": ["Зелёный", "Синий", "Красный", "Жёлтый"],
         "answer": 1},
        {"question": "Сколько будет 2 + 2?",
         "options": ["3", "4", "5", "22"],
         "answer": 1},
        {"question": "Какая планета ближе всего к Солнцу?",
         "options": ["Венера", "Марс", "Меркурий", "Земля"],
         "answer": 2},
    ]

    def on_pre_enter(self, *args):
        self.load_question()
        # Запускаем генерацию открытых вопросов заранее для ускорения
        app = App.get_running_app()
        if not getattr(app, 'open_questions_preloading', False):
            app.open_questions_preloading = True
            threading.Thread(target=app.preload_open_questions).start()

    def load_question(self):
        if not self.questions or self.question_index >= len(self.questions):
            return

        try:
            q = self.questions[self.question_index]
            self.current_question_text = q.get('question', 'Ошибка загрузки вопроса')
            box = self.ids.options_box
            box.clear_widgets()
            options = q.get('options', [])
            for idx, opt in enumerate(options):
                btn = OptionButton(text=str(opt), size_hint_y=None)
                btn.background_normal = ''
                btn.background_down = ''
                btn.option_index = idx
                btn.bind(on_release=self.select_option)
                box.add_widget(btn)
            self.selected = None
            self.result_text = ''
            self.answered = False
            self.highlighted_button = None
        except Exception as e:
            print(f"Error loading question: {e}")
            self.current_question_text = "Ошибка отображения вопроса"

    def select_option(self, widget):
        if getattr(self, 'answered', False):
            return
        self.selected = widget.option_index
        if self.highlighted_button and self.highlighted_button is not widget:
            self.highlighted_button.set_selected(False)
        widget.set_selected(True)
        self.highlighted_button = widget
        self.evaluate_selection()

    def evaluate_selection(self):
        if self.selected is None:
            return
        q = self.questions[self.question_index]
        self.answered = True
        if self.selected == q['answer']:
            self.result_text = 'Правильно! ✓'
            self.score += 1
        else:
            self.result_text = f"Неправильно. Верно: {q['options'][q['answer']]}"
            options = q.get('options', [])
            selected_text = options[self.selected] if 0 <= self.selected < len(options) else ''
            correct_text = options[q['answer']] if 0 <= q['answer'] < len(options) else ''
            explanation = {
                'question': q.get('question', 'Вопрос'),
                'selected': selected_text,
                'correct': correct_text
            }
            if not hasattr(self, 'wrong_explanations'):
                self.wrong_explanations = []
            self.wrong_explanations.append(explanation)
        # автоматический переход без задержки
        self.auto_next_question()

    def next_question(self):
        if not getattr(self, 'answered', False):
            self.result_text = 'Сначала выберите вариант.'
            return
        if self.question_index + 1 < len(self.questions):
            self.question_index += 1
            self.load_question()
        else:
            self.finish_test()

    def auto_next_question(self):
        """Автоматический переход к следующему вопросу"""
        if self.question_index + 1 < len(self.questions):
            self.question_index += 1
            self.load_question()
        else:
            self.finish_test()

    def finish_test(self):
        percent = 0
        if self.questions:
            percent = int(round(100 * self.score / len(self.questions)))
        # Сохраняем результаты MC теста для финального отчёта
        app = App.get_running_app()
        app.mc_test_score = self.score
        app.mc_test_total = len(self.questions)
        app.mc_test_percent = percent
        app.mc_test_errors = self.get_error_explanations()
        # Переходим к открытым вопросам (они уже генерируются)
        app.transition_to_open_questions()

    def reset_quiz(self):
        """
        Сбрасывает состояние теста для перезапуска.
        
        Обнуляет счётчик вопросов, очки, выбор и список ошибок.
        """
        self.question_index = 0
        self.score = 0
        self.selected = None
        self.highlighted_button = None
        self.answered = False
        self.wrong_explanations = []
        self.load_question()

    def get_error_explanations(self):
        """Возвращает список ошибок для финального отчёта"""
        return getattr(self, 'wrong_explanations', [])


class OpenAnswerScreen(Screen):
    """
    Экран для развёрнутых ответов (open-ended questions).
    
    Пользователь вводит развёрнутый текстовый ответ,
    который оценивается LLM по шкале 0-10.
    Полная оценка и рекомендации показываются на финальном экране.
    """
    pass


class FinalScreen(Screen):
    """
    Финальный экран с результатами обеих частей теста.
    
    Отображает:
    - Общий процент и счёт
    - Работу над ошибками для MC теста
    - Работу над ошибками для развёрнутых ответов
    - Быструю шпаргалку по теме
    - Рекомендации для дальнейшего изучения
    - Нижнюю навигацию (домой, поиск, настройки)
    
    Атрибуты:
        score_text: Форматированная строка с результатами
        note_text: Краткая шпаргалка
        nav_visible: Видимость навигации (всегда True)
    """
    score_text = StringProperty('')
    note_text = StringProperty('')
    nav_visible = BooleanProperty(False)

    def set_score(self, score, total, percent):
        """Устанавливает текст с общим результатом"""
        self.score_text = f'{percent}% ({score}/{total} правильных ответов)'

    def set_quick_note(self, text):
        """Устанавливает краткую шпаргалку"""
        self.note_text = text or 'Быстрая шпаргалка пока отсутствует.'

    def set_followup_topics(self, topics, loading=False):
        """
        Отображает список рекомендованных тем для дальнейшего изучения.
        
        Args:
            topics: Список названий тем
            loading: Флаг загрузки (показывает "подготавливаются...")
        """
        layout = self.ids.followup_topics_box
        layout.clear_widgets()
        if not topics:
            message = 'Темы подготавливаются...' if loading else 'Темы пока отсутствуют.'
            layout.add_widget(Label(
                text=message,
                halign='center',
                valign='middle',
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=dp(30)
            ))
            return
        # Создаём кнопки для каждой рекомендованной темы
        for topic in topics:
            btn = RoundedButton(
                text=topic,
                size_hint_y=None,
                height=dp(48),
                bg_color=(0.2, 0.55, 0.35, 1),  # Зелёный оттенок
                font_size='16sp'
            )
            btn.bind(on_release=lambda inst, t=topic: App.get_running_app().start_followup_topic(t))
            layout.add_widget(btn)

    def set_error_explanations(self, errors):
        """
        Отображает список ошибок из обеих частей теста.
        
        Args:
            errors: Список словарей с ошибками
                   Может содержать {'divider': True} для визуального разделения секций
        """
        layout = self.ids.error_explanations_box
        layout.clear_widgets()
        if not errors:
            layout.add_widget(Label(
                text='Ошибок нет. Отличная работа! 🎉',
                halign='left',
                valign='middle',
                color=(0.15, 0.55, 0.9, 1),
                size_hint_y=None,
                height=dp(30)
            ))
            return
        for item in errors:
            if item.get('divider'):
                layout.add_widget(SectionDivider(size_hint_y=None, height=dp(22)))
                continue
            question = item.get('question', 'Вопрос')
            correct = item.get('correct', '')
            selected = item.get('selected', '')
            
            # Пропускаем пустые разделители
            if not question and not correct and not selected:
                spacer = Widget(size_hint_y=None, height=dp(8))
                layout.add_widget(spacer)
                continue
            
            correct_answer = correct or 'не указан'
            label = Label(
                text=f"[b]{question}[/b]\nПравильный ответ: {correct_answer}",
                markup=True,
                halign='left',
                valign='top',
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(80)
            )
            label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - dp(24), None)))
            label.bind(texture_size=lambda inst, size: setattr(inst, 'height', max(dp(80), size[1] + dp(24))))
            layout.add_widget(label)

    def on_scroll_y(self, scroll_y):
        # show navigation when scrolled to bottom (scroll_y near 0)
        threshold = 0.05
        nav_should_show = scroll_y <= threshold
        if self.nav_visible != nav_should_show:
            self.nav_visible = nav_should_show


class ChatScreen(Screen):
    chat_history = ListProperty([])
    selected_image = StringProperty(None, allownone=True)

    def send_message(self):
        text_input = self.ids.message_input
        message = text_input.text.strip()
        
        if not message and not self.selected_image:
            return

        self.add_message(message, "user", self.selected_image)
        
        text_input.text = ""
        image_path = self.selected_image
        self.selected_image = None
        self.ids.attach_btn.text = "📎"  # Сбрасываем иконку
        
        threading.Thread(target=self._send_request_thread, args=(message, image_path)).start()

    def _send_request_thread(self, message, image_path):
        app = App.get_running_app()
        api_key = None
        
        # Получаем API ключ из настроек (правильный путь к хранилищу)
        if hasattr(app, 'settings_store') and app.settings_store.exists('api'):
            data = app.settings_store.get('api')
            api_key = data.get('api_key', data.get('key'))
        
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")

        # Fallback/Cleanup
        if api_key:
            api_key = api_key.strip()
        
        # Проверяем корректность ключа
        if not api_key or not api_key.startswith("sk-or-"):
             print("[Chat] WARNING: No valid API key found!")
             Clock.schedule_once(lambda dt: self.on_response({"error": "API ключ не настроен. Перейдите в Настройки и сохраните ключ OpenRouter."}))
             return

        history = []
        for msg in self.chat_history[-10:]:
             history.append({'role': msg['role'], 'content': msg['text']})

        print(f"[Chat] Sending request with key: {api_key[:10]}...")
        response = chat_with_image(message, image_path, history=history, api_key=api_key)
        
        Clock.schedule_once(lambda dt: self.on_response(response))

    def on_response(self, response):
        if 'error' in response:
            self.add_message(f"Ошибка: {response['error']}", "system")
        else:
            self.add_message(response['content'], "assistant")

    def add_message(self, text, role, image=None):
        self.chat_history.append({'role': role, 'text': text, 'image': image})
        
        # Контейнер для сообщения
        msg_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=[10, 10], spacing=5)
        
        # Фон сообщения (визуальное выделение)
        with msg_box.canvas.before:
            Color(*((0.8, 0.9, 1, 1) if role == 'user' else (1, 1, 1, 1)))
            RoundedRectangle(pos=msg_box.pos, size=msg_box.size, radius=[10])
            
        # Обновление фона при изменении размера/позиции
        def update_rect(instance, value):
            instance.canvas.before.children[2].pos = instance.pos
            instance.canvas.before.children[2].size = instance.size
        msg_box.bind(pos=update_rect, size=update_rect)

        total_height = dp(20) # Padding

        if image:
            try:
                img = Image(source=image, size_hint_y=None, height=dp(200), allow_stretch=True, keep_ratio=True)
                msg_box.add_widget(img)
                total_height += dp(200) + dp(5)
            except Exception as e:
                print(f"Error loading image: {e}")

        if text:
            lbl = Label(text=text, size_hint_y=None, color=(0,0,0,1), markup=True)
            lbl.bind(width=lambda *x: setattr(lbl, 'text_size', (lbl.width, None)))
            lbl.bind(texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1]))
            msg_box.add_widget(lbl)
            # Мы не знаем высоту сразу, поэтому используем bind
            def update_height(instance, value):
                # Пересчитываем высоту контейнера
                h = dp(20)
                for child in msg_box.children:
                    h += child.height + msg_box.spacing
                msg_box.height = h
            lbl.bind(texture_size=update_height)
            total_height += dp(40) # Начальная оценка

        msg_box.height = total_height

        # Обертка для выравнивания
        wrapper = AnchorLayout(anchor_x='right' if role == 'user' else 'left', size_hint_y=None)
        wrapper.add_widget(msg_box)
        
        # Связываем высоту обертки с высотой сообщения
        msg_box.bind(height=lambda *x: setattr(wrapper, 'height', msg_box.height))
        
        self.ids.chat_list.add_widget(wrapper)

    def show_image_chooser(self):
        """Показывает выбор изображения: галерея на Android, диалог на Desktop"""
        if IS_ANDROID:
            # На Android используем нативный file picker
            try:
                from plyer import filechooser
                
                def on_file_selected(selection):
                    """Callback когда пользователь выбрал файл"""
                    if selection and len(selection) > 0:
                        path = selection[0]
                        print(f"[Chat] Selected image: {path}")
                        self.selected_image = path
                        self.ids.attach_btn.text = "📷"
                
                # Запрашиваем разрешения на чтение файлов (Android 6+)
                try:
                    from android.permissions import request_permissions, Permission
                    request_permissions([
                        Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE
                    ])
                except Exception as e:
                    print(f"[Chat] Permissions error: {e}")
                
                # Открываем file picker с фильтром по изображениям
                filechooser.open_file(
                    on_selection=on_file_selected,
                    filters=["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp", "*.bmp"],
                    mime_type="image/*"
                )
            except Exception as e:
                print(f"[Chat] Error opening file chooser: {e}")
                # Fallback на текстовый ввод
                self._show_text_input_chooser()
        else:
            # На Desktop показываем диалог с вводом пути или используем plyer
            try:
                from plyer import filechooser
                
                def on_file_selected(selection):
                    if selection and len(selection) > 0:
                        path = selection[0]
                        print(f"[Chat] Selected image: {path}")
                        self.selected_image = path
                        self.ids.attach_btn.text = "📷"
                
                filechooser.open_file(
                    on_selection=on_file_selected,
                    filters=[
                        ("Images", "*.jpg;*.jpeg;*.png;*.gif;*.webp;*.bmp"),
                        ("All files", "*.*")
                    ]
                )
            except Exception as e:
                print(f"[Chat] Plyer not available, using text input: {e}")
                self._show_text_input_chooser()
    
    def _show_text_input_chooser(self):
        """Fallback метод: текстовый ввод URL или пути"""
        from kivy.uix.popup import Popup
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Подсказка с примерами
        hint_label = Label(
            text='Введите URL или локальный путь к изображению',
            size_hint_y=None,
            height=dp(30),
            color=(0.5, 0.5, 0.5, 1),
            font_size='12sp'
        )
        text_input = TextInput(
            hint_text='https://example.com/image.jpg или /sdcard/image.jpg',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
        cancel_btn = Button(text='Отмена')
        ok_btn = Button(text='OK')
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(ok_btn)
        
        content.add_widget(hint_label)
        content.add_widget(text_input)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='Добавить изображение',
            content=content,
            size_hint=(0.9, None),
            height=dp(200)
        )
        
        def on_select(instance):
            path = text_input.text.strip()
            if path:
                self.selected_image = path
                self.ids.attach_btn.text = "📷"
            popup.dismiss()
        
        def on_cancel(instance):
            popup.dismiss()
            
        ok_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=on_cancel)
        popup.open()

class MyApp(App):
    """
    Главный класс приложения SmartTest.
    
    Управляет всей логикой приложения:
    - Инициализация хранилищ данных (курсы, настройки, кеш)
    - Генерация тестов и теории через LLM
    - Переходы между экранами
    - Кеширование часто используемых данных
    - Предзагрузка открытых вопросов во время MC теста
    
    Атрибуты:
        difficulty: Текущая сложность ('легкий', 'средний', 'сложный')
        storage: CourseStorage для сохранения курсов
        settings_store: JsonStore для настроек пользователя
        open_questions_cache: Кеш открытых вопросов для быстрого доступа
        mc_test_score/mc_test_total: Результаты MC теста для финального отчёта
        preloaded_open_questions: Предзагруженные открытые вопросы
    """
    difficulty = StringProperty('легкий')

    def build(self):
        """
        Инициализация приложения.
        
        Создаёт необходимые директории, инициализирует хранилища,
        загружает кеш и строит UI из KV разметки.
        
        Returns:
            Widget: Корневой виджет приложения (ScreenManager)
        """
        print("[MAIN] MyApp.build() starting...")
        try:
            # Используем директорию данных приложения (безопасное место для файлов)
            data_dir = self.user_data_dir
            print(f"[MAIN] user_data_dir: {data_dir}")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"[MAIN] Created data_dir")

            # Определяем пути к файлам хранения
            courses_path = os.path.join(data_dir, 'courses.json')  # Все курсы и тесты
            settings_path = os.path.join(data_dir, 'settings.json')  # Настройки пользователя
            self.topic_memory_file = os.path.join(data_dir, 'course_topics.json')  # История тем
            self._last_api_key = None
            self.last_material = ''  # Последний загруженный материал
            
            # Путь к кешу открытых вопросов для ускорения генерации
            self.open_questions_cache_path = os.path.join(data_dir, 'open_questions_cache.json')
            self.open_questions_cache = self._load_open_questions_cache()
            
            print(f"[MAIN] courses_path: {courses_path}")
            print(f"[MAIN] settings_path: {settings_path}")
            
            # Создаём хранилище курсов
            print("[MAIN] Creating CourseStorage...")
            self.storage = CourseStorage(filename=courses_path)
            self._last_saved_meta = None
            print("[MAIN] CourseStorage created")
            
            # Создаём хранилище настроек
            print("[MAIN] Creating JsonStore...")
            self.settings_store = JsonStore(settings_path)
            print("[MAIN] JsonStore created")
            
            # Загружаем и строим UI из KV разметки
            print("[MAIN] Loading KV string...")
            root = Builder.load_string(KV)
            print("[MAIN] KV loaded successfully")
            
            self.log("App started. Storage initialized.")
            print("[MAIN] build() complete!")
            return root
        except Exception as e:
            print(f"[MAIN] ERROR in build(): {e}")
            print(f"[MAIN] Traceback: {tb_module.format_exc()}")
            raise

    def _load_open_questions_cache(self):
        """
        Загружает кеш открытых вопросов из файла.
        
        Кеш позволяет избежать повторной генерации одинаковых вопросов
        для одной и той же темы и сложности.
        
        Returns:
            dict: Словарь с кешированными вопросами {ключ: вопросы}
                  Ключ имеет формат "{topic}|{difficulty}"
        """
        if not getattr(self, 'open_questions_cache_path', None):
            return {}
        try:
            if os.path.exists(self.open_questions_cache_path):
                with open(self.open_questions_cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            self.log(f"Ошибка загрузки кеша открытых вопросов: {e}")
        return {}

    def _save_open_questions_cache(self):
        """
        Сохраняет кеш открытых вопросов в файл.
        
        Вызывается автоматически после добавления новых вопросов в кеш.
        """
        if not getattr(self, 'open_questions_cache_path', None):
            return
        try:
            with open(self.open_questions_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.open_questions_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"Ошибка сохранения кеша открытых вопросов: {e}")

    def _get_open_questions_cache_key(self, topic):
        """
        Генерирует ключ кеша для открытых вопросов.
        
        Ключ формируется из темы и сложности для уникальной идентификации.
        
        Args:
            topic: Тема курса
            
        Returns:
            str: Ключ в формате "{topic_lowercase}|{difficulty}"
        """
        normalized_topic = (topic or '').strip().lower()
        difficulty = getattr(self, 'difficulty', 'легкий') or 'легкий'
        return f"{normalized_topic}|{difficulty}"

    def get_cached_open_questions(self, topic):
        """
        Получает кешированные открытые вопросы для темы.
        
        Args:
            topic: Тема курса
            
        Returns:
            list|None: Список вопросов если найдены в кеше, иначе None
        """
        key = self._get_open_questions_cache_key(topic)
        return self.open_questions_cache.get(key)

    def cache_open_questions(self, topic, questions):
        """
        Сохраняет открытые вопросы в кеш.
        
        Args:
            topic: Тема курса
            questions: Список сгенерированных вопросов для кеширования
        """
        if not questions:
            return
        key = self._get_open_questions_cache_key(topic)
        self.open_questions_cache[key] = questions
        self._save_open_questions_cache()

    def log(self, message):
        """
        Логирует сообщение в консоль и UI.
        
        Args:
            message: Текст сообщения для логирования
        """
        print(message)
        try:
            main_screen = self.root.get_screen('main')
            settings_screen = main_screen.ids.tab_manager.get_screen('settings')
            log_label = settings_screen.ids.debug_log
            # Сохраняем последние 2000 символов логов
            log_label.text = f"{message}\n{log_label.text}"[:2000]
        except Exception:
            pass

    def load_settings_ui(self):
        """
        Загружает сохраненные настройки в UI.
        
        Заполняет поля ввода на экране настроек сохраненными значениями.
        """
        main_screen = self.root.get_screen('main')
        settings_screen = main_screen.ids.tab_manager.get_screen('settings')
        
        if self.settings_store.exists('api'):
            # Загружаем API ключ из настроек
            data = self.settings_store.get('api')
            key = data.get('api_key', data.get('key', ''))
            settings_screen.ids.api_key_input.text = key
    
    def save_settings(self):
        """
        Сохраняет настройки из UI в хранилище.
        
        Показывает статус сохранения пользователю.
        """
        try:
            main_screen = self.root.get_screen('main')
            settings_screen = main_screen.ids.tab_manager.get_screen('settings')
            key = settings_screen.ids.api_key_input.text.strip()
            
            # Сохраняем API ключ
            self.settings_store.put('api', api_key=key)
            settings_screen.ids.status_label.text = "Настройки сохранены!"
            # Очищаем сообщение через 2 секунды
            Clock.schedule_once(lambda dt: setattr(settings_screen.ids.status_label, 'text', ''), 2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            # Показываем ошибку пользователю
            try:
                err_msg = str(e)[:30]  # Первые 30 символов ошибки
                settings_screen.ids.status_label.text = f"Ошибка: {err_msg}"
            except:
                pass

    def set_difficulty(self, level):
        self.difficulty = level

    def start_generation(self):
        # Check if API key is set
        api_key = None
        if self.settings_store.exists('api'):
            data = self.settings_store.get('api')
            api_key = data.get('api_key', data.get('key'))
        self._last_api_key = api_key
        
        if not api_key:
            self.log("WARNING: No API key configured! Using offline mode.")
        
        # Quick network check before generation
        main_screen = self.root.get_screen('main')
        network_status = main_screen.ids.network_status.text
        if network_status == '📵':
            self.log("WARNING: No internet connection detected!")
        
        # Access SearchScreen through MainScreen -> ScreenManager
        search_screen = main_screen.ids.tab_manager.get_screen('search')
        topic = search_screen.ids.topic_input.text.strip()
        if not topic:
            topic = "Общие знания"
        
        # Переходим на экран загрузки и запускаем генерацию в отдельном потоке
        self.root.current = 'loading'
        threading.Thread(target=self.generate_quiz_thread, args=(topic, self.difficulty)).start()

    def generate_quiz_thread(self, topic, difficulty):
        """
        Генерирует тест в отдельном потоке.
        
        Вызывает LLM для создания теории и вопросов.
        Не блокирует UI во время генерации.
        
        Args:
            topic: Тема для генерации
            difficulty: Уровень сложности
        """
        # Получаем API ключ из настроек
        api_key = None
        if self.settings_store.exists('api'):
            data = self.settings_store.get('api')
            api_key = data.get('api_key', data.get('key'))
        
        self.log(f"Starting generation for {topic}...")
        self.log(f"API key available: {'Yes' if api_key else 'No'}")
        
        try:
            # Вызываем LLM для генерации курса
            result = generate_quiz(topic, difficulty, api_key=api_key)
            self.log(f"Generation completed. Has error: {'error' in result}")
        except Exception as e:
            self.log(f"Exception during generation: {e}")
            result = None
        
        # Возвращаемся в главный поток для обновления UI
        Clock.schedule_once(lambda dt: self.on_generation_complete(result))

    def on_generation_complete(self, result):
        """
        Обрабатывает результат генерации теста.
        
        Сохраняет курс в хранилище, подготавливает экраны,
        переключает на экран теории или сразу на тест.
        
        Args:
            result: Словарь с сгенерированным курсом {questions, theory, meta}
        """
        if result and 'questions' in result:
            if 'error' in result and result['error']:
                self.log(f"Generation error: {result['error']}")
            else:
                self.log("Generation successful")

            # Сохраняем сгенерированный курс в хранилище
            self.storage.save(result)
            
            # Загружаем вопросы в QuizScreen
            quiz_screen = self.root.get_screen('quiz')
            quiz_screen.questions = result['questions']
            
            # Сохраняем метаданные курса
            meta = result.get('meta', {})
            topic = meta.get('topic', '')
            difficulty = meta.get('difficulty', '')
            theory_text = result.get('theory', '') or ''
            
            # Создаём краткую заметку из первых 200 символов теории
            snippet = ' '.join(theory_text.splitlines())[:200]
            if snippet:
                meta.setdefault('notes', {})['quick_hint'] = snippet
            
            self._last_saved_meta = meta
            self.last_material = f"Тема: {topic}\n\n{theory_text}" if topic else theory_text
            
            # Если есть теория, показываем её перед тестом
            if 'theory' in result and result['theory']:
                theory_screen = self.root.get_screen('theory')
                theory_screen.theory_content = result['theory']
                theory_screen.meta_title = f"Тема: {topic}" if topic else ''
                theory_screen.meta_sub = f"Сложность: {difficulty}" if difficulty else ''
                self.root.current = 'theory'
            else:
                # Если теории нет, сразу запускаем тест
                self.start_quiz()
        else:
            # Если ошибка, возвращаемся на главную и показываем уведомление (в консоль пока)
            print("Failed to generate quiz")
            self.root.current = 'main'

    def prepare_followup_topics(self):
        if not getattr(self, 'root', None):
            return
        final_screen = self.root.get_screen('final')
        final_screen.set_followup_topics([], loading=True)
        prev_material = self.last_material or ''

        def worker():
            topics = generate_next_topics(prev_material, n=5, api_key=self._last_api_key, memory_file=self.topic_memory_file)
            if not topics:
                topics = get_course_topics(self.topic_memory_file)
            if topics:
                topics = topics[:5]
            Clock.schedule_once(lambda dt: final_screen.set_followup_topics(topics, loading=False))

        threading.Thread(target=worker, daemon=True).start()

    def show_combined_results(self, open_score, open_max, open_percent, open_errors):
        """
        Показывает комбинированный отчёт о прохождении обеих частей.
        
        Объединяет результаты MC теста и открытых вопросов в один финальный отчёт
        с визуальным разделением между секциями.
        
        Args:
            open_score: Количество правильных развёрнутых ответов
            open_max: Общее количество развёрнутых вопросов
            open_percent: Процент правильных развёрнутых ответов
            open_errors: Список ошибок из развёрнутых ответов
        """
        final_screen = self.root.get_screen('final')
        
        # Получаем данные MC теста, сохранённые ранее
        mc_score = getattr(self, 'mc_test_score', 0)
        mc_total = getattr(self, 'mc_test_total', 0)
        mc_percent = getattr(self, 'mc_test_percent', 0)
        mc_errors = getattr(self, 'mc_test_errors', [])
        
        # Вычисляем общий процент (среднее арифметическое)
        total_percent = int((mc_percent + open_percent) / 2)
        
        # Устанавливаем общий заголовок с результатами
        final_screen.set_score(mc_score + open_score, mc_total + open_max, total_percent)
        
        # Подготавливаем краткие заметки по теме
        note_text = ''
        topic = ''
        difficulty = self.difficulty
        if self._last_saved_meta:
            topic = self._last_saved_meta.get('topic', '')
            difficulty = self._last_saved_meta.get('difficulty', difficulty)
            note_text = self._last_saved_meta.get('notes', {}).get('quick_hint', '')
        if not note_text:
            note_text = (self.last_material or '').strip()[:240]
        final_screen.set_quick_note(note_text)
        
        # Комбинируем ошибки из двух разделов в один список
        combined_errors = []
        
        # Добавляем заголовок и ошибки MC части
        if mc_errors:
            combined_errors.append({
                'question': '═══ РАБОТА НАД ОШИБКАМИ: ТЕСТОВАЯ ЧАСТЬ ═══',
                'selected': f'Результат: {mc_percent}% ({mc_score}/{mc_total})',
                'correct': ''
            })
            combined_errors.extend(mc_errors)
        
        # Добавляем разделитель и заголовок для открытых вопросов
        if open_errors:
            if mc_errors:
                # Визуальный разделитель между секциями
                combined_errors.append({'divider': True})
            combined_errors.append({
                'question': '═══ РАБОТА НАД ОШИБКАМИ: РАЗВЁРНУТЫЕ ОТВЕТЫ ═══',
                'selected': f'Результат: {open_percent}% ({open_score}/{open_max})',
                'correct': ''
            })
            combined_errors.extend(open_errors)
        
        # Отображаем все ошибки в едином списке
        final_screen.set_error_explanations(combined_errors)

        # Сохраняем в историю
        if topic and difficulty:
            timestamp = datetime.utcnow().isoformat()
            entry = {
                'timestamp': timestamp,
                'score_percent': total_percent,
                'difficulty': difficulty,
                'mc_score': f'{mc_score}/{mc_total}',
                'open_score': f'{open_score}/{open_max}'
            }
            def updater(course):
                meta = course.setdefault('meta', {})
                history = meta.setdefault('history', [])
                history.insert(0, entry)
                meta.setdefault('notes', {})['quick_hint'] = note_text
            self.storage.update_entry(topic, difficulty, updater)

        self.adjust_difficulty(total_percent)
        self.prepare_followup_topics()

    def handle_quiz_result(self, score, total, percent, errors=None):
        final_screen = self.root.get_screen('final')
        final_screen.set_score(score, total, percent)
        note_text = ''
        topic = ''
        difficulty = self.difficulty
        if self._last_saved_meta:
            topic = self._last_saved_meta.get('topic', '')
            difficulty = self._last_saved_meta.get('difficulty', difficulty)
            note_text = self._last_saved_meta.get('notes', {}).get('quick_hint', '')
        if not note_text:
            note_text = (self.last_material or '').strip()[:240]
        final_screen.set_quick_note(note_text)
        final_screen.set_error_explanations(errors or [])

        if topic and difficulty:
            timestamp = datetime.utcnow().isoformat()
            entry = {
                'timestamp': timestamp,
                'score_percent': percent,
                'difficulty': difficulty
            }
            def updater(course):
                meta = course.setdefault('meta', {})
                history = meta.setdefault('history', [])
                history.insert(0, entry)
                meta.setdefault('notes', {})['quick_hint'] = note_text
            self.storage.update_entry(topic, difficulty, updater)

        self.adjust_difficulty(percent)
        self.prepare_followup_topics()

    def adjust_difficulty(self, percent):
        """
        Автоматически корректирует сложность на основе результата.
        
        Повышает сложность при результате >= 80%
        Понижает сложность при результате <= 40%
        
        Args:
            percent: Процент правильных ответов
        """
        levels = ['легкий', 'средний', 'эксперт']
        try:
            current_idx = levels.index(self.difficulty)
        except ValueError:
            current_idx = 0

        # Повышаем уровень при хорошем результате
        if percent >= 80 and current_idx < len(levels) - 1:
            current_idx += 1
        # Понижаем при плохом результате
        elif percent <= 40 and current_idx > 0:
            current_idx -= 1

        new_level = levels[current_idx]
        if new_level != self.difficulty:
            self.log(f"Адаптация сложности: {self.difficulty} → {new_level} (результат {percent}%)")
            self.difficulty = new_level

    def preload_open_questions(self):
        """
        Предзагружает открытые вопросы во время прохождения MC теста.
        
        Запускается в отдельном потоке сразу при входе на экран MC теста.
        Сначала проверяет кеш, затем генерирует новые вопросы если нужно.
        Значительно ускоряет переход к развёрнутым ответам.
        """
        topic = ''
        if self._last_saved_meta:
            topic = self._last_saved_meta.get('topic', 'Общие знания')
        if not topic:
            topic = 'Общие знания'
        
        # Получаем API ключ для генерации
        api_key = None
        if self.settings_store.exists('api'):
            data = self.settings_store.get('api')
            api_key = data.get('api_key', data.get('key'))
        
        self.log(f"Предзагрузка открытых вопросов по теме: {topic}...")
        
        # Сначала проверяем кеш
        cached = self.get_cached_open_questions(topic)
        if cached:
            # Вопросы найдены в кеше - используем их
            self.preloaded_open_questions = cached
            self.log("Открытые вопросы загружены из кеша")
            return
        
        # Кеша нет - генерируем новые вопросы
        try:
            questions = generate_open_questions(topic, n=3, difficulty=self.difficulty, api_key=api_key)
            self.preloaded_open_questions = questions
            # Сохраняем в кеш для будущих использований
            self.cache_open_questions(topic, questions)
            self.log(f"Открытые вопросы предзагружены успешно")
        except Exception as e:
            self.log(f"Ошибка предзагрузки открытых вопросов: {e}")
            self.preloaded_open_questions = []

    def transition_to_open_questions(self):
        """
        Переход к открытым вопросам с проверкой готовности.
        
        Проверяет, загрузились ли вопросы в фоне. Если да - сразу показывает их,
        если нет - показывает экран загрузки и ждёт готовности.
        """
        if hasattr(self, 'preloaded_open_questions'):
            # Вопросы уже предзагружены - сразу показываем
            self.on_open_questions_generated(self.preloaded_open_questions)
        else:
            # Показываем экран загрузки и ждём завершения предзагрузки
            self.root.current = 'loading'
            Clock.schedule_once(lambda dt: self.check_preload_ready(), 0.5)
    
    def check_preload_ready(self):
        """
        Периодически проверяет готовность предзагруженных вопросов.
        
        Вызывается каждые 0.5 секунд до тех пор, пока вопросы не будут готовы.
        """
        if hasattr(self, 'preloaded_open_questions'):
            # Вопросы готовы - показываем экран с ними
            self.on_open_questions_generated(self.preloaded_open_questions)
        else:
            # Продолжаем ждать
            Clock.schedule_once(lambda dt: self.check_preload_ready(), 0.5)

    def start_open_questions(self):
        """
        Запускает генерацию открытых вопросов после MC теста.
        
        Этот метод используется как резервный, если предзагрузка не сработала.
        """
        self.root.current = 'loading'
        
        # Получаем тему из последнего сохраненного курса
        topic = ''
        if self._last_saved_meta:
            topic = self._last_saved_meta.get('topic', 'Общие знания')
        if not topic:
            topic = 'Общие знания'
        
        threading.Thread(target=self.generate_open_questions_thread, args=(topic,)).start()

    def generate_open_questions_thread(self, topic):
        """Генерируем открытые вопросы в отдельном потоке"""
        api_key = None
        if self.settings_store.exists('api'):
            data = self.settings_store.get('api')
            api_key = data.get('api_key', data.get('key'))
        
        self.log(f"Генерация открытых вопросов по теме: {topic}...")
        cached = self.get_cached_open_questions(topic)
        if cached:
            self.log("Используем кешированные открытые вопросы")
            Clock.schedule_once(lambda dt: self.on_open_questions_generated(cached))
            return
        try:
            questions = generate_open_questions(topic, n=3, difficulty=self.difficulty, api_key=api_key)
            self.cache_open_questions(topic, questions)
            Clock.schedule_once(lambda dt: self.on_open_questions_generated(questions))
        except Exception as e:
            self.log(f"Ошибка генерации открытых вопросов: {e}")
            Clock.schedule_once(lambda dt: self.on_open_questions_generated([]))

    def on_open_questions_generated(self, questions):
        """Обработка сгенерированных открытых вопросов"""
        if not questions:
            self.log("Не удалось сгенерировать открытые вопросы. Переход к результатам.")
            # Показываем финальный экран с результатами MC теста
            self.show_final_results()
            return
        
        # Сохраняем открытые вопросы
        self.open_questions = questions
        self.current_open_idx = 0
        self.open_answers_history = []
        
        # Переходим на экран открытых вопросов
        self.show_open_question()
        self.root.current = 'open_answer'

    def show_open_question(self):
        """Отображает текущий открытый вопрос"""
        if not hasattr(self, 'open_questions') or self.current_open_idx >= len(self.open_questions):
            # Все вопросы пройдены, показываем результаты
            self.finish_open_session()
            return

        q = self.open_questions[self.current_open_idx]
        screen = self.root.get_screen('open_answer')
        
        screen.ids.progress_label.text = f"Вопрос {self.current_open_idx + 1} из {len(self.open_questions)}"
        screen.ids.question_label.text = q.get('question', 'Ошибка загрузки вопроса')
        screen.ids.answer_input.text = ''
        screen.ids.answer_input.readonly = False
        screen.ids.feedback_label.text = ''
        screen.ids.action_button.text = 'ОТПРАВИТЬ ✓'
        screen.ids.action_button.disabled = False
        screen.ids.skip_button.disabled = False

    def handle_open_answer_action(self):
        """Обрабатывает нажатие кнопки действия (ОТПРАВИТЬ/ДАЛЕЕ)"""
        screen = self.root.get_screen('open_answer')
        btn_text = screen.ids.action_button.text
        
        if 'ОТПРАВИТЬ' in btn_text:
            # Режим отправки ответа
            answer = screen.ids.answer_input.text.strip()
            if not answer:
                return
            
            # Блокируем интерфейс во время оценки
            screen.ids.answer_input.readonly = True
            screen.ids.action_button.disabled = True
            screen.ids.action_button.text = 'ОЦЕНКА... ⏳'
            screen.ids.skip_button.disabled = True
            
            # Получаем текущий вопрос и заметки к нему
            q = self.open_questions[self.current_open_idx]
            notes = q.get('notes', '')
            
            # Запускаем оценку в отдельном потоке
            threading.Thread(target=self.evaluate_answer_thread, args=(q['question'], answer, notes)).start()
            
        elif 'ДАЛЕЕ' in btn_text:
            # Режим перехода к следующему вопросу
            self.next_open_question()

    def evaluate_answer_thread(self, question, answer, notes):
        """
        Оценивает развёрнутый ответ через LLM в отдельном потоке.
        
        Не блокирует UI во время оценки, которая может занять несколько секунд.
        
        Args:
            question: Текст вопроса
            answer: Ответ пользователя
            notes: Дополнительные заметки для оценки
        """
        api_key = None
        if self.settings_store.exists('api'):
            data = self.settings_store.get('api')
            api_key = data.get('api_key', data.get('key'))
            
        try:
            # Вызываем LLM для оценки ответа
            result = evaluate_answer(question, answer, notes, api_key=api_key)
            Clock.schedule_once(lambda dt: self.on_answer_evaluated(result, answer))
        except Exception as e:
            self.log(f"Ошибка оценки ответа: {e}")
            Clock.schedule_once(lambda dt: self.on_answer_evaluated(None, answer))

    def on_answer_evaluated(self, result, answer_text):
        """
        Отображает результат оценки ответа.
        
        Показывает только баллы без подробного разбора.
        Полный разбор будет показан на финальном экране.
        
        Args:
            result: Результат оценки от LLM {score, max_score, feedback, recommendations}
            answer_text: Текст ответа пользователя
        """
        screen = self.root.get_screen('open_answer')
        screen.ids.action_button.disabled = False
        screen.ids.skip_button.disabled = False
        
        if not result:
            # Ошибка оценки - даём возможность повторить
            screen.ids.feedback_label.text = "[color=ff0000]❌ Ошибка оценки. Попробуйте еще раз.[/color]"
            screen.ids.action_button.text = 'ОТПРАВИТЬ ✓'
            screen.ids.answer_input.readonly = False
            return

        score = result.get('score', 0)
        max_score = result.get('max_score', 10)
        
        # Показываем только оценку без детального разбора
        feedback = f"[b][color=0d74d6]Оценка: {score}/{max_score} баллов[/color][/b]\n\n"
        feedback += f"[color=666666]Подробный разбор будет в работе над ошибками[/color]"
            
        screen.ids.feedback_label.text = feedback
        screen.ids.action_button.text = 'ДАЛЕЕ →'
        
        # Сохраняем историю ответа для финального отчёта
        self.open_answers_history.append({
            'question': self.open_questions[self.current_open_idx],
            'answer': answer_text,
            'evaluation': result
        })

    def skip_open_question(self):
        """Пропускает текущий открытый вопрос"""
        self.open_answers_history.append({
            'question': self.open_questions[self.current_open_idx],
            'answer': '',
            'evaluation': {'score': 0, 'max_score': 10, 'commentary': 'Пропущено', 'suggested_improvements': ''}
        })
        self.next_open_question()

    def next_open_question(self):
        """Переходит к следующему открытому вопросу"""
        self.current_open_idx += 1
        self.show_open_question()

    def finish_open_session(self):
        """Завершает сессию открытых вопросов и показывает комбинированный отчёт"""
        # Подсчитываем баллы за открытые вопросы
        open_score = sum([item['evaluation'].get('score', 0) for item in self.open_answers_history])
        open_max = len(self.open_answers_history) * 10
        open_percent = int((open_score / open_max * 100) if open_max > 0 else 0)
        
        # Формируем список ошибок для открытых вопросов
        open_errors = []
        for item in self.open_answers_history:
            eval_data = item['evaluation']
            # Добавляем только вопросы с ошибками или неполным баллом
            if eval_data.get('suggested_improvements') or eval_data.get('score', 10) < 10:
                open_errors.append({
                    'question': item['question'].get('question', '')[:60] + '...',  # Сокращаем длинные вопросы
                    'selected': f"Ваша оценка: {eval_data.get('score', 0)}/10",
                    'correct': eval_data.get('suggested_improvements', eval_data.get('commentary', ''))
                })
        
        # Показываем комбинированный финальный экран с обеими секциями
        self.show_combined_results(open_score, open_max, open_percent, open_errors)
        self.root.current = 'final'

    def start_followup_topic(self, topic):
        """
        Начинает новый курс по рекомендованной теме.
        
        Args:
            topic: Название темы для изучения
        """
        main_screen = self.root.get_screen('main')
        main_screen.ids.tab_manager.current = 'search'
        search_screen = main_screen.ids.tab_manager.get_screen('search')
        search_screen.ids.topic_input.text = topic
        self.root.current = 'loading'
        threading.Thread(target=self.generate_quiz_thread, args=(topic, self.difficulty)).start()

    def delete_current_course(self):
        """
        Удаляет текущий активный курс из истории.
        """
        if not self._last_saved_meta:
            return
        topic = self._last_saved_meta.get('topic')
        difficulty = self._last_saved_meta.get('difficulty', '')
        if not topic:
            return
        removed = self.storage.delete(topic, difficulty)
        if removed:
            self.log(f"Курс '{topic}' ({difficulty}) удалён из истории.")
            self._last_saved_meta = None
            self.load_saved_courses_ui()

    def delete_saved_course(self, topic, difficulty):
        """
        Удаляет сохранённый курс из истории.
        
        Args:
            topic: Название темы курса
            difficulty: Уровень сложности
        """
        if not topic:
            return
        removed = self.storage.delete(topic, difficulty)
        if not removed:
            return
        self.log(f"Курс '{topic}' ({difficulty}) удалён из истории.")
        # Если удаляем текущий активный курс, очищаем ссылку
        if self._last_saved_meta and self._last_saved_meta.get('topic') == topic and \
                self._last_saved_meta.get('difficulty') == difficulty:
            self._last_saved_meta = None
        self.load_saved_courses_ui()

    def load_saved_courses_ui(self):
        main_screen = self.root.get_screen('main')
        saved_screen = main_screen.ids.tab_manager.get_screen('saved')
        grid = saved_screen.ids.courses_grid
        grid.clear_widgets()
        
        courses = self.storage.get_all()
        if not courses:
            lbl = Label(text="Нет сохраненных курсов", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(40))
            grid.add_widget(lbl)
            return

        for course in courses:
            meta = course.get('meta', {})
            topic = meta.get('topic', 'Без темы')
            diff = meta.get('difficulty', '')
            
            btn = CourseCard(topic=topic, difficulty=diff)
            # Use a closure to capture the specific course
            btn.bind(on_release=lambda x, c=course: self.start_saved_course(c))
            grid.add_widget(btn)

    def start_saved_course(self, course):
        self.on_generation_complete(course)

    def start_quiz_from_theory(self):
        """
        Запускает тест с экрана теории.
        
        Вызывается кнопкой "Начать тест" на экране теории.
        """
        self.start_quiz()

    def start_quiz(self):
        """
        Запускает MC тест и сбрасывает предзагрузку открытых вопросов.
        
        Инициирует новую предзагрузку открытых вопросов в фоне.
        """
        quiz = self.root.get_screen('quiz')
        quiz.reset_quiz()
        # Сбрасываем флаги предзагрузки для нового теста
        self.open_questions_preloading = False
        if hasattr(self, 'preloaded_open_questions'):
            delattr(self, 'preloaded_open_questions')
        self.root.current = 'quiz'

    def restart_quiz(self):
        """
        Перезапускает MC тест с начала.
        
        Сбрасывает прогресс и начинает тест заново.
        """
        quiz = self.root.get_screen('quiz')
        quiz.reset_quiz()
        self.root.current = 'quiz'

    def exit_to_main(self):
        """
        Возвращает на главный экран приложения.
        
        Обработчик для кнопки "Домой" в нижней навигации.
        """
        if self.root:
            self.root.current = 'main'

    def return_to_theory(self):
        """
        Возвращает на экран теории.
        
        Используется для повторного чтения материала перед тестом.
        """
        if self.root:
            self.root.current = 'theory'

    def goto_search_tab(self):
        """
        Переключает на таб поиска на главном экране.
        
        Обработчик для кнопки "Поиск" в нижней навигации.
        """
        if not self.root:
            return
        self.root.current = 'main'
        try:
            main_screen = self.root.get_screen('main')
            main_screen.ids.tab_manager.current = 'search'
        except Exception:
            pass


# ============================================================================
# ТОЧКА ВХОДА ПРИЛОЖЕНИЯ
# ============================================================================
if __name__ == '__main__':
    print("[MAIN] === Starting MyApp ===")
    try:
        # Создаём и запускаем экземпляр приложения
        app = MyApp()
        print("[MAIN] MyApp instance created")
        app.run()  # Запускает главный цикл Kivy
    except Exception as e:
        # Логируем критические ошибки при запуске
        print(f"[MAIN] FATAL ERROR: {e}")
        print(f"[MAIN] Traceback: {tb_module.format_exc()}")
        raise
