from helpyourself.app_logic import HelpYourselfLogic
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
import warnings
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
        content = BoxLayout(orientation='vertical', spacing=10)
        question_input = TextInput(hint_text="How are you doing today?")
        submit_btn = Button(text="Submit")

        def submit_action(_):
            answer = question_input.text.strip()
            self.logic.take_health_check()
            popup.dismiss()
            self.update_ui()

        submit_btn.bind(on_release=submit_action)
        content.add_widget(question_input)
        content.add_widget(submit_btn)

        popup = Popup(title="Health Check", content=content, size_hint=(0.7, 0.4))
        popup.open()

    def check_out(self, instance):
        self.logic.check_out()
        self.update_ui()


if __name__ == "__main__":
    HelpYourselfApp().run()
