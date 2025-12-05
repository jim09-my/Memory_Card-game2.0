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
        self._create_account_tab(notebook)
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
• 精美的UI界面设计，采用青绿色和芥末黄色调
• 多种游戏模式，满足不同挑战需求
• 丰富的成就系统，记录您的成长历程
• 道具系统，提供更多策略选择
• 完善的账号系统，数据云端同步
• 积分奖励机制，激励持续游戏
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
            "1. 开始游戏 - 进入游戏模式选择界面，可以选择不同难度和挑战模式开始游戏。",
            "2. 道具商城 - 在商城中，您可以使用游戏积分购买各种实用道具。",
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
        """创建账号系统选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="🔑 账号系统")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        content = """
游戏提供完整的账号系统：

• 创建个人账号保存游戏进度
• 登录后可在任何设备继续游戏
• 账号数据自动保存

注意事项：
• 请妥善保管您的账号信息
• 不同设备登录同一账号可同步游戏数据
• 如忘记密码，请联系客服处理
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
        
        # 基本规则
        basic_rules_title = tk.Label(
            scrollable_frame,
            text="基本规则：",
            font=("Arial Rounded MT Bold", 14, "bold"),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light']
        )
        basic_rules_title.pack(padx=20, pady=(20, 10), anchor="w")
        
        basic_rules = [
            "1. 游戏开始时，所有卡牌背面朝上",
            "2. 每次可翻转两张卡牌",
            "3. 如果两张卡牌匹配，它们将保持正面朝上",
            "4. 如果不匹配，卡牌将翻转回背面",
            "5. 目标是找出所有配对，完成所有卡牌匹配"
        ]
        
        for rule in basic_rules:
            label = tk.Label(
                scrollable_frame,
                text=rule,
                font=("Arial", 12),
                fg=UIConfig.COLORS['text_dark'],
                bg=UIConfig.COLORS['bg_light'],
                justify=tk.LEFT,
                wraplength=800
            )
            label.pack(padx=40, pady=2, anchor="w")
            
        # 特殊机制
        special_mechanics_title = tk.Label(
            scrollable_frame,
            text="特殊机制：",
            font=("Arial Rounded MT Bold", 14, "bold"),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light']
        )
        special_mechanics_title.pack(padx=20, pady=(20, 10), anchor="w")
        
        special_mechanics = [
            "• 连续失败洗牌：连续多次翻转错误会触发卡牌重新洗牌",
            "• 计时器：部分模式有时间限制",
            "• 积分系统：根据完成速度、翻牌次数等获得积分奖励"
        ]
        
        for mechanic in special_mechanics:
            label = tk.Label(
                scrollable_frame,
                text=mechanic,
                font=("Arial", 12),
                fg=UIConfig.COLORS['text_dark'],
                bg=UIConfig.COLORS['bg_light'],
                justify=tk.LEFT,
                wraplength=800
            )
            label.pack(padx=40, pady=2, anchor="w")
            
        # 道具使用
        item_usage_title = tk.Label(
            scrollable_frame,
            text="道具使用：",
            font=("Arial Rounded MT Bold", 14, "bold"),
            fg=UIConfig.COLORS['text_dark'],
            bg=UIConfig.COLORS['bg_light']
        )
        item_usage_title.pack(padx=20, pady=(20, 10), anchor="w")
        
        item_usage = [
            "• 提示道具：帮助您找到配对卡牌",
            "• 时间延长：在计时模式中获得更多时间",
            "• 防洗牌道具：防止连续失败触发的洗牌效果",
            "• 时间静止：在终极模式中冻结时间10秒（仍可翻牌配对）"
        ]
        
        for usage in item_usage:
            label = tk.Label(
                scrollable_frame,
                text=usage,
                font=("Arial", 12),
                fg=UIConfig.COLORS['text_dark'],
                bg=UIConfig.COLORS['bg_light'],
                justify=tk.LEFT,
                wraplength=800
            )
            label.pack(padx=40, pady=2, anchor="w")
            
    def _create_achievements_tab(self, notebook):
        """创建成就系统选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="🏆 成就系统")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        content = """
游戏包含丰富的成就系统，完成特定条件可获得成就徽章和积分奖励：

• 首次胜利 - 完成第一场游戏
• 连续登录奖励 - 连续登录3天、7天、14天、30天
• 完美通关 - 零失误通关任意模式
• 打破个人记录 - 刷新普通模式个人最佳用时
• 百战不殆 - 累计游玩100局
• 千分达人 - 累计获得积分达到5000
• 速通专家 - 在限定时间内完成游戏
• 道具达人 - 累计使用道具一定次数
• 连胜成就 - 连续通关多场游戏

每个成就都有对应的积分奖励，帮助您更快地积累游戏资源。
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
        
    def _create_points_tab(self, notebook):
        """创建积分获取方式选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="💎 积分获取方式")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        content = """
积分是游戏中的重要资源，可以通过多种方式获取：

日常奖励：
• 每日登录奖励：100积分
• 连续登录3天：额外200积分
• 连续登录7天：额外500积分

游戏奖励：
• 普通模式胜利：200积分
• 极限模式胜利：1200积分
• 打破个人记录：300积分
• 完美通关：500积分

成就奖励：
• 完成各类成就可获得相应积分奖励
• 不同难度的成就奖励不同

积分用途：
• 在道具商城购买各种实用道具
• 解锁特殊功能和皮肤
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
        
    def _create_tips_tab(self, notebook):
        """创建游戏提示选项卡"""
        frame = tk.Frame(notebook, bg=UIConfig.COLORS['bg_light'])
        notebook.add(frame, text="📝 游戏提示")
        
        canvas, scrollbar, scrollable_frame = self._create_scrollable_frame(frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tips = [
            "• 记住卡牌位置是获胜的关键，建议先观察再翻牌",
            "• 合理使用道具应对难题，特别是在极限模式中",
            "• 每天登录获取额外奖励，保持连续登录可获得更多奖励",
            "• 挑战不同模式锻炼不同能力，逐步提升游戏水平",
            "• 注意时间限制，在必要时使用时间延长道具",
            "• 观察卡牌图案特征，有助于快速识别和记忆",
            "• 在普通模式熟悉规则，在极限模式挑战自我",
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