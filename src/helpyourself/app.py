from helpyourself.app_logic import HelpYourselfLogic
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
import warnings
import requests  # Add this import at the top
import openai
warnings.filterwarnings("ignore", category=ResourceWarning)

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._color = Color(0.2, 0.6, 1, 1)
            self._rect = RoundedRectangle(radius=[20], pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

class HelpYourselfApp(App):
    def __init__(self):
        super().__init__()
        self.logic = HelpYourselfLogic()

    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Top bar with status and user info
        self.top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.status_label = Label()
        self.logic.bind(status=lambda instance, value: setattr(self.status_label, 'text', f"Status: {value}"))
        self.user_info_label = Label(text="", halign="right", valign="middle")
        self.top_bar.add_widget(self.status_label)
        self.top_bar.add_widget(self.user_info_label)
        self.layout.add_widget(self.top_bar)

        # Button bar at the bottom
        self.button_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.15,
            spacing=20,
            padding=[0, 10, 0, 0]
        )
        self.layout.add_widget(self.button_bar)

        self.current_button = None
        self.update_ui()

        return self.layout

    def update_ui(self):
        button_kwargs = {
            "size_hint_y": 0.6,
            "size_hint_x": 0.30,
        }

        view_btn = RoundedButton(text="View All Check Ins", **button_kwargs)
        view_btn.callback = self.open_view_checkins_popup
        view_btn.bind(on_release=view_btn.callback)

        if self.logic.status == "Not Checked In":
            main_btn = RoundedButton(text="Check In", **button_kwargs)
            main_btn.callback = self.open_check_in_popup
            main_btn.bind(on_release=main_btn.callback)
            self.current_button = main_btn
            user_info = ""
            buttons = [main_btn, view_btn]
        elif self.logic.status in ["Checked In", "Health Check Complete"]:
            checkout_btn = RoundedButton(text="Check Out", **button_kwargs)
            checkout_btn.callback = self.check_out
            checkout_btn.bind(on_release=checkout_btn.callback)

            check_health_btn = RoundedButton(text="Check Health", **button_kwargs)
            check_health_btn.callback = self.open_health_check_popup
            check_health_btn.bind(on_release=check_health_btn.callback)

            user_info = f"{getattr(self.logic, 'checked_in_name', '')} (Checked In)"
            buttons = [checkout_btn, check_health_btn]
        else:
            main_btn = None
            user_info = ""
            buttons = [view_btn]

        self.button_bar.clear_widgets()
        self.button_bar.add_widget(Widget(size_hint_x=0.25))
        for btn in buttons:
            self.button_bar.add_widget(btn)
        self.button_bar.add_widget(Widget(size_hint_x=0.25))

        # Update status and user info labels
        if self.logic.status == "Checked In" and getattr(self.logic, "checked_in_name", ""):
            self.status_label.text = f"Checked In: {self.logic.checked_in_name}"
        else:
            self.status_label.text = f"Status: {self.logic.status}"
        self.user_info_label.text = user_info

    def open_check_in_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        name_input = TextInput(hint_text="Enter your name")
        submit_btn = Button(text="Submit")

        def submit_action(_):
            name = name_input.text.strip()
            if name:
                self.logic.check_in(name)
                popup.dismiss()
                self.update_ui()

        submit_btn.bind(on_release=submit_action)
        content.add_widget(name_input)
        content.add_widget(submit_btn)

        popup = Popup(title="Check In", content=content, size_hint=(0.7, 0.4))
        popup.open()

    def open_view_checkins_popup(self, instance):
        checkins = self.logic.get_all_checkins()
        content = BoxLayout(orientation='vertical', spacing=10, size_hint=None)
        if not checkins:
            content.add_widget(Label(text="No check-ins yet.", size_hint_y=None, height=30))
        else:
            for entry in checkins:
                content.add_widget(Label(text=entry, size_hint_y=None, height=30))

        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, None), size=(400, 300))
        scroll.add_widget(content)

        popup = Popup(
            title="All Check Ins",
            content=scroll,
            size_hint=(None, None),
            size=(420, 320),
            auto_dismiss=True
        )
        popup.open()

    def open_health_check_popup(self, instance):
        self.health_answers = {}
        self._ask_health_question(0)

    def _ask_health_question(self, step):
        questions = [
            ("How are you doing today?", "how_feeling"),
            ("Are you taking any meds? If yes, which ones?", "meds"),
            ("Have you been diagnosed with anything? If yes, what?", "diagnosis"),
        ]
        if step >= len(questions):
            self._process_health_answers()
            return

        question_text, key = questions[step]
        content = BoxLayout(orientation='vertical', spacing=10)
        input_box = TextInput(hint_text=question_text)
        submit_btn = Button(text="Next")

        def submit_action(_):
            self.health_answers[key] = input_box.text.strip()
            popup.dismiss()
            self._ask_health_question(step + 1)

        submit_btn.bind(on_release=submit_action)
        content.add_widget(Label(text=question_text))
        content.add_widget(input_box)
        content.add_widget(submit_btn)

        popup = Popup(title="Health Check", content=content, size_hint=(0.7, 0.4))
        popup.open()

    def _process_health_answers(self):
        feeling = self.health_answers.get("how_feeling", "").strip()
        diagnosis = self.health_answers.get("diagnosis", "")
        meds = self.health_answers.get("meds", "")

        # Always search for the feeling with "solutions"
        recommendations = self._get_recommendations(feeling, diagnosis, meds)
        self._show_health_summary(recommendations)

    def _get_recommendations(self, feeling, diagnosis, meds):
        prompt = (
            f"A user reports: '{feeling}'. "
            f"Diagnosis: '{diagnosis}'. "
            f"Medications: '{meds}'. "
            "Give a brief, safe, general self-care recommendation. "
            "If it's serious, advise to consult a healthcare professional."
        )
        try:
            client = openai.OpenAI()  # New: create a client instance
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Could not fetch AI recommendations: {e}"

    def _show_health_summary(self, recommendations):
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.scrollview import ScrollView
        from kivy.core.window import Window
        from kivy.clock import Clock

        popup_width = int(Window.width * 0.6)
        max_popup_height = int(Window.height * 0.8)
        button_width = int(popup_width * 0.5)
        button_height = 40
        vertical_spacing = 10
        horizontal_padding = 40  # <-- Increased for more right/left space

        # Label for recommendations
        rec_label = Label(
            text="[b]Health Recommendations:[/b]\n\n" + recommendations,
            markup=True,
            halign="left",
            valign="top",
            size_hint_x=None,
            size_hint_y=None,
            text_size=(popup_width - 2 * horizontal_padding, None),
            width=popup_width - 2 * horizontal_padding,
        )

        def update_label_height(instance, value):
            rec_label.height = rec_label.texture_size[1]

        rec_label.bind(texture_size=update_label_height)

        scroll = ScrollView(
            size_hint=(None, None),
            size=(popup_width - 2 * horizontal_padding, 100),  # Initial guess, will be updated
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=10,
        )
        scroll.add_widget(rec_label)

        # Center the close button in a horizontal BoxLayout
        button_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=button_height,
            padding=[0, 10, 0, 0]
        )
        button_box.add_widget(Widget(size_hint_x=0.5))
        close_btn = Button(
            text="Close",
            size_hint=(None, None),
            width=button_width,
            height=button_height,
        )
        button_box.add_widget(close_btn)
        button_box.add_widget(Widget(size_hint_x=0.5))

        content = BoxLayout(
            orientation='vertical',
            spacing=vertical_spacing,
            padding=[horizontal_padding, vertical_spacing, horizontal_padding, vertical_spacing],
            size_hint=(None, None),
            width=popup_width,
        )
        content.add_widget(scroll)
        content.add_widget(button_box)

        popup = Popup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(popup_width, 200),  # Initial guess, will be updated
            auto_dismiss=True,
            separator_height=0,  # <-- Hide the blue separator bar
            separator_color=(0, 0, 0, 0),  # <-- Make separator transparent (extra safety)
        )

        def adjust_popup(*args):
            total_content_height = rec_label.height + button_height + 3 * vertical_spacing
            popup.height = min(total_content_height, max_popup_height)
            scroll.height = popup.height - button_height - 2 * vertical_spacing
            # Ensure label and scroll widths match
            rec_label.text_size = (popup_width - 2 * horizontal_padding, None)
            rec_label.width = popup_width - 2 * horizontal_padding
            scroll.width = popup_width - 2 * horizontal_padding

        Clock.schedule_once(adjust_popup, 0.1)

        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def check_out(self, instance):
        self.logic.check_out()
        self.update_ui()


if __name__ == "__main__":
    HelpYourselfApp().run()
