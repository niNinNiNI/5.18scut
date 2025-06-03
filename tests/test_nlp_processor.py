import pytest
from unittest.mock import Mock, patch
from nlp_processor import NLPProcessor, Intent
from topic_registry import TopicRegistry, TopicDefinition


class TestNLPProcessor:
    @pytest.fixture
    def processor(self):
        return NLPProcessor()

    def test_handle_missing_topic(self, processor):
        """测试处理不存在的话题"""
        # Mock topic_registry.get_topic返回None
        with patch.object(processor.topic_registry, 'get_topic', return_value=None):
            response = processor._retrieve_info("测试查询", "不存在的话题")
            assert response == "找不到相关信息，请尝试其他查询"

    def test_handle_missing_topic_file(self, processor):
        """测试处理话题文件缺失的情况"""
        # Mock一个话题定义但文件不存在
        mock_topic = TopicDefinition(
            display_name="测试话题",
            keywords=["测试"],
            data_file="不存在的文件.md",
            description="测试描述"
        )
        with patch.object(processor.topic_registry, 'get_topic', return_value=mock_topic):
            response = processor._retrieve_info("测试查询", "测试话题")
            assert response == "找不到相关信息，请尝试其他查询"

    def test_handle_invalid_topic_path(self, processor):
        """测试处理话题文件路径错误的情况"""
        # Mock一个话题定义但路径格式错误
        mock_topic = TopicDefinition(
            display_name="基础生活服务",
            keywords=["宿舍"],
            data_file="data/topics/Basic Life Services .md",  # 实际文件名是Basic_Life_Services.md
            description="测试描述"
        )
        with patch.object(processor.topic_registry, 'get_topic', return_value=mock_topic):
            response = processor._retrieve_info("宿舍问题", "基础生活服务")
            assert response == "找不到相关信息，请尝试其他查询"

    def test_handle_api_failure(self):
        """测试处理API调用失败的情况"""
        with patch('nlp_processor.openai.OpenAI') as mock_openai:
            # 创建mock客户端
            mock_client = mock_openai.return_value
            # Mock API调用抛出普通异常
            mock_client.chat.completions.create.side_effect = ValueError(
                "API错误")

            # 创建processor实例(此时会使用mock的OpenAI)
            processor = NLPProcessor()

            # Mock一个有效的话题
            mock_topic = TopicDefinition(
                display_name="有效话题",
                keywords=["有效"],
                data_file="data/topics/Valid_Topic.md",
                description="有效描述",
                content="有效内容"
            )
            with patch.object(processor.topic_registry, 'get_topic', return_value=mock_topic):
                response = processor._retrieve_info("有效查询", "有效话题")
                assert response == "服务暂时不可用"

    def test_detect_intent_unknown(self, processor):
        """测试识别未知意图"""
        intent = processor._detect_intent("随机字符串")
        assert intent.name == "UNKNOWN"
        assert intent.confidence == 0.0
