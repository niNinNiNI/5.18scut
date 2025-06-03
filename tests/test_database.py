import pytest
from database import DatabaseManager
import bcrypt


@pytest.fixture
def db_manager(tmp_path):
    """测试用的数据库管理器"""
    db_path = tmp_path / "test.db"
    return DatabaseManager(str(db_path))


def test_create_and_verify_user(db_manager):
    """测试用户创建和验证"""
    username = "testuser"
    password = "testpass123"

    # 测试创建用户
    assert db_manager.create_user(username, password) is True

    # 测试验证正确密码
    assert db_manager.verify_user(username, password) is True

    # 测试验证错误密码
    assert db_manager.verify_user(username, "wrongpass") is False


def test_password_hashing():
    """测试密码哈希"""
    password = "testpass123"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # 验证哈希是否正确
    assert bcrypt.checkpw(password.encode(), hashed) is True
    assert bcrypt.checkpw("wrongpass".encode(), hashed) is False


def test_chat_logging(db_manager):
    """测试聊天记录功能"""
    username = "testuser2"
    password = "testpass456"
    db_manager.create_user(username, password)

    user_id = db_manager.get_user_id(username)
    assert user_id is not None

    # 测试记录聊天
    log_id = db_manager.log_chat(
        user_id, "test query", "test response", "test topic")
    assert log_id is not None

    # 测试获取聊天历史
    history = db_manager.get_chat_history(user_id)
    assert len(history) == 1
    assert history[0]["query"] == "test query"
    assert history[0]["response"] == "test response"
