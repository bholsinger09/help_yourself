import pytest
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget


# ... your HelpYourselfApp class and methods here ...


def test_cli_app_builds():
    app = HelpYourselfApp()
    layout = app.build()
    assert layout is not None


class HelpYourselfApp(App):
    # ... other methods ...

    def update_ui(self):
        # Button style
        button_kwargs = {
            "size_hint_y": 0.6,
            "size_hint_x": 0.25,
        }

        # Always show "View All Check Ins" button
        view_btn = RoundedButton(text="View All Check Ins", **button_kwargs)
        view_btn.callback = self.open_view_checkins_popup
        view_btn.bind(on_release=view_btn.callback)

        # Determine which button(s) to show and set user_info
        if self.logic.status == "Not Checked In":
            main_btn = RoundedButton(text="Check In", **button_kwargs)
            main_btn.callback = self.open_check_in_popup
            main_btn.bind(on_release=main_btn.callback)
            self.current_button = main_btn
            user_info = ""
            buttons = [main_btn, view_btn]
        elif self.logic.status in ["Checked In", "Health Check Complete"]:
            # Show "Check Out" button
            checkout_btn = RoundedButton(text="Check Out", **button_kwargs)
            checkout_btn.callback = self.check_out
            checkout_btn.bind(on_release=checkout_btn.callback)
            user_info = f"{getattr(self.logic, 'checked_in_name', '')} (Checked In)"
            buttons = [checkout_btn, view_btn]
        else:
            main_btn = None
            user_info = ""
            buttons = [view_btn]

        # Add empty space, buttons, and empty space to center them
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
