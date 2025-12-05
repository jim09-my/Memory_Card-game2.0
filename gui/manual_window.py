import tkinter as tk
from tkinter import ttk
from config import UIConfig


class ManualWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("SCAU 记忆翻牌游戏说明书")
        self.window.geometry("900x700")
        self.window.config(bg=UIConfig.COLORS['primary'])
        self.window.resizable(False, False)
        
        # 居中显示
        self._center_window()
        
        # 创建界面元素
        self._create_widgets()
        
        # 设置关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = tk.Label(
            self.window,
            text="SCAU 记忆翻牌游戏说明书",
            font=("Arial Rounded MT Bold", 24, "bold"),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['primary']
        )
        title_label.pack(pady=(20, 10))
        
        # 创建笔记本控件用于选项卡
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 配置样式
        self._configure_styles()
        
        # 创建各个选项卡
        self._create_game_intro_tab(notebook)
        self._create_interface_tab(notebook)
        self._create_account_tab(notebook) # 对应道具商城内容
        self._create_gameplay_tab(notebook)
        self._create_achievements_tab(notebook)
        self._create_points_tab(notebook)
        self._create_tips_tab(notebook)
        
    def _configure_styles(self):
        """配置样式"""
        style = ttk.Style()
        style.configure(
            "Custom.TNotebook",
            background=UIConfig.COLORS['primary']
        )
        style.configure(
            "Custom.TNotebook.Tab",
            background=UIConfig.COLORS['primary'],
            foreground=UIConfig.COLORS['text_light'],
            padding=[15, 8],
            font=("Arial Rounded MT Bold", 18)
        )
        style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", UIConfig.COLORS['bg_light'])],
            foreground=[("selected", UIConfig.COLORS['text_dark'])]
        )
        
    def _create_scrollable_frame(self, parent):
        """创建可滚动的框架"""
        canvas = tk.Canvas(parent, bg=UIConfig.COLORS['bg_light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UIConfig.COLORS['bg_light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return canvas, scrollbar, scrollable_frame
        
    def _create_game_intro_tab(self, notebook):
        """创建游戏简介选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="🎮 游戏简介")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 内容
        content = """
欢迎来到 SCAU 记忆翻牌游戏！这是一款考验记忆力、反应力与策略的经典卡牌翻牌游戏。通过翻牌配对来锻炼您的记忆力，解锁成就，提升等级，成为记忆大师！

游戏特色：
• 多种游戏模式，满足不同挑战需求
• 丰富的成就系统，记录您的成长历程
• 道具系统，提供更多策略选择
• 积分奖励机制，激励持续游戏

祝您玩得开心~
        """
        
        label = tk.Label(
            scrollable_frame,
            text=content.strip(),
            font=("Arial", 12),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light'],
            justify=tk.LEFT,
            wraplength=800
        )
        label.pack(padx=20, pady=20, anchor="w")
        
    def _create_interface_tab(self, notebook):
        """创建主界面功能说明选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="📱 主界面功能说明")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 标题
        title = tk.Label(
            scrollable_frame,
            text="主界面包含以下核心功能区：",
            font=("Arial Rounded MT Bold", 14, "bold"),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light']
        )
        title.pack(padx=20, pady=(20, 10), anchor="w")
        
        # 功能列表
        features = [
            "1. 开始游戏 - 进入游戏模式选择界面，可以选择不同难度和挑战模式开始游戏（具体详见游戏玩法）(*^▽^*)。",
            "2. 道具商城 - 在商城中，您可以使用游戏积分购买各种实用道具（具体详见道具商城）🎁。",
            "3. 游戏生涯 - 查看您的游戏记录、成就和进步历程。",
            "4. 个人主页 - 展示您的个人信息和详细统计数据。"
        ]
        
        for feature in features:
            label = tk.Label(
                scrollable_frame,
                text=feature,
                font=("Arial", 12),
                fg=UIConfig.COLORS['text_dark'],
                bg=UIConfig.COLORS['bg_light'],
                justify=tk.LEFT,
                wraplength=800
            )
            label.pack(padx=40, pady=5, anchor="w")
            
    def _create_account_tab(self, notebook):
        """创道具商城选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="🎁 道具商城")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        content = """
游戏提供丰富的道具可以使用：

·提示道具：价值200积分，帮助您找到一对未配对的卡片位置。
·时间延长道具：价值300积分，增加30秒游戏时间，适用于限时模式。
·防洗牌道具：价值400积分，防止下一次因连续失败触发的洗牌。
·时间静止道具：价值500积分，冻结计时10秒，适用于终极挑战模式。

注意事项：
• 提示道具在各个模式均可使用，帮助您更轻松找到配对。
• 时间延长道具仅适用于终极挑战模式，帮助您争取更多时间完成挑战。
• 防洗牌道具仅在洗牌模式生效，防止因连续失败触发的洗牌。
• 时间静止道具仅适用于终极挑战模式，冻结倒计时10秒。
        """
        
        label = tk.Label(
            scrollable_frame,
            text=content.strip(),
            font=("Arial", 12),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light'],
            justify=tk.LEFT,
            wraplength=800
        )
        label.pack(padx=20, pady=20, anchor="w")
        
    def _create_gameplay_tab(self, notebook):
        """创建游戏玩法选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="🎯 游戏玩法")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 定义通用样式参数
        header_font = ("Arial Rounded MT Bold", 14, "bold")
        sub_header_font = ("Arial Rounded MT Bold", 12, "bold")
        body_font = ("Arial", 12)
        text_fg = UIConfig.COLORS['text_dark']
        bg_color = UIConfig.COLORS['bg_light']
        wrap_len = 800

        # --- 第一部分：三种游戏模式 ---
        tk.Label(
            scrollable_frame,
            text="一、三种游戏模式 ",
            font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 10), anchor="w")

        modes = [
            "1. 普通模式 ：默认4x4网格（共16张卡片），无时间限制，适合休闲体验。",
            "2. 终极挑战模式 ：4x9网格（卡片数量更多），仅120秒时间限制，需快速完成配对。",
            "3. 洗牌模式：同4x9网格，180秒时间限制；新增“连续失败洗牌”机制——连续7次匹配失误会打乱未配对卡片（有警告提示）。"
        ]
        for mode in modes:
            tk.Label(
                scrollable_frame, text=mode, font=body_font,
                fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
            ).pack(padx=40, pady=4, anchor="w")

        # --- 第二部分：核心规则 ---
        tk.Label(
            scrollable_frame,
            text="二、核心规则 ",
            font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 10), anchor="w")

        rules = [
            "1. 翻牌配对：每次点击两张卡片，图案/数值相同则保持翻开并消除，不同则自动翻回。",
            "2. 胜负判定：找出所有配对即通关；限时模式下时间耗尽则挑战失败。"
        ]
        for rule in rules:
            tk.Label(
                scrollable_frame, text=rule, font=body_font,
                fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
            ).pack(padx=40, pady=4, anchor="w")

        # --- 第三部分：操作方式 ---
        tk.Label(
            scrollable_frame,
            text="三、操作方式 ",
            font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 10), anchor="w")

        controls = [
            "1. 翻牌：点击界面中的卡片即可翻转。",
            "2. 道具使用：点击底部对应道具按钮（提示、时间延长、防洗牌、时间静止）。",
            "3. 暂停/继续：游戏中可随时暂停⏸，再次启动即可恢复▶。",
            "4. 结算：通关或失败后会弹出提示弹窗，确认后返回主界面。"
        ]
        for control in controls:
            tk.Label(
                scrollable_frame, text=control, font=body_font,
                fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
            ).pack(padx=40, pady=4, anchor="w")

        # --- 第四部分：道具与特殊机制 ---
        tk.Label(
            scrollable_frame,
            text="四、道具",
            font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 10), anchor="w")

        items = [
            "• 提示：短暂显示一对未配对卡片的位置，消耗对应道具。",
            "• 时间延长：限时模式专用，增加30秒剩余时间。",
            "• 防洗牌：终极洗牌模式专用，阻止下一次因连续失败触发的洗牌。",
            "• 时间静止：终极挑战模式专用，冻结计时10秒。"
        ]
        for item in items:
            tk.Label(
                scrollable_frame, text=item, font=body_font,
                fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
            ).pack(padx=40, pady=2, anchor="w")
        
        # 底部留白
        tk.Label(scrollable_frame, text="", bg=bg_color).pack(pady=20)
            
    def _create_achievements_tab(self, notebook):
        """创建成就系统选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="🏆 成就系统")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 样式配置
        header_font = ("Arial Rounded MT Bold", 14, "bold")
        body_font = ("Arial", 12)
        text_fg = UIConfig.COLORS['text_dark']
        bg_color = UIConfig.COLORS['bg_light']
        wrap_len = 800

        # 开头介绍
        tk.Label(
            scrollable_frame,
            text="游戏内置29项成就（28项积分成就+1项隐藏荣誉），达成即领奖励，积分叠加无上限！",
            font=body_font, fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
        ).pack(padx=20, pady=(20, 10), anchor="w")

        # 数据结构：标题 + 内容列表
        sections = [
            ("一、新手必备（5项·简单易拿）", [
                "1. 完成1场游戏 —— 100分",
                "2. 首次通关任意模式 —— 50分",
                "3. 首次使用任意道具 —— 10分",
                "4. 首次通关终极模式 —— 75分",
                "5. 普通模式通关10次 —— 300分"
            ]),
            ("二、进阶挑战（8项·稳步积累）", [
                "1. 累计游玩50局 —— 200分",
                "2. 累计游玩100局 —— 300分",
                "3. 累计积分达5000分 —— 500分",
                "4. 普通模式通关30次 —— 300分",
                "5. 终极模式通关5次 —— 800分",
                "6. 终极模式通关30次 —— 1000分",
                "7. 累计使用道具10次 —— 150分",
                "8. 累计使用道具50次 —— 500分"
            ]),
            ("三、高手专属（9项·技术解锁）", [
                "1. 无道具通关10次 —— 500分",
                "2. 普通模式零失误通关 —— 666分",
                "3. 普通模式45秒内通关 —— 300分",
                "4. 普通模式零失误+50秒内通关 —— 666分",
                "5. 普通模式通关步数≤32步 —— 320分",
                "6. 终极模式零失误通关 —— 6666分",
                "7. 终极模式80秒内通关 —— 600分",
                "8. 终极模式零失误+100秒内通关 —— 6666分",
                "9. 终极模式无道具通关5次 —— 1200分"
            ]),
            ("四、连胜&活跃（8项·持续参与）", [
                "1. 连胜3场 —— 200分",
                "2. 连胜5场 —— 400分",
                "3. 连胜7场 —— 600分",
                "4. 连胜10场 —— 1000分",
                "5. 无道具连胜10场 —— 500分",
                "6. 终极模式连胜10场 —— 800分",
                "7. 单日完成10局游戏 —— 200分",
                "8. 单日用遍4种道具 —— 50分"
            ]),
            ("五、隐藏成就（1项·专属荣誉）", [
                "名称：误闯天家",
                "触发：通过隐藏操作进入开发者模式（登录界面连续点击Logo等）",
                "奖励：专属荣誉标识（0积分）",
                "说明：解锁后仅记录成就，象征探索精神，无实际积分加成"
            ])
        ]

        # 循环创建部分
        for title, items in sections:
            tk.Label(
                scrollable_frame, text=title, font=header_font,
                fg=text_fg, bg=bg_color
            ).pack(padx=20, pady=(15, 5), anchor="w")
            
            for item in items:
                tk.Label(
                    scrollable_frame, text=item, font=body_font,
                    fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
                ).pack(padx=40, pady=2, anchor="w")

        # 底部说明
        tk.Label(
            scrollable_frame, text="成就说明：", font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 5), anchor="w")
        
        notes = [
            "1. 所有成就达成后自动解锁，积分实时到账并弹窗提示；",
            "2. 总计29项成就，覆盖新手到高手全阶段，玩得越久奖励越丰厚！"
        ]
        for note in notes:
            tk.Label(
                scrollable_frame, text=note, font=body_font,
                fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
            ).pack(padx=40, pady=2, anchor="w")

        tk.Label(scrollable_frame, text="", bg=bg_color).pack(pady=20)
        
    def _create_points_tab(self, notebook):
        """创建积分获取规则选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="💎 积分获取指南")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 样式配置
        header_font = ("Arial Rounded MT Bold", 14, "bold")
        sub_header_font = ("Arial Rounded MT Bold", 12, "bold")
        body_font = ("Arial", 12)
        text_fg = UIConfig.COLORS['text_dark']
        bg_color = UIConfig.COLORS['bg_light']
        wrap_len = 800

        # 一、初始福利
        tk.Label(
            scrollable_frame, text="一、初始登录福利", font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 10), anchor="w")

        welfare_items = [
            "1. 新注册即得500初始积分",
            "2. 连续登录奖励：3天200分、7天500分、14天600分、30天1200分",
            "3. 累计登录30天（非连续）：额外300分"
        ]
        for item in welfare_items:
            tk.Label(
                scrollable_frame, text=item, font=body_font,
                fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
            ).pack(padx=40, pady=2, anchor="w")

        # 二、通关积分
        tk.Label(
            scrollable_frame, text="二、游戏通关积分（最低保障100分）", font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 10), anchor="w")

        game_modes_points = [
            ("普通模式", [
                "• 基础分：200分",
                "• 加分：60秒内+100分、120秒内+50分、零失误+500分",
                "• 扣分：每次失误-5分"
            ]),
            ("终极模式", [
                "• 基础分：1200分",
                "• 加分：60秒内+300分、90秒内+150分、零失误+500分",
                "• 扣分：每次失误-5分"
            ]),
            ("终极洗牌模式", [
                "• 基础分：1200分",
                "• 加分：90秒内+300分、135秒内+150分、零失误+500分",
                "• 扣分：每次失误-5分"
            ])
        ]

        for mode_name, points_info in game_modes_points:
            tk.Label(
                scrollable_frame, text=mode_name, font=sub_header_font,
                fg=text_fg, bg=bg_color
            ).pack(padx=30, pady=(10, 5), anchor="w")
            for info in points_info:
                tk.Label(
                    scrollable_frame, text=info, font=body_font,
                    fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
                ).pack(padx=50, pady=1, anchor="w")

        # 三、成就额外积分
        tk.Label(
            scrollable_frame, text="三、成就额外积分（达成自动解锁）", font=header_font,
            fg=text_fg, bg=bg_color
        ).pack(padx=20, pady=(20, 10), anchor="w")

        achieve_cats = [
            ("新手必备（简单易拿）", [
                "• 完成1场游戏：100分 | 首次通关任意模式：50分",
                "• 首次用道具：10分 | 首次过终极模式：75分",
                "• 普通模式通关10次：300分"
            ]),
            ("进阶挑战（稳步积累）", [
                "• 累计玩50局：200分 | 100局：300分",
                "• 累计积分5000分：500分",
                "• 普通模式通关30次：300分",
                "• 终极模式通关5次：800分 | 30次：1000分",
                "• 累计用道具10次：150分 | 50次：500分"
            ]),
            ("高手专属（技术解锁）", [
                "• 无道具通关10次：500分",
                "• 普通模式零失误：666分 | 45秒内通关：300分",
                "• 普通模式零失误+50秒内：666分 | 步数≤32：320分",
                "• 终极模式零失误：6666分 | 80秒内通关：600分",
                "• 终极模式零失误+100秒内：6666分 | 无道具通关5次：1200分"
            ]),
            ("连胜&活跃（持续参与）", [
                "• 连胜3场：200分 | 5场：400分 | 7场：600分 | 10场：1000分",
                "• 无道具连胜10场：500分 | 终极模式连胜10场：800分",
                "• 单日玩10局：200分 | 单日用遍4种道具：50分"
            ])
        ]

        for cat_name, cat_items in achieve_cats:
            tk.Label(
                scrollable_frame, text=cat_name, font=sub_header_font,
                fg=text_fg, bg=bg_color
            ).pack(padx=30, pady=(10, 5), anchor="w")
            for item in cat_items:
                tk.Label(
                    scrollable_frame, text=item, font=body_font,
                    fg=text_fg, bg=bg_color, justify=tk.LEFT, wraplength=wrap_len
                ).pack(padx=50, pady=1, anchor="w")

        tk.Label(scrollable_frame, text="", bg=bg_color).pack(pady=20)
        
    def _create_tips_tab(self, notebook):
        """创建游戏提示选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="📝 游戏提示")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tips = [
            "• 记住卡牌位置是获胜的关键，建议先观察再翻牌",
            "• 合理使用道具应对难题，特别是在终极模式中",
            "• 每天登录获取额外奖励，保持连续登录可获得更多奖励",
            "• 挑战不同模式锻炼不同能力，逐步提升游戏水平",
            "• 注意时间限制，在必要时使用时间延长道具",
            "• 观察卡牌图案特征，有助于快速识别和记忆",
            "• 在普通模式熟悉规则，在终极模式挑战自我",
            "• 完成成就不仅能获得成就感，还能获取丰厚积分奖励"
        ]
        
        title = tk.Label(
            scrollable_frame,
            text="以下是一些有助于提升游戏体验和成绩的小贴士：",
            font=("Arial Rounded MT Bold", 14, "bold"),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light']
        )
        title.pack(padx=20, pady=(20, 10), anchor="w")
        
        for tip in tips:
            label = tk.Label(
                scrollable_frame,
                text=f"• {tip}",
                font=("Arial", 12),
                fg=UIConfig.COLORS['text_dark'],
                bg=UIConfig.COLORS['bg_light'],
                justify=tk.LEFT,
                wraplength=800
            )
            label.pack(padx=40, pady=5, anchor="w")
            
        # 结束语
        footer = tk.Label(
            scrollable_frame,
            text="\n祝您游戏愉快！如有任何问题或建议，请随时反馈。\n",
            font=("Arial", 12, "italic"),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light']
        )
        footer.pack(padx=20, pady=20, anchor="w")
        
    def _on_close(self):
        """关闭窗口"""
        self.window.destroy()
        
    def show(self):
        """显示窗口"""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()