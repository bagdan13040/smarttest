from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import threading
from llm import generate_quiz

# Warm light background
Window.clearcolor = (0.95, 0.93, 0.90, 1)
Window.size = (360, 700)

KV = """
ScreenManager:
    HomeScreen:
    LoadingScreen:
    TheoryScreen:
    QuizScreen:
    FinalScreen:

<TheoryScreen>:
    name: 'theory'
    BoxLayout:
        orientation: 'vertical'
        padding: 16
        spacing: 12

        Label:
            text: 'Теория'
            color: 0.15, 0.55, 0.9, 1
            font_size: '24sp'
            bold: True
            size_hint_y: None
            height: 40

        BoxLayout:
            size_hint_y: None
            height: 40
            spacing: 8
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
                padding: [10, 10]
                markup: True

        RoundedButton:
            text: 'ПЕРЕЙТИ К ТЕСТУ'
            font_size: '18sp'
            bold: True
            size_hint: None, None
            size: 280, 50
            pos_hint: {'center_x': 0.5}
            bg_color: (0.15, 0.55, 0.9, 1)
            color: 1, 1, 1, 1
            on_release: app.start_quiz_from_theory()

<LoadingScreen>:
    name: 'loading'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 12
        Widget:
            size_hint_y: 0.3
        DotSpinner:
            size_hint_y: None
            height: 40
            pos_hint: {'center_x': 0.5}
        Label:
            text: 'Генерация курса'
            color: 0.5, 0.5, 0.5, 1
            font_size: '16sp'
            halign: 'center'
            size_hint_y: None
            height: 30
        Widget:
            size_hint_y: 0.3

<card@BoxLayout>:
    padding: [16, 8, 16, 16]
    spacing: 10
    canvas.before:
        Color:
            rgba: (0.95, 0.93, 0.90, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20]

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        padding: [12, 8, 12, 8]
        spacing: 8

        BoxLayout:
            size_hint_y: None
            height: 56
            padding: 0, 6
            canvas.before:
                Color:
                    rgba: (0.15, 0.55, 0.9, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [16]
            Label:
                text: 'Kivy Light App'
                color: 1, 1, 1, 1
                bold: True
                font_size: '22sp'

        card:
            orientation: 'vertical'
            size_hint_y: None
            height: 320
            Label:
                text: 'Добро пожаловать! Введите тему для теста:'
                color: 0.15, 0.55, 0.9, 1
                font_size: '18sp'
                halign: 'center'
                valign: 'middle'
                text_size: self.width - 24, None
                size_hint_y: None
                height: 60

            TextInput:
                id: topic_input
                hint_text: 'Например: Космос'
                multiline: False
                size_hint_y: None
                height: 50
                font_size: '18sp'
                padding: [10, 12]
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
                height: 20

            BoxLayout:
                size_hint_y: None
                height: 40
                spacing: 10
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
                height: 10

            RoundedButton:
                text: 'НАЧАТЬ ТЕСТ'
                font_size: '20sp'
                bold: True
                size_hint: None, None
                size: 280, 60
                pos_hint: {'center_x': 0.5}
                bg_color: (0.15, 0.55, 0.9, 1)
                color: 1, 1, 1, 1
                on_release: app.start_generation()

        Widget:

<QuizScreen>:
    name: 'quiz'
    question_index: 0
    score: 0
    BoxLayout:
        orientation: 'vertical'
        padding: 16
        spacing: 12

        Label:
            id: question_label
            text: root.current_question_text
            color: 0.15, 0.55, 0.9, 1
            font_size: '22sp'
            bold: True
            text_size: self.width - 30, None
            halign: 'center'
            valign: 'middle'
            size_hint_y: 0.35

        Label:
            text: str(root.question_index + 1) + '/' + str(len(root.questions))
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: 30
            halign: 'center'
            font_size: '16sp'

        GridLayout:
            id: options_box
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: 12

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
        padding: 16
        spacing: 20

        Label:
            text: 'Результат'
            color: 0.15, 0.55, 0.9, 1
            font_size: '32sp'
            bold: True
            size_hint_y: None
            height: 60

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
            size: 280, 60
            pos_hint: {'center_x': 0.5}
            bg_color: (0.15, 0.55, 0.9, 1)
            color: 1, 1, 1, 1
            on_release: app.restart_quiz()

        RoundedButton:
            text: 'ВЫЙТИ ИЗ ТЕСТА'
            font_size: '18sp'
            bold: True
            size_hint: None, None
            size: 280, 60
            pos_hint: {'center_x': 0.5}
            bg_color: (0.8, 0.3, 0.3, 1)
            color: 1, 1, 1, 1
            on_release: app.root.current = 'home'
"""


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
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
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
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
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
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(texture_size=self._update_height)

    def _update_rect(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self.text_size = (self.width - 20, None)

    def _update_height(self, *args):
        self.height = max(60, self.texture_size[1] + 30)

    def set_selected(self, selected: bool):
        self._bg_color.rgba = self.selected_color if selected else self.default_color
        self.color = (1, 1, 1, 1) if selected else (0, 0, 0, 1)


class HomeScreen(Screen):
    pass


class LoadingScreen(Screen):
    pass


class TheoryScreen(Screen):
    theory_content = StringProperty('')
    meta_title = StringProperty('')
    meta_sub = StringProperty('')


class DotSpinner(BoxLayout):
    """A tiny spinner made of three dots that pulse sequentially."""
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', spacing=8, size_hint=(None, None), **kwargs)
        self.size = (120, 40)
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
        root = Builder.load_string(KV)
        return root

    def set_difficulty(self, level):
        self.difficulty = level

    def start_generation(self):
        home = self.root.get_screen('home')
        topic = home.ids.topic_input.text.strip()
        if not topic:
            topic = "Общие знания"
        
        self.root.current = 'loading'
        threading.Thread(target=self.generate_quiz_thread, args=(topic, self.difficulty)).start()

    def generate_quiz_thread(self, topic, difficulty):
        result = generate_quiz(topic, difficulty)
        Clock.schedule_once(lambda dt: self.on_generation_complete(result))

    def on_generation_complete(self, result):
        if result and 'questions' in result:
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
            self.root.current = 'home'

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
