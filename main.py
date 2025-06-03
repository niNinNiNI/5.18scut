
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
    校园智能助手核心类，负责管理整个应用程序的生命周期和功能实现。

    该类封装了校园智能助手的所有功能，包括:
    - 用户界面构建和管理
    - 用户认证流程
    - 话题选择和问答处理
    - 对话历史记录管理
    - 与外部服务(OpenAI API)的集成

    主要属性:
        root (tk.Tk): 主Tkinter窗口对象
        current_user (dict): 当前登录用户的信息字典
        chat_history (list): 当前会话的聊天记录列表
        nlp_processor: NLP处理模块实例
        db: 数据库操作模块实例

    主要方法:
        __init__: 初始化应用程序并构建GUI
        show_login_window: 显示登录/注册界面
        setup_chat_interface: 构建聊天主界面
        login_user: 处理用户登录逻辑
        register_user: 处理用户注册逻辑
        handle_query: 处理用户查询并生成回答
        update_chat_history: 更新并显示聊天历史

    使用示例:
        >>> assistant = CampusAssistant()
        >>> assistant.run()  # 启动应用程序

    注意事项:
        1. 需要先正确配置.env文件中的OPENAI_API_KEY
        2. 数据库模块需要提前初始化
        3. GUI样式依赖于ttk的clam主题
    """

    def __init__(self):
        """
        初始化校园智能助手应用程序。

        该方法负责:
        1. 初始化核心功能模块(NLP处理器和用户数据库)
        2. 配置GUI全局样式和主题
        3. 创建主窗口和容器
        4. 显示初始登录界面

        属性初始化:
            nlp_processor: NLP处理模块实例
            user_manager: 用户数据库管理实例
            current_user: 当前登录用户(初始为None)
            current_topic: 当前选择的话题(初始为None)
            root: 主Tkinter窗口对象
            main_container: 主内容容器框架
            chat_history: 当前会话的对话历史记录
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
        显示登录/注册界面。

        该方法负责:
        1. 清理当前界面内容
        2. 构建登录界面框架和布局
        3. 创建用户名和密码输入表单
        4. 添加登录、注册和游客模式按钮
        5. 设置初始焦点和界面美化

        界面元素:
            - 标题区域: 显示应用名称和"用户登录"提示
            - 表单区域: 用户名和密码输入框
            - 按钮区域: 登录、注册和游客模式按钮
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
        处理用户登录逻辑。

        该方法负责:
        1. 获取并验证用户输入
        2. 调用数据库验证用户凭证
        3. 处理登录成功/失败情况
        4. 更新应用程序状态

        流程:
            1. 获取用户名和密码输入
            2. 检查输入是否为空
            3. 调用数据库验证用户
            4. 根据验证结果:
               - 成功: 更新当前用户并显示话题选择界面
               - 失败: 显示错误消息
            5. 捕获并处理可能的数据库错误

        异常处理:
            - 捕获数据库操作异常并显示友好错误消息
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
        处理用户注册逻辑。

        该方法负责:
        1. 获取并验证用户输入
        2. 检查用户名是否已存在
        3. 调用数据库创建新用户
        4. 处理注册成功/失败情况
        5. 更新应用程序状态

        流程:
            1. 从输入框获取用户名和密码
            2. 检查输入是否为空
            3. 调用数据库创建用户
            4. 根据操作结果:
               - 成功: 更新当前用户并跳转到话题选择界面
               - 失败: 显示相应错误消息
            5. 捕获并处理可能的数据库错误

        输入要求:
            - 用户名: 非空字符串
            - 密码: 非空字符串

        异常处理:
            - 捕获数据库操作异常并显示友好错误消息
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
        """创建聊天界面组件"""
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
        # 清除现有界面
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

        # 添加话题按钮 - 使用网格布局
        for i, (topic_id, display_name, desc) in enumerate(topics):
            row = i // 2
            col = i % 2
            btn = ttk.Button(
                scrollable_frame,
                text=f'{display_name} ({topic_id})\n{desc}',
                command=lambda t=topic_id: self.set_topic(t),
                style='Topic.TButton',
                width=45
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 配置话题按钮样式
        style = ttk.Style()
        style.configure('Topic.TButton', font=('微软雅黑', 13),
                        padding=10, foreground='#333',
                        background='#e8f4f8')
        style.map('Topic.TButton',
                  background=[('active', '#d0e8f0'), ('pressed', "#96bbce")])

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
        # 清除现有界面
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
        """处理用户输入"""
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
    """主程序入口"""
    from config import Config
    if Config.DEBUG:
        print("=== 调试模式已启用 ===")

    assistant = CampusAssistant()
    # 启动GUI主循环
    assistant.root.mainloop()


if __name__ == "__main__":
    main()
