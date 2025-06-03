import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv(
        'OPENAI_BASE_URL', 'https://api.gptsapi.net/v1')  # 默认使用用户提供的URL
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///campus_assistant.db')

    # 应用配置
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'  # 从环境变量读取初始状态（true/false）

    @staticmethod
    def toggle_debug(state: bool):
        Config.DEBUG = state  # 静态方法用于切换调试状态
