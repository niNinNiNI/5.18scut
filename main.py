
"""
校园智能助手主程序模块

该模块实现了校园智能助手的图形用户界面(GUI)和核心功能逻辑，包括：
- 用户登录/注册系统
- 校园话题选择界面
- 智能问答聊天界面
- 对话历史记录查看
- 系统配置管理

主要类:
    CampusAssistant: 实现助手核心功能的GUI应用类

依赖:
    - tkinter: 用于构建GUI界面
    - nlp_processor: 自然语言处理模块
    - database: 用户和对话历史数据管理
    - openai: 大语言模型API访问



代码结构说明:
1. 初始化部分:
   - 加载环境变量和配置
   - 初始化各功能模块

2. GUI构建部分:
   - 主窗口和框架创建
   - 样式配置
   - 各界面组件(登录、话题选择、聊天等)

3. 核心功能:
   - 用户认证管理
   - 话题选择和处理
   - 聊天交互
   - 历史记录管理

4. 辅助功能:
   - 调试支持
   - 错误处理
   - 状态管理

"""

"""
校园智能助手主程序模块 - 详细注释版

本模块实现了校园智能助手的图形用户界面(GUI)和核心功能逻辑，采用MVC-like架构：
- Model: database.py, nlp_processor.py 处理数据和业务逻辑
- View: 本文件中的GUI组件 (tkinter实现)
- Controller: CampusAssistant类协调模型和视图

主要功能流程:
1. 初始化应用程序 (加载配置、创建主窗口)
2. 用户认证 (登录/注册/游客模式)
3. 话题选择 (用户选择感兴趣的主题)
4. 聊天交互 (处理用户查询并生成回答)
5. 历史记录管理 (保存和查看对话历史)

关键设计特点:
- 模块化设计: 功能分离到不同模块
- 响应式GUI: 使用ttk主题和自定义样式
- 状态管理: 跟踪当前用户、话题和对话历史
- 错误处理: 异常捕获和用户友好提示
- 动画效果: 消息发送/接收动画增强用户体验

注意: 本文件是应用程序的入口点和核心控制器，协调各模块工作。
"""

import os
import time
from nlp_processor import NLPProcessor
from database import DatabaseManager
import openai
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox

# 加载并检查环境变量
load_dotenv()  # 从.env文件加载环境变量
if not os.getenv("OPENAI_API_KEY"):
    # 如果缺少OpenAI API密钥则抛出异常，确保程序不会在没有API密钥的情况下运行
    raise ValueError("请正确配置.env文件中的OPENAI_API_KEY")


class CampusAssistant:
    """
    校园智能助手核心类 (控制器)

    职责:
    - 管理应用程序生命周期
    - 协调用户界面和业务逻辑
    - 处理用户交互事件
    - 维护应用程序状态

    关键属性说明:
        root: 主Tkinter窗口 (应用程序容器)
        current_user: 当前登录用户 (None表示游客模式)
        current_topic: 当前选择的话题ID (academic, life_services等)
        message_history: 当前会话的消息历史 (用于上下文对话)
        nlp_processor: NLP处理实例 (负责查询理解和响应生成)
        user_manager: 用户数据库管理实例 (处理用户认证和历史存储)

    状态管理:
        - 用户状态: 登录用户/游客
        - 话题状态: 当前选择的话题
        - 界面状态: 当前显示的界面 (登录/话题选择/聊天)

    设计模式:
        - 观察者模式: GUI事件绑定到处理方法
        - 分层架构: 分离界面、控制和数据处理
        - 状态模式: 不同界面对应不同的状态和行为
    """

    def __init__(self):
        """
        应用程序初始化 (构造函数)

        关键初始化步骤:
        1. 核心模块初始化: 
           - NLP处理器 (自然语言理解与生成)
           - 用户数据库管理器 (用户认证和历史存储)
        2. 状态初始化:
           - current_user: None (未登录)
           - current_topic: None (未选择话题)
           - message_history: 空列表 (无对话历史)
        3. GUI系统初始化:
           - 创建主窗口 (root)
           - 配置全局样式 (主题/颜色/字体)
           - 创建主容器框架 (main_container)
        4. 显示初始界面 (登录窗口)

        样式配置说明:
           - 主题: 'clam' (ttk内置主题)
           - 配色方案: 
                primary_color = '#4a98f7' (主色调-蓝)
                secondary_color = '#e8f4ff' (辅助色-浅蓝)
                background_color = '#f8fbff' (背景色)
                text_color = '#2c3e50' (文字色)
                accent_color = '#2ecc71' (强调色-绿)
           - 组件样式: 为按钮、标签、输入框等定义统一风格

        注意: 所有GUI组件都使用ttk样式系统，确保界面一致性和可维护性。
        """
        # 初始化核心功能模块
        self.nlp_processor = NLPProcessor()  # 自然语言处理模块
        self.user_manager = DatabaseManager()  # 用户数据库管理模块
        self.current_user = None  # 当前登录用户，None表示未登录或游客模式
        self.current_topic = None  # 当前选择的话题，None表示未选择
        # 消息历史记录，格式为[{"role": "user/assistant", "content": "消息内容"}]
        self.message_history = []

        # 配置GUI全局样式 - 使用clam主题作为基础
        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题

        # 定义配色方案
        primary_color = '#4a98f7'  # 主色调(蓝色)
        secondary_color = '#e8f4ff'  # 次要色调(浅蓝)
        background_color = '#f8fbff'  # 背景色(浅白蓝)
        text_color = '#2c3e50'  # 主要文字颜色(深蓝灰)
        accent_color = '#2ecc71'  # 强调色(绿色)

        # 配置标准按钮样式 (再次增大字号和尺寸)
        style.configure('TButton',
                        font=('微软雅黑', 18, 'bold'),  # 增大字号到18
                        foreground='white',  # 文字颜色
                        background=primary_color,  # 背景色
                        borderwidth=1,  # 边框宽度
                        relief='solid',  # 边框样式
                        padding=15)  # 增大内边距到15
        # 按钮交互状态样式
        style.map('TButton',
                  background=[('active', '#3a7ad9'), ('pressed', '#2a5a9b')])

        # 配置强调按钮样式(用于重要操作)
        style.configure('Accent.TButton',
                        font=('微软雅黑', 20, 'bold'),  # 增大字号到18
                        background=accent_color,  # 绿色背景
                        foreground='white',  # 白色文字
                        padding=17)  # 增大内边距到15
        style.map('Accent.TButton',
                  background=[('active', '#27ae60'), ('pressed', '#1e8449')])

        # 配置话题选择按钮样式 (再次增大字号和尺寸)
        style.configure('Topic.TButton',
                        font=('微软雅黑', 19),  # 增大字号到17
                        foreground=text_color,  # 文字颜色
                        background=secondary_color,  # 浅蓝背景
                        padding=20)  # 增大内边距到18
        # 话题按钮交互状态
        style.map('Topic.TButton',
                  background=[('active', '#d0e8f0'), ('pressed', '#b8d8e8')])

        # 配置标签样式
        style.configure('TLabel',
                        font=('微软雅黑', 15),  # 标准字体(增大2pt)
                        foreground=text_color,  # 文字颜色
                        background=background_color)  # 背景色

        # 配置输入框样式
        style.configure('TEntry',
                        font=('微软雅黑', 15),  # 标准字体(增大2pt)
                        fieldbackground='#ffffff',  # 输入区域背景(白色)
                        foreground=text_color,  # 文字颜色
                        borderwidth=1,  # 边框宽度
                        relief='solid',  # 边框样式
                        padding=5)  # 内边距

        # 配置框架样式
        style.configure('TFrame',
                        background=background_color)  # 框架背景色

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title('校园智能助手')  # 窗口标题
        self.root.geometry('900x700')  # 初始窗口大小
        self.root.configure(bg='#f5f5f5')  # 窗口背景色

        # 创建主内容容器 - 用于容纳所有界面组件
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)  # 填充整个窗口

        # 显示初始登录界面
        self.show_login_window()  # 进入登录/注册流程

    def show_login_window(self):
        """
        构建并显示登录/注册界面

        GUI结构:
        [标题框架]
          |- 主标题: "校园智能助手"
          |- 副标题: "用户登录"

        [表单框架]
          |- 用户名标签和输入框
          |- 密码标签和输入框

        [按钮容器]
          |- 登录按钮 (绑定login_user方法)
          |- 注册按钮 (绑定register_user方法)
          |- 游客模式按钮 (绑定guest_mode方法)
          |- 退出按钮 (销毁窗口)

        布局技术:
          - 使用Frame嵌套实现层次结构
          - grid布局管理表单元素
          - pack布局管理整体框架
          - 边距(padx/pady)创建呼吸空间

        用户体验优化:
          - 输入框自动聚焦 (username_entry.focus_set())
          - 密码字段掩码显示 (show='*')
          - 统一按钮样式和交互状态
          - 响应式布局 (fill/expand选项)

        注意: 此方法会清除main_container中所有现有组件，然后重建登录界面。
        """
        # 清理当前界面 - 移除所有现有组件
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # 创建主登录框架 - 使用TFrame样式
        login_frame = ttk.Frame(self.main_container)
        login_frame.pack(fill=tk.BOTH, expand=True)
        login_frame.configure(style='TFrame')  # 应用背景色样式

        # 创建标题区域
        title_frame = ttk.Frame(login_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=20)  # 水平填充，添加边距

        # 主标题 - 应用名称
        ttk.Label(title_frame,
                  text='校园智能助手',
                  font=('微软雅黑', 20, 'bold'),  # 再增大2pt
                  foreground="#4c97f3").pack()  # 蓝色主色调
        # 副标题 - 当前功能提示
        ttk.Label(title_frame,
                  text='用户登录',
                  font=('微软雅黑', 16),  # 再增大2pt
                  foreground='#2c3e50').pack(pady=5)  # 深灰色文字

        # 创建表单容器 - 用于放置输入框和按钮
        login_container = ttk.Frame(login_frame)
        login_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 表单边框 - 为表单添加视觉层次
        form_border = ttk.Frame(login_container)
        form_border.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 表单内容框架
        login_form = ttk.Frame(form_border)
        login_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 用户名输入行
        ttk.Label(login_form,
                  text='用户名:',
                  font=('微软雅黑', 12)).grid(
            row=0, column=0,
            sticky='e', padx=5, pady=10)
        self.username_entry = ttk.Entry(login_form,
                                        font=('微软雅黑', 12))
        self.username_entry.grid(row=0, column=1,
                                 sticky='ew', padx=5, pady=10)

        # 密码输入行
        ttk.Label(login_form,
                  text='密码:',
                  font=('微软雅黑', 12)).grid(
            row=1, column=0,
            sticky='e', padx=5, pady=10)
        self.password_entry = ttk.Entry(
            login_form,
            show='*',  # 密码显示为星号
            font=('微软雅黑', 12))
        self.password_entry.grid(row=1, column=1,
                                 sticky='ew', padx=5, pady=10)

        # 配置表单列权重 - 使输入框可以水平扩展
        login_form.grid_columnconfigure(1, weight=1)

        # 添加装饰分隔线
        ttk.Separator(form_border, orient='horizontal').pack(
            fill=tk.X, pady=10)

        # 创建按钮容器 - 用于放置操作按钮
        button_container = ttk.Frame(login_form)
        button_container.grid(row=2, column=0, columnspan=2,
                              sticky='ew', padx=20, pady=10)
        button_container.grid_columnconfigure(0, weight=1)  # 左侧扩展

        # 登录和注册按钮组
        button_frame = ttk.Frame(button_container)
        button_frame.grid(row=0, column=0, sticky='w')

        # 登录按钮 - 使用强调样式
        ttk.Button(button_frame,
                   text='登录',
                   command=self.login_user,  # 绑定登录方法
                   style='Accent.TButton',
                   width=10).grid(row=0, column=0, padx=5)

        # 注册按钮 - 标准样式
        ttk.Button(button_frame,
                   text='注册',
                   command=self.register_user,  # 绑定注册方法
                   style='TButton',
                   width=10).grid(row=0, column=1, padx=5)

        # 游客模式和退出按钮 - 放置在右侧
        ttk.Button(button_container,
                   text='游客模式',
                   command=self.guest_mode,  # 绑定游客模式方法
                   style='TButton',
                   width=15).grid(row=0, column=1,
                                  sticky='e', pady=5)

        # 退出按钮
        ttk.Button(button_container,
                   text='退出',
                   command=self.root.destroy,
                   style='TButton',
                   width=15).grid(row=0, column=2,
                                  sticky='e', padx=5)

        # 设置初始焦点到用户名输入框 - 提升用户体验
        self.username_entry.focus_set()

    def login_user(self):
        """
        用户登录处理逻辑

        步骤:
        1. 获取输入: 从GUI输入框获取用户名和密码
        2. 输入验证: 检查非空 (空输入显示警告)
        3. 凭证验证: 通过user_manager.verify_user检查数据库
        4. 状态切换:
           - 成功: 设置current_user -> 显示话题选择界面
           - 失败: 显示错误提示
        5. 异常处理: 捕获数据库异常并显示错误

        安全考虑:
           - 密码在内存中以明文暂存 (短暂存在)
           - 数据库验证使用安全比对 (数据库模块处理)
           - 错误消息不透露具体系统细节 (防止信息泄露)

        注意: 登录成功后，应用程序状态变为认证用户状态，可访问历史记录等功能。
        """
        # 获取并清理输入
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # 输入验证
        if not username or not password:
            messagebox.showwarning('提示', '用户名和密码不能为空')
            return

        try:
            # 调用数据库验证用户
            if self.user_manager.verify_user(username, password):
                # 登录成功处理
                self.current_user = username  # 更新当前用户状态
                self.show_topic_selection()    # 跳转到话题选择界面
            else:
                # 登录失败处理
                messagebox.showerror('错误', '用户名或密码错误')
        except Exception as e:
            # 数据库错误处理
            messagebox.showerror('数据库错误', f'验证失败: {str(e)}')

    def register_user(self):
        """
        用户注册处理逻辑

        步骤:
        1. 获取输入: 从GUI输入框获取用户名和密码
        2. 输入验证: 检查非空 (空输入显示警告)
        3. 用户创建: 通过user_manager.create_user创建新用户
        4. 冲突处理: 用户名已存在时显示错误
        5. 状态切换:
           - 成功: 设置current_user -> 显示话题选择界面
           - 失败: 保持登录界面
        6. 异常处理: 捕获数据库异常并显示错误

        安全考虑:
           - 密码在数据库中应哈希存储 (由数据库模块处理)
           - 用户名需满足数据库约束 (长度、字符集等)

        注意: 注册成功后自动登录并进入话题选择界面。
        """
        # 获取并清理输入
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # 输入验证
        if not username or not password:
            messagebox.showwarning('提示', '用户名和密码不能为空')
            return

        try:
            # 调用数据库创建用户
            if self.user_manager.create_user(username, password):
                # 注册成功处理
                self.current_user = username  # 更新当前用户状态
                self.show_topic_selection()   # 跳转到话题选择界面
            else:
                # 用户名已存在情况
                messagebox.showerror('错误', '用户名已存在')
        except Exception as e:
            # 数据库错误处理
            messagebox.showerror('数据库错误', f'注册失败: {str(e)}')

    def guest_mode(self):
        self.current_user = None
        self.show_topic_selection()

    def setup_chat_interface(self):
        """
        构建聊天界面组件

        界面结构:
        [聊天记录框] (带滚动条)
          |- 消息显示区域 (Text组件)
          |- 垂直滚动条

        [输入控制区]
          |- 消息输入框 (Entry组件)
          |- 清除按钮 (清除聊天记录)
          |- 发送按钮 (触发消息处理)

        [状态栏] (底部)
          |- 显示当前状态和最后更新时间

        关键组件说明:
          1. chat_history: Text组件, 显示对话内容
          2. user_input: Entry组件, 用户输入消息
          3. send_btn: 发送按钮, 绑定on_send方法
          4. clear_btn: 清除按钮, 绑定clear_chat方法
          5. status_bar: 状态标签, 显示系统状态

        样式特性:
          - 聊天消息气泡样式 (通过tag实现)
          - 响应式布局 (随窗口缩放)
          - 动画效果 (消息发送/接收动画)
          - 状态提示 (实时状态更新)

        注意: 此方法创建所有聊天界面组件，但不显示欢迎消息 (由set_topic触发)
        """
        # 保存组件引用以便后续销毁
        self.chat_frame = ttk.Frame(self.root, style='TFrame')
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 聊天记录显示框 - 添加圆角和阴影效果
        chat_container = ttk.Frame(self.chat_frame, style='TFrame')
        chat_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加边框和阴影效果
        chat_border = ttk.Frame(chat_container)
        chat_border.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 聊天历史框 - 美化样式 (减小高度确保状态栏可见)
        self.chat_history = tk.Text(
            chat_border, state='disabled', wrap=tk.WORD,
            width=80, height=13, font=('微软雅黑', 15),  # 高度从25减小到20
            bg='#ffffff', fg='#2c3e50',
            padx=15, pady=15,
            selectbackground='#4a98f7', selectforeground='white',
            borderwidth=0, highlightthickness=0)

        scrollbar = ttk.Scrollbar(chat_border, command=self.chat_history.yview)
        self.chat_history.configure(yscrollcommand=scrollbar.set)

        # 使用grid布局
        self.chat_history.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        scrollbar.grid(row=0, column=1, sticky='ns')
        chat_border.grid_rowconfigure(0, weight=1)
        chat_border.grid_columnconfigure(0, weight=1)

        # 输入框和发送按钮 - 添加圆角和阴影
        input_container = ttk.Frame(self.chat_frame)
        input_container.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.input_frame = ttk.Frame(input_container)
        self.input_frame.pack(fill=tk.X, pady=5)

        # 输入控件框架 - 添加背景和圆角
        input_controls = ttk.Frame(self.input_frame)
        input_controls.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.user_input = ttk.Entry(
            input_controls, font=('微软雅黑', 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X,
                             expand=True, padx=(0, 10), ipady=5)

        # 清除按钮 - 使用强调样式
        self.clear_btn = ttk.Button(
            input_controls, text='清除', command=self.clear_chat,
            style='Accent.TButton', width=8)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 发送按钮 - 使用强调样式
        self.send_btn = ttk.Button(
            input_controls, text='发送', command=self.on_send,
            style='Accent.TButton', width=8)
        self.user_input.bind('<Return>', lambda event: self.on_send(event))
        self.send_btn.pack(side=tk.LEFT)

        # 添加底部装饰线
        ttk.Separator(input_container, orient='horizontal').pack(
            fill=tk.X, pady=5)

        # 底部状态栏 - 美化样式
        status_frame = ttk.Frame(self.chat_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))

        self.status_bar = ttk.Label(
            status_frame, text='就绪',
            anchor=tk.W, font=('微软雅黑', 11),  # 增大2pt
            background='#e8f4ff',
            padding=(10, 5))
        self.status_bar.pack(fill=tk.X)

        # 设置焦点到输入框
        self.user_input.focus_set()

    def clear_chat(self):
        """清除聊天记录"""
        self.chat_history.configure(state='normal')
        self.chat_history.delete('1.0', tk.END)
        self.chat_history.configure(state='disabled')
        self.status_bar.config(text='聊天记录已清除')

    def on_send(self, event=None):
        print("发送事件被触发")  # 调试信息
        print(f"事件来源: {'按钮' if event is None else '回车键'}")  # 调试信息

        query = self.user_input.get().strip()
        if not query:
            return

        print(f"用户输入: {query}")  # 调试信息
        self.user_input.delete(0, tk.END)
        self.user_input.focus_set()

        print("正在更新聊天记录...")  # 调试信息
        self.update_chat_history(query, 'user')
        response = self.handle_query(query)
        self.update_chat_history(response, 'assistant')
        print("聊天记录更新完成")  # 调试信息

    def update_chat_history(self, message: str, role: str):
        """
        更新聊天历史显示 (核心渲染方法)

        功能:
        1. 将消息添加到聊天记录文本框
        2. 根据消息角色应用不同样式
        3. 实现消息发送/接收动画效果
        4. 自动滚动到底部显示最新消息

        参数:
          message: 消息内容字符串
          role: 消息角色 ('user'或'assistant')

        渲染逻辑:
          - 用户消息: 蓝色气泡 (右侧显示)
          - 助手消息: 绿色气泡 (左侧显示)
          - 添加时间戳和角色标签

        动画效果:
          - 用户消息: "发送中..."动画
          - 助手消息: 逐字显示效果 (模拟输入过程)

        技术实现:
          1. 使用Text组件的tag系统定义样式
          2. 定时器模拟动画效果 (time.sleep)
          3. 状态栏实时更新
          4. 自动滚动 (see tk.END)

        注意: 此方法会修改聊天记录组件的状态 (normal->disabled切换)
        """
        self.chat_history.configure(state='normal')

        # 获取当前时间
        timestamp = time.strftime('%H:%M', time.localtime())

        # 设置不同角色的文本样式
        if role == 'user':
            # 用户消息样式 - 蓝色气泡
            self.chat_history.tag_configure('user_msg',
                                            foreground='#ffffff',
                                            font=('微软雅黑', 11),
                                            background='#1a73e8',
                                            lmargin1=20, lmargin2=20,
                                            rmargin=10,
                                            spacing1=5, spacing3=5,
                                            borderwidth=5,
                                            relief='ridge')

            self.chat_history.tag_configure('user_header',
                                            foreground='#3498db',
                                            font=('微软雅黑', 9, 'bold'))

            # 添加发送动画效果
            self.status_bar.config(text="消息发送中...")
            self.root.update()

            self.chat_history.insert(
                tk.END, f'[{timestamp}] 你:\n', 'user_header')
            self.chat_history.insert(tk.END, f'{message}\n\n', 'user_msg')

            # 模拟发送动画
            for i in range(3):
                self.status_bar.config(text=f"消息发送中{'.'*(i+1)}")
                self.root.update()
                time.sleep(0.2)
        else:
            # 助手消息样式 - 绿色气泡
            self.chat_history.tag_configure('assistant_msg',
                                            foreground='#ffffff',
                                            font=('微软雅黑', 11),
                                            background='#0b8043',
                                            lmargin1=20, lmargin2=20,
                                            rmargin=10,
                                            spacing1=5, spacing3=5,
                                            borderwidth=5,
                                            relief='ridge')

            self.chat_history.tag_configure('assistant_header',
                                            foreground='#27ae60',
                                            font=('微软雅黑', 9, 'bold'))

            # 添加接收动画效果
            self.status_bar.config(text="正在接收回复...")
            self.root.update()

            self.chat_history.insert(
                tk.END, f'[{timestamp}] 助手:\n', 'assistant_header')

            # 逐字显示效果
            words = message.split(' ')
            for i, word in enumerate(words):
                self.chat_history.insert(tk.END, word + ' ', 'assistant_msg')
                if i % 3 == 0:  # 每3个单词更新一次
                    self.chat_history.see(tk.END)
                    self.root.update()
                    time.sleep(0.05)
            self.chat_history.insert(tk.END, '\n\n', 'assistant_msg')

        self.chat_history.configure(state='disabled')
        self.chat_history.see(tk.END)

        # 更新状态栏
        topic_name = self.current_topic if self.current_topic else "未选择"
        self.status_bar.config(
            text=f"当前话题: {topic_name} | 最后消息: {timestamp} | 状态: 就绪")

    def show_topic_selection(self):
        """
        显示话题选择界面

        界面特点:
          - 网格布局话题按钮 (2列)
          - 可滚动区域 (支持大量话题)
          - 响应式设计 (按钮自适应大小)
          - 视觉分组 (使用Frame容器)

        话题数据结构:
          [ (topic_id, display_name, description), ... ]

        按钮功能:
          - 每个话题按钮绑定set_topic方法
          - 历史记录按钮 (登录用户可见)
          - 退出程序按钮

        布局技术:
          1. Canvas+Scrollbar实现可滚动区域
          2. grid布局管理话题按钮
          3. 动态行/列配置 (grid_rowconfigure/columnconfigure)
          4. 样式映射 (Topic.TButton样式)

        注意: 此界面是应用程序的主导航界面，登录状态影响可用功能。
        """
        # 清除所有现有界面组件（除了main_container）
        for widget in self.root.winfo_children():
            if widget != self.main_container:
                widget.destroy()

        # 清除主容器内的组件
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # 创建话题选择界面 - 美化样式
        topic_frame = ttk.Frame(self.main_container)
        topic_frame.pack(fill=tk.BOTH, expand=True)
        topic_frame.configure(style='TFrame')

        # 添加标题
        title_frame = ttk.Frame(topic_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(title_frame, text='请选择查询话题',
                  font=('微软雅黑', 16, 'bold'),
                  foreground='#4a98f7').pack()

        # 主框架容器
        main_container = ttk.Frame(topic_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 主框架
        main_frame = ttk.Frame(main_container, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 创建话题列表（直接显示所有话题）
        topics = [
            ("academic",       "学术资源",       "图书馆、学术支持、学习资源等"),
            ("life_services",  "基础生活服务",   "宿舍、洗衣、水电等基础生活服务"),
            ("activities",     "校园活动",       "社团活动、讲座、比赛等"),
            ("navigation",     "校园导航",       "校园地图、建筑位置、设施使用等"),
            ("policies",       "校园政策",       "校园规定、安全事项、紧急处理等"),
            ("courses",        "选课指南",       "选课流程、课程评价、学分要求等"),
            ("contacts",       "重要联系方式",   "重要电话、办公部门联系方式等"),
            ("procedures",     "办事流程",       "各类申请流程、手续办理等"),
            ("dining",         "餐饮选项",       "食堂、周边餐厅、外卖等"),
            ("transportation", "周边交通",       "公交、地铁、共享单车等交通信息")
        ]

        # 创建可滚动区域
        canvas = tk.Canvas(main_frame, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 配置网格布局
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        # 配置话题按钮样式 - 先于按钮创建
        style = ttk.Style()
        style.configure('Topic.TButton',
                        font=('微软雅黑', 14),  # 增大字号
                        padding=(15, 12),      # 增加内边距
                        foreground='#333',
                        background='#e8f4f8',
                        wraplength=300)        # 设置自动换行
        style.map('Topic.TButton',
                  background=[('active', '#d0e8f0'), ('pressed', "#96bbce")])

        # 添加话题按钮 - 使用网格布局并填充空间
        for i, (topic_id, display_name, desc) in enumerate(topics):
            row = i // 2
            col = i % 2

            # 创建带自动换行的按钮文本
            btn_text = f'{display_name}\n({topic_id})\n{desc}'

            btn = ttk.Button(
                scrollable_frame,
                text=btn_text,
                command=lambda t=topic_id: self.set_topic(t),
                style='Topic.TButton',
            )
            # 使用sticky='nsew'让按钮填充整个网格单元
            btn.grid(row=row, column=col, padx=15,
                     pady=15, sticky='nsew')  # 增加边距

            # 配置按钮所在的行和列权重为1，使其可扩展
            scrollable_frame.grid_rowconfigure(row, weight=1)
            scrollable_frame.grid_columnconfigure(col, weight=1)

        # 布局Canvas和滚动条 - 确保Canvas填充整个可用空间
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 配置主框架的权重，确保Canvas可扩展
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # 添加底部按钮区域（垂直排列）
        button_container = ttk.Frame(main_frame)
        button_container.pack(fill=tk.X, pady=10)

        # 创建垂直排列的按钮框架
        vertical_btn_frame = ttk.Frame(button_container)
        vertical_btn_frame.pack(anchor=tk.CENTER)  # 居中显示

        # 历史记录按钮（仅登录用户可见）
        if self.current_user:
            history_btn = ttk.Button(
                vertical_btn_frame,
                text='查看历史记录',
                command=self.show_chat_history_gui,
                style='TButton'
            )
            history_btn.pack(pady=5, fill=tk.X)  # 垂直排列，上下间距5px

        # 退出按钮
        exit_btn = ttk.Button(
            vertical_btn_frame,
            text='退出程序',
            command=self.root.destroy,
            style='TButton'
        )
        exit_btn.pack(pady=5, fill=tk.X)  # 垂直排列，上下间距5px

    def get_topic_name(self, topic_id: str) -> str:
        """根据话题ID获取显示名称"""
        topic_map = {
            "academic": "学术资源",
            "life_services": "基础生活服务",
            "activities": "校园活动",
            "navigation": "校园导航",
            "policies": "校园政策",
            "courses": "选课指南",
            "contacts": "重要联系方式",
            "procedures": "办事流程",
            "dining": "餐饮选项",
            "transportation": "周边交通"
        }
        return topic_map.get(topic_id, "通用话题")

    def set_topic(self, topic_id: str):
        # 清除所有现有界面组件
        for widget in self.root.winfo_children():
            if widget != self.main_container:  # 保留主容器
                widget.destroy()

        # 清除主容器内的组件
        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.current_topic = topic_id

        # 创建聊天界面
        self.setup_chat_interface()

        # 发送欢迎消息
        welcome_msg = f"""欢迎使用校园智能助手！
        
当前话题: {self.get_topic_name(topic_id)}
您可以:
- 直接输入问题获取解答
- 输入"切换"或"change"更换话题
- 或点击"返回话题选择"按钮返上一级
请问有什么可以帮您？"""
        self.update_chat_history(welcome_msg, 'assistant')

        # 添加功能按钮区域并保存引用
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # 返回话题选择按钮
        ttk.Button(self.button_frame,
                   text='返回话题选择',
                   command=self.show_topic_selection,
                   style='Accent.TButton').pack(side=tk.LEFT, padx=5)

        # 历史记录按钮(仅登录用户可见)
        if self.current_user:
            ttk.Button(self.button_frame,
                       text='查看历史记录',
                       command=self.show_chat_history_gui,
                       style='Accent.TButton').pack(side=tk.LEFT, padx=5)

        # 退出按钮
        ttk.Button(self.button_frame,
                   text='退出系统',
                   command=self.root.destroy,
                   style='TButton').pack(side=tk.RIGHT, padx=5)

    def login_or_register(self) -> bool:
        """处理用户登录或注册(GUI版本)"""
        self.show_login_window()
        return True

    def select_topic(self) -> bool:
        """处理话题选择"""
        self.show_topic_selection()
        return True

    def main_menu(self) -> bool:
        """主菜单(GUI版本)"""
        self.show_topic_selection()
        return True

    def handle_query(self, user_input: str) -> str:
        """
        处理用户查询 (核心业务逻辑)

        功能流程:
        1. 特殊命令处理:
           - 话题切换 ("切换", "change")
           - 调试模式控制 ("开启调试"/"关闭调试")

        2. 普通查询处理:
           a. 准备查询参数:
              - 用户输入文本
              - 当前话题ID
              - 最近的对话历史 (最后10条)
           b. 调用NLP处理器生成响应
           c. 更新消息历史
           d. 记录对话历史到数据库 (登录用户)

        3. 返回助手响应

        关键组件交互:
          - nlp_processor.process_query: 生成自然语言响应
          - user_manager.log_chat: 记录对话历史 (数据库)

        状态管理:
          - 维护message_history列表 (当前会话历史)
          - 跟踪current_topic (当前话题上下文)

        注意: 此方法连接用户界面和NLP处理核心，是系统的关键路径。
        """
        # 处理话题切换命令
        if user_input.lower() in ["切换", "change"]:
            self.show_topic_selection()
            return "请选择新的话题"

        # 处理调试模式控制指令
        if "开启调试" in user_input:
            from config import Config
            Config.toggle_debug(True)
            return "已成功开启全局调试模式"
        elif "关闭调试" in user_input:
            from config import Config
            Config.toggle_debug(False)
            return "已成功关闭全局调试模式"

        # 显示当前话题状态
        topic_status = f"当前话题: {self.current_topic}" if self.current_topic else "当前检索范围: 全部话题"
        print(f"[系统提示] {topic_status}")

        # 使用NLP处理器处理查询
        response = self.nlp_processor.process_query(
            user_input,
            self.current_topic,
            # 限制历史记录长度
            # 显式转换为list
            list(self.message_history[-10:]) if self.message_history else None
        )

        # 更新消息历史
        self.message_history.append({"role": "user", "content": user_input})
        self.message_history.append({"role": "assistant", "content": response})

        # 记录对话历史到数据库
        if self.current_user:
            try:
                user_id = self.user_manager.get_user_id(self.current_user)
                if user_id:
                    success = self.user_manager.log_chat(
                        user_id,
                        user_input,
                        response,
                        self.current_topic
                    )
                    if not success:
                        print(f"[警告] 未能记录对话历史到数据库")
            except Exception as e:
                print(f"[错误] 记录对话历史失败: {str(e)}")

        return response

    def show_chat_history_gui(self):
        """在GUI中显示历史记录"""
        if not self.current_user:
            messagebox.showinfo("提示", "请先登录以查看历史记录")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("历史记录")
        history_window.geometry("800x600")

        text = tk.Text(history_window, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(history_window, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(expand=True, fill=tk.BOTH)

        user_id = self.user_manager.get_user_id(self.current_user)
        if not user_id:
            text.insert(tk.END, "无法获取用户信息")
            return

        history = self.user_manager.get_chat_history(user_id)
        if not history:
            text.insert(tk.END, "暂无历史记录")
            return

        text.insert(tk.END, "=== 历史对话记录 ===\n\n")
        for i, record in enumerate(history, 1):
            text.insert(tk.END, f"记录 #{i}\n")
            text.insert(tk.END, f"时间: {record['timestamp']}\n")
            if record['topic']:
                text.insert(tk.END, f"话题: {record['topic']}\n")
            text.insert(tk.END, f"问题: {record['query']}\n")
            text.insert(tk.END, f"回答: {record['response']}\n\n")


def main():
    """
    应用程序主入口

    功能:
    1. 检查调试模式配置
    2. 创建CampusAssistant实例
    3. 启动主事件循环 (mainloop)

    执行流程:
      if __name__ == "__main__":
          -> 调用main()
          -> 创建CampusAssistant实例
          -> 启动GUI主循环

    注意: 这是应用程序的启动点，直接执行此文件时运行。
    """
    from config import Config
    if Config.DEBUG:
        print("=== 调试模式已启用 ===")

    assistant = CampusAssistant()
    # 启动GUI主循环
    assistant.root.mainloop()


if __name__ == "__main__":
    main()
