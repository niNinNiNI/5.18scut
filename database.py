import sqlite3
import json
from typing import Optional, List, Dict
from datetime import datetime
import bcrypt


class DatabaseManager:
    """数据库管理类"""

    def __init__(self, db_path: str = "campus_assistant.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """创建必要的表"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    preferences TEXT DEFAULT '{"language":"zh","notification":true}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    topic TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

    def create_user(self, username: str, password: str) -> bool:
        """创建新用户"""
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hashed)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> bool:
        """验证用户凭据"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if row:
            return bcrypt.checkpw(password.encode(), row["password_hash"])
        return False

    def log_chat(self, user_id: int, query: str, response: str, topic: Optional[str] = None) -> Optional[int]:
        """记录聊天日志"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO chat_logs (user_id, query, response, topic) VALUES (?, ?, ?, ?)",
                (user_id, query, response, topic)
            )
            return cursor.lastrowid

    def get_user_id(self, username: str) -> Optional[int]:
        """获取用户ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            return row["id"] if row else None

    def update_preferences(self, username: str, preferences: dict) -> bool:
        """更新用户偏好设置"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE users SET preferences = ? WHERE username = ?",
                    (json.dumps(preferences), username)
                )
            return True
        except sqlite3.Error:
            return False

    def get_preferences(self, username: str) -> Optional[dict]:
        """获取用户偏好设置"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT preferences FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            return json.loads(row["preferences"]) if row and row["preferences"] else None

    def get_chat_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """获取用户聊天历史"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT query, response, timestamp, topic FROM chat_logs "
                "WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            return [dict(row) for row in cursor]
