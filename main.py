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
    from kivymd.app import MDApp # KivyMD App
    from kivymd.uix.button import MDIconButton # KivyMD Icon Button
    from kivymd.uix.label import MDIcon # KivyMD Icon
    from kivy.lang import Builder  # Парсер KV языка для описания UI
    from kivy.core.window import Window  # Управление окном приложения
    from kivy.uix.screenmanager import ScreenManager, Screen  # Менеджер экранов
    from kivy.uix.boxlayout import BoxLayout  # Линейный layout
    from kivy.uix.floatlayout import FloatLayout  # Layout для позиционирования
    from kivy.uix.anchorlayout import AnchorLayout  # Layout для центрирования
    from kivy.uix.gridlayout import GridLayout  # Табличный layout
    from kivy.uix.label import Label  # Текстовые метки
    from kivy.uix.image import Image  # Изображения
    from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior  # Поведение кнопок
    from kivy.uix.button import Button  # Стандартные кнопки
    from kivy.uix.togglebutton import ToggleButton  # Переключаемые кнопки
    from kivy.uix.scrollview import ScrollView  # Прокручиваемые области
    from kivy.uix.textinput import TextInput  # Поля ввода текста
    from kivy.uix.modalview import ModalView  # Модальные окна
    from kivy.uix.widget import Widget  # Базовый виджет
    from kivy.metrics import dp  # Density-independent pixels для кросс-платформенности
    from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty  # Реактивные свойства

    print("[MAIN] graphics imported")
    from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse  # Графические примитивы
    print("[MAIN] Clock imported")
    from kivy.clock import Clock  # Планировщик событий
    from kivy.animation import Animation # Анимации
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


# Попытка найти системный шрифт с поддержкой emoji
def detect_emoji_font():
    """Return a path to an emoji-capable font if available, otherwise None."""
    candidates = []
    if sys.platform == 'win32':
        candidates = [
            r'C:\Windows\Fonts\seguiemj.ttf',  # Segoe UI Emoji
            r'C:\Windows\Fonts\Segoe UI Emoji.ttf',
        ]
    elif sys.platform == 'darwin':
        candidates = [
            '/System/Library/Fonts/Apple Color Emoji.ttc',
            '/System/Library/Fonts/Apple Color Emoji.ttf',
        ]
    else:
        # Linux / Android common locations
        candidates = [
            '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',
            '/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf',
            '/usr/share/fonts/truetype/emoji/NotoColorEmoji.ttf',
            '/system/fonts/NotoColorEmoji.ttf',
        ]

    for p in candidates:
        try:
            if p and os.path.exists(p):
                print(f"[MAIN] Found emoji font: {p}")
                return p
        except Exception:
            pass

    # Fallback: try to scan common font directories for filenames containing 'emoji'
    fonts_dirs = []
    if sys.platform == 'win32':
        fonts_dirs = [r'C:\Windows\Fonts']
    elif sys.platform == 'darwin':
        fonts_dirs = ['/System/Library/Fonts', '/Library/Fonts']
    else:
        fonts_dirs = ['/usr/share/fonts', '/usr/local/share/fonts', '/system/fonts']

    for fd in fonts_dirs:
        try:
            if not os.path.isdir(fd):
                continue
            for root, dirs, files in os.walk(fd):
                for f in files:
                    lf = f.lower()
                    if 'emoji' in lf or 'noto' in lf and 'color' in lf:
                        cand = os.path.join(root, f)
                        print(f"[MAIN] Found emoji font by scan: {cand}")
                        return cand
        except Exception:
            continue

    print('[MAIN] No emoji-capable font found on system')
    return None


# Detect emoji font at import time
EMOJI_FONT_PATH = detect_emoji_font()

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


class RoadmapStorage:
    """
    Класс для управления хранилищем обучающих программ (roadmaps).
    
    Хранит:
    - Структуру roadmap (узлы, связи, позиции)
    - Прогресс прохождения каждого узла
    - Связанные курсы для каждого узла
    
    Файл: roadmaps.json в директории пользовательских данных приложения
    """
    
    def __init__(self, filename='roadmaps.json'):
        """
        Инициализация хранилища roadmaps.
        
        Args:
            filename: Путь к JSON файлу для хранения roadmaps
        """
        self.filename = filename
        self.roadmaps = self.load()
    
    def load(self):
        """
        Загружает roadmaps из JSON файла.
        
        Returns:
            dict: Словарь roadmaps {roadmap_id: roadmap_data} или пустой словарь
        """
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save(self, roadmap_id, roadmap_data):
        """
        Сохраняет roadmap в хранилище.
        
        Args:
            roadmap_id: Уникальный идентификатор roadmap
            roadmap_data: Данные roadmap {title, description, nodes, progress}
        """
        self.roadmaps[roadmap_id] = roadmap_data
        self._write()
    
    def get(self, roadmap_id):
        """
        Получает roadmap по ID.
        
        Args:
            roadmap_id: ID roadmap
            
        Returns:
            dict|None: Данные roadmap или None если не найдена
        """
        return self.roadmaps.get(roadmap_id)
    
    def get_all(self):
        """
        Возвращает все roadmaps.
        
        Returns:
            dict: Словарь всех roadmaps
        """
        return self.roadmaps
    
    def update_node_progress(self, roadmap_id, node_id, completed, course_data=None):
        """
        Обновляет прогресс узла в roadmap.
        
        Args:
            roadmap_id: ID roadmap
            node_id: ID узла
            completed: Завершен ли узел (bool)
            course_data: Опциональные данные связанного курса
        """
        roadmap = self.roadmaps.get(roadmap_id)
        if not roadmap:
            return
        
        if 'progress' not in roadmap:
            roadmap['progress'] = {}
        
        # Гарантируем, что ID узла — строка (для JSON ключей)
        node_id = str(node_id)
        
        roadmap['progress'][node_id] = {
            'completed': completed,
            'course_data': course_data,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        self._write()
    
    def get_node_progress(self, roadmap_id, node_id):
        """
        Получает прогресс узла.
        
        Args:
            roadmap_id: ID roadmap
            node_id: ID узла
            
        Returns:
            dict|None: Данные прогресса или None
        """
        roadmap = self.roadmaps.get(roadmap_id)
        if not roadmap:
            return None
        # Гарантируем, что ID узла — строка
        return roadmap.get('progress', {}).get(str(node_id))
    
    def delete(self, roadmap_id):
        """
        Удаляет roadmap.
        
        Args:
            roadmap_id: ID roadmap
            
        Returns:
            bool: True если удалена, False если не найдена
        """
        if roadmap_id in self.roadmaps:
            del self.roadmaps[roadmap_id]
            self._write()
            return True
        return False
    
    def _write(self):
        """Записывает roadmaps в JSON файл."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.roadmaps, f, ensure_ascii=False, indent=2)


# ============================================================================
# KV MARKUP LANGUAGE - ДЕКЛАРАТИВНОЕ ОПИСАНИЕ ИНТЕРФЕЙСА
# ============================================================================
# Kivy использует язык KV для описания UI компонентов
# Формат: ClassName: с отступами для вложенных элементов
# Свойства: property: value
# Привязки: self.property для реактивных обновлений

KV = """
#:import dp kivy.metrics.dp
#:import Window kivy.core.window.Window

#:set color_bg (0.95, 0.94, 0.92, 1)
#:set color_card (1, 1, 1, 1)
#:set color_primary (0.15, 0.55, 0.9, 1)
#:set color_success_bg (0.82, 0.98, 0.87, 1)
#:set color_success (0.01, 0.6, 0.33, 1)
#:set color_orange (0.86, 0.41, 0.01, 1)
#:set color_text_gray (0.4, 0.44, 0.52, 1)
#:set color_text_dark (0.1, 0.1, 0.1, 1)

<Card@BoxLayout>:
    canvas.before:
        Color:
            rgba: color_card
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(20)]

# Главный менеджер экранов - переключает между основными экранами приложения
ScreenManager:
    MainScreen:
    LoadingScreen:
    TheoryScreen:
    QuizScreen:
    OpenAnswerScreen:
    FinalScreen:
    RoadmapScreen:
    RoadmapsListScreen:
    LessonsListScreen:

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
    canvas.before:
        Color:
            rgba: color_bg
        Rectangle:
            pos: self.pos
            size: self.size
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
            
            Widget:

        # Менеджер табов - переключает между сохраненными, поиском, настройками
        ScreenManager:
            id: tab_manager
            size_hint: (1, 1)
            SavedScreen:
                name: 'saved'
            SearchScreen:
                name: 'search'
            ChatScreen:
                name: 'chat'
            SettingsScreen:
                name: 'settings'
                
        # Нижняя навигация - фиксированная панель с кнопками табов
        BoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: [dp(12), dp(8), dp(12), dp(8)]
            spacing: dp(20)  # Уменьшили для 4 кнопок
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
                    icon_source: 'home'
                    target_screen: 'saved'
                    group: 'main_nav'

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    id: nav_search
                    size: dp(34), dp(34)
                    icon_source: 'magnify'
                    target_screen: 'search'
                    group: 'main_nav'

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    id: nav_chat
                    size: dp(34), dp(34)
                    icon_source: 'chat'
                    target_screen: 'chat'
                    group: 'main_nav'

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                IconToggleButton:
                    id: nav_settings
                    size: dp(34), dp(34)
                    icon_source: 'cog'
                    target_screen: 'settings'
                    group: 'main_nav'

<SavedScreen>:
    name: 'saved'
    on_enter: app.update_profile_stats()
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            padding: [dp(16), dp(16)]
            spacing: dp(10)
            size_hint_y: None
            height: self.minimum_height
            
            # Профиль пользователя
            BoxLayout:
                orientation: 'horizontal'
                spacing: dp(12)
                size_hint_y: None
                height: dp(70)
                
                # Аватар
                FloatLayout:
                    size_hint: None, None
                    size: dp(56), dp(56)
                    canvas.before:
                        Color:
                            rgba: 0.15, 0.55, 0.9, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]
                    Label:
                        text: app.gamification.username[0].upper() if app.gamification.username else 'С'
                        font_size: '28sp'
                        bold: True
                        color: 1, 1, 1, 1
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                
                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    Label:
                        id: profile_name
                        text: app.gamification.username
                        color: 0.1, 0.1, 0.1, 1
                        font_size: '20sp'
                        bold: True
                        halign: 'left'
                        valign: 'bottom'
                        text_size: self.size
                        size_hint_y: 0.5
                    Label:
                        id: profile_level
                        text: str(app.gamification.level) + ' УРОВЕНЬ ОБУЧЕНИЯ'
                        color: 0.5, 0.5, 0.5, 1
                        font_size: '12sp'
                        halign: 'left'
                        valign: 'top'
                        text_size: self.size
                        size_hint_y: 0.5
            
            # Статистика
            GridLayout:
                cols: 2
                spacing: dp(12)
                size_hint_y: None
                height: dp(100)
                
                # Общий XP
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(12)
                    spacing: dp(4)
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]
                    MDIcon:
                        icon: 'star'
                        font_size: '24sp'
                        theme_text_color: 'Custom'
                        text_color: 0.15, 0.55, 0.9, 1
                        size_hint_y: None
                        height: dp(30)
                        halign: 'center'
                    Label:
                        id: total_xp
                        text: str(app.gamification.xp)
                        color: 0.1, 0.1, 0.1, 1
                        font_size: '24sp'
                        bold: True
                        size_hint_y: None
                        height: dp(30)
                        halign: 'center'
                    Label:
                        text: 'ОБЩИЙ XP'
                        color: 0.6, 0.6, 0.6, 1
                        font_size: '11sp'
                        size_hint_y: None
                        height: dp(20)
                        halign: 'center'
                
                # Streak
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(12)
                    spacing: dp(4)
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]
                    MDIcon:
                        icon: 'fire'
                        font_size: '24sp'
                        theme_text_color: 'Custom'
                        text_color: 0.98, 0.4, 0.2, 1
                        size_hint_y: None
                        height: dp(30)
                        halign: 'center'
                    Label:
                        id: streak_days
                        text: str(app.gamification.streak) + ' дн.'
                        color: 0.1, 0.1, 0.1, 1
                        font_size: '24sp'
                        bold: True
                        size_hint_y: None
                        height: dp(30)
                        halign: 'center'
                    Label:
                        text: 'УДАРНЫЙ РЕЖИМ'
                        color: 0.6, 0.6, 0.6, 1
                        font_size: '11sp'
                        size_hint_y: None
                        height: dp(20)
                        halign: 'center'
            
            # Прогресс до следующего уровня
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(8)
                size_hint_y: None
                height: dp(50)
                padding: [dp(0), dp(4)]
                
                BoxLayout:
                    size_hint_y: None
                    height: dp(20)
                    Label:
                        text: 'ПРОГРЕСС ДО ' + str(app.gamification.level + 1) + ' УРОВНЯ'
                        color: 0.6, 0.6, 0.6, 1
                        font_size: '11sp'
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size
                    Label:
                        id: level_progress_percent
                        text: str(app.gamification.get_level_progress()) + '%'
                        color: 0.15, 0.55, 0.9, 1
                        font_size: '13sp'
                        bold: True
                        halign: 'right'
                        valign: 'middle'
                        text_size: self.size
                        size_hint_x: None
                        width: dp(50)
                
                MDProgressBar:
                    id: level_progress_bar
                    size_hint_y: None
                    height: dp(12)
                    value: 0
                    max: 100
                    color: 0.15, 0.55, 0.9, 1
                    background_color: 0.9, 0.9, 0.9, 1
            
            Widget:
                size_hint_y: None
                height: dp(24)
                
            # Вертикальные кнопки управления
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(18)
                size_hint_y: None
                height: dp(190)
                padding: [dp(8), 0]
                
                RoundedButton:
                    text: 'МОИ ПРОГРАММЫ\\n[size=14sp][color=#ffffffcc]Курсы обучения в процессе[/color][/size]'
                    font_size: '18sp'
                    bold: True
                    markup: True
                    bg_color: 0.15, 0.55, 0.9, 1
                    on_release: app.root.current = 'roadmaps_list'
                    
                RoundedButton:
                    text: 'ПРОЙДЕННЫЕ УРОКИ\\n[size=14sp][color=#ffffffcc]История одиночных занятий[/color][/size]'
                    font_size: '18sp'
                    bold: True
                    markup: True
                    bg_color: 0.2, 0.45, 0.75, 1
                    on_release: app.root.current = 'lessons_list'
            
            Widget:
                size_hint_y: None
                height: dp(20)

<RoadmapsListScreen>:
    name: 'roadmaps_list'
    on_enter: app.load_roadmaps_list()
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.95, 0.93, 0.90, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(16), dp(8)]
            canvas.before:
                Color:
                    rgba: 0.15, 0.55, 0.9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            MDIconButton:
                icon: 'arrow-left'
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                on_release: app.root.current = 'main'
            
            Label:
                text: 'Список программ'
                color: 1, 1, 1, 1
                font_size: '20sp'
                bold: True
                halign: 'left'
                valign: 'middle'
                text_size: self.size
        
        ScrollView:
            BoxLayout:
                id: roadmaps_grid_full
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(16), dp(16)]
                spacing: dp(12)

<LessonsListScreen>:
    name: 'lessons_list'
    on_enter: app.load_lessons_list()
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.95, 0.93, 0.90, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(16), dp(8)]
            canvas.before:
                Color:
                    rgba: 0.2, 0.45, 0.75, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            MDIconButton:
                icon: 'arrow-left'
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                on_release: app.root.current = 'main'
            
            Label:
                text: 'История уроков'
                color: 1, 1, 1, 1
                font_size: '20sp'
                bold: True
                halign: 'left'
                valign: 'middle'
                text_size: self.size
        
        ScrollView:
            BoxLayout:
                id: lessons_grid_full
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(16), dp(16)]
                spacing: dp(12)

<SearchScreen>:
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            padding: [dp(12), dp(8), dp(12), dp(8)]
            spacing: dp(8)
            size_hint_y: None
            height: self.minimum_height

            BoxLayout:
                padding: [dp(16), dp(16), dp(16), dp(20)]
                spacing: dp(12)
                canvas.before:
                    Color:
                        rgba: (0.95, 0.93, 0.90, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(20)]
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height + dp(20)
                
                Label:
                    text: 'Добро пожаловать! Введите тему:'
                    color: 0.15, 0.55, 0.9, 1
                    font_size: '18sp'
                    bold: True
                    halign: 'center'
                    size_hint_y: None
                    height: dp(30)

                TextInput:
                    id: topic_input
                    hint_text: 'Например: Python программирование'
                    multiline: False
                    size_hint_y: None
                    height: dp(50)
                    font_size: '16sp'
                    padding: [dp(12), dp(14)]
                    background_normal: ''
                    background_active: ''
                    foreground_color: 0.1, 0.1, 0.1, 1
                    cursor_color: 0.15, 0.55, 0.9, 1
                    canvas:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]
                
                Widget:
                    size_hint_y: None
                    height: dp(12)
                
                # Переключатель режима
                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    orientation: 'horizontal'
                    spacing: dp(12)
                    padding: [dp(12), 0]
                    canvas.before:
                        Color:
                            rgba: (0.15, 0.55, 0.9, 0.05)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]
                    
                    Label:
                        text: 'Программа обучения'
                        color: 0.2, 0.2, 0.2, 1
                        font_size: '16sp'
                        size_hint_x: 1
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    # Инфо-кнопка
                    Button:
                        text: 'i'
                        size_hint: None, None
                        size: dp(26), dp(26)
                        pos_hint: {'center_y': 0.5}
                        background_normal: ''
                        background_color: 0, 0, 0, 0
                        color: 0.15, 0.55, 0.9, 1
                        font_size: '14sp'
                        bold: True
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.55, 0.9, 0.1
                            Ellipse:
                                pos: self.pos
                                size: self.size
                            Color:
                                rgba: 0.15, 0.55, 0.9, 0.4
                            Line:
                                circle: (self.center_x, self.center_y, self.width/2 - dp(1))
                                width: dp(1)
                        on_release: app.show_mode_info()

                    RoundSwitch:
                        id: mode_switch
                        active: app.learning_mode == 'roadmap'
                        size_hint: None, None
                        size: dp(54), dp(30)
                        pos_hint: {'center_y': 0.5}
                        on_active: app.set_learning_mode('roadmap' if self.active else 'single')
                
                Widget:
                    size_hint_y: None
                    height: dp(8)

                Label:
                    text: 'Сложность:'
                    color: 0.5, 0.5, 0.5, 1
                    font_size: '13sp'
                    halign: 'left'
                    size_hint_y: None
                    height: dp(20)
                    text_size: self.width, None

                BoxLayout:
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(8)
                    DifficultyButton:
                        text: 'Легкий'
                        state: 'down'
                        group: 'difficulty'
                        on_release: app.set_difficulty('легкий')
                    DifficultyButton:
                        text: 'Средний'
                        group: 'difficulty'
                        on_release: app.set_difficulty('средний')
                    DifficultyButton:
                        text: 'Эксперт'
                        group: 'difficulty'
                        on_release: app.set_difficulty('эксперт')

                Widget:
                    size_hint_y: None
                    height: dp(12)

                RoundedButton:
                    id: start_button
                    text: 'СОЗДАТЬ ПРОГРАММУ' if mode_switch.active else 'НАЧАТЬ УРОК'
                    font_size: '18sp'
                    bold: True
                    bg_color: (0.3, 0.7, 0.3, 1) if mode_switch.active else (0.15, 0.55, 0.9, 1)
                    size_hint: None, None
                    size: dp(280), dp(56)
                    pos_hint: {'center_x': 0.5}
                    on_release: app.start_learning()

            Widget:
                size_hint_y: None
                height: dp(20)

<SettingsScreen>:
    on_enter: app.load_settings_ui()
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            padding: [dp(16), dp(24), dp(16), dp(24)]
            spacing: dp(8)
            size_hint_y: None
            height: self.minimum_height
            
            Label:
                text: 'Настройки'
                color: 0.15, 0.55, 0.9, 1
                font_size: '22sp'
                bold: True
                size_hint_y: None
                height: dp(40)
                halign: 'left'
                text_size: (self.width, None)
            
            Widget:
                size_hint_y: None
                height: dp(20)
            
            # Поле имени
            Label:
                text: 'ИМЯ В ПРИЛОЖЕНИИ'
                color: 0.6, 0.6, 0.6, 1
                font_size: '11sp'
                size_hint_y: None
                height: dp(20)
                halign: 'left'
                text_size: (self.width, None)
            
            TextInput:
                id: username_input
                text: app.gamification.username
                multiline: False
                size_hint_y: None
                height: dp(50)
                font_size: '16sp'
                padding: [dp(14), dp(14)]
                background_normal: ''
                background_active: ''
                foreground_color: 0.1, 0.1, 0.1, 1
                cursor_color: 0.15, 0.55, 0.9, 1
                canvas:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]
            
            Widget:
                size_hint_y: None
                height: dp(24)
            
            # API ключ
            Label:
                text: 'API КЛЮЧ OPENROUTER'
                color: 0.6, 0.6, 0.6, 1
                font_size: '11sp'
                size_hint_y: None
                height: dp(20)
                halign: 'left'
                text_size: (self.width, None)

            TextInput:
                id: api_key_input
                hint_text: 'sk-or-...'
                multiline: False
                size_hint_y: None
                height: dp(50)
                font_size: '16sp'
                padding: [dp(14), dp(14)]
                background_normal: ''
                background_active: ''
                foreground_color: 0.1, 0.1, 0.1, 1
                cursor_color: 0.15, 0.55, 0.9, 1
                canvas:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]

            Widget:
                size_hint_y: None
                height: dp(24)
            
            # --- ПЕРСОНАЛИЗАЦИЯ (НОВОЕ) ---
            Label:
                text: 'ВАШИ ИНТЕРЕСЫ И ХОББИ'
                color: 0.6, 0.6, 0.6, 1
                font_size: '11sp'
                size_hint_y: None
                height: dp(20)
                halign: 'left'
                text_size: (self.width, None)
            
            TextInput:
                id: interests_input
                hint_text: 'Например: гонки, кулинария, космос...'
                multiline: True
                size_hint_y: None
                height: dp(80)
                font_size: '16sp'
                padding: [dp(14), dp(14)]
                background_normal: ''
                background_active: ''
                foreground_color: 0.1, 0.1, 0.1, 1
                cursor_color: 0.15, 0.55, 0.9, 1
                canvas:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]

            Widget:
                size_hint_y: None
                height: dp(16)
            
            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(12)
                Label:
                    text: 'ПЕРСОНАЛИЗАЦИЯ КУРСОВ'
                    color: 0.2, 0.2, 0.2, 1
                    font_size: '14sp'
                    halign: 'left'
                    text_size: (self.width, None)
                RoundSwitch:
                    id: personalization_switch
                    active: False
                    size_hint_x: None
                    width: dp(50)
                    pos_hint: {'center_y': .5}

            Widget:
                size_hint_y: None
                height: dp(24)

            RoundedButton:
                text: 'СОХРАНИТЬ ИЗМЕНЕНИЯ'
                font_size: '16sp'
                bold: True
                size_hint: 1, None
                height: dp(52)
                bg_color: (0.15, 0.55, 0.9, 1)
                color: 1, 1, 1, 1
                on_release: app.save_settings()
            
            Widget:
                size_hint_y: None
                height: dp(32)

            Label:
                text: 'Лог ошибок:'
                color: 0.5, 0.5, 0.5, 1
                font_size: '14sp'
                size_hint_y: None
                height: dp(20)
                halign: 'left'
                text_size: (self.width, None)
            
            Widget:
                size_hint_y: None
                height: dp(8)

            BoxLayout:
                size_hint_y: None
                height: dp(100)
                padding: [dp(10), dp(10)]
                canvas.before:
                    Color:
                        rgba: 0.95, 0.95, 0.95, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(8)]
                Label:
                    id: debug_log
                    text: 'Ожидание событий...'
                    color: 0.3, 0.3, 0.3, 1
                    font_size: '11sp'
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'


<ChatBubble>:
    size_hint_y: None
    height: self.texture_size[1] + dp(20)
    text_size: self.width - dp(20), None
    valign: 'middle'
    padding: dp(10), dp(10)
    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<AIAssistantPopup>:
    size_hint: 0.92, None
    height: dp(580)
    background_color: 1, 1, 1, 0
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(20), dp(20), dp(20), dp(20)]
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: 0
        AnchorLayout:
            size_hint_y: None
            height: dp(60)
            BoxLayout:
                size_hint_x: None
                width: root.width
                padding: [dp(14), dp(8)]
                spacing: dp(10)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.x, self.y - dp(12)
                        size: self.width, self.height + dp(12)
                        radius: [dp(18), dp(18), 0, 0]
                BoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(12)
                    size_hint_x: 1
                    MDIcon:
                        icon: 'robot'
                        font_size: '40sp'
                        theme_text_color: 'Custom'
                        text_color: 0.15, 0.55, 0.9, 1
                        size_hint: None, None
                        size: dp(40), dp(40)
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_x: 1
                        Label:
                            text: 'Smart Помощник'
                            color: 0.08, 0.12, 0.2, 1
                            bold: True
                            font_size: '16sp'
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'КОНТЕКСТНЫЙ РАЗБОР'
                            color: 0.53, 0.61, 0.72, 1
                            font_size: '12sp'
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                    AnchorLayout:
                        anchor_x: 'right'
                        MDIconButton:
                            icon: 'chevron-down'
                            icon_size: '32sp'
                            theme_text_color: 'Custom'
                            text_color: 0.4, 0.4, 0.4, 1
                            size_hint: None, None
                            size: dp(40), dp(40)
                            on_release: root.dismiss()

        # Chat Area
        ScrollView:
            id: scroll_view
            do_scroll_x: False
            canvas.before:
                Color:
                    rgba: 0.98, 0.98, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            BoxLayout:
                id: chat_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(14)
                spacing: dp(10)

        # Input Area
        BoxLayout:
            size_hint_y: None
            height: dp(74)
            padding: [dp(14), dp(10), dp(14), dp(18)]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            TextInput:
                id: input_field
                hint_text: 'Ваш вопрос по теме...'
                hint_text_color_focus: 0.7, 0.7, 0.7, 1
                hint_text_color_normal: 0.8, 0.8, 0.8, 1
                multiline: False
                size_hint: 0.85, 1
                padding: [dp(14), dp(10)]
                background_normal: ''
                background_active: ''
                foreground_color: 0.1, 0.1, 0.1, 1
                font_size: '14sp'
                canvas:
                    Color:
                        rgba: 0.97, 0.98, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(20)]
            AnchorLayout:
                size_hint_x: 0.15
                anchor_x: 'center'
                MDIconButton:
                    icon: 'send'
                    icon_size: '24sp'
                    theme_text_color: 'Custom'
                    text_color: 1, 1, 1, 1
                    size_hint: None, None
                    size: dp(50), dp(50)
                    on_release: root.send_message()
                    canvas.before:
                        Color:
                            rgba: 0.15, 0.55, 0.9, 1
                        Ellipse:
                            pos: self.x + dp(2), self.y + dp(2)
                            size: self.width - dp(4), self.height - dp(4)
                # spacing/padding handled in parent

<TheoryScreen>:
    name: 'theory'
    canvas.before:
        Color:
            rgba: color_bg
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(16), dp(40), dp(16), dp(16)]
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            IconButton:
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': .5}
                default_source: 'arrow-left'
                pressed_source: 'arrow-left'
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
                font_size: '22sp'
                bold: True
                halign: 'center'
                text_size: self.size
                valign: 'middle'

            IconButton:
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': .5}
                icon: 'robot'
                theme_text_color: "Custom"
                text_color: 0.15, 0.55, 0.9, 1
                on_release: root.open_ai_assistant()
                canvas.before:
                    Color:
                        rgba: (0.9, 0.9, 0.9, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]

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
            id: theory_scroll
            BoxLayout:
                id: theory_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(10), dp(10)]
                spacing: dp(4)

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
    canvas.before:
        Color:
            rgba: color_bg
        Rectangle:
            pos: self.pos
            size: self.size
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
    canvas.before:
        Color:
            rgba: color_bg
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: [dp(20), dp(40), dp(20), dp(16)]
        spacing: dp(24)

        # Progress Bar with percentage
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(12)
            
            Widget:
                size_hint_y: None
                height: dp(8)
                canvas:
                    Color:
                        rgba: (0.85, 0.85, 0.85, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(4)]
                    Color:
                        rgba: color_primary
                    RoundedRectangle:
                        pos: self.pos
                        size: (self.width * ((root.question_index + 1) / max(1, len(root.questions))), self.height) if root.questions else (0, self.height)
                        radius: [dp(4)]
            
            Label:
                text: str(int(((root.question_index + 1) / max(1, len(root.questions))) * 100)) + '%' if root.questions else '0%'
                color: color_text_gray
                font_size: '14sp'
                size_hint_x: None
                width: dp(50)
                halign: 'right'
                valign: 'middle'

        # Question header
        Label:
            text: 'ВОПРОС ' + str(root.question_index + 1) + ' ИЗ ' + str(len(root.questions))
            color: color_text_gray
            font_size: '11sp'
            bold: True
            size_hint_y: None
            height: dp(20)
            halign: 'left'
            text_size: self.width, None

        # Question text
        Label:
            id: question_label
            text: root.current_question_text
            color: color_text_dark
            font_size: '20sp'
            bold: True
            text_size: self.width, None
            halign: 'left'
            valign: 'top'
            size_hint_y: None
            height: self.texture_size[1]

        # Answer options
        GridLayout:
            id: options_box
            cols: 1
            size_hint_y: 1
            spacing: dp(12)

        # Result label at bottom
        Label:
            id: result_label
            text: root.result_text
            size_hint_y: None
            height: self.texture_size[1] if root.result_text else dp(10)
            color: 0.25, 0.25, 0.25, 1
            font_size: '14sp'
            halign: 'center'
        
        Widget:

<OpenAnswerScreen>:
    name: 'open_answer'
    canvas.before:
        Color:
            rgba: color_bg
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(16), dp(40), dp(16), dp(16)]
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            IconButton:
                size_hint: None, None
                size: dp(36), dp(36)
                default_source: 'arrow-left'
                pressed_source: 'arrow-left'
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

        # Input Area: attach button, separate rounded input field, send button
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(10), dp(8)]
            spacing: dp(10)

            BoxLayout:
                id: input_container
                size_hint_x: 1
                size_hint_y: None
                height: dp(44)
                pos_hint: {'center_y': 0.5}
                padding: [dp(8), 0]
                canvas.before:
                    # Background for input field (rounded)
                    Color:
                        rgba: 0.95, 0.95, 0.95, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12), dp(12), dp(12), dp(12)]
                    # Outline (border) around the rounded input field
                    Color:
                        rgba: 0.78, 0.78, 0.78, 1
                    Line:
                        rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
                        width: 1

                TextInput:
                    id: message_input
                    hint_text: 'Сообщение...'
                    multiline: False
                    size_hint_x: 1
                    size_hint_y: 1
                    background_normal: ''
                    background_active: ''
                    background_color: 0, 0, 0, 0
                    padding: [dp(6), dp(10)]
                    foreground_color: 0, 0, 0, 1

            IconButton:
                id: send_btn
                size_hint: None, None
                size: dp(32), dp(32)
                pos_hint: {'center_y': 0.5}
                default_source: 'send'
                pressed_source: 'send'
                on_release: root.send_message()
                # No background fill: icon-only button

<FinalScreen>:
    name: 'final'
    canvas.before:
        Color:
            rgba: color_bg
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: [dp(16), dp(40), dp(16), dp(16)]
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
                spacing: dp(16)
                padding: [0, dp(12), 0, dp(120)]

                # Back Button
                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    padding: [0, 0, 0, 0]
                    IconButton:
                        size_hint: None, None
                        size: dp(36), dp(36)
                        pos_hint: {'center_y': 0.5}
                        default_source: 'arrow-left'
                        pressed_source: 'arrow-left'
                        on_release: app.exit_to_main()
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 0.9
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(12)]
                    Widget:

                # Success Icon
                AnchorLayout:
                    anchor_x: 'center'
                    anchor_y: 'center'
                    size_hint_y: None
                    height: dp(80)
                    
                    Widget:
                        size_hint: None, None
                        size: dp(64), dp(64)
                        canvas:
                            Color:
                                rgba: color_success_bg
                            Ellipse:
                                pos: self.pos
                                size: self.size
                            Color:
                                rgba: color_success
                            Line:
                                width: dp(3)
                                points: [self.x + dp(18), self.y + dp(32), self.x + dp(28), self.y + dp(22), self.x + dp(46), self.y + dp(42)]

                # Header Text
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(60)
                    Label:
                        text: 'Готово!'
                        color: color_text_dark
                        font_size: '28sp'
                        bold: True
                        halign: 'center'
                    Label:
                        text: 'Курс успешно завершен.'
                        color: color_text_gray
                        font_size: '16sp'
                        halign: 'center'

                # Stats Cards
                BoxLayout:
                    size_hint_y: None
                    height: dp(100)
                    spacing: dp(16)

                    # Test Score Card
                    Card:
                        orientation: 'vertical'
                        padding: dp(12)
                        Label:
                            id: score_percent
                            text: '0%'
                            color: color_primary
                            font_size: '24sp'
                            bold: True
                        Label:
                            text: 'ТЕСТ'
                            color: color_text_gray
                            font_size: '12sp'
                            bold: True

                    # Reasoning Score Card
                    Card:
                        orientation: 'vertical'
                        padding: dp(12)
                        Label:
                            id: reasoning_score
                            text: '0/10'
                            color: color_orange
                            font_size: '24sp'
                            bold: True
                        Label:
                            text: 'РАССУЖДЕНИЕ'
                            color: color_text_gray
                            font_size: '12sp'
                            bold: True

                # AI Verdict Card
                Card:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height
                    
                    BoxLayout:
                        size_hint_y: None
                        height: dp(24)
                        spacing: dp(8)
                        Label:
                            text: '💬 Вердикт ИИ'
                            color: color_text_dark
                            font_size: '16sp'
                            bold: True
                            halign: 'left'
                            text_size: self.size

                    Label:
                        id: ai_verdict
                        text: '...'
                        color: color_text_gray
                        font_size: '14sp'
                        italic: True
                        text_size: self.width, None
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'

                    Widget:
                        size_hint_y: None
                        height: dp(10)

                    Label:
                        text: 'КАК УЛУЧШИТЬ'
                        color: color_text_gray
                        font_size: '10sp'
                        bold: True
                        size_hint_y: None
                        height: dp(20)
                        halign: 'left'
                        text_size: self.size

                    Label:
                        id: improvement_text
                        text: '...'
                        color: color_primary
                        font_size: '14sp'
                        text_size: self.width, None
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'

                # Error Explanations
                Label:
                    text: 'Работа над ошибками'
                    color: color_text_dark
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

                # Followup Topics
                Label:
                    text: 'Темы для углубления'
                    color: color_text_dark
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

<RoadmapScreen>:
    name: 'roadmap'
    canvas.before:
        Color:
            rgba: color_bg
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: [0, dp(30), 0, 0]
        
        # Header с названием roadmap
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(16), dp(8)]
            canvas.before:
                Color:
                    rgba: 0.15, 0.55, 0.9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            MDIconButton:
                icon: 'arrow-left'
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                size_hint_x: None
                width: dp(48)
                on_release: app.return_from_roadmap()
            
            Label:
                id: roadmap_title
                text: 'Обучающая программа'
                color: 1, 1, 1, 1
                font_size: '20sp'
                bold: True
                halign: 'left'
                valign: 'middle'
                text_size: self.size
        
        # Описание roadmap
        Label:
            id: roadmap_description
            text: 'Выберите узел для начала обучения'
            color: 0.5, 0.5, 0.5, 1
            font_size: '14sp'
            size_hint_y: None
            height: dp(40)
            halign: 'center'
            padding: [dp(16), dp(8)]
        
        # ScrollView с дорожной картой
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            
            BoxLayout:
                id: roadmap_canvas
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [0, dp(20)]
                spacing: 0

<RoadmapNode>:
    size_hint_y: None
    height: dp(180)
    canvas:
        # Вертикальная линия соединения
        Color:
            rgba: 0.9, 0.9, 0.9, 1
        Line:
            points: [self.x + dp(48), self.y, self.x + dp(48), self.top]
            width: dp(3)

    # Левая часть: Иконка
    FloatLayout:
        size_hint: None, 1
        width: dp(100)
        
        # Контейнер иконки (теперь кликабельный)
        ClickableBox:
            pos: root.x + dp(18), root.top - dp(80)
            size_hint: None, None
            size: dp(60), dp(60)
            on_release: root.dispatch('on_action_click') if root.status in ['in_progress', 'completed'] else root.dispatch('on_node_click')
            
            canvas.before:
                # Фон - зеленый если завершен, синий если активен, серый если закрыт
                Color:
                    rgba: (0.3, 0.7, 0.3, 1) if root.status == 'completed' else ((1, 1, 1, 1) if root.status == 'in_progress' else (0.96, 0.96, 0.96, 1))
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(16),]
                
                # Обводка для активного
                Color:
                    rgba: (0.15, 0.55, 0.9, 1) if root.status == 'in_progress' else (0, 0, 0, 0)
                Line:
                    rounded_rectangle: (self.x, self.y, self.width, self.height, dp(16))
                    width: dp(2)
            
            # Сама иконка (текст/эмодзи)
            Label:
                text: '✓' if root.status == 'completed' else root.icon_text
                font_size: '32sp'
                # Белый если завершен, синий если активен, серый если нет
                color: (1, 1, 1, 1) if root.status == 'completed' else ((0.15, 0.55, 0.9, 1) if root.status == 'in_progress' else (0.7, 0.7, 0.7, 1))
                center_x: self.parent.center_x
                center_y: self.parent.center_y

    # Правая часть: Контент
    BoxLayout:
        orientation: 'vertical'
        padding: [0, dp(20), dp(20), dp(10)]
        spacing: dp(5)
        # Начинаем справа от иконки
        pos_hint: {'x': 0}
        
        # Интерактивная область для клика по тексту
        ClickableBox:
            on_release: root.dispatch('on_action_click') if root.status in ['in_progress', 'completed'] else root.dispatch('on_node_click')
            orientation: 'vertical'
            
            # Заголовок
            Label:
                text: root.node_title
                color: (0.1, 0.1, 0.1, 1) if root.status != 'locked' else (0.6, 0.6, 0.6, 1)
                font_size: '17sp'
                bold: True
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1] + dp(5)
                halign: 'left'
            
            # Статус текстом (добавим если нужно, но пока хватит цвета)
            Label:
                text: 'ЗАВЕРШЕНО' if root.status == 'completed' else ('ДОСТУПНО' if root.status == 'in_progress' else 'ЗАБЛОКИРОВАНО')
                color: (0.3, 0.7, 0.3, 1) if root.status == 'completed' else ((0.15, 0.55, 0.9, 1) if root.status == 'in_progress' else (0.6, 0.6, 0.6, 1))
                font_size: '12sp'
                bold: True
                text_size: self.width, None
                size_hint_y: None
                height: dp(15)
                halign: 'left'

            # Описание
            Label:
                text: root.node_description
                color: (0.5, 0.5, 0.5, 1)
                font_size: '13sp'
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'left'
                max_lines: 4
                line_height: 1.2
        
        # Спейсер
        Widget:
            size_hint_y: 1


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
            default_source='trash-can',
            pressed_source='trash-can'
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

class RoadmapCard(ButtonBehavior, BoxLayout):
    """
    Карточка дорожной карты для отображения в списке сохранённых программ.
    
    Атрибуты:
        roadmap_id: ID дорожной карты
        title: Название программы
        description: Краткое описание
    """
    bg_color = ListProperty([0.9, 0.95, 1, 1])
    
    def __init__(self, roadmap_id, title, description, **kwargs):
        super().__init__(**kwargs)
        self.roadmap_id = roadmap_id
        self.title = title
        self.description = description
        self.orientation = 'vertical'
        self.padding = [dp(16), dp(12)]
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(130)
        
        with self.canvas.before:
            self._rect_color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Заголовок и кнопка удаления
        top_row = BoxLayout(size_hint_y=None, height=dp(32))
        
        icon = MDIcon(
            icon="map-marker-path",
            size_hint_x=None,
            width=dp(24),
            theme_text_color="Custom",
            text_color=(0.15, 0.55, 0.9, 1)
        )
        top_row.add_widget(icon)
        
        title_label = Label(
            text=title,
            color=(0.1, 0.1, 0.1, 1),
            font_size='18sp',
            bold=True,
            halign='left',
            valign='middle',
            text_size=(self.width, None),
            padding=[dp(8), 0]
        )
        title_label.bind(size=lambda inst, size: setattr(inst, 'text_size', (size[0], None)))
        top_row.add_widget(title_label)
        
        delete_btn = IconButton(
            size_hint=(None, None),
            size=(dp(26), dp(26)),
            default_source='trash-can',
            pressed_source='trash-can'
        )
        delete_btn.bind(on_release=lambda inst, rid=roadmap_id: App.get_running_app().delete_roadmap(rid))
        top_row.add_widget(delete_btn)
        
        self.add_widget(top_row)
        
        # Описание
        desc_label = Label(
            text=description,
            color=(0.4, 0.4, 0.4, 1),
            font_size='13sp',
            halign='left',
            valign='top',
            text_size=(self.width, None),
            shorten=True,
            shorten_from='right'
        )
        desc_label.bind(size=lambda inst, size: setattr(inst, 'text_size', (size[0], None)))
        self.add_widget(desc_label)
        
        # Инфо о модулях
        modules_label = Label(
            text="Обучающая программа • Просмотр",
            color=(0.15, 0.55, 0.9, 1),
            font_size='12sp',
            bold=True,
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(20),
            text_size=(self.width, None),
        )
        modules_label.bind(size=lambda inst, size: setattr(inst, 'text_size', (size[0], None)))
        self.add_widget(modules_label)

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

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Затемняем цвет при нажатии
            base_color = self.bg_color
            factor = 0.6  # 60% от исходной яркости
            self._rect_color.rgba = (base_color[0] * factor, base_color[1] * factor, 
                                     base_color[2] * factor, base_color[3])
            # Восстанавливаем цвет через 100ms (быстрый импульс)
            Clock.schedule_once(lambda dt: self._restore_color(), 0.1)
        return super().on_touch_down(touch)

    def _restore_color(self):
        """Восстанавливает исходный цвет"""
        self._rect_color.rgba = self.bg_color

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)


class RoundSwitch(ButtonBehavior, Widget):
    """
    Кастомный круглый переключатель (Switch) в современном стиле.
    """
    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(50), dp(28))
        self.bind(active=self._update_canvas, pos=self._update_canvas, size=self._update_canvas)
        
    def on_release(self):
        self.active = not self.active
        
    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Трек (фон)
            if self.active:
                Color(0.15, 0.55, 0.9, 1) # Активный синий
            else:
                Color(0.8, 0.8, 0.8, 1) # Серый неактивный
            
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height/2])
            
            # Большой круглый «палец» (thumb)
            Color(1, 1, 1, 1)
            padding = dp(2)
            thumb_size = self.height - padding * 2
            
            if self.active:
                # Справа
                thumb_x = self.right - thumb_size - padding
            else:
                # Слева
                thumb_x = self.x + padding
                
            Ellipse(pos=(thumb_x, self.y + padding), size=(thumb_size, thumb_size))


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


class IconButton(MDIconButton):
    """
    Кнопка-иконка с поддержкой смены изображения при нажатии.
    
    Используется для небольших действий типа удаления, закрытия и т.д.
    
    Атрибуты:
        default_source: Имя иконки в нормальном состоянии
        pressed_source: Имя иконки при нажатии
    """
    default_source = StringProperty('')
    pressed_source = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_text_color = "Custom"
        self.text_color = (0.2, 0.2, 0.2, 1)
        self.bind(state=self._update_source)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.text_color = (0.2 * 0.6, 0.2 * 0.6, 0.2 * 0.6, 0.8)
            # Восстанавливаем цвет через 100ms (быстрый импульс)
            Clock.schedule_once(lambda dt: setattr(self, 'text_color', (0.2, 0.2, 0.2, 1)), 0.1)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            Animation(opacity=0.6, d=0.05, t='out_quad').start(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        Animation(opacity=1.0, d=0.1, t='out_quad').start(self)
        return super().on_touch_up(touch)

    def _update_source(self, instance, value):
            self.icon = self.default_source

    def on_default_source(self, instance, value):
        """Устанавливает иконку по умолчанию"""
        if self.state != 'down' and value:
            self.icon = value
    
    def _update_source(self, instance, state):
        """Обновляет иконку при изменении состояния"""
        if state == 'down' and self.pressed_source:
            self.icon = self.pressed_source
        elif self.default_source:
            self.icon = self.default_source


class GamificationSystem:
    """
    Система геймификации для отслеживания прогресса пользователя.
    
    Отслеживает:
    - Общий XP (опыт)
    - Уровень пользователя
    - Streak (дни подряд использования)
    - Имя пользователя
    
    XP начисляется за:
    - Чтение теории: 10 XP
    - Правильный ответ в MC тесте: 5 XP
    - Правильный ответ (7-10 баллов) в развёрнутом ответе: 10 XP
    - Частично правильный (4-6 баллов): 5 XP
    """
    XP_PER_LEVEL = 300
    
    def __init__(self, storage_path):
        self.storage_path = storage_path
        self.data = self._load()
        
    def _load(self):
        """Загружает данные из файла"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'username': 'Студент',
            'xp': 0,
            'level': 1,
            'streak': 0,
            'last_activity_date': None,
            'completed_courses': []
        }
    
    def save(self):
        """Сохраняет данные в файл"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[GAMIFICATION] Ошибка сохранения: {e}")
    
    @property
    def username(self):
        return self.data.get('username', 'Студент')
    
    @username.setter
    def username(self, value):
        self.data['username'] = value
        self.save()
    
    @property
    def xp(self):
        return self.data.get('xp', 0)
    
    @property
    def level(self):
        return self.data.get('level', 1)
    
    @property
    def streak(self):
        return self.data.get('streak', 0)
    
    def add_xp(self, amount, reason=""):
        """Добавляет XP и проверяет повышение уровня"""
        self.data['xp'] = self.data.get('xp', 0) + amount
        self._check_level_up()
        self._update_streak()
        self.save()
        print(f"[GAMIFICATION] +{amount} XP за {reason}. Всего XP: {self.xp}, Уровень: {self.level}")
    
    def _check_level_up(self):
        """Проверяет и повышает уровень при достаточном XP"""
        xp_for_next_level = self._xp_for_level(self.level + 1)
        while self.xp >= xp_for_next_level:
            self.data['level'] = self.data.get('level', 1) + 1
            print(f"[GAMIFICATION] 🎉 Новый уровень: {self.level}!")
            xp_for_next_level = self._xp_for_level(self.level + 1)
    
    def _xp_for_level(self, level):
        """Возвращает XP необходимый для достижения уровня"""
        level_index = max(0, level - 1)
        return level_index * self.XP_PER_LEVEL
    
    def get_level_progress(self):
        """Возвращает прогресс до следующего уровня в процентах"""
        current_level_xp = self._xp_for_level(self.level)
        next_level_xp = self._xp_for_level(self.level + 1)
        xp_in_level = self.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        if xp_needed <= 0:
            return 100
        progress = int((xp_in_level / xp_needed) * 100)
        return max(0, min(100, progress))
    
    @property
    def level_progress(self):
        """Свойство для удобного доступа к прогрессу"""
        return self.get_level_progress()
    
    def _update_streak(self):
        """Обновляет streak (дни подряд)"""
        from datetime import datetime, timedelta
        today = datetime.now().date().isoformat()
        last_date = self.data.get('last_activity_date')
        
        if last_date == today:
            # Уже был активен сегодня
            return
        
        if last_date:
            last_dt = datetime.fromisoformat(last_date).date()
            today_dt = datetime.now().date()
            days_diff = (today_dt - last_dt).days
            
            if days_diff == 1:
                # Следующий день подряд
                self.data['streak'] = self.data.get('streak', 0) + 1
            elif days_diff > 1:
                # Пропущен день - сброс
                self.data['streak'] = 1
        else:
            # Первый день
            self.data['streak'] = 1
        
        self.data['last_activity_date'] = today

    def _update_source(self, instance, state):
        """Меняет иконку в зависимости от состояния кнопки"""
        if state == 'down' and self.pressed_source:
            self.icon = self.pressed_source
        elif self.default_source:
            self.icon = self.default_source


class IconToggleButton(ButtonBehavior, MDIcon):
    """
    Кнопка-иконка с поддержкой переключения (toggle).
    
    Используется в нижней навигации для переключения между табами.
    Меняет цвет при активации.
    
    Атрибуты:
        icon_source: Имя иконки
        target_screen: Имя целевого экрана для переключения
        active_color: Цвет иконки в активном состоянии (синий)
        inactive_color: Цвет иконки в неактивном состоянии (серый)
    """
    icon_source = StringProperty('')
    target_screen = StringProperty('')
    active_color = ListProperty([0.15, 0.55, 0.9, 1])
    inactive_color = ListProperty([0.5, 0.5, 0.5, 1])
    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_text_color = "Custom"
        self.text_color = self.inactive_color
        self.halign = "center"
        self.valign = "middle"
        self.font_size = "28sp"
        self.bind(active=self._update_style)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.text_color = (self.text_color[0] * 0.7, self.text_color[1] * 0.7, 
                               self.text_color[2] * 0.7, 0.9)
            # Восстанавливаем цвет через 100ms (быстрый импульс)
            Clock.schedule_once(lambda dt: self._update_style(self, self.active), 0.1)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)

    def on_icon_source(self, instance, value):
        """Устанавливает иконку"""
        if value:
            self.icon = value

    def _update_style(self, instance, value):
        """Меняет цвет иконки в зависимости от active"""
        if value:
            self.text_color = self.active_color  # Синий когда активна
        else:
            self.text_color = self.inactive_color  # Серый когда неактивна

    def on_release(self):
        """Переключает выделение при нажатии. Повторный клик НЕ снимает выделение."""
        app = App.get_running_app()
        try:
            main_screen = app.root.get_screen('main')
        except Exception:
            main_screen = None

        # Если уже активен — ничего не делаем (оставляем выделение)
        if self.active:
            return

        # Снимаем выделение с других кнопок
        if main_screen:
            for btn_id in ('nav_saved', 'nav_search', 'nav_chat', 'nav_settings'):
                try:
                    btn = main_screen.ids.get(btn_id)
                    if btn and btn is not self and hasattr(btn, 'active'):
                        btn.active = False
                except Exception:
                    pass

        # Активируем себя и переключаем экран
        self.active = True
        if self.target_screen and main_screen:
            try:
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
    default_color = (0.96, 0.96, 0.96, 1)
    selected_color = (0.85, 0.92, 1, 1)
    text_color = (0.2, 0.2, 0.2, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = self.text_color
        self.halign = 'left'
        self.valign = 'middle'
        self.padding = [dp(16), dp(12)]
        with self.canvas.before:
            self._bg_color = Color(*self.default_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(texture_size=self._update_height)

    def _update_rect(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self.text_size = (self.width - dp(32), None)

    def _update_height(self, *args):
        self.height = max(dp(60), self.texture_size[1] + dp(30))

    def set_selected(self, selected: bool):
        """Устанавливает выбранное состояние кнопки"""
        self._bg_color.rgba = self.selected_color if selected else self.default_color
        # Text color remains dark for readability on light blue
        self.color = (0.1, 0.3, 0.6, 1) if selected else self.text_color


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
        # The `network_status` widget may have been removed from the header.
        # Guard access to avoid AttributeError when self.ids doesn't contain it.
        if 'network_status' not in self.ids:
            # Nothing to update in the UI; just return silently.
            return

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
    """Главный экран профиля с кнопками перехода к спискам"""
    pass


class RoadmapsListScreen(Screen):
    """Экран со списком всех программ обучения (дорожных карт)"""
    pass


class LessonsListScreen(Screen):
    """Экран со списком всех одиночных уроков"""
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


class ClickableBox(ButtonBehavior, BoxLayout):
    """
    Layout that behaves like a button (clickable).
    """
    pass


class RoadmapNode(BoxLayout):
    """
    Узел дорожной карты обучения (новый дизайн).
    """
    node_id = StringProperty('')
    node_title = StringProperty('Узел')
    node_description = StringProperty('')
    node_topics_text = StringProperty('')
    node_type = StringProperty('main')
    status = StringProperty('not_started')  # 'locked', 'not_started', 'in_progress', 'completed'
    icon_text = StringProperty('📚')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        # Events
        self.register_event_type('on_node_click')
        self.register_event_type('on_action_click')

    def on_node_click(self, *args):
        pass

    def on_action_click(self, *args):
        pass

    def on_status(self, instance, value):
        pass


class RoadmapScreen(Screen):
    """
    Экран визуализации обучающей программы (roadmap).
    
    Отображает дорожную карту с узлами обучения и связями между ними.
    """
    roadmap_data = None  # Хранит данные дорожной карты
    
    def on_enter(self):
        """Загружаем и отображаем дорожную карту при входе на экран"""
        app = App.get_running_app()
        if hasattr(app, 'current_roadmap_id') and app.current_roadmap_id:
            # Загружаем свежие данные из хранилища (с учетом обновленного прогресса)
            roadmap = app.roadmap_storage.get(app.current_roadmap_id)
            if roadmap:
                app.current_roadmap = roadmap
                self.load_roadmap(roadmap)
        elif hasattr(app, 'current_roadmap') and app.current_roadmap:
            self.load_roadmap(app.current_roadmap)
    
    def load_roadmap(self, roadmap_data):
        """Загружает и отображает дорожную карту"""
        self.roadmap_data = roadmap_data
        
        # Обновляем заголовок и описание
        self.ids.roadmap_title.text = roadmap_data.get('title', 'Обучающая программа')
        desc = roadmap_data.get('description', '')
        time_est = roadmap_data.get('estimated_time', '')
        if time_est:
            desc += f"\n⏱ {time_est}"
        self.ids.roadmap_description.text = desc
        
        # Очищаем canvas
        canvas = self.ids.roadmap_canvas
        canvas.clear_widgets()
        
        modules = roadmap_data.get('modules', [])
        if not modules:
            canvas.add_widget(Label(
                text='Нет модулей для отображения',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            ))
            return
        
        # Сортируем модули по order
        modules = sorted(modules, key=lambda m: m.get('order', 999))
        
        # Гарантируем наличие строковых ID у каждого модуля
        for idx, m in enumerate(modules):
            if not m.get('id'):
                m['id'] = f'module_{idx}'
            else:
                m['id'] = str(m['id']) # Приводим к строке
        
        # Вычисляем позиции модулей
        self._create_roadmap_layout(canvas, modules)
    
    def _create_roadmap_layout(self, canvas, modules):
        """Создаёт вертикальный список модулей (Timeline design)"""
        # Параметры
        module_height = dp(180)  # Высота одного блока
        
        # Получаем прогресс из данных роадмапы и приводим ключи к строкам
        raw_progress = self.roadmap_data.get('progress', {})
        progress = {str(k): v for k, v in raw_progress.items()}
        
        # Создаём модули вертикально
        last_completed = True # Первый узел всегда доступен, если предыдущий завершен
        
        for idx, module in enumerate(modules):
            m_id = str(module.get('id', ''))
            m_progress = progress.get(m_id, {})
            is_completed = m_progress.get('completed', False)
            
            # Format description from topics
            topics = module.get('topics', [])
            desc_text = module.get('description', '')
            if not desc_text and topics:
                desc_text = ", ".join(str(t) for t in topics)
            
            # Логика статуса:
            # 1. Если завершен -> completed
            # 2. Если не завершен, но предыдущий завершен -> in_progress (доступен)
            # 3. Иначе -> locked
            if is_completed:
                status = 'completed'
            elif last_completed:
                status = 'in_progress'
            else:
                status = 'locked'
            
            # Обновляем флаг для следующего узла
            last_completed = is_completed
            
            # Создаём виджет модуля через BoxLayout
            node = RoadmapNode(
                node_id=m_id,
                node_title=module.get('title', 'Модуль'),
                node_description=desc_text,
                status=status,
                icon_text=str(idx + 1),
                size_hint_y=None,
                height=module_height
            )
            
            # При клике - показываем детали (через эвент)
            node.bind(on_node_click=lambda instance, m=module: self.on_node_click(m))
            node.bind(on_action_click=lambda instance, m=module: self.start_module(m))
            
            canvas.add_widget(node)
            
    def start_module(self, module):
        """Запуск модуля - загружает из памяти или генерирует новый"""
        # Close popup first
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
        
        app = App.get_running_app()
        difficulty = module.get('difficulty', 'легкий')
        topic = module.get('title', '')
        
        # Запоминаем текущий узел для прогресса (приводим ID к строке)
        app.current_node_id = str(module.get('id', ''))
        
        # Проверяем, есть ли уже такой курс в памяти (сохраненных)
        # Если есть - сразу открываем, если нет - генерируем
        saved_course = app.storage.find(topic, difficulty)
        
        if saved_course:
            app.log(f"Модуль '{topic}' ({difficulty}) найден в сохраненных. Запускаем...")
            app.start_saved_course(saved_course)
        else:
            app.log(f"Модуль '{topic}' ({difficulty}) не найден. Начинаем генерацию...")
            # Переходим на экран загрузки
            app.root.current = 'loading'
            # Переход к генерации в отдельном потоке
            threading.Thread(target=app.generate_quiz_thread, args=(topic, difficulty), daemon=True).start()
    
    def on_node_click(self, module):
        """Обработчик клика на узел - показывает детали модуля"""
        self.show_module_details(module)
    
    def show_module_details(self, module):
        """Показывает детали модуля и предлагает начать обучение"""
        app = App.get_running_app()
        
        # Формируем текст с деталями
        details = f"📚 {module.get('title', 'Модуль')}\n\n"
        
        description = module.get('description', '')
        if description:
            details += f"{description}\n\n"
        
        topics = module.get('topics', [])
        if topics:
            details += "📝 Что изучим:\n"
            for topic in topics:
                details += f"  • {topic}\n"
            details += "\n"
        
        difficulty = module.get('difficulty', '')
        if difficulty:
            details += f"🎯 Сложность: {difficulty}\n"
        
        hours = module.get('estimated_hours', 0)
        if hours:
            details += f"⏱ Время: ~{hours} часов\n"
        
        prereqs = module.get('prerequisites', [])
        if prereqs:
            details += f"\n⚠ Требуется пройти: {', '.join(prereqs)}\n"
        
        if not description and not topics and not difficulty and not hours:
            details += "Нажмите 'Начать изучение' чтобы\nсгенерировать курс по этой теме.\n"
        
        # Создаём popup с деталями
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        scroll = ScrollView(size_hint_y=0.7)
        details_label = Label(
            text=details,
            markup=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        details_label.bind(
            texture_size=lambda inst, size: setattr(inst, 'height', size[1] + dp(20))
        )
        details_label.bind(
            width=lambda inst, w: setattr(inst, 'text_size', (w - dp(40), None))
        )
        scroll.add_widget(details_label)
        content.add_widget(scroll)
        
        # Кнопки действий
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        start_btn = RoundedButton(
            text='Начать изучение',
            bg_color=(0.15, 0.55, 0.9, 1),
            size_hint_x=0.6
        )
        
        close_btn = RoundedButton(
            text='Закрыть',
            bg_color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.4
        )
        
        buttons.add_widget(start_btn)
        buttons.add_widget(close_btn)
        content.add_widget(buttons)
        
        popup = ModalView(size_hint=(0.9, 0.7), background_color=(0, 0, 0, 0))
        popup_box = BoxLayout(orientation='vertical')
        popup_box.canvas.before.clear()
        with popup_box.canvas.before:
            Color(0.95, 0.93, 0.90, 1)
            popup_box._rect = RoundedRectangle(pos=popup_box.pos, size=popup_box.size, radius=[dp(20)])
        popup_box.bind(pos=lambda inst, val: setattr(inst._rect, 'pos', val))
        popup_box.bind(size=lambda inst, val: setattr(inst._rect, 'size', val))
        
        popup_box.add_widget(content)
        popup.add_widget(popup_box)
        
        # Действия кнопок
        close_btn.bind(on_release=lambda x: popup.dismiss())
        start_btn.bind(on_release=lambda x: self._start_module_learning(module, popup))
        
        popup.open()
    
    def _start_module_learning(self, module, popup):
        """Начинает обучение по выбранному модулю"""
        popup.dismiss()
        app = App.get_running_app()
        
        # Используем название модуля как тему
        topic = module.get('title', 'Тема')
        difficulty = module.get('difficulty', 'средний')
        
        # Запоминаем текущий узел для прогресса (приводим к строке)
        m_id = str(module.get('id', ''))
        app.current_node_id = m_id
        
        # Сохраняем информацию о модуле для отслеживания прогресса
        if not hasattr(app, 'roadmap_progress'):
            app.roadmap_progress = {}
        app.roadmap_progress[m_id] = {
            'status': 'in_progress',
            'current_topic': topic,
            'completed_topics': []
        }
        
        # Переходим на экран загрузки
        app.root.current = 'loading'
        
        # Запускаем генерацию
        threading.Thread(
            target=app.generate_quiz_thread,
            args=(topic, difficulty),
            daemon=True
        ).start()


class ChatBubble(Label):
    """Виджет сообщения в чате"""
    bg_color = ListProperty([0.95, 0.95, 0.95, 1])

class AIAssistantPopup(ModalView):
    """
    Всплывающее окно с ИИ-ассистентом для вопросов по теории.
    """
    theory_text = StringProperty('')
    history = ListProperty([])

    def __init__(self, theory_text, **kwargs):
        super().__init__(**kwargs)
        self.theory_text = theory_text
        self.history = []
        # Try to load saved history for this material/topic
        try:
            app = App.get_running_app()
            # Use a short key derived from the beginning of theory_text or app.last_material
            key = None
            if getattr(app, 'last_material', None):
                key = app.last_material.strip()[:200]
            if not key:
                key = (theory_text or '')[:200]
            # normalize key
            key = key.replace('\n', ' ').strip()
            self._storage_key = key
            # Ensure ai_chat_history exists on app
            if not hasattr(app, 'ai_chat_history'):
                app.ai_chat_history = {}
            saved = app.ai_chat_history.get(self._storage_key)
            if saved and isinstance(saved, list):
                # load into history and render
                self.history = saved.copy()
        except Exception as e:
            # Log the exception to the app log for easier debugging
            try:
                app = App.get_running_app()
                app.log(f"Ошибка при загрузке истории AI-помощника: {e}\n{tb_module.format_exc()}")
            except Exception:
                print(f"[MAIN] Ошибка при загрузке истории AI-помощника: {e}")
            self._storage_key = None

    def on_open(self):
        """When popup opens, render saved history messages into chat UI"""
        try:
            # Small delay to ensure ids are ready
            def render(dt):
                for msg in self.history:
                    role = msg.get('role')
                    content = msg.get('content', '')
                    self.add_message(content, is_user=(role == 'user'))
            Clock.schedule_once(render, 0.01)
            # Focus on input field
            Clock.schedule_once(lambda dt: self.ids.input_field.focus, 0.1)
        except Exception as e:
            try:
                App.get_running_app().log(f"Ошибка в on_open: {e}")
            except:
                print(f"[MAIN] Ошибка в on_open: {e}")

    def send_message(self):
        txt_input = self.ids.input_field
        question = txt_input.text.strip()
        if not question:
            return

        # Добавляем вопрос пользователя
        self.add_message(question, is_user=True)
        self.history.append({"role": "user", "content": question})
        # Persist immediately
        try:
            app = App.get_running_app()
            if getattr(self, '_storage_key', None):
                app.ai_chat_history[self._storage_key] = self.history.copy()
                app._save_ai_chat_history()
        except Exception:
            pass
        txt_input.text = ''

        # Показываем индикатор загрузки
        self.loading_bubble = self.add_message("Анализирую...", is_user=False)
        
        # Запускаем в потоке
        threading.Thread(target=self._get_answer, args=(question,), daemon=True).start()

    def _get_answer(self, question):
        app = App.get_running_app()
        api_key = None
        
        if hasattr(app, 'settings_store') and app.settings_store.exists('api'):
             data = app.settings_store.get('api')
             api_key = data.get('api_key', data.get('key'))
        
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
            
        # Формируем историю для контекста
        # Добавляем системный промпт с теорией
        context_history = [
            {
                "role": "system",
                "content": f"Ты — полезный ассистент учителя. Твоя задача — отвечать на вопросы студента ТОЛЬКО по приведенному ниже учебному материалу. Если вопрос не связан с материалом, вежливо укажи на это.\n\nМАТЕРИАЛ КУРСА:\n{self.theory_text[:5000]}"
            }
        ]
        
        # Добавляем предыдущие сообщения (исключая последнее, которое передается как message)
        # self.history уже содержит текущий вопрос пользователя последним элементом
        if len(self.history) > 1:
            context_history.extend(self.history[:-1])
            
        response = chat_with_image(question, None, history=context_history, api_key=api_key)
        
        answer_text = ""
        if 'error' in response:
            answer_text = f"Ошибка: {response['error']}"
        else:
            answer_text = response.get('content', 'Нет ответа')
        
        # Обновляем UI в главном потоке
        Clock.schedule_once(lambda dt: self._update_answer(answer_text))

    def _update_answer(self, answer):
        # Удаляем "Анализирую..."
        if hasattr(self, 'loading_bubble'):
             try:
                self.ids.chat_list.remove_widget(self.loading_bubble.parent)
             except:
                pass
        
        self.add_message(answer, is_user=False)
        self.history.append({"role": "assistant", "content": answer})
        # Persist history after assistant reply
        try:
            app = App.get_running_app()
            if getattr(self, '_storage_key', None):
                app.ai_chat_history[self._storage_key] = self.history.copy()
                app._save_ai_chat_history()
        except Exception:
            pass

    def on_dismiss(self):
        """Save history when popup is closed."""
        try:
            app = App.get_running_app()
            if getattr(self, '_storage_key', None):
                app.ai_chat_history[self._storage_key] = self.history.copy()
                app._save_ai_chat_history()
        except Exception:
            pass

    def add_message(self, text, is_user):
        """Добавляет сообщение в чат"""
        
        # Контейнер для выравнивания
        bubble_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            padding=[dp(10), dp(5)],
            spacing=dp(5)
        )
        
        if is_user:
            bubble_box.add_widget(Widget()) # Spacer слева
            
        if is_user:
            color = [0.15, 0.55, 0.9, 1]
            text_color = (1, 1, 1, 1)
        else:
            color = [1, 1, 1, 1]
            text_color = (0.09, 0.12, 0.17, 1)

        lbl = ChatBubble(
            text=text,
            bg_color=color,
            size_hint_x=None,
            width=min(dp(320), Window.width * 0.72),
            color=text_color
        )
        
        bubble_box.add_widget(lbl)
        
        if not is_user:
            bubble_box.add_widget(Widget()) # Spacer справа

        # Высота контейнера зависит от высоты бабла
        def update_height(instance, value):
            bubble_box.height = value + dp(10)
        lbl.bind(height=update_height)
            
        self.ids.chat_list.add_widget(bubble_box)
        
        # Прокрутка вниз
        def scroll_to_bottom(dt):
            self.ids.scroll_view.scroll_to(bubble_box)
        Clock.schedule_once(scroll_to_bottom, 0.1)
        
        return lbl


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

    def _add_paragraph_label(self, container, text):
        """Вспомогательный метод для добавления одной метки параграфа с правильными отступами"""
        # Очистка от неподдерживаемых тегов типа [p], [/p] и Markdown остатков
        import re
        text = re.sub(r'\[/?p\]', '', text)
        text = text.replace('**', '').replace('###', '').replace('##', '')
        
        if not text.strip():
            return
        lbl = Label(
            text=text,
            color=(0.15, 0.15, 0.15, 1),
            font_size='16sp',
            size_hint_y=None,
            halign='left',
            valign='top',
            markup=True,
            padding=[dp(8), dp(2)]
        )
        # Динамическая привязка размеров
        lbl.bind(width=lambda l, w: setattr(l, 'text_size', (w - dp(16), None)))
        lbl.bind(texture_size=lambda l, s: setattr(l, 'height', s[1] + dp(4)))
        container.add_widget(lbl)

    def on_theory_content(self, instance, value):
        """Парсит теорию и создаёт компактные виджеты для удобного чтения"""
        if 'theory_container' not in self.ids:
            return
            
        container = self.ids.theory_container
        container.clear_widgets()
        
        if not value:
            return
            
        # Разбиваем текст по переносам строк
        raw_lines = value.split('\n')
        
        for line in raw_lines:
            line = line.strip()
            if not line:
                # Добавляем пустой спейсер для визуального разделения
                container.add_widget(Widget(size_hint_y=None, height=dp(8)))
                continue

            # Если строка слишком длинная (стена текста), разбиваем её принудительно
            if len(line) > 800:
                words = line.split(' ')
                current_chunk = []
                current_len = 0
                
                for word in words:
                    current_chunk.append(word)
                    current_len += len(word) + 1
                    if current_len > 550: # Оптимальный размер "короткого" абзаца
                        self._add_paragraph_label(container, ' '.join(current_chunk))
                        current_chunk = []
                        current_len = 0
                
                if current_chunk:
                    self._add_paragraph_label(container, ' '.join(current_chunk))
            else:
                # Обычная строка
                self._add_paragraph_label(container, line)

    def open_ai_assistant(self):
        """Открывает окно диалога с ИИ"""
        try:
            popup = AIAssistantPopup(theory_text=self.theory_content)
            popup.open()
        except Exception as e:
            # Log and show a small error popup so user knows what happened
            try:
                App.get_running_app().log(f"Ошибка при открытии AI-попапа: {e}\n{tb_module.format_exc()}")
            except Exception:
                print(f"[MAIN] Ошибка при открытии AI-попапа: {e}")
            # Show a simple message to user
            try:
                mv = ModalView(size_hint=(0.8, None), height=dp(140))
                box = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
                box.add_widget(Label(text='Не удалось открыть ассистента. Попробуйте позже.', halign='center'))
                btn = Button(text='Закрыть', size_hint=(None, None), size=(dp(120), dp(40)))
                btn.bind(on_release=lambda *_: mv.dismiss())
                box.add_widget(Widget())
                box.add_widget(btn)
                mv.add_widget(box)
                mv.open()
            except Exception:
                pass


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
        app = App.get_running_app()
        if self.selected == q['answer']:
            self.result_text = 'Правильно! ✓'
            self.score += 1
            # Начисляем XP за правильный ответ
            app.gamification.add_xp(5, "правильный ответ в тесте")
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

    def set_test_score(self, percent):
        if hasattr(self.ids, 'score_percent'):
            self.ids.score_percent.text = f"{percent}%"

    def set_reasoning_score(self, score, total):
        if hasattr(self.ids, 'reasoning_score'):
            self.ids.reasoning_score.text = f"{score}/{total}"

    def set_ai_verdict(self, text):
        if hasattr(self.ids, 'ai_verdict'):
            self.ids.ai_verdict.text = f'"{text}"' if text else '"Нет данных"'

    def set_improvement(self, text):
        if hasattr(self.ids, 'improvement_text'):
            self.ids.improvement_text.text = text or "Нет рекомендаций"

    def set_score(self, score, total, percent):
        """Устанавливает текст с общим результатом (Legacy support)"""
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

        # Добавляем кнопку возврата в меню в конце списка
        try:
            from kivy.uix.boxlayout import BoxLayout
            app = App.get_running_app()
            is_roadmap = hasattr(app, 'current_roadmap_id') and app.current_roadmap_id is not None
            
            btn_box = BoxLayout(size_hint_y=None, height=dp(56), padding=[0, dp(8)])
            btn_text = 'ВЕРНУТЬСЯ В ПРОГРАММУ' if is_roadmap else 'ВЕРНУТЬСЯ В МЕНЮ'
            
            return_btn = RoundedButton(
                text=btn_text, 
                size_hint=(1, None), 
                height=dp(40), 
                bg_color=(0.15, 0.55, 0.9, 1), 
                color=(1,1,1,1)
            )
            
            def _on_return(inst):
                app = App.get_running_app()
                if app:
                    if is_roadmap:
                        app.root.current = 'roadmap'
                    else:
                        app.exit_to_main()
            
            return_btn.bind(on_release=_on_return)
            btn_box.add_widget(return_btn)
            layout.add_widget(btn_box)
        except Exception as e:
            self.log(f"Failed to add return button: {e}")

    def on_scroll_y(self, scroll_y):
        # show navigation when scrolled to bottom (scroll_y near 0)
        threshold = 0.05
        nav_should_show = scroll_y <= threshold
        if self.nav_visible != nav_should_show:
            self.nav_visible = nav_should_show


class ChatScreen(Screen):
    chat_history = ListProperty([])

    def send_message(self):
        text_input = self.ids.message_input
        message = text_input.text.strip()
        
        if not message:
            return

        self.add_message(message, "user")
        
        text_input.text = ""
        # Иконка автоматически сбрасывается на default_source
        
        threading.Thread(target=self._send_request_thread, args=(message,)).start()

    def _send_request_thread(self, message):
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
        response = chat_with_image(message, None, history=history, api_key=api_key)
        
        Clock.schedule_once(lambda dt: self.on_response(response))

    def on_response(self, response):
        if 'error' in response:
            self.add_message(f"Ошибка: {response['error']}", "system")
        else:
            self.add_message(response['content'], "assistant")

    def add_message(self, text, role):
        """Add a text-only message to the chat history and render it.

        The app no longer supports image attachments; this function
        renders only the text part of messages.
        """
        self.chat_history.append({'role': role, 'text': text})

        # Контейнер для сообщения
        msg_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=[10, 10], spacing=5)

        # Фон сообщения (визуальное выделение)
        with msg_box.canvas.before:
            Color(*((0.8, 0.9, 1, 1) if role == 'user' else (1, 1, 1, 1)))
            RoundedRectangle(pos=msg_box.pos, size=msg_box.size, radius=[10])

        # Обновление фона при изменении размера/позиции
        def update_rect(instance, value):
            # children layout may vary between Kivy versions; try-safe update
            try:
                instance.canvas.before.children[2].pos = instance.pos
                instance.canvas.before.children[2].size = instance.size
            except Exception:
                pass

        msg_box.bind(pos=update_rect, size=update_rect)

        # Создаём метку с текстом сообщения
        label_kwargs = {'text': text or '', 'size_hint_y': None, 'color': (0, 0, 0, 1), 'markup': True}

        # Decide whether to use emoji font for this specific message.
        # If the text contains Cyrillic characters, prefer the default font
        # to ensure Russian renders correctly. Use emoji font only when
        # message contains emoji and no Cyrillic.
        def _is_emoji(cp):
            return (
                0x1F600 <= cp <= 0x1F64F or
                0x1F300 <= cp <= 0x1F5FF or
                0x1F680 <= cp <= 0x1F6FF or
                0x1F1E6 <= cp <= 0x1F1FF or
                0x2600 <= cp <= 0x26FF or
                0x2700 <= cp <= 0x27BF or
                0x1F900 <= cp <= 0x1F9FF or
                0xFE00 <= cp <= 0xFE0F
            )

        txt = text or ''
        has_cyr = any(0x0400 <= ord(ch) <= 0x04FF for ch in txt)
        has_emoji = any(_is_emoji(ord(ch)) for ch in txt)
        if EMOJI_FONT_PATH and has_emoji and not has_cyr:
            label_kwargs['font_name'] = EMOJI_FONT_PATH

        lbl = Label(**label_kwargs)
        lbl.bind(width=lambda *x: setattr(lbl, 'text_size', (lbl.width, None)))

        # Когда текст прорендерится, пересчитаем высоту контейнера
        def update_height(instance, value):
            h = dp(20)
            for child in msg_box.children:
                h += child.height + msg_box.spacing
            msg_box.height = h

        lbl.bind(texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1]))
        lbl.bind(texture_size=update_height)

        msg_box.add_widget(lbl)

        # Обертка для выравнивания
        wrapper = AnchorLayout(anchor_x='right' if role == 'user' else 'left', size_hint_y=None)
        wrapper.add_widget(msg_box)

        # Связываем высоту обертки с высотой сообщения
        msg_box.bind(height=lambda *x: setattr(wrapper, 'height', msg_box.height))

        self.ids.chat_list.add_widget(wrapper)

class MyApp(MDApp):
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
        learning_mode: Режим обучения ('single' или 'roadmap')
        storage: CourseStorage для сохранения курсов
        settings_store: JsonStore для настроек пользователя
        open_questions_cache: Кеш открытых вопросов для быстрого доступа
        mc_test_score/mc_test_total: Результаты MC теста для финального отчёта
        preloaded_open_questions: Предзагруженные открытые вопросы
    """
    difficulty = StringProperty('легкий')
    learning_mode = StringProperty('single')

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
            # Load AI chat histories
            self.ai_chat_history_path = os.path.join(data_dir, 'ai_chat_history.json')
            self.ai_chat_history = self._load_ai_chat_history()
            
            # Инициализация системы геймификации
            self.gamification_path = os.path.join(data_dir, 'gamification.json')
            self.gamification = GamificationSystem(self.gamification_path)
            
            print(f"[MAIN] courses_path: {courses_path}")
            print(f"[MAIN] settings_path: {settings_path}")
            
            # Создаём хранилище курсов
            print("[MAIN] Creating CourseStorage...")
            self.storage = CourseStorage(filename=courses_path)
            self._last_saved_meta = None
            print("[MAIN] CourseStorage created")
            
            # Создаём хранилище roadmaps
            print("[MAIN] Creating RoadmapStorage...")
            roadmaps_path = os.path.join(data_dir, 'roadmaps.json')
            self.roadmap_storage = RoadmapStorage(filename=roadmaps_path)
            self.current_roadmap_id = None  # Текущая активная roadmap
            print("[MAIN] RoadmapStorage created")
            
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

    def on_start(self):
        super().on_start()
        Clock.schedule_once(self._refresh_initial_ui, 0)

    def _refresh_initial_ui(self, dt):
        try:
            self.load_settings_ui()
            self.update_profile_stats()
        except Exception as e:
            print(f"Error refreshing initial UI: {e}")

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

    def _load_ai_chat_history(self):
        """Load persistent AI chat histories from disk.

        Structure: {"theory_id_or_topic": [ {"role":"user|assistant|system","content":"..."}, ... ] }
        """
        path = getattr(self, 'ai_chat_history_path', None)
        if not path:
            return {}
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            self.log(f"Ошибка загрузки истории общения ИИ: {e}")
        return {}

    def _save_ai_chat_history(self):
        path = getattr(self, 'ai_chat_history_path', None)
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.ai_chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"Ошибка сохранения истории общения ИИ: {e}")

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
        try:
            main_screen = self.root.get_screen('main')
            settings_screen = main_screen.ids.tab_manager.get_screen('settings')
            
            if self.settings_store.exists('api'):
                # Загружаем API ключ из настроек
                data = self.settings_store.get('api')
                key = data.get('api_key', data.get('key', ''))
                settings_screen.ids.api_key_input.text = key
            
            # Загружаем интересы
            if self.settings_store.exists('personalization'):
                p_data = self.settings_store.get('personalization')
                settings_screen.ids.interests_input.text = p_data.get('interests', '')
                settings_screen.ids.personalization_switch.active = p_data.get('enabled', False)
            
            # Загружаем данные геймификации
            settings_screen.ids.username_input.text = self.gamification.username
        except Exception as e:
            print(f"Error loading settings UI: {e}")
    
    def save_settings(self):
        """
        Сохраняет настройки из UI в хранилище.
        
        Показывает статус сохранения пользователю.
        """
        try:
            main_screen = self.root.get_screen('main')
            settings_screen = main_screen.ids.tab_manager.get_screen('settings')
            key = settings_screen.ids.api_key_input.text.strip()
            username = settings_screen.ids.username_input.text.strip()
            interests = settings_screen.ids.interests_input.text.strip()
            personalization_enabled = settings_screen.ids.personalization_switch.active
            
            # Сохраняем API ключ
            self.settings_store.put('api', api_key=key)
            
            # Сохраняем персонализацию
            self.settings_store.put('personalization', interests=interests, enabled=personalization_enabled)
            self.log(f"Settings saved: Personalization: {'ENABLED' if personalization_enabled else 'DISABLED'}, Interests: '{interests}'")
            
            # Сохраняем имя пользователя
            if username:
                self.gamification.username = username
            
            # Обновляем UI профиля
            self.load_settings_ui()
            
            # Показываем сообщение об успехе
            from kivymd.toast import toast
            toast("Настройки сохранены!")
        except Exception as e:
            print(f"Error saving settings: {e}")
            try:
                from kivymd.toast import toast
                toast(f"Ошибка: {str(e)[:30]}")
            except:
                pass

    def set_difficulty(self, level):
        self.difficulty = level
    
    def set_learning_mode(self, mode):
        """Устанавливает режим обучения: 'single' или 'roadmap'"""
        self.learning_mode = mode
        self.log(f"Learning mode set to: {mode}")

    def show_mode_info(self):
        """Показывает информацию о режимах обучения"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        info_text = (
            "[b]Программа обучения:[/b]\n"
            "Создается пошаговый план из нескольких блоков для глубокого погружения в тему.\n\n"
        )
        
        label = Label(
            text=info_text, 
            markup=True, 
            color=(0.2, 0.2, 0.2, 1),
            text_size=(dp(240), None),
            halign='left',
            valign='top'
        )
        label.bind(texture_size=lambda inst, size: setattr(inst, 'height', size[1]))
        
        content.add_widget(label)
        
        close_btn = RoundedButton(
            text='ПОНЯТНО',
            size_hint=(None, None),
            size=(dp(140), dp(44)),
            pos_hint={'center_x': 0.5}
        )
        
        view = ModalView(
            size_hint=(None, None),
            size=(dp(280), dp(240)),
            background_color=(0, 0, 0, 0),
            overlay_color=(0, 0, 0, 0)
        )
        
        def update_bg(inst, *args):
            inst.canvas.before.clear()
            with inst.canvas.before:
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(20)])
                Color(0.15, 0.55, 0.9, 0.3)
                Line(rounded_rectangle=(inst.x, inst.y, inst.width, inst.height, dp(20)), width=dp(1))
        
        view.bind(pos=update_bg, size=update_bg)
        update_bg(view) # Initial call
        
        close_btn.on_release = view.dismiss
        content.add_widget(close_btn)
        
        view.add_widget(content)
        view.open()
    
    def start_learning(self):
        """Запускает обучение в выбранном режиме"""
        self.log(f"start_learning called with mode: {self.learning_mode}")
        if self.learning_mode == 'roadmap':
            self.start_roadmap_generation()
        else:
            self.start_generation()

    def start_generation(self):
        try:
            # Check if API key is set
            api_key = None
            if self.settings_store.exists('api'):
                data = self.settings_store.get('api')
                api_key = data.get('api_key', data.get('key'))
            self._last_api_key = api_key
            
            if not api_key:
                self.log("WARNING: No API key configured! Using offline mode.")
                # Show error message to user
                self._show_generation_error("API ключ не настроен. Перейдите в Настройки и сохраните ключ OpenRouter.")
                return
            
            # Get main screen to access search input
            main_screen = self.root.get_screen('main')
            
            # Access SearchScreen through MainScreen -> ScreenManager
            search_screen = main_screen.ids.tab_manager.get_screen('search')
            topic = search_screen.ids.topic_input.text.strip()
            
            # Сбрасываем роадмапу при начале одиночного урока
            self.current_roadmap_id = None
            self.current_node_id = None
            
            if not topic:
                self.log("WARNING: No topic entered, using default")
                topic = "Общие знания"
            
            self.log(f"Starting generation for topic: {topic}, difficulty: {self.difficulty}")
            
            # Переходим на экран загрузки и запускаем генерацию в отдельном потоке
            self.root.current = 'loading'
            threading.Thread(target=self.generate_quiz_thread, args=(topic, self.difficulty), daemon=True).start()
            
        except Exception as e:
            self.log(f"ERROR in start_generation: {e}")
            self.log(f"Traceback: {tb_module.format_exc()}")
            self._show_generation_error(f"Ошибка запуска генерации: {str(e)}")
    
    def start_roadmap_generation(self):
        """Запускает генерацию обучающей программы (roadmap)"""
        try:
            # Получаем API ключ
            api_key = None
            if self.settings_store.exists('api'):
                data = self.settings_store.get('api')
                api_key = data.get('api_key', data.get('key'))
            
            if not api_key:
                self.log("WARNING: No API key for roadmap generation")
                self._show_generation_error("API ключ не настроен. Перейдите в Настройки.")
                return
            
            # Получаем тему
            main_screen = self.root.get_screen('main')
            search_screen = main_screen.ids.tab_manager.get_screen('search')
            topic = search_screen.ids.topic_input.text.strip()
            
            if not topic:
                self.log("WARNING: No topic for roadmap")
                return
            
            self.log(f"Starting roadmap generation for: {topic} (difficulty: {self.difficulty})")
            
            # Сбрасываем текущее состояние роадмапы
            self.current_roadmap_id = None
            self.current_node_id = None
            
            # Переходим на экран загрузки и запускаем генерацию
            self.root.current = 'loading'
            threading.Thread(target=self.generate_roadmap_thread, args=(topic, api_key, self.difficulty), daemon=True).start()
            
        except Exception as e:
            self.log(f"ERROR in start_roadmap_generation: {e}")
            self._show_generation_error(f"Ошибка: {str(e)}")
    
    def generate_roadmap_thread(self, topic, api_key, difficulty):
        """Генерирует roadmap в отдельном потоке"""
        try:
            # Для быстрого тестирования можно использовать mock
            USE_MOCK = False  # Установите True для мгновенной генерации
            
            if USE_MOCK:
                from llm import generate_mock_roadmap
                self.log("Using mock roadmap for fast testing")
                roadmap = generate_mock_roadmap(topic, level=difficulty)
            else:
                from llm import generate_learning_roadmap
                
                # Получаем настройки персонализации
                interests = ""
                personalization_enabled = False
                if self.settings_store.exists('personalization'):
                    p_data = self.settings_store.get('personalization')
                    interests = p_data.get('interests', '')
                    personalization_enabled = p_data.get('enabled', False)
                
                roadmap = generate_learning_roadmap(
                    topic, 
                    level=difficulty, 
                    api_key=api_key,
                    interests=interests if personalization_enabled else None
                )
            
            if roadmap.get('error'):
                Clock.schedule_once(lambda dt: self._show_generation_error(roadmap['error']))
                return
            
            # Сохраняем roadmap
            roadmap_id = f"{topic.lower().replace(' ', '_')}_{int(__import__('time').time())}"
            self.roadmap_storage.save(roadmap_id, roadmap)
            self.current_roadmap_id = roadmap_id
            self.current_roadmap = roadmap  # Для доступа из RoadmapScreen
            
            # Переходим на экран roadmap
            Clock.schedule_once(lambda dt: self._show_roadmap_screen())
            
        except Exception as e:
            error_msg = f"Ошибка генерации программы: {str(e)}"
            self.log(f"ERROR in generate_roadmap_thread: {e}")
            self.log(f"Traceback: {tb_module.format_exc()}")
            Clock.schedule_once(lambda dt: self._show_generation_error(error_msg))
    
    def _show_roadmap_screen(self):
        """Переключает на экран roadmap"""
        self.root.current = 'roadmap'
    
    def show_roadmap(self, roadmap_id):
        """Отображает roadmap на экране"""
        try:
            roadmap = self.roadmap_storage.get(roadmap_id)
            if not roadmap:
                self.log(f"Roadmap not found: {roadmap_id}")
                return
            
            screen = self.root.get_screen('roadmap')
            screen.ids.roadmap_title.text = roadmap.get('title', 'Обучающая программа')
            screen.ids.roadmap_description.text = roadmap.get('description', '')
            
            # Очищаем и заполняем canvas
            canvas = screen.ids.roadmap_canvas
            canvas.clear_widgets()
            
            nodes = roadmap.get('nodes', [])
            progress = roadmap.get('progress', {})
            
            # Рисуем линии связей (зависимости)
            self._draw_roadmap_connections(canvas, nodes)
            
            # Создаем узлы
            for node in nodes:
                node_id = node.get('id', '')
                node_progress = progress.get(node_id, {})
                
                # Определяем статус
                if node_progress.get('completed'):
                    status = 'completed'
                elif node_progress.get('course_data'):
                    status = 'in_progress'
                else:
                    status = 'not_started'
                
                # Создаем виджет узла
                node_widget = RoadmapNode(
                    node_id=node_id,
                    node_title=node.get('title', 'Узел'),
                    node_description=node.get('description', ''),
                    node_type=node.get('type', 'main'),
                    status=status
                )
                
                # Позиционируем узел
                pos = node.get('position', {'x': 0.5, 'y': 0.5})
                node_widget.pos_hint = {'x': pos['x'] - 0.09, 'y': 1 - pos['y'] - 0.04}
                
                # Привязываем клик
                node_widget.bind(on_release=lambda w, nid=node_id: self.on_roadmap_node_click(nid))
                
                canvas.add_widget(node_widget)
            
            self.root.current = 'roadmap'
            
        except Exception as e:
            self.log(f"ERROR in show_roadmap: {e}")
            self.log(tb_module.format_exc())
    
    def _draw_roadmap_connections(self, canvas, nodes):
        """Рисует линии связей между узлами"""
        # TODO: Реализовать рисование линий через canvas
        pass
    
    def on_roadmap_node_click(self, node_id):
        """Обработка клика по узлу roadmap"""
        try:
            if not self.current_roadmap_id:
                return
            
            roadmap = self.roadmap_storage.get(self.current_roadmap_id)
            if not roadmap:
                return
            
            # Находим узел
            node = next((n for n in roadmap.get('nodes', []) if n['id'] == node_id), None)
            if not node:
                return
            
            # Проверяем прогресс
            progress = self.roadmap_storage.get_node_progress(self.current_roadmap_id, node_id)
            
            # ВАЖНО: Всегда запоминаем текущий узел перед началом
            self.current_node_id = str(node_id)
            
            if progress and progress.get('course_data'):
                # Курс уже создан - открываем
                self.on_generation_complete(progress['course_data'])
            else:
                # Генерируем новый курс
                topic = node.get('title', '')
                self.log(f"Generating course for roadmap node: {topic}")
                self.root.current = 'loading'
                threading.Thread(
                    target=self.generate_quiz_for_roadmap_node,
                    args=(node_id, topic, self.difficulty),
                    daemon=True
                ).start()
                
        except Exception as e:
            self.log(f"ERROR in on_roadmap_node_click: {e}")
    
    def generate_quiz_for_roadmap_node(self, node_id, topic, difficulty):
        """Генерирует курс для узла roadmap"""
        # Запоминаем текущий узел для последующей отметки как завершенного
        self.current_node_id = str(node_id)
        
        result = None
        try:
            from llm import generate_quiz
            result = generate_quiz(topic, difficulty, api_key=self._last_api_key)
            
            if result and not result.get('error'):
                # Сохраняем прогресс узла
                self.roadmap_storage.update_node_progress(
                    self.current_roadmap_id,
                    str(node_id),
                    completed=False,
                    course_data=result
                )
                
                Clock.schedule_once(lambda dt: self.on_generation_complete(result))
            else:
                error_msg = result.get('error', 'Неизвестная ошибка') if result else 'Ошибка генерации'
                Clock.schedule_once(lambda dt: self._show_generation_error(error_msg))
        except Exception as e:
            self.log(f"ERROR in generate_quiz_for_roadmap_node: {e}")
            Clock.schedule_once(lambda dt: self._show_generation_error(f"Ошибка: {str(e)}"))
    
    def return_from_roadmap(self):
        """Возврат из roadmap в главное меню"""
        self.root.current = 'main'

    def generate_quiz_thread(self, topic, difficulty):
        """
        Генерирует тест в отдельном потоке.
        
        Вызывает LLM для создания теории и вопросов.
        Не блокирует UI во время генерации.
        
        Args:
            topic: Тема для генерации
            difficulty: Уровень сложности
        """
        result = None
        error_message = None
        
        try:
            # Получаем API ключ из настроек
            api_key = None
            if self.settings_store.exists('api'):
                data = self.settings_store.get('api')
                api_key = data.get('api_key', data.get('key'))
            
            if not api_key:
                error_message = "API ключ не найден в настройках"
                self.log(f"ERROR: {error_message}")
                result = {'error': error_message}
            else:
                self.log(f"Starting generation for {topic}...")
                self.log(f"Difficulty: {difficulty}")
                
                # Получаем настройки персонализации
                interests = ""
                personalization_enabled = False
                if self.settings_store.exists('personalization'):
                    p_data = self.settings_store.get('personalization')
                    interests = p_data.get('interests', '')
                    personalization_enabled = p_data.get('enabled', False)
                
                self.log(f"Personalization enabled: {personalization_enabled}")
                if personalization_enabled and interests:
                    self.log(f"Using interests for context: {interests[:30]}...")
                
                # Вызываем LLM для генерации курса
                result = generate_quiz(
                    topic, 
                    difficulty, 
                    api_key=api_key,
                    interests=interests if personalization_enabled else None
                )
                
                if result:
                    if 'error' in result:
                        error_message = result.get('error', 'Неизвестная ошибка')
                        self.log(f"Generation completed with error: {error_message}")
                    else:
                        self.log("Generation completed successfully")
                        # Verify result structure
                        if 'questions' not in result or not result['questions']:
                            error_message = "LLM вернул пустой список вопросов"
                            result = {'error': error_message}
                            self.log(f"ERROR: {error_message}")
                else:
                    error_message = "LLM вернул пустой результат"
                    result = {'error': error_message}
                    self.log(f"ERROR: {error_message}")
                    
        except Exception as e:
            error_message = f"Ошибка при генерации: {str(e)}"
            self.log(f"EXCEPTION in generate_quiz_thread: {e}")
            self.log(f"Traceback: {tb_module.format_exc()}")
            result = {'error': error_message}
        
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
        try:
            # Проверяем наличие результата
            if not result:
                self.log("ERROR: No result from generation")
                self._show_generation_error("Не удалось сгенерировать курс. Проверьте подключение к интернету и API ключ.")
                return
            
            # Проверяем наличие ошибки в результате
            if 'error' in result:
                error_msg = result.get('error', 'Неизвестная ошибка')
                self.log(f"Generation error: {error_msg}")
                self._show_generation_error(f"Ошибка генерации: {error_msg}")
                return
            
            # Проверяем наличие вопросов
            if 'questions' not in result or not result['questions']:
                self.log("ERROR: No questions in result")
                self._show_generation_error("LLM не вернул вопросы. Попробуйте другую тему или проверьте API ключ.")
                return
            
            self.log("Generation successful")
            self.log(f"Questions count: {len(result['questions'])}")

            # Сохраняем сгенерированный курс в хранилище
            try:
                self.storage.save(result)
                self.log("Course saved to storage")
            except Exception as e:
                self.log(f"WARNING: Failed to save course: {e}")
                # Continue anyway - saving is not critical
            
            # Загружаем вопросы в QuizScreen
            quiz_screen = self.root.get_screen('quiz')
            quiz_screen.questions = result['questions']
            
            # Сохраняем метаданные курса
            meta = result.get('meta', {})
            topic = meta.get('topic', 'Без названия')
            difficulty = meta.get('difficulty', self.difficulty)
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
                self.log("Switched to theory screen")
            else:
                # Если теории нет, сразу запускаем тест
                self.log("No theory, starting quiz directly")
                self.start_quiz()
                
        except Exception as e:
            self.log(f"EXCEPTION in on_generation_complete: {e}")
            self.log(f"Traceback: {tb_module.format_exc()}")
            self._show_generation_error(f"Внутренняя ошибка: {str(e)}")

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
        
        # Вычисляем общий процент
        if open_max > 0:
            total_percent = int((mc_percent + open_percent) / 2)
        else:
            total_percent = mc_percent
        
        # Устанавливаем общий заголовок с результатами
        final_screen.set_score(mc_score + open_score, mc_total + open_max, total_percent)
        
        # --- NEW: Set specific stats for the new design ---
        final_screen.set_test_score(mc_percent)
        # For reasoning, we show score/10 (average) or total score?
        # The image shows "0/10". If there are multiple questions, maybe average score?
        # Or maybe the user wants the total score?
        # "0/10" looks like a score for a single question or an average.
        # Let's show the average score out of 10.
        avg_open_score = 0
        if len(self.open_answers_history) > 0:
            total_open_score = sum([item['evaluation'].get('score', 0) for item in self.open_answers_history])
            avg_open_score = round(total_open_score / len(self.open_answers_history), 1)
            if avg_open_score.is_integer():
                avg_open_score = int(avg_open_score)
        
        final_screen.set_reasoning_score(avg_open_score, 10)

        # Extract verdict and improvement
        verdict = "Тест завершен. Проанализируйте свои ошибки ниже."
        improvement = "Изучите теоретический материал еще раз."
        
        # Try to get a summary or use the last answer's feedback
        # Ideally, we would ask LLM for a summary, but for now let's use the last meaningful feedback
        if self.open_answers_history:
            # Find the answer with the lowest score to give improvement advice
            sorted_answers = sorted(self.open_answers_history, key=lambda x: x['evaluation'].get('score', 0))
            worst_answer = sorted_answers[0]
            
            if worst_answer['evaluation'].get('feedback'):
                verdict = worst_answer['evaluation'].get('feedback')
            
            if worst_answer['evaluation'].get('suggested_improvements'):
                improvement = worst_answer['evaluation'].get('suggested_improvements')

        final_screen.set_ai_verdict(verdict)
        final_screen.set_improvement(improvement)
        
        # --- NEW: Update Roadmap Progress ---
        current_node_id = getattr(self, 'current_node_id', None)
        current_roadmap_id = getattr(self, 'current_roadmap_id', None)
        
        if current_node_id and current_roadmap_id:
            # Считаем пройденным всегда (независимо от балла)
            self.log(f"Узел {current_node_id} завершен. Балл: {total_percent}%. Сохраняем прогресс...")
            self.roadmap_storage.update_node_progress(
                current_roadmap_id,
                current_node_id,
                completed=True
            )
            
            # Очищаем чтобы не сработало дважды (но сохраняем roadmap_id для возврата)
            self.current_node_id = None
        else:
            self.log(f"Информация о роадмапе отсутствует: Node={current_node_id}, Roadmap={current_roadmap_id}")
        # ------------------------------------
        
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
                'question': 'РАБОТА НАД ОШИБКАМИ: ТЕСТОВАЯ ЧАСТЬ',
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
                'question': 'РАБОТА НАД ОШИБКАМИ: РАЗВЁРНУТЫЕ ОТВЕТЫ',
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
            # Показываем финальный экран с результатами только MC теста
            self.show_combined_results(0, 0, 0, [])
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
        
        # Начисляем XP за ответ в зависимости от оценки
        if score >= 7:
            # Отличный ответ
            self.gamification.add_xp(10, "отличный развёрнутый ответ")
        elif score >= 4:
            # Хороший ответ
            self.gamification.add_xp(5, "хороший развёрнутый ответ")
        
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
        
        # Обновляем UI профиля после завершения сессии
        try:
            self.update_profile_stats()
        except Exception as e:
            print(f"Error updating profile UI: {e}")
        
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
            self.update_profile_stats()

    def update_profile_stats(self):
        """Обновляет статистику профиля на главном экране"""
        main_screen = self.root.get_screen('main')
        saved_screen = main_screen.ids.tab_manager.get_screen('saved')
        
        try:
            saved_screen.ids.profile_name.text = self.gamification.username
            saved_screen.ids.profile_level.text = f"{self.gamification.level} УРОВЕНЬ ОБУЧЕНИЯ"
            saved_screen.ids.total_xp.text = str(self.gamification.xp)
            saved_screen.ids.streak_days.text = f"{self.gamification.streak} дн."
            
            # Обновляем прогресс-бар и текст процента
            progress = self.gamification.get_level_progress()
            saved_screen.ids.level_progress_percent.text = f"{progress}%"
            if hasattr(saved_screen.ids, 'level_progress_bar'):
                saved_screen.ids.level_progress_bar.value = progress
        except Exception as e:
            self.log(f"Error updating profile UI: {e}")

    def load_roadmaps_list(self):
        """Загружает список всех программ обучения на отдельный экран"""
        screen = self.root.get_screen('roadmaps_list')
        grid = screen.ids.roadmaps_grid_full
        grid.clear_widgets()
        
        roadmaps = self.roadmap_storage.get_all()
        if not roadmaps:
            lbl = Label(text="У вас пока нет программ обучения", 
                       color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(40))
            grid.add_widget(lbl)
            return

        # Сортируем по времени (новые сверху)
        for rid in sorted(roadmaps.keys(), reverse=True):
            rdata = roadmaps[rid]
            title = rdata.get('title', 'Программа обучения')
            desc = rdata.get('description', '')
            if not desc:
                count = len(rdata.get('modules', []))
                desc = f"Программа из {count} модулей"
            
            card = RoadmapCard(roadmap_id=rid, title=title, description=desc)
            card.bind(on_release=lambda x, i=rid, d=rdata: self.start_roadmap(i, d))
            grid.add_widget(card)

    def load_lessons_list(self):
        """Загружает список всех одиночных уроков на отдельный экран"""
        screen = self.root.get_screen('lessons_list')
        grid = screen.ids.lessons_grid_full
        grid.clear_widgets()
        
        courses = self.storage.get_all()
        if not courses:
            lbl = Label(text="У вас пока нет пройденных уроков", 
                       color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(40))
            grid.add_widget(lbl)
            return

        for course in courses:
            meta = course.get('meta', {})
            topic = meta.get('topic', 'Без темы')
            diff = meta.get('difficulty', '')
            
            btn = CourseCard(topic=topic, difficulty=diff)
            btn.bind(on_release=lambda x, c=course: self.start_saved_course(c))
            grid.add_widget(btn)

    def delete_saved_course(self, topic, difficulty):
        """Удаляет сохранённый курс и обновляет список уроков"""
        if not topic: return
        removed = self.storage.delete(topic, difficulty)
        if not removed: return
        self.log(f"Курс '{topic}' ({difficulty}) удалён.")
        
        if hasattr(self, '_last_saved_meta') and self._last_saved_meta and \
                self._last_saved_meta.get('topic') == topic and \
                self._last_saved_meta.get('difficulty') == difficulty:
            self._last_saved_meta = None
            
        # Обновляем список на экране уроков
        self.load_lessons_list()

    def delete_roadmap(self, roadmap_id):
        """Удаляет программу обучения и обновляет список программ"""
        if not roadmap_id: return
        self.roadmap_storage.delete(roadmap_id)
        self.log(f"Программа {roadmap_id} удалена.")
        # Обновляем список на экране программ
        self.load_roadmaps_list()

    def start_roadmap(self, roadmap_id, roadmap_data):
        """Открывает детальный экран программы обучения"""
        self.current_roadmap_id = roadmap_id
        self.current_roadmap = roadmap_data
        self.root.current = 'roadmap'
        self.log(f"Открываем программу: {roadmap_data.get('title')}")

    def start_saved_course(self, course):
        self.on_generation_complete(course)

    def start_quiz_from_theory(self):
        """
        Запускает тест с экрана теории.
        
        Вызывается кнопкой "Начать тест" на экране теории.
        Начисляет XP за прочтение теории.
        """
        # Начисляем XP за прочтение теории
        self.gamification.add_xp(10, "прочтение теории")
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
    
    def _show_generation_error(self, message):
        """
        Показывает ошибку генерации пользователю.
        
        Обновляет экран загрузки с сообщением об ошибке,
        затем через 3 секунды возвращает на главный экран.
        
        Args:
            message: Текст сообщения об ошибке
        """
        self.log(f"Showing generation error to user: {message}")
        
        try:
            # Если мы на экране загрузки, показываем ошибку там
            if self.root.current == 'loading':
                loading_screen = self.root.get_screen('loading')
                if hasattr(loading_screen.ids, 'fact_label'):
                    loading_screen.ids.fact_label.text = f"❌ Ошибка:\n\n{message}"
                    loading_screen.ids.fact_label.color = (0.9, 0.3, 0.3, 1)  # Красный цвет
                
                # Через 4 секунды возвращаемся на главный экран
                Clock.schedule_once(lambda dt: setattr(self.root, 'current', 'main'), 4)
            else:
                # Если не на экране загрузки, сразу переходим на главный
                self.root.current = 'main'
                
            # Также логируем в настройках (если есть debug_log)
            try:
                settings_screen = self.root.get_screen('settings')
                if hasattr(settings_screen.ids, 'debug_log'):
                    current_log = settings_screen.ids.debug_log.text
                    settings_screen.ids.debug_log.text = f"{message}\n{current_log}"
            except:
                pass  # Не критично, если не удалось обновить лог
                
        except Exception as e:
            self.log(f"ERROR in _show_generation_error: {e}")
            # В крайнем случае просто возвращаемся на главный экран
            self.root.current = 'main'


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
