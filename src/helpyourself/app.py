import sqlite3
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock


DB_NAME = "checkins.db"


class CheckInApp(App):
    def build(self):
        # Set window size to 25% of screen
        Window.size = (
            Window.system_size[0] * 0.25,
            Window.system_size[1] * 0.25
        )

        self.init_db()

        self.layout = FloatLayout()

        # Top-right label with ~5% padding from right edge
        self.status_label = Label(
            text="Checked In: ",
            size_hint=(None, None),
            size=(190, 30),           # slightly smaller width for padding
            pos_hint={'right': 0.95, 'top': 1},  # shifted left 5%
            halign='right',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.layout.add_widget(self.status_label)

        self.btn_checkin = Button(
            text='Check Me In',
            size_hint=(0.4, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            background_color=(1, 0, 0, 1),  # Red
            color=(0, 0, 1, 1)  # Blue text
        )
        self.btn_checkin.bind(on_release=self.show_input_popup)
        self.layout.add_widget(self.btn_checkin)

        btn_view = Button(
            text='View All Check-Ins',
            size_hint=(0.4, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            background_color=(0, 0.5, 0, 1),  # Dark green
            color=(1, 1, 1, 1)  # White text
        )
        btn_view.bind(on_release=self.show_checkin_history)
        self.layout.add_widget(btn_view)

        return self.layout

    def init_db(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timestamp DATETIME
            )
        ''')
        conn.commit()
        conn.close()

    def save_checkin(self, name):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO checkins (name, timestamp) VALUES (?, CURRENT_TIMESTAMP)', (name,)
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
        return rows

    def show_input_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        input_box = TextInput(
            hint_text='Enter your first name',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        content.add_widget(input_box)

        btn_submit = Button(text='Submit', size_hint_y=None, height=40)
        content.add_widget(btn_submit)

        popup = Popup(
            title='Check In',
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=False
        )

        def on_submit(_instance):
            name = input_box.text.strip()
            if name:
                self.save_checkin(name)
                popup.dismiss()
                self.show_greeting(name)

        btn_submit.bind(on_release=on_submit)
        popup.open()

    def show_greeting(self, name):
        # Update the top-right label with the checked-in name
        self.status_label.text = f"Checked In: {name}"

        # Change the check-in button to "Take Health Check"
        self.btn_checkin.text = "Take Health Check"
        # Optionally change button action here:
        # self.btn_checkin.unbind(on_release=self.show_input_popup)
        # self.btn_checkin.bind(on_release=self.take_health_check)

        greeting = Popup(
            title='Welcome',
            content=Label(text=f'Hello, {name}!', font_size=20),
            size_hint=(None, None),
            size=(300, 200)
        )
        greeting.open()

        # Auto-dismiss after 2 seconds
        Clock.schedule_once(lambda dt: greeting.dismiss(), 2)

    def show_checkin_history(self, instance):
        checkins = self.get_all_checkins()
        if not checkins:
            content = Label(text="No check-ins yet.",
                            size_hint_y=None, height=30)
        else:
            content = BoxLayout(orientation='vertical',
                                spacing=5, padding=10, size_hint_y=None)
            content.height = max(200, len(checkins) * 30)
            for name, timestamp in checkins:
                lbl = Label(text=f"{timestamp}: {name}",
                            size_hint_y=None, height=30)
                content.add_widget(lbl)

        scroll = ScrollView(size_hint=(1, None), size=(400, 300))
        scroll.add_widget(content)

        popup = Popup(
            title="Check-In History",
            content=scroll,
            size_hint=(None, None),
            size=(420, 320),
            auto_dismiss=True
        )
        popup.open()

    # Example placeholder for health check action
    def take_health_check(self, instance):
        popup = Popup(
            title="Health Check",
            content=Label(text="Health check feature coming soon!"),
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()


if __name__ == '__main__':
    CheckInApp().run()
