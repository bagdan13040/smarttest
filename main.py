from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp
import threading
import random
import json
import os
import uuid
try:
    from llm import generate_quiz
except Exception as e:
    print(f"Error importing llm: {e}")
    # Fallback if llm fails to load (e.g. missing requests)
    def generate_quiz(topic, difficulty):
        return {
            "theory": f"Ошибка загрузки модуля LLM: {e}. Проверьте логи.",
            "questions": [
                {"question": "Ошибка", "options": ["Ок", "Ок", "Ок", "Ок"], "answer": 0}
            ]
        }

# Warm light background
Window.clearcolor = (0.95, 0.93, 0.90, 1)
# Window.size = (360, 700) # Removed to allow proper scaling on Android

INTERESTING_FACTS = [
    "Первый компьютерный баг был настоящим мотыльком, застрявшим в реле.",
    "Сердце синего кита весит столько же, сколько автомобиль.",
    "Мёд — единственный продукт, который никогда не портится. Его находили в гробницах фараонов.",
    "Венера — единственная планета Солнечной системы, вращающаяся по часовой стрелке.",
    "Осьминоги имеют три сердца и голубую кровь.",
    "Бананы с ботанической точки зрения являются ягодами, а клубника — нет.",
    "В теле человека достаточно железа, чтобы сделать гвоздь длиной 7 см.",
    "Колибри — единственная птица, способная летать назад.",
    "ДНК человека и банана совпадают на 50%.",
    "Самая короткая война в истории длилась 38 минут (между Британией и Занзибаром).",
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
    def __init__(self, filename='courses.json'):
        self.filename = filename
        self.courses = self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save(self, course):
        # Check if course already exists (by topic and difficulty) to avoid duplicates
        for c in self.courses:
            if c.get('meta', {}).get('topic') == course.get('meta', {}).get('topic') and \
               c.get('meta', {}).get('difficulty') == course.get('meta', {}).get('difficulty'):
                return
        
        self.courses.insert(0, course)
        self._write()

    def _write(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)
            
    def get_all(self):
        return self.courses

KV = """
#:import dp kivy.metrics.dp

ScreenManager:
    MainScreen:
    LoadingScreen:
    TheoryScreen:
    QuizScreen:
    FinalScreen:

<NavButton@ToggleButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    group: 'nav'
    allow_no_selection: False
    color: (0.5, 0.5, 0.5, 1) if self.state == 'normal' else (0.15, 0.55, 0.9, 1)
    bold: True if self.state == 'down' else False
    font_size: '16sp'
    halign: 'center'
    valign: 'middle'
    text_size: self.size
    canvas.before:
        Color:
            rgba: (0.15, 0.55, 0.9, 1) if self.state == 'down' else (0, 0, 0, 0)
        Line:
            points: [self.x + self.width * 0.2, self.y + self.height - 2, self.x + self.width * 0.8, self.y + self.height - 2]
            width: 2 if self.state == 'down' else 0.001

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        size_hint: (1, 1)
        padding: [0, dp(30), 0, 0]  # Top padding for status bar
        
        ScreenManager:
            id: tab_manager
            size_hint: (1, 1)
            SavedScreen:
                name: 'saved'
            SearchScreen:
                name: 'search'
            SettingsScreen:
                name: 'settings'
                
        BoxLayout:
            size_hint_y: None
            height: dp(80)  # Increased height
            padding: [0, dp(5)]
            size_hint_x: 1
            orientation: 'horizontal'
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 0.9, 0.9, 0.9, 1
                Line:
                    points: [self.x, self.y + self.height, self.x + self.width, self.y + self.height]
                    width: 1
            
            NavButton:
                text: 'Мои курсы'
                state: 'down'
                on_release: tab_manager.current = 'saved'
                size_hint_x: 0.33
                
            NavButton:
                text: 'Поиск'
                state: 'normal'
                on_release: tab_manager.current = 'search'
                size_hint_x: 0.33

            NavButton:
                text: 'Настройки'
                state: 'normal'
                on_release: tab_manager.current = 'settings'
                size_hint_x: 0.33

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
        spacing: dp(16)
        
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
            height: dp(30)
            halign: 'left'
            text_size: (self.width, None)

        TextInput:
            id: api_key_input
            hint_text: 'sk-or-...'
            multiline: False
            size_hint_y: None
            height: dp(50)
            font_size: '16sp'
            padding: [dp(10), dp(12)]
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
            size: dp(280), dp(50)
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
            height: dp(30)

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
            
            Button:
                text: '<'
                size_hint_x: None
                width: 50
                background_normal: ''
                background_color: (0,0,0,0)
                color: (0.15, 0.55, 0.9, 1)
                font_size: '24sp'
                bold: True
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
                halign: 'left'
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

        RoundedButton:
            text: 'ПЕРЕЙТИ К ТЕСТУ'
            font_size: '18sp'
            bold: True
            size_hint: None, None
            size: dp(280), dp(50)
            pos_hint: {'center_x': 0.5}
            bg_color: (0.15, 0.55, 0.9, 1)
            color: 1, 1, 1, 1
            on_release: app.start_quiz_from_theory()

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
            
            Button:
                text: '<'
                size_hint_x: None
                width: dp(50)
                background_normal: ''
                background_color: (0,0,0,0)
                color: (0.15, 0.55, 0.9, 1)
                font_size: '24sp'
                bold: True
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

<FinalScreen>:
    name: 'final'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(20)

        Label:
            text: 'Результат'
            color: 0.15, 0.55, 0.9, 1
            font_size: '32sp'
            bold: True
            size_hint_y: None
            height: dp(60)

        Label:
            id: score_label
            text: root.score_text
            color: 0.2, 0.2, 0.2, 1
            font_size: '24sp'
            halign: 'center'
            valign: 'top'
            size_hint_y: 1
            text_size: self.width, None

        RoundedButton:
            text: 'ПРОЙТИ ЕЩЁ РАЗ'
            font_size: '18sp'
            bold: True
            size_hint: None, None
            size: dp(280), dp(60)
            pos_hint: {'center_x': 0.5}
            bg_color: (0.15, 0.55, 0.9, 1)
            color: 1, 1, 1, 1
            on_release: app.restart_quiz()

        RoundedButton:
            text: 'ВЫЙТИ ИЗ ТЕСТА'
            font_size: '18sp'
            bold: True
            size_hint: None, None
            size: dp(280), dp(60)
            pos_hint: {'center_x': 0.5}
            bg_color: (0.8, 0.3, 0.3, 1)
            color: 1, 1, 1, 1
            on_release: app.root.current = 'main'
"""


class CourseCard(ButtonBehavior, BoxLayout):
    bg_color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, topic, difficulty, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(16), dp(12)]
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(90)
        
        with self.canvas.before:
            self._rect_color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Topic Label
        self.add_widget(Label(
            text=topic,
            color=(0.2, 0.2, 0.2, 1),
            font_size='18sp',
            bold=True,
            halign='left',
            valign='middle',
            text_size=(self.width, None),
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Difficulty Label
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
    bg_color = ListProperty([0.15, 0.55, 0.9, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.halign = 'center'
        self.valign = 'middle'
        with self.canvas.before:
            self._rect_color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(bg_color=self._update_color)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self.text_size = (self.width, None)

    def _update_color(self, *args):
        self._rect_color.rgba = self.bg_color


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
        self._bg_color.rgba = self.selected_color if selected else self.default_color
        self.color = (1, 1, 1, 1) if selected else (0, 0, 0, 1)


class MainScreen(Screen):
    pass

class SavedScreen(Screen):
    pass

class SearchScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class LoadingScreen(Screen):
    def start_fact_cycle(self):
        self.update_fact()
        self._fact_event = Clock.schedule_interval(self.update_fact, 7)

    def stop_fact_cycle(self):
        if hasattr(self, '_fact_event'):
            self._fact_event.cancel()

    def update_fact(self, dt=None):
        fact = random.choice(INTERESTING_FACTS)
        self.ids.fact_label.text = f"Интересный факт:\n{fact}"


class TheoryScreen(Screen):
    theory_content = StringProperty('')
    meta_title = StringProperty('')
    meta_sub = StringProperty('')


class DotSpinner(BoxLayout):
    """A tiny spinner made of three dots that pulse sequentially."""
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(8), size_hint=(None, None), **kwargs)
        self.size = (dp(120), dp(40))
        self.dots = [Label(text='•', font_size='28sp', color=(0.6,0.6,0.6,1)) for _ in range(3)]
        for d in self.dots:
            self.add_widget(d)
        self._idx = 0
        self._event = Clock.schedule_interval(self._pulse, 0.4)

    def _pulse(self, dt):
        for i, d in enumerate(self.dots):
            if i == self._idx:
                d.color = (0.15, 0.55, 0.9, 1)
            else:
                d.color = (0.6,0.6,0.6,1)
        self._idx = (self._idx + 1) % len(self.dots)

    def on_parent(self, widget, parent):
        # Stop animation when removed
        if parent is None and getattr(self, '_event', None):
            self._event.cancel()


class QuizScreen(Screen):
    question_index = NumericProperty(0)
    score = NumericProperty(0)
    result_text = StringProperty('')
    current_question_text = StringProperty('')

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
        final = self.manager.get_screen('final')
        final.set_score(self.score, len(self.questions))
        self.manager.current = 'final'

    def reset_quiz(self):
        self.question_index = 0
        self.score = 0
        self.selected = None
        self.highlighted_button = None
        self.answered = False
        self.load_question()


class FinalScreen(Screen):
    score_text = StringProperty('')

    def set_score(self, score, total):
        self.score_text = f'Вы набрали {score} из {total}.'


class MyApp(App):
    difficulty = StringProperty('легкий')

    def build(self):
        # Use the application's private data directory for storage
        data_dir = self.user_data_dir
        courses_path = os.path.join(data_dir, 'courses.json')
        settings_path = os.path.join(data_dir, 'settings.json')
        
        self.storage = CourseStorage(filename=courses_path)
        self.settings_store = JsonStore(settings_path)
        
        root = Builder.load_string(KV)
        return root

    def load_settings_ui(self):
        main_screen = self.root.get_screen('main')
        settings_screen = main_screen.ids.tab_manager.get_screen('settings')
        
        if self.settings_store.exists('api'):
            key = self.settings_store.get('api')['key']
            settings_screen.ids.api_key_input.text = key

    def save_settings(self):
        try:
            main_screen = self.root.get_screen('main')
            settings_screen = main_screen.ids.tab_manager.get_screen('settings')
            key = settings_screen.ids.api_key_input.text.strip()
            
            self.settings_store.put('api', key=key)
            settings_screen.ids.status_label.text = "Настройки сохранены!"
            Clock.schedule_once(lambda dt: setattr(settings_screen.ids.status_label, 'text', ''), 2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            # Try to show error on screen if possible
            try:
                settings_screen.ids.status_label.text = "Ошибка сохранения"
            except:
                pass

    def set_difficulty(self, level):
        self.difficulty = level

    def start_generation(self):
        # Access SearchScreen through MainScreen -> ScreenManager
        main_screen = self.root.get_screen('main')
        search_screen = main_screen.ids.tab_manager.get_screen('search')
        topic = search_screen.ids.topic_input.text.strip()
        if not topic:
            topic = "Общие знания"
        
        self.root.current = 'loading'
        threading.Thread(target=self.generate_quiz_thread, args=(topic, self.difficulty)).start()

    def generate_quiz_thread(self, topic, difficulty):
        # Get API key from settings
        api_key = None
        if self.settings_store.exists('api'):
            api_key = self.settings_store.get('api')['key']
            
        result = generate_quiz(topic, difficulty, api_key=api_key)
        Clock.schedule_once(lambda dt: self.on_generation_complete(result))

    def on_generation_complete(self, result):
        if result and 'questions' in result:
            # Save the generated course
            self.storage.save(result)
            
            # Сохраняем вопросы в QuizScreen
            quiz_screen = self.root.get_screen('quiz')
            quiz_screen.questions = result['questions']
            
            # Если есть теория, показываем её
            if 'theory' in result and result['theory']:
                theory_screen = self.root.get_screen('theory')
                theory_screen.theory_content = result['theory']
                # meta: topic/difficulty/notes
                meta = result.get('meta', {})
                topic = meta.get('topic', '')
                difficulty = meta.get('difficulty', '')
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
        self.start_quiz()

    def start_quiz(self):
        quiz = self.root.get_screen('quiz')
        quiz.reset_quiz()
        self.root.current = 'quiz'

    def restart_quiz(self):
        quiz = self.root.get_screen('quiz')
        quiz.reset_quiz()
        self.root.current = 'quiz'


if __name__ == '__main__':
    MyApp().run()
