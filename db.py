import sqlite3

from models import Status


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _init_schema(self):
        assert self.conn is not None
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                card_idm TEXT NOT NULL UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS status_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def find_user_by_card(self, card_idm: str) -> sqlite3.Row | None:
        cur = self.conn.execute(
            """
            SELECT u.* FROM users u
            JOIN cards c ON c.user_id = u.id
            WHERE c.card_idm = ?
            """,
            (card_idm,),
        )
        return cur.fetchone()

    def list_users(self) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT id, name, student_id FROM users ORDER BY name"
        )
        return cur.fetchall()

    def find_user_by_student_id(self, student_id: str) -> sqlite3.Row | None:
        cur = self.conn.execute(
            "SELECT * FROM users WHERE student_id = ?", (student_id,)
        )
        return cur.fetchone()

    def register_user(self, student_id: str, name: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO users (student_id, name) VALUES (?, ?)", (student_id, name)
        )
        self.conn.commit()
        return cur.lastrowid

    def add_card(self, user_id: int, card_idm: str):
        self.conn.execute(
            "INSERT INTO cards (user_id, card_idm) VALUES (?, ?)", (user_id, card_idm)
        )
        self.conn.commit()

    def log_status(self, user_id: int, status: Status):
        self.conn.execute(
            "INSERT INTO status_log (user_id, status) VALUES (?, ?)",
            (user_id, int(status)),
        )
        self.conn.commit()

    def latest_statuses(self) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            """
            SELECT u.id, u.name, u.student_id, s.status, s.timestamp
            FROM users u
            LEFT JOIN status_log s ON s.id = (
                SELECT id FROM status_log
                WHERE user_id = u.id
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
            )
            ORDER BY u.name
            """
        )
        return cur.fetchall()

    def recent_logs(self, limit: int = 50) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            """
            SELECT s.timestamp, u.name, s.status
            FROM status_log s
            JOIN users u ON u.id = s.user_id
            ORDER BY s.timestamp DESC, s.id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
