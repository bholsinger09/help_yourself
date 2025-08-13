import os
import sqlite3
import pytest
from helpyourself.app_logic import HelpYourselfLogic, DB_PATH


@pytest.fixture(autouse=True)
def clean_db(tmp_path, monkeypatch):
    # Use a temp DB for each test
    db_file = tmp_path / "test_checkins.db"
    monkeypatch.setattr("helpyourself.app_logic.DB_PATH", db_file)
    yield
    if db_file.exists():
        db_file.unlink()


def test_initial_state():
    logic = HelpYourselfLogic()
    assert logic.status == "Not Checked In"
    assert logic.button_label == "Check In"
    assert logic.checked_in_name == ""


def test_check_in_updates_status_and_button():
    logic = HelpYourselfLogic()
    logic.check_in("Alice")
    assert logic.status == "Checked In"
    assert logic.button_label == "Take Health Check"
    assert logic.checked_in_name == "Alice"


def test_health_check_updates_status_and_button():
    logic = HelpYourselfLogic()
    logic.check_in("Bob")
    logic.take_health_check()
    assert logic.status == "Health Check Complete"
    assert logic.button_label == "Checked In"


def test_check_in_then_health_check():
    logic = HelpYourselfLogic()
    logic.check_in("Alice")
    logic.take_health_check()
    assert logic.status == "Health Check Complete"
    assert logic.button_label == "Checked In"


def test_check_out_resets_state():
    logic = HelpYourselfLogic()
    logic.check_in("Charlie")
    logic.take_health_check()
    logic.check_out()
    assert logic.status == "Not Checked In"
    assert logic.button_label == "Check In"
    assert logic.checked_in_name == ""


def test_get_all_checkins():
    logic = HelpYourselfLogic()
    logic.check_in("Daisy")
    logic.check_in("Eve")
    checkins = logic.get_all_checkins()
    assert any("Daisy" in entry for entry in checkins)
    assert any("Eve" in entry for entry in checkins)
