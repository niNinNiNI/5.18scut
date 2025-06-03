import os
import json
import bcrypt
from typing import Dict, Optional, TypedDict, List
from datetime import datetime


class UserPreferences(TypedDict):
    """用户偏好设置类型"""
    language: str
    notification: bool


class HistoryRecord(TypedDict):
    """历史记录类型"""
    query: str
    response: str
    timestamp: str


class UserData(TypedDict):
    """用户数据类型"""
    password: str
    preferences: UserPreferences
    history: List[HistoryRecord]


class UserManagerJSON:
    """用户管理系统(JSON文件版)"""

    def __init__(self, data_file: str = "users.json") -> None:
        self.data_file = data_file
        self.users: Dict[str, UserData] = {}
        self.default_prefs = UserPreferences(
            language='zh',
            notification=True
        )
        self._load_data()

    def _load_data(self) -> None:
        """加载用户数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)

    def _save_data(self) -> None:
        """保存用户数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def register(self, username: str, password: str) -> bool:
        """用户注册"""
        if not username or not password or username in self.users:
            return False

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.users[username] = UserData(
            password=hashed,
            preferences=UserPreferences(**self.default_prefs),
            history=[]
        )
        self._save_data()
        return True

    def login(self, username: str, password: str) -> bool:
        """用户登录验证"""
        user = self.users.get(username)
        return user is not None and bcrypt.checkpw(
            password.encode(),
            user['password'].encode()
        )

    def get_user(self, username: str) -> Optional[UserData]:
        """获取用户信息"""
        user = self.users.get(username)
        if not user:
            return None

        return {
            'password': '',  # 密码不返回
            'preferences': user['preferences'],
            'history': user['history']
        }

    def update_preferences(self, username: str, preferences: UserPreferences) -> bool:
        """更新用户偏好设置"""
        if username not in self.users:
            return False

        self.users[username]['preferences'].update(preferences)
        self._save_data()
        return True

    def add_history(self, username: str, query: str, response: str) -> bool:
        """添加对话历史记录"""
        if username not in self.users:
            return False

        self.users[username]['history'].append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        self._save_data()
        return True
