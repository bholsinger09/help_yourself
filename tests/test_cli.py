import pytest
from helpyourself.cli import HelpYourselfApp


def test_cli_app_builds():
    app = HelpYourselfApp()
    layout = app.build()
    assert layout is not None
