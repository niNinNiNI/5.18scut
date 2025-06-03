"""
校园助手NLP处理模块
功能：
1. 识别用户查询意图
2. 处理问候类查询
3. 检索校园相关信息
4. 调用OpenAI API生成回答

主要组件：
- Intent类：存储意图识别结果
- NLPProcessor类：核心处理逻辑
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
import re
import openai
import os
from topic_registry import TopicRegistry, TopicDefinition
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class Intent:
    """存储意图识别结果的数据类

    属性：
    name: 意图名称(GREETING/SCHOOL_RELATED/UNKNOWN)
    confidence: 置信度(0.0-1.0)
    """
    name: str
    confidence: float


class NLPProcessor:
    """校园助手NLP处理核心类

    功能：
    - 识别用户查询意图
    - 处理问候类查询
    - 检索校园信息
    - 调用OpenAI API生成回答
    """

    def __init__(self):
        """初始化NLP处理器

        初始化组件：
        - 话题注册表(TopicRegistry)
        - OpenAI客户端
        """
        self.topic_registry = TopicRegistry()
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.gptsapi.net')
        )

    def process_query(self, query: str, topic: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        处理用户查询并返回响应
        参数:
            query: 用户查询文本
            topic: 可选的话题名称
            history: 可选的历史对话记录，格式为[{"role": "user/assistant", "content": "消息内容"}]
        返回:
            响应内容
        """
        # 1. 识别意图
        intent = self._detect_intent(query)

        # 2. 处理问候类意图
        if intent.name == "GREETING":
            return self._handle_greeting(query)

        # 3. 检索信息
        return self._retrieve_info(query, topic, history)

    def _detect_intent(self, text: str) -> Intent:
        """
        识别用户查询意图

        参数:
            text: 用户输入的查询文本(已转换为小写并去除首尾空格)

        返回:
            Intent: 包含意图名称和置信度的对象

        实现细节:
        1. 问候类识别:
           - 使用预设关键词集合(你好/hi/hello等)
           - 完全匹配时返回GREETING意图
           - 置信度设为1.0(完全确定)

        2. 校园相关识别:
           - 通过TopicRegistry查询匹配的话题
           - 使用话题关键词进行匹配
           - 匹配成功返回SCHOOL_RELATED意图
           - 置信度设为0.9(高度可信)

        3. 默认情况:
           - 返回UNKNOWN意图
           - 置信度设为0.0(无法识别)

        技术特点:
        - 基于关键词的快速匹配
        - 支持中英文混合查询
        - 预处理文本(小写转换+去空格)
        - 可扩展的意图分类体系
        """
        text = text.lower().strip()

        # 问候类关键词匹配
        greetings = {"你好", "hi", "hello", "早上好", "下午好", "晚上好"}
        if any(g in text for g in greetings):
            return Intent(name="GREETING", confidence=1.0)

        # 话题关键词匹配
        matched_topics = self.topic_registry.find_topics_by_keyword(text)
        if matched_topics:
            return Intent(name="SCHOOL_RELATED", confidence=0.8)

        return Intent(name="UNKNOWN", confidence=0.0)

    def _handle_greeting(self, text: str) -> str:
        """
        处理问候类查询

        参数:
            text: 用户输入的问候文本(已转换为小写)

        返回:
            str: 对应的问候响应文本

        支持多种问候语和语言(中英文)
        """
        responses = {
            "你好": "你好！我是校园助手，有什么可以帮你的吗？",
            "hi": "Hi! 我是校园助手，有什么可以帮你的吗？",
            "hello": "Hello! 我是校园助手，有什么可以帮你的吗？",
            "谢谢": "不客气，很高兴能帮到你！",
            "thanks": "You're welcome! Glad to help!",
            "再见": "再见，祝你学习愉快！",
            "拜拜": "拜拜，有问题随时来找我哦~"
        }
        return responses.get(text.lower(), "你好！有什么可以帮你的吗？")

    def _retrieve_info(self, query: str, topic: Optional[str], history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        检索校园相关信息

        参数:
            query: 用户查询文本
            topic: 可选的话题名称
            history: 可选的历史对话记录，格式为[{"role": "user/assistant", "content": "消息内容"}]

        返回:
            str: 检索结果或错误信息

        处理流程:
        1. 获取相关话题文档
        2. 使用OpenAI API生成回答
        """
        # 调试：打印所有可用话题（仅调试模式显示）
        from config import Config
        if Config.DEBUG:
            print("可用话题列表:")
            for topic_name, topic_def in self.topic_registry.topics.items():
                print(f"- {topic_name}: {topic_def.data_file}")
                # 验证文件是否存在
                file_path = os.path.join(
                    os.path.dirname(__file__), topic_def.data_file)
                print(f"  文件路径: {file_path}")
                print(f"  文件存在: {os.path.exists(file_path)}")
        # 获取相关话题文档
        if topic:
            topic_def = self.topic_registry.get_topic(topic)
            if topic_def:  # 确保 topic_def 不是 None
                # 显式调用加载内容，确保内容被填充
                self.topic_registry._load_topic_content(topic_def)
                if Config.DEBUG:
                    print(
                        f"DEBUG - Explicit load for {topic_def.display_name}, content snippet: {topic_def.content[:100] if topic_def.content else 'None'}")
            docs = [topic_def] if topic_def else []
        else:
            docs = list(self.topic_registry.topics.values())
            # 如果是查询所有话题，也确保它们的内容被加载
            for t_def in docs:
                if not t_def.content:
                    self.topic_registry._load_topic_content(t_def)
                    if Config.DEBUG:
                        print(
                            f"DEBUG - Explicit load for ALL topics - {t_def.display_name}, content snippet: {t_def.content[:100] if t_def.content else 'None'}")

        if not docs:
            return "找不到相关信息，请尝试其他查询"

        # 进一步调试，检查第一个文档的内容（仅调试模式显示）
        if Config.DEBUG and docs and docs[0]:
            print(
                f"DEBUG - First doc in docs: {docs[0].display_name}, content snippet after potential load: {docs[0].content[:100] if docs[0].content else 'None'}")

        # 检查文档内容是否为空
        for doc in docs:
            if Config.DEBUG:
                print(f"DEBUG - 话题内容检查: {doc.display_name}")
                print(
                    f"DEBUG - 内容长度: {len(doc.content) if doc.content else 0}")
            # 修改后逻辑（去除空白后判断）
            if not doc.content.strip():
                return "找不到相关信息，请尝试其他查询"

        # 构建OpenAI提示模板
        context = "\n\n".join(
            f"## {doc.display_name}\n{doc.description}\n{doc.content}"
            for doc in docs
        )

        # 强制显示调试信息（仅调试模式显示）
        if Config.DEBUG:
            print("=== DEBUG INFO START ===\n")
            print(f"DEBUG - 加载的话题内容长度: {len(context)}")
            print(f"DEBUG - 查询关键词: {query}")
            print(f"DEBUG - 匹配的话题: {topic}")
            print(f"DEBUG - 文档数量: {len(docs)}")
            print(f"DEBUG - 第一个文档内容长度: {len(docs[0].content) if docs else 0}")
            print(
                f"DEBUG - 第一个文档内容片段: {docs[0].content[:200] if docs else '无内容'}")
            print("=== DEBUG INFO END ===\n")

        # 构建消息列表
        messages = []

        # 添加系统提示
        system_prompt = """你是一个专业的校园助手，请根据以下信息回答问题：
        
{context}

回答要求:
1. 严格遵循文档内容,若文档中找不到则返回找不到相关信息
2. 简洁明了(3-5句话)
3. 使用与问题相同的语言
4. 如涉及流程，分步骤说明
5. 结合对话历史上下文进行回答"""
        messages.append(
            {"role": "system", "content": system_prompt.format(context=context)})

        # 添加历史对话
        if history:
            messages.extend(history)

        # 添加当前问题
        messages.append({"role": "user", "content": query})

        try:
            # 调用OpenAI API生成回答
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.5,
                max_tokens=5000
            )
            result = response.choices[0].message.content
            if not result or "找不到" in result:
                # 如果API返回空或找不到信息，直接返回相关文档内容
                return docs[0].content.split("\n")[0] + "\n\n" + "\n".join(docs[0].content.split("\n")[1:4])
            return result
        except Exception as e:
            # 明确检查openai特定异常
            if hasattr(e, '__module__') and e.__module__.startswith('openai'):
                if isinstance(e, openai.AuthenticationError):
                    return "API认证失败，请检查配置"
                elif isinstance(e, openai.APIConnectionError):
                    return "网络连接失败，请检查网络设置"
                elif isinstance(e, openai.RateLimitError):
                    return "请求过于频繁，请稍后再试"
                else:
                    return "服务暂时不可用"
            else:
                return "服务暂时不可用"
