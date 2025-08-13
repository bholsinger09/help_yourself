from helpyourself.app_logic import HelpYourselfLogic
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
import sqlite3
import os

DB_NAME = "checkins.db"


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)  # Fully transparent
        with self.canvas.before:
            self._color = Color(0.2, 0.6, 1, 1)
            self._rect = RoundedRectangle(
                radius=[20], pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

# ...existing code...


# ...existing imports and RoundedButton...

class HelpYourselfApp(App):
    def __init__(self):
        super().__init__()  # <-- Add this line!
        self.status = "Not Checked In"
        self.button_label = "Check In"
        self.checked_in_name = ""
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_checkin(self, name):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO checkins (name) VALUES (?)', (name,)
        )
        conn.commit()
        conn.close()

    def get_all_checkins(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            'SELECT name, timestamp FROM checkins ORDER BY timestamp DESC')
        rows = cur.fetchall()
        conn.close()
        return [f"{timestamp}: {name}" for name, timestamp in rows]

    def check_in(self, name):
        self.checked_in_name = name
        self.status = "Checked In"
        self.button_label = "Take Health Check"
        self.save_checkin(name)

    def take_health_check(self):
        self.status = "Health Check Complete"
        self.button_label = ""
        
    def build(self):
        self.logic = HelpYourselfLogic()
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Top bar with status and user info
        self.top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        if self.logic.status == "Checked In" and getattr(self.logic, "checked_in_name", ""):
            status_text = f"Checked In: {self.logic.checked_in_name}"
        else:
            status_text = f"Status: {self.logic.status}"
        self.status_label = Label(
            text=status_text,
            halign="left",
            valign="middle"
        )
        self.user_info_label = Label(
            text="", halign="right", valign="middle"
        )
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
        button_kwargs = {'size_hint_y': None, 'height': 50}

        # Create the "View All Check Ins" button
        view_btn = RoundedButton(text="View All Check Ins", **button_kwargs)
        view_btn.callback = self.open_view_checkins_popup
        view_btn.bind(on_release=view_btn.callback)

        # Determine which button to show and set user_info
        if self.logic.status == "Not Checked In":
            self.logic.button_label = "Check In"
            main_btn = RoundedButton(text="Check In", **button_kwargs)
            main_btn.callback = self.open_check_in_popup
            main_btn.bind(on_release=main_btn.callback)
            self.current_button = main_btn
            user_info = ""
        elif self.logic.status == "Checked In":
            self.logic.button_label = "Take Health Check"
            main_btn = RoundedButton(text="Take Health Check", **button_kwargs)
            main_btn.callback = self.open_health_check_popup
            main_btn.bind(on_release=main_btn.callback)
            self.current_button = main_btn
            user_info = f"{getattr(self.logic, 'checked_in_name', '')} (Checked In)"
        else:
            self.logic.button_label = ""
            main_btn = None
            user_info = f"{getattr(self.logic, 'checked_in_name', '')} (Checked In)" if getattr(
                self.logic, 'checked_in_name', '') else ""

        # Add empty space, buttons, and empty space to center them
        self.button_bar.clear_widgets()
        self.button_bar.add_widget(Widget(size_hint_x=0.25))
        if main_btn:
            self.button_bar.add_widget(main_btn)
        self.button_bar.add_widget(view_btn)
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
                self.logic.check_in(name)  # Save to DB and update logic
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
            content.add_widget(
                Label(text="No check-ins yet.", size_hint_y=None, height=30))
        else:
            for entry in checkins:
                content.add_widget(
                    Label(text=entry, size_hint_y=None, height=30))

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
            self.update_ui()  # removes the button completely after health check

        submit_btn.bind(on_release=submit_action)
        content.add_widget(question_input)
        content.add_widget(submit_btn)

        popup = Popup(title="Health Check",
                      content=content, size_hint=(0.7, 0.4))
        popup.open()

    def open_view_checkins_popup(self, instance):
        # Dummy implementation, replace with your logic
        content = BoxLayout(orientation='vertical', spacing=10)
        checkins_label = Label(text="All check ins:\n" + "\n".join(
            self.logic.get_all_checkins() if hasattr(self.logic, 'get_all_checkins') else ["No data"]))
        close_btn = Button(text="Close")
        content.add_widget(checkins_label)
        content.add_widget(close_btn)
        popup = Popup(title="All Check Ins",
                      content=content, size_hint=(0.7, 0.4))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    HelpYourselfApp().run()
