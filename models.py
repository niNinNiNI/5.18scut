from dataclasses import dataclass


@dataclass
class TopicDocument:
    """主题文档数据结构"""
    title: str
    keywords: list[str]
    content: str
