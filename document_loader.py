import os
import re
from typing import Dict, List, Tuple
from models import TopicDocument


class DocumentLoader:
    """Markdown文档加载器"""

    def __init__(self, data_dir: str = "data/topics"):
        self.data_dir = data_dir

    def load_all_documents(self) -> Dict[str, TopicDocument]:
        """加载所有主题文档"""
        documents = {}

        # 遍历data目录下的Markdown文件
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(self.data_dir, filename)
                topic_name = filename[:-3]  # 移除.md后缀
                documents[topic_name] = self._parse_document(filepath)

        return documents

    def _parse_document(self, filepath: str) -> TopicDocument:
        """解析单个Markdown文档"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取文档标题
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(
            1) if title_match else os.path.basename(filepath)[:-3]

        # 提取关键词并生成同音词变体
        keywords_match = re.search(
            r"\*\*关键词\*\*:\s*(.+)$", content, re.MULTILINE)
        base_keywords = [kw.strip() for kw in keywords_match.group(
            1).split("、")] if keywords_match else []

        # 生成同音词/近音词变体
        keywords = []
        homophone_map = {
            '清真': ['清蒸'],
            '饭堂': ['食堂'],
            '餐厅': ['饭厅'],
            '选课': ['改选', '退选'],
            '快递': ['配送'],
            '社团': ['协会', '组织'],
            '成绩': ['分数', '绩点'],
            '导师': ['老师', '教授'],
            '论文': ['文章', '报告'],
            '作业': ['任务', '练习'],
            '讲座': ['报告会', '研讨会'],
            '维修': ['修理', '检修']
        }
        for kw in base_keywords:
            keywords.append(kw)
            for orig, variants in homophone_map.items():
                if orig in kw:
                    for var in variants:
                        keywords.append(kw.replace(orig, var))

        # 去重
        keywords = list(set(keywords))

        # 处理剩余内容 - 移除标题和关键词行
        remaining_content = content.split('\n', 1)[1]  # 移除标题行
        if keywords_match:
            # 找到关键词行并移除
            remaining_content = remaining_content.replace(
                keywords_match.group(0), '', 1)

        return TopicDocument(
            title=title,
            keywords=keywords,
            content=remaining_content.strip(),  # 使用剩余内容
        )


# 示例用法
if __name__ == "__main__":
    loader = DocumentLoader()
    documents = loader.load_all_documents()
    print(f"已加载 {len(documents)} 个主题文档")
    for topic, doc in documents.items():
        print(f"\n主题: {doc.title}")
        print(f"关键词: {', '.join(doc.keywords)}")
        print(f"文档内容长度: {len(doc.content)} 字符")
