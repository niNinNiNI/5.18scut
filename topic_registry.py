"""统一管理校园助手系统的话题和关键词"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TopicDefinition:
    """话题定义数据类"""
    display_name: str      # 显示名称
    keywords: List[str]    # 关联关键词
    data_file: str         # 数据文件路径
    description: str       # 话题描述
    content: str = ""      # 文件内容


class TopicRegistry:
    """话题注册中心"""

    def __init__(self):
        self.topics: Dict[str, TopicDefinition] = self._initialize_topics()
        self._load_topic_contents()

    def _load_topic_contents(self):
        """加载所有话题文件内容"""
        import os
        # 获取当前文件所在目录（topic_registry.py的路径即项目根目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = current_dir  # 直接使用当前文件所在目录作为项目根目录
        for topic_id, topic_def in self.topics.items():
            try:
                # data_file已经是相对于项目根目录的路径，如 'data/topics/file.md'
                # 所以直接将BASE_DIR（项目根目录）与data_file拼接
                file_path = os.path.join(BASE_DIR, topic_def.data_file.replace('/', os.sep))
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        topic_def.content = f.read()
                else:
                    print(f"警告: 话题文件不存在 - {file_path}")
            except Exception as e:
                print(f"加载话题内容失败 {topic_id}: {str(e)}")

    def _initialize_topics(self) -> Dict[str, TopicDefinition]:
        """初始化标准话题集合"""
        return {
            "academic": TopicDefinition(
                display_name="学术资源",
                keywords=["图书馆", "学术支持", "学习资源", "文献", "数据库"],
                data_file="data/topics/Academic_Resources.md",
                description="图书馆、学术支持、学习资源等相关信息"
            ),
            "life_services": TopicDefinition(
                display_name="基础生活服务",
                keywords=["宿舍", "洗衣", "水电", "维修", "保洁"],
                data_file="data/topics/Basic_Life_Services.md",
                description="宿舍、洗衣、水电等基础生活服务信息"
            ),
            "activities": TopicDefinition(
                display_name="校园活动",
                keywords=["社团", "活动", "讲座", "比赛", "晚会"],
                data_file="data/topics/Campus_Activities_and_Events.md",
                description="社团活动、讲座、比赛等校园活动信息"
            ),
            "dining": TopicDefinition(
                display_name="餐饮选项",
                keywords=["食堂", "清真食堂", "餐厅", "外卖", "美食", "营业时间"],
                data_file="data/topics/Campus_and_Nearby_Dining_Options.md",
                description="食堂、周边餐厅、外卖等餐饮信息"
            ),
            "navigation": TopicDefinition(
                display_name="校园导航",
                keywords=["地图", "建筑", "设施", "位置", "导航"],
                data_file="data/topics/Campus_Navigation_and_Facilities.md",
                description="校园地图、建筑位置、设施使用等信息"
            ),
            "policies": TopicDefinition(
                display_name="校园政策",
                keywords=["规定", "安全", "紧急", "违纪", "申诉"],
                data_file="data/topics/Campus_Policies_and_Safety.md",
                description="校园规定、安全事项、紧急处理等信息"
            ),
            "courses": TopicDefinition(
                display_name="选课指南",
                keywords=["选课", "课程", "学分", "退选", "改选"],
                data_file="data/topics/Course_Selection_Guide.md",
                description="选课流程、课程评价、学分要求等信息"
            ),
            "contacts": TopicDefinition(
                display_name="重要联系方式",
                keywords=["电话", "办公", "部门", "紧急", "联系"],
                data_file="data/topics/Important_Contact_Numbers.md",
                description="重要电话、办公部门联系方式等信息"
            ),
            "procedures": TopicDefinition(
                display_name="办事流程",
                keywords=["申请", "流程", "手续", "审批", "备案"],
                data_file="data/topics/Procedures_and_Processes.md",
                description="各类申请流程、手续办理等信息"
            ),
            "transportation": TopicDefinition(
                display_name="周边交通",
                keywords=["公交", "地铁", "校车", "共享单车", "电动车"],
                data_file="data/topics/Surrounding_Transportation.md",
                description="公交、地铁、共享单车等交通信息"
            )
        }

    def get_topic(self, topic_id: str) -> Optional[TopicDefinition]:
        """获取指定话题的定义"""
        topic = self.topics.get(topic_id.lower())
        if topic and not topic.content:
            self._load_topic_content(topic)
        return topic

    def _load_topic_content(self, topic_def: TopicDefinition):
        """加载单个话题文件内容"""
        import os
        # 获取当前文件所在目录（topic_registry.py的路径即项目根目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = current_dir  # 直接使用当前文件所在目录作为项目根目录
        try:
            # data_file已经是相对于项目根目录的路径，如 'data/topics/file.md'
            # 所以直接将BASE_DIR（项目根目录）与data_file拼接
            file_path = os.path.join(BASE_DIR, topic_def.data_file.replace('/', os.sep))
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    topic_def.content = f.read()
            else:
                print(f"警告: 话题文件不存在 - {file_path}")
        except Exception as e:
            print(f"加载话题内容失败 {topic_def.display_name}: {str(e)}")

    def list_topics(self) -> Dict[str, str]:
        """获取所有话题的显示名称和描述"""
        return {k: f"{v.display_name} - {v.description}"
                for k, v in self.topics.items()}

    def find_topics_by_keyword(self, keyword: str) -> List[str]:
        """通过关键词查找相关话题"""
        keyword = keyword.lower().strip()
        return [topic_id for topic_id, definition in self.topics.items()
                if any(keyword in k.lower() for k in definition.keywords)]
