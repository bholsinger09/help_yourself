import sqlite3
from pathlib import Path
from kivy.properties import StringProperty
from kivy.event import EventDispatcher

DB_PATH = Path(__file__).parent.parent / "checkins.db"


class HelpYourselfLogic(EventDispatcher):
    """Logic and state for the HelpYourself app (MVVM ViewModel)."""
    status = StringProperty("Not Checked In")
    button_label = StringProperty("Check In")
    checked_in_name = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._create_tables()
        self._load_state()

    def _create_tables(self):
        """Ensure required tables exist."""
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY, name TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            # Always create the status table first
            cur.execute(
                "CREATE TABLE IF NOT EXISTS status (id INTEGER PRIMARY KEY, state TEXT, button TEXT, checked_in_name TEXT)"
            )
            # Now check for missing columns (future-proofing)
            cur.execute("PRAGMA table_info(status)")
            columns = [row[1] for row in cur.fetchall()]
            if "checked_in_name" not in columns:
                cur.execute("ALTER TABLE status ADD COLUMN checked_in_name TEXT")
            conn.commit()

    def _load_state(self):
        """Load persisted state from the database."""
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT state, button, checked_in_name FROM status WHERE id=1")
            row = cur.fetchone()
            if row:
                self.status, self.button_label, self.checked_in_name = row
            else:
                self.status = "Not Checked In"
                self.button_label = "Check In"
                self.checked_in_name = ""
                self._save_state()

    def _save_state(self):
        """Persist current state to the database."""
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO status (id, state, button, checked_in_name) VALUES (1, ?, ?, ?)",
                (self.status, self.button_label, self.checked_in_name)
            )
            conn.commit()

    def save_checkin(self, name):
        """Save a new check-in to the database."""
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO checkins (name) VALUES (?)", (name,)
            )
            conn.commit()

    def check_in(self, name):
        """Handle user check-in."""
        self.checked_in_name = name
        self.status = "Checked In"
        self.button_label = "Take Health Check"
        self.save_checkin(name)
        self._save_state()

    def take_health_check(self):
        """Handle health check completion."""
        self.status = "Health Check Complete"
        self.button_label = "Checked In"
        self._save_state()

    def check_out(self):
        """Handle user check-out."""
        self.status = "Not Checked In"
        self.button_label = "Check In"
        self.checked_in_name = ""
        self._save_state()

    def get_all_checkins(self):
        """Return all check-ins as formatted strings."""
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, timestamp FROM checkins ORDER BY timestamp DESC")
            rows = cur.fetchall()
        return [f"{timestamp}: {name}" for name, timestamp in rows]
