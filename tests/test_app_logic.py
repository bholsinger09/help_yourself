import pytest
from helpyourself.app_logic import HelpYourselfLogic


def test_initial_state():
    logic = HelpYourselfLogic()
    assert logic.status == "Not Checked In"
    assert logic.button_label == "Check In"


def test_check_in_updates_status_and_button():
    logic = HelpYourselfLogic()
    logic.check_in()
    assert logic.status == "Checked In"
    assert logic.button_label == "Take Health Check"


def test_health_check_updates_status_and_button():
    logic = HelpYourselfLogic()
    logic.take_health_check()
    assert logic.status == "Health Check Complete"
    assert logic.button_label == "Checked In"


def test_check_in_then_health_check():
    logic = HelpYourselfLogic()
    logic.check_in()
    logic.take_health_check()
    assert logic.status == "Health Check Complete"
    assert logic.button_label == "Checked In"


def test_check_out_resets_state():
    logic = HelpYourselfLogic()
    # Check-out from initial state
    logic.check_out()
    assert logic.status == "Not Checked In"
    assert logic.button_label == "Check In"

    # Check-out after check-in
    logic.check_in()
    logic.check_out()
    assert logic.status == "Not Checked In"
    assert logic.button_label == "Check In"

    # Check-out after health check
    logic.check_in()
    logic.take_health_check()
    logic.check_out()
    assert logic.status == "Not Checked In"
    assert logic.button_label == "Check In"
