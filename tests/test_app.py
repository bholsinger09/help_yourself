from helpyourself.app_logic import HelpYourselfLogic
import pytest
from helpyourself.app import HelpYourselfApp


@pytest.fixture
def app_instance():
    app = HelpYourselfApp()
    return app


def test_app_builds(app_instance):
    layout = app_instance.build()
    assert layout is not None
    # Check that the layout has children (top bar and button bar)
    assert len(layout.children) >= 2
    # Check that status_label exists
    assert hasattr(app_instance, "status_label")
    # Check that button_bar exists
    assert hasattr(app_instance, "button_bar")
