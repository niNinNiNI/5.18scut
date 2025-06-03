import json
from database import DatabaseManager
from user_json import UserManagerJSON


def migrate_users():
    """将用户数据从JSON迁移到SQLite数据库"""
    json_manager = UserManagerJSON()
    db_manager = DatabaseManager()

    # 迁移用户数据
    for username, user_data in json_manager.users.items():
        password = user_data['password']
        if not db_manager.create_user(username, password):
            print(f"Failed to migrate user: {username}")

    print("User migration completed")


if __name__ == "__main__":
    migrate_users()
