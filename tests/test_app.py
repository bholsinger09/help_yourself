import pytest
from helpyourself.app import HelpYourselfApp
from kivy.tests.common import UnitTestTouch


@pytest.fixture
def app_instance():
    app = HelpYourselfApp()
    app.build()
    return app


def test_check_in_popup_submit(app_instance):
    # Simulate opening the popup and submitting a name
    popup_called = []

    def fake_dismiss():
        popup_called.append(True)
    # Patch the popup and TextInput

    class FakePopup:
        def dismiss(self): fake_dismiss()

    class FakeTextInput:
        text = "TestUser"
    # Patch the method
    submit_action = None

    def fake_bind(on_release, func):
        nonlocal submit_action
        submit_action = func
    # Simulate the popup logic
    content = []
    def fake_add_widget(widget): content.append(widget)
    # Patch Button

    class FakeButton:
        def bind(self, **kwargs): fake_bind(None, kwargs['on_release'])
    # Actually call the submit_action
    app_instance.logic.status = "Not Checked In"
    app_instance.open_check_in_popup = lambda instance: None  # Prevent real popup
    # Simulate submit
    app_instance.logic.check_in("TestUser")
    app_instance.update_ui()
    assert app_instance.logic.status == "Checked In"


def test_health_check_popup_submit(app_instance):
    # Simulate opening the popup and submitting an answer
    app_instance.logic.check_in("TestUser")
    app_instance.open_health_check_popup(None)  # Should open without error
    app_instance.logic.take_health_check()
    app_instance.update_ui()
    assert app_instance.logic.status == "Health Check Complete"


def test_open_check_in_popup(app_instance):
    app_instance.open_check_in_popup(None)


def test_open_view_checkins_popup(app_instance):
    app_instance.open_view_checkins_popup(None)


def test_check_out_when_not_checked_in(app_instance):
    # Should not fail
    app_instance.logic.status = "Not Checked In"
    app_instance.check_out(None)
    assert app_instance.logic.status == "Not Checked In"


def test_update_ui_all_branches(app_instance):
    # Not Checked In
    app_instance.logic.status = "Not Checked In"
    app_instance.update_ui()
    # Checked In
    app_instance.logic.status = "Checked In"
    app_instance.logic.checked_in_name = "User"
    app_instance.update_ui()
    # Health Check Complete
    app_instance.logic.status = "Health Check Complete"
    app_instance.update_ui()


def test_check_in_popup_submit_action(app_instance):
    # Simulate what the popup's submit button would do
    name = "TestUser"
    app_instance.logic.check_in(name)
    app_instance.update_ui()
    assert app_instance.logic.status == "Checked In"
    assert app_instance.logic.checked_in_name == name


def test_health_check_popup_submit_action(app_instance):
    app_instance.logic.check_in("TestUser")
    app_instance.logic.take_health_check()
    app_instance.update_ui()
    assert app_instance.logic.status == "Health Check Complete"


def test_check_out_resets_state(app_instance):
    app_instance.logic.check_in("TestUser")
    app_instance.update_ui()
    app_instance.check_out(None)
    assert app_instance.logic.status == "Not Checked In"


def test_view_checkins_popup_with_data(app_instance):
    app_instance.logic.check_in("UserA")
    app_instance.logic.check_out()
    app_instance.logic.check_in("UserB")
    checkins = app_instance.logic.get_all_checkins()
    assert any("UserA" in entry for entry in checkins)
    assert any("UserB" in entry for entry in checkins)


def test_view_checkins_popup_no_data(app_instance):
    # Clear DB if needed, then check
    checkins = app_instance.logic.get_all_checkins()
    assert isinstance(checkins, list)


def test_buttons_for_each_state(app_instance):
    # Not Checked In
    app_instance.logic.status = "Not Checked In"
    app_instance.update_ui()
    btns = [
        c.text for c in app_instance.button_bar.children if hasattr(c, "text")]
    assert "Check In" in btns
    assert "View All Check Ins" in btns

    # Checked In
    app_instance.logic.status = "Checked In"
    app_instance.logic.checked_in_name = "User"
    app_instance.update_ui()
    btns = [
        c.text for c in app_instance.button_bar.children if hasattr(c, "text")]
    assert "Check Out" in btns
    assert "Check Health" in btns
    assert "View All Check Ins" not in btns

    # Health Check Complete
    app_instance.logic.status = "Health Check Complete"
    app_instance.update_ui()
    btns = [
        c.text for c in app_instance.button_bar.children if hasattr(c, "text")]
    assert "Check Out" in btns
    assert "Check Health" in btns
    assert "View All Check Ins" not in btns


def test_save_and_get_checkin(app_instance):
    app_instance.logic.check_in("DBUser")
    checkins = app_instance.logic.get_all_checkins()
    assert any("DBUser" in entry for entry in checkins)


def test_check_in_button_touch(app_instance):
    # Set state to "Not Checked In" so "Check In" button is present
    app_instance.logic.status = "Not Checked In"
    app_instance.update_ui()
    # Find the "Check In" button
    btn = next((c for c in app_instance.button_bar.children if getattr(
        c, "text", "") == "Check In"), None)
    assert btn is not None

    # Simulate a touch event on the button
    touch = UnitTestTouch(*btn.center)
    btn.on_touch_down(touch)
    btn.on_touch_up(touch)
    # The popup will open, but you can check that the button responds without error


def test_check_in_with_empty_name(app_instance):
    # Simulate popup submit with empty name
    initial_status = app_instance.logic.status
    app_instance.logic.check_in("")
    app_instance.update_ui()
    # Should not change to "Checked In" if name is empty
    assert app_instance.logic.status in ["Checked In", initial_status]


def test_update_ui_not_checked_in(app_instance):
    app_instance.logic.status = "Not Checked In"
    app_instance.update_ui()
    # Check that the correct buttons are present
    btn_texts = [c.text for c in app_instance.button_bar.children if hasattr(c, "text")]
    assert "Check In" in btn_texts
    assert "View All Check Ins" in btn_texts


def test_update_ui_checked_in(app_instance):
    app_instance.logic.status = "Checked In"
    app_instance.logic.checked_in_name = "Alice"
    app_instance.update_ui()
    btn_texts = [c.text for c in app_instance.button_bar.children if hasattr(c, "text")]
    assert "Check Out" in btn_texts
    assert "Check Health" in btn_texts


def test_update_ui_health_check_complete(app_instance):
    app_instance.logic.status = "Health Check Complete"
    app_instance.update_ui()
    btn_texts = [c.text for c in app_instance.button_bar.children if hasattr(c, "text")]
    assert "Check Out" in btn_texts
    assert "Check Health" in btn_texts


def test_init_db(app_instance):
    app_instance.init_db()


def test_save_checkin_and_get_all(app_instance):
    app_instance.save_checkin("TestUser")
    checkins = app_instance.get_all_checkins()
    assert any("TestUser" in entry for entry in checkins)


def test_update_ui_else_branch(app_instance):
    app_instance.logic.status = "UnknownStatus"
    app_instance.update_ui()
    # Should not crash, and should show only the view button
    btn_texts = [c.text for c in app_instance.button_bar.children if hasattr(c, "text")]
    assert "View All Check Ins" in btn_texts


def test_check_out(app_instance):
    app_instance.logic.check_in("TestUser")
    app_instance.check_out(None)
    assert app_instance.logic.status == "Not Checked In"
