import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "checkins.db"


class HelpYourselfLogic:
    def save_checkin(self, name):
        # Create the checkins table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY, name TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        # Insert the check-in
        self.cursor.execute(
            "INSERT INTO checkins (name) VALUES (?)", (name,)
        )
        self.conn.commit()
    def __init__(self):
        
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_table()
        self.status = "Not Checked In"
        self.button_label = "Check In"
        self.checked_in_name = ""
        self._save_state()

    def _create_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS status (id INTEGER PRIMARY KEY, state TEXT, button TEXT)"
        )
        self.conn.commit()

    def _load_state(self):
        self.cursor.execute("SELECT state, button FROM status WHERE id=1")
        row = self.cursor.fetchone()
        if row:
            self.status, self.button_label = row
        else:
            self.status = "Not Checked In"
            self.button_label = "Check In"
            self._save_state()

    def _save_state(self):
        self.cursor.execute(
            "INSERT OR REPLACE INTO status (id, state, button) VALUES (1, ?, ?)",
            (self.status, self.button_label)
        )
        self.conn.commit()

    def check_in(self, name):
       self.checked_in_name = name
       self.status = "Checked In"
       self.button_label = "Take Health Check"
       self.save_checkin(name)

    def take_health_check(self):
        self.status = "Health Check Complete"
        self.button_label = "Checked In"
        self._save_state()

    def check_out(self):
        self.status = "Not Checked In"
        self.button_label = "Check In"
        self.checked_in_name = ""  # <-- Add this line
        self._save_state()

    def get_all_checkins(self):
        self.cursor.execute("SELECT name, timestamp FROM checkins ORDER BY timestamp DESC")
        rows = self.cursor.fetchall()
        return [f"{timestamp}: {name}" for name, timestamp in rows]
