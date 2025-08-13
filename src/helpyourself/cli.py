from helpyourself.app_logic import HelpYourselfLogic
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App


class HelpYourselfApp(App):
    def build(self):
        self.logic = HelpYourselfLogic()
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Status label
        self.status_label = Label(
            text=f"Status: {self.logic.status}, Button: {self.logic.button_label}")
        self.layout.add_widget(self.status_label)

        # Current active button
        self.current_button = None
        self.update_ui()

        return self.layout


def update_ui(self):
    print(f"Updating UI. Current status: {self.logic.status}")

    # Remove all buttons currently in layout except the status label
    for child in list(self.layout.children):
        if isinstance(child, Button):
            print(f"Removing button: {child.text}")
            self.layout.remove_widget(child)
            try:
                if hasattr(child, 'callback'):
                    child.unbind(on_release=child.callback)
            except Exception as e:
                print(f"Error unbinding: {e}")

    self.current_button = None

    # Determine which button to show
    if self.logic.status == "Not Checked In":
        self.logic.button_label = "Check In"
        btn = Button(text="Check In")
        btn.callback = self.open_check_in_popup
        btn.bind(on_release=btn.callback)
        self.layout.add_widget(btn)
        self.current_button = btn
        print("Added Check In button")
    elif self.logic.status == "Checked In":
        self.logic.button_label = "Take Health Check"
        btn = Button(text="Take Health Check")

        def health_check_callback(instance):
            self.open_health_check_popup(instance)

        btn.callback = health_check_callback
        btn.bind(on_release=btn.callback)
        self.layout.add_widget(btn)
        self.current_button = btn
        print("Added Take Health Check button")
    elif self.logic.status == "Health Check Complete":
        self.logic.button_label = ""
        print("No button after health check")

    # Update status label
    self.status_label.text = f"Status: {self.logic.status}, Button: {self.logic.button_label}"

    def open_check_in_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        name_input = TextInput(hint_text="Enter your name")
        submit_btn = Button(text="Submit")

        def submit_action(_):
            name = name_input.text.strip()
            if name:
                self.logic.check_in()
                popup.dismiss()
                self.update_ui()  # replaces the button completely

        submit_btn.bind(on_release=submit_action)
        content.add_widget(name_input)
        content.add_widget(submit_btn)

        popup = Popup(title="Check In", content=content, size_hint=(0.7, 0.4))
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


if __name__ == "__main__":
    HelpYourselfApp().run()
