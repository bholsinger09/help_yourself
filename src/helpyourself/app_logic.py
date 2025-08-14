import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "checkins.db"


class HelpYourselfLogic:
    def __init__(self):
        self.status = "Not Checked In"
        self.button_label = "Check In"
        self.checked_in_name = ""
        self._create_tables()
        self._load_state()

    def _create_tables(self):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY, name TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS status (id INTEGER PRIMARY KEY, state TEXT, button TEXT)"
            )
            conn.commit()

    def _load_state(self):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT state, button FROM status WHERE id=1")
            row = cur.fetchone()
            if row:
                self.status, self.button_label = row
            else:
                self.status = "Not Checked In"
                self.button_label = "Check In"
                self._save_state()

    def _save_state(self):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO status (id, state, button) VALUES (1, ?, ?)",
                (self.status, self.button_label)
            )
            conn.commit()

    def save_checkin(self, name):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY, name TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            cur.execute(
                "INSERT INTO checkins (name) VALUES (?)", (name,)
            )
            conn.commit()

    def check_in(self, name):
        self.checked_in_name = name
        self.status = "Checked In"
        self.button_label = "Take Health Check"
        self.save_checkin(name)
        self._save_state()

    def take_health_check(self):
        self.status = "Health Check Complete"
        self.button_label = "Checked In"
        self._save_state()

    def check_out(self):
        self.status = "Not Checked In"
        self.button_label = "Check In"
        self.checked_in_name = ""
        self._save_state()

    def get_all_checkins(self):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, timestamp FROM checkins ORDER BY timestamp DESC")
            rows = cur.fetchall()
        return [f"{timestamp}: {name}" for name, timestamp in rows]
