import tkinter as tk
from tkinter import ttk
from config import UIConfig

# --- 绘图辅助函数 ---
def draw_rounded_rect(canvas, x, y, w, h, r, fill, outline="", tags="bg_rect"):
    """绘制圆角矩形"""
    x, y = x+1, y+1
    w, h = w-2, h-2
    canvas.delete(tags)
    canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline=outline, tags=tags)
    canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline=outline, tags=tags)
    canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline=outline, tags=tags)
    canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline=outline, tags=tags)
    canvas.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline=outline, tags=tags)
    canvas.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline=outline, tags=tags)
    canvas.tag_lower(tags)

# --- 自定义圆角标签按钮 ---
class CandyTabButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=120, height=36, selected=False):
        super().__init__(master, width=width, height=height, 
                         bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.text = text
        self.command = command
        self.btn_w = width
        self.btn_h = height
        self._selected = selected
        self._hover = False
        
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self._draw()

    def set_selected(self, val):
        self._selected = val
        self._draw()

    def _draw(self):
        self.delete('all')
        if self._selected:
            bg_col = '#FFD54F' 
            fg_col = '#5D4037'
        elif self._hover:
            bg_col = '#80DEEA'
            fg_col = '#006064'
        else:
            bg_col = '#B2DFDB'
            fg_col = '#455A64'
        
        r = 10 
        draw_rounded_rect(self, 0, 0, self.btn_w, self.btn_h, r, fill=bg_col, tags="btn_bg")
        font_style = ("Microsoft YaHei UI", 10, "bold")
        self.create_text(self.btn_w/2, self.btn_h/2, text=self.text, font=font_style, fill=fg_col)

    def _on_click(self, e):
        if self.command: self.command()
    def _on_enter(self, e):
        self._hover = True
        if not self._selected: self.config(cursor='hand2')
        self._draw()
    def _on_leave(self, e):
        self._hover = False
        self.config(cursor='')
        self._draw()

# --- 主窗口类 ---
class ManualWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("游戏说明书")
        self.window.geometry("1100x750")
        self.window.config(bg=UIConfig.COLORS['primary'])
        self.window.resizable(False, False)
        
        self._center_window()
        self._configure_custom_styles()
        
        self.tabs = {}
        self.current_tab = None
        self.inner_frame = None
        
        self._create_header()
        self._create_nav_bar()
        self._create_content_area()
        
        self.window.after(50, lambda: self._switch_tab("game_intro"))
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

    def _center_window(self):
        self.window.update_idletasks()
        w, h = 1100, 750
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _configure_custom_styles(self):
        style = ttk.Style()
        try: style.theme_use('clam')
        except: pass
        style.configure("Candy.Vertical.TScrollbar", gripcount=0, background='#80CBC4', 
                        troughcolor='white', bordercolor='white', lightcolor='#80CBC4',
                        darkcolor='#80CBC4', arrowsize=0)

    def _create_header(self):
        header = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        header.pack(fill=tk.X, pady=(15, 5))
        tk.Label(header, text="SCAU 记忆翻牌游戏说明书", 
                 font=("Microsoft YaHei UI", 26, "bold"),
                 fg='white', bg=UIConfig.COLORS['primary']).pack()

    def _create_nav_bar(self):
        nav_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        center_frame = tk.Frame(nav_frame, bg=UIConfig.COLORS['primary'])
        center_frame.pack(anchor=tk.CENTER)
        
        tabs = [
            ("game_intro", "🎮 游戏简介"),
            ("interface", "📱 界面与账号"),
            ("account", "🎁 道具商城"), 
            ("gameplay", "🎯 游戏玩法"),
            ("achievements", "🏆 成就系统"),
            ("points", "💎 积分获取"), 
            ("tips", "📝 游戏技巧") 
        ]
        
        for key, name in tabs:
            text_len = len(name)
            btn_w = 100 + (text_len - 4) * 12 if text_len > 4 else 100
            btn = CandyTabButton(center_frame, text=name, width=btn_w, height=36,
                                 command=lambda k=key: self._switch_tab(k))
            btn.pack(side=tk.LEFT, padx=4) 
            self.tabs[key] = btn

    def _create_content_area(self):
        container = tk.Frame(self.window, bg=UIConfig.COLORS['primary'], padx=20)
        container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.bg_canvas = tk.Canvas(container, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.inner_frame = tk.Frame(self.bg_canvas, bg='white')
        self.window_item = self.bg_canvas.create_window(0, 0, window=self.inner_frame, anchor='nw')
        self.bg_canvas.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        w, h = event.width, event.height
        draw_rounded_rect(self.bg_canvas, 0, 0, w, h, 15, fill='white', tags='bg_rect')
        self.bg_canvas.tag_lower('bg_rect')
        self.bg_canvas.tag_raise(self.window_item)
        inner_w, inner_h = max(1, w - 20), max(1, h - 20)
        self.bg_canvas.coords(self.window_item, 10, 10)
        self.bg_canvas.itemconfigure(self.window_item, width=inner_w, height=inner_h)

    def _switch_tab(self, key):
        if not self.inner_frame: return
        if self.current_tab: self.tabs[self.current_tab].set_selected(False)
        self.tabs[key].set_selected(True)
        self.current_tab = key
        
        for widget in self.inner_frame.winfo_children(): widget.destroy()
        self._create_scroll_view(key)

    def _create_scroll_view(self, key):
        scrollbar = ttk.Scrollbar(self.inner_frame, orient="vertical", style="Candy.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 5))
        
        text_widget = tk.Text(self.inner_frame, bg='white', bd=0, 
                              highlightthickness=0,
                              font=("Microsoft YaHei UI", 11), 
                              fg='#333333', 
                              wrap=tk.WORD,
                              padx=30, pady=20, 
                              spacing1=5, spacing2=4, spacing3=5, 
                              yscrollcommand=scrollbar.set,
                              cursor='arrow')
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        self._fill_content(text_widget, key)
        text_widget.config(state='disabled')

    def _fill_content(self, text_widget, key):
        # --- 标签样式配置 ---
        # H1: 大标题
        text_widget.tag_configure("h1", font=("Microsoft YaHei UI", 16, "bold"), foreground="#00897B", spacing3=10)
        
        # H2: 二级标题 (间距调整)
        text_widget.tag_configure("h2", font=("Microsoft YaHei UI", 13, "bold"), foreground="#00695C", 
                                  spacing1=15, spacing3=5)
        
        # H3: 三级标题 (用于替代之前的 ####, 字体稍小但加粗)
        text_widget.tag_configure("h3", font=("Microsoft YaHei UI", 12, "bold"), foreground="#00796B", 
                                  spacing1=10, spacing3=2)
        
        text_widget.tag_configure("body", font=("Microsoft YaHei UI", 11), foreground="#37474F")
        
        text_widget.tag_configure("highlight", foreground="#EF6C00", font=("Microsoft YaHei UI", 11, "bold"))
        
        # 加粗文本 (替代 ** **)
        text_widget.tag_configure("bold_text", font=("Microsoft YaHei UI", 11, "bold"), foreground="#37474F")
        
        # 列表项 (带缩进)
        text_widget.tag_configure("tip_item", 
                                  font=("Microsoft YaHei UI", 11), 
                                  foreground="#37474F",
                                  lmargin1=30, lmargin2=30,
                                  spacing1=2, spacing2=2)
                                  
        text_widget.tag_configure("italic_footer", 
                                  font=("Microsoft YaHei UI", 11, "italic"), 
                                  foreground="#546E7A",
                                  justify='right',
                                  spacing1=20)

        if key == "game_intro": self._content_intro(text_widget)
        elif key == "interface": self._content_interface(text_widget)
        elif key == "account": self._content_shop(text_widget)
        elif key == "gameplay": self._content_gameplay(text_widget)
        elif key == "achievements": self._content_achievements(text_widget)
        elif key == "points": self._content_points(text_widget)
        elif key == "tips": self._content_tips(text_widget)

    # --- 内容填充 ---

    def _content_intro(self, t):
        t.insert(tk.END, "🎮 游戏简介\n", "h1")
        t.insert(tk.END, "欢迎来到 SCAU 记忆翻牌游戏！\n这是一款考验记忆力、反应力与策略的经典卡牌翻牌游戏。通过翻牌配对来锻炼您的记忆力，解锁成就，提升等级，成为记忆大师！\n\n", "body")
        
        t.insert(tk.END, "游戏特色：\n", "bold_text")
        features = [
            "多种游戏模式，满足不同挑战需求",
            "丰富的成就系统，记录您的成长历程",
            "道具系统，提供更多策略选择",
            "积分奖励机制，激励持续游戏"
        ]
        for f in features:
            t.insert(tk.END, f"• {f}\n", "tip_item")

    def _content_interface(self, t):
        t.insert(tk.END, "📱 主界面功能说明\n", "h1")
        t.insert(tk.END, "主界面包含以下核心功能区：\n", "body")
        items = [
            ("1. 开始游戏", "进入游戏模式选择界面，可以选择不同难度和挑战模式开始游戏（具体详见游戏玩法）(*^▽^*)"),
            ("2. 道具商城", "在商城中，您可以使用游戏积分购买各种实用道具（具体详见道具商城）🎁"),
            ("3. 游戏生涯", "查看您的游戏记录、成就和进步历程。"),
            ("4. 个人主页", "展示您的个人信息和详细统计数据。")
        ]
        for title, desc in items:
            t.insert(tk.END, f"{title}", "bold_text")
            t.insert(tk.END, f" - {desc}\n", "tip_item")

        t.insert(tk.END, "🔑 登录系统\n", "h2")
        t.insert(tk.END, "游戏提供完整的账号系统：\n", "body")
        t.insert(tk.END, "• 创建个人账号保存游戏进度\n", "tip_item")
        t.insert(tk.END, "• 账号数据自动保存\n\n", "tip_item")
        
        # --- 修复：注意事项与列表空隙缩小 ---
        t.insert(tk.END, "注意事项：\n", "bold_text")
        # 移除前面的 \n，减小空隙
        t.insert(tk.END, "• 请妥善保管您的账号信息\n", "tip_item")
        t.insert(tk.END, "• 如忘记密码，请联系管理员处理\n", "tip_item")

        t.insert(tk.END, "👮 管理员系统\n", "h2")
        admin_items = [
            "1. 游戏设有专门的管理员账号，用于维护系统秩序",
            "2. 管理员可以查看所有用户的数据，历史记录，得分，注册天数......",
            "3. 管理员具有修改账户密码的功能，可以帮助用户重置密码",
            "4. 管理员导出所有用户的数据（json或者csv格式）"
        ]
        for item in admin_items:
            t.insert(tk.END, f"{item}\n", "tip_item")

    def _content_shop(self, t):
        t.insert(tk.END, "🛍️ 道具商城系统\n", "h1")
        shop_items = [
            ("1. 透视眼", "价值200积分，帮助您找到一对未配对的卡片位置。"),
            ("2. 时间胶囊", "价值300积分，增加30秒游戏时间，适用于限时模式。"),
            ("3. 防洗牌护盾", "价值400积分，防止下一次因连续失败触发的洗牌。"),
            ("4. 时间静止", "价值250积分，冻结计时10秒，适用于终极挑战模式。")
        ]
        for title, desc in shop_items:
            t.insert(tk.END, f"{title}：", "highlight")
            t.insert(tk.END, f"{desc}\n", "tip_item")

    def _content_gameplay(self, t):
        t.insert(tk.END, "🕹️ 游戏玩法说明\n", "h1")
        
        t.insert(tk.END, "一、三种游戏模式\n", "h2")
        modes = [
            ("1. 普通模式", "默认4x4网格（共16张卡片），无时间限制，适合休闲体验。"),
            ("2. 终极挑战模式", "4x9网格（卡片数量更多），仅120秒时间限制，需快速完成配对。"),
            ("3. 终极洗牌模式", "同4x9网格，180秒时间限制；新增“连续失败洗牌”机制——连续7次匹配失误会打乱未配对卡片（有UI警告提示）。")
        ]
        for title, desc in modes:
            t.insert(tk.END, f"{title}：", "bold_text")
            t.insert(tk.END, f"{desc}\n", "tip_item")

        t.insert(tk.END, "二、核心规则\n", "h2")
        t.insert(tk.END, "1. 翻牌配对：每次点击两张卡片，图案/数值相同则保持翻开并消除，不同则自动翻回。\n", "tip_item")
        t.insert(tk.END, "2. 胜负判定：找出所有配对即通关；限时模式下时间耗尽则挑战失败。\n", "tip_item")

        t.insert(tk.END, "三、操作方式\n", "h2")
        ops = [
            "1. 翻牌：点击界面中的卡片即可。",
            "2. 道具使用：点击底部对应道具按钮（透视眼、时间胶囊、防洗牌护盾、时间静止）。",
            "3. 暂停/继续：游戏中可随时暂停，再次启动即可恢复。",
            "4. 结算：通关或失败后会弹出提示弹窗，确认后返回主界面。"
        ]
        for op in ops:
            t.insert(tk.END, f"{op}\n", "tip_item")

        t.insert(tk.END, "四、道具\n", "h2")
        props = [
            "• 透视眼：短暂显示一对未配对卡片的位置，消耗对应道具。",
            "• 时间胶囊：限时模式专用，增加30秒剩余时间。",
            "• 防洗牌护盾：终极洗牌模式专用，阻止下一次因连续失败触发的洗牌。",
            "• 时间静止：终极挑战模式专用，冻结计时10秒。"
        ]
        for p in props:
            t.insert(tk.END, f"{p}\n", "tip_item")
        
        t.insert(tk.END, "\n游戏内置36项积分成就，达成即领奖励，积分叠加无上限！\n", "body")

    def _content_achievements(self, t):
        t.insert(tk.END, "🎖️ 成就系统\n", "h1")
        t.insert(tk.END, "特色：", "bold_text")
        t.insert(tk.END, "按类别梳理用户所获得的成就，一共设置了36个成就。\n\n", "body")
        t.insert(tk.END, "具体的成就可查看成就系统\n", "body")

        sections = [
            ("一、入门成就（6项）", [
                "1. 初次尝试：完成第一场游戏 —— 100分", 
                "2. 首胜加冕：首次通关任意模式 —— 50分",
                "3. 初试终极：首次通关终极模式 —— 75分", 
                "4. 初用道具：首次使用任意道具 —— 10分",
                "5. 打破个人纪录：刷新普通模式个人最佳用时 —— 100分",
                "6. 普通大师：普通模式通关10次 —— 300分"
            ]),
            ("二、成长与挑战（8项）", [
                "1. 毅力十足：累计游玩50局 —— 200分", 
                "2. 百战不殆：累计游玩100局 —— 300分",
                "3. 千分达人：累计获得积分达到5000 —— 500分", 
                "4. 普通老练：普通模式通关30次 —— 300分",
                "5. 终极征服者：终极模式通关5次 —— 800分", 
                "6. 终极精进：终极模式通关30次 —— 1000分",
                "7. 道具达人：累计使用道具50次 —— 500分", 
                "8. 常回家看看：累计登录天数30（非连续） —— 300分"
            ]),
            ("三、活跃达人（7项）", [
                "1. 工具达人：累计使用道具10次 —— 150分", 
                "2. 工具全能：单日四种道具各至少使用一次 —— 50分",
                "3. 每日十局：单日完成10局 —— 200分",
                "4. 活跃签到·3：连续登录3天 —— 200分", 
                "5. 活跃签到·7：连续登录7天 —— 500分",
                "6. 活跃签到·14：连续登录14天 —— 600分",
                "7. 活跃签到·30：连续登录30天 —— 1200分"
            ]),
            ("四、连胜纪录（6项）", [
                "1. 连胜三场：连续通关3场 —— 200分", 
                "2. 势不可挡：连续通关5场 —— 400分",
                "3. 七连胜：连续通关7场 —— 600分", 
                "4. 十连胜：连续通关10场 —— 1000分",
                "5. 终极十连：终极模式连续通关10场 —— 800分", 
                "6. 无道具十连：无道具连续通关10场 —— 500分"
            ]),
            ("五、技术巅峰（9项）", [
                "1. 清心寡欲：无道具通关10次 —— 500分", 
                "2. 终极无道具5：终极模式无道具通关5次 —— 1200分",
                "3. 省步高手：普通模式通关步数≤32 —— 320分",
                "4. 速通·普通：普通模式45秒内通关 —— 300分", 
                "5. 速通·终极：终极模式80秒内通关 —— 600分",
                "6. 零失误·普通：普通模式失误数为0通关 —— 666分", 
                "7. 零失误·终极：终极模式失误数为0通关 —— 6666分",
                "8. 无双·普通：普通模式零失误且≤50秒通关 —— 666分",
                "9. 无双·终极：终极模式零失误且≤100秒通关 —— 6666分"
            ])
        ]
        
        for title, items in sections:
            t.insert(tk.END, f"{title}\n", "h2")
            for i in items:
                t.insert(tk.END, f"{i}\n", "tip_item")

        t.insert(tk.END, "\n成就说明\n", "h2")
        t.insert(tk.END, "1. 所有成就达成后自动解锁，积分实时到账并弹窗提示；\n", "tip_item")
        t.insert(tk.END, "2. 总计36项成就，覆盖新手到高手全阶段，玩得越久奖励越丰厚！\n", "tip_item")

    def _content_points(self, t):
        t.insert(tk.END, "🏆 积分获取指南\n", "h1")
        
        t.insert(tk.END, "一、初始登录福利\n", "h2")
        t.insert(tk.END, "1. 新注册即得500初始积分\n", "tip_item")
        t.insert(tk.END, "2. 连续登录奖励：3天200分、7天500分、14天600分、30天1200分\n", "tip_item")
        t.insert(tk.END, "3. 累计登录30天（非连续）：额外300分\n", "tip_item")

        t.insert(tk.END, "二、游戏通关积分（最低保障100分）\n", "h2")
        
        t.insert(tk.END, "普通模式\n", "h3")
        t.insert(tk.END, "• 基础分：200分\n", "tip_item")
        t.insert(tk.END, "• 加分：60秒内+100分、120秒内+50分、零失误+500分\n", "tip_item")
        t.insert(tk.END, "• 扣分：每次失误-5分\n", "tip_item")

        t.insert(tk.END, "终极模式\n", "h3")
        t.insert(tk.END, "• 基础分：1200分\n", "tip_item")
        t.insert(tk.END, "• 加分：60秒内+300分、90秒内+150分、零失误+500分\n", "tip_item")
        t.insert(tk.END, "• 扣分：每次失误-5分\n", "tip_item")

        t.insert(tk.END, "终极洗牌模式\n", "h3")
        t.insert(tk.END, "• 基础分：1200分\n", "tip_item")
        t.insert(tk.END, "• 加分：90秒内+300分、135秒内+150分、零失误+500分\n", "tip_item")
        t.insert(tk.END, "• 扣分：每次失误-5分\n", "tip_item")

        t.insert(tk.END, "三、成就额外积分（达成自动解锁）\n", "h2")
        
        t.insert(tk.END, "入门成就\n", "h3")
        t.insert(tk.END, "• 初次尝试(100)、首胜加冕(50)、初试终极(75)\n", "tip_item")
        t.insert(tk.END, "• 初用道具(10)、打破纪录(100)、普通大师(300)\n", "tip_item")

        t.insert(tk.END, "成长与挑战\n", "h3")
        t.insert(tk.END, "• 毅力十足(200)、百战不殆(300)、千分达人(500)\n", "tip_item")
        t.insert(tk.END, "• 普通老练(300)、终极征服者(800)、终极精进(1000)\n", "tip_item")
        t.insert(tk.END, "• 道具达人(500)、常回家看看(300)\n", "tip_item")

        t.insert(tk.END, "活跃达人\n", "h3")
        t.insert(tk.END, "• 工具达人(150)、工具全能(50)、每日十局(200)\n", "tip_item")
        t.insert(tk.END, "• 活跃签到：3天(200)、7天(500)、14天(600)、30天(1200)\n", "tip_item")

        t.insert(tk.END, "连胜纪录\n", "h3")
        t.insert(tk.END, "• 连胜：3场(200)、5场(400)、7场(600)、10场(1000)\n", "tip_item")
        t.insert(tk.END, "• 终极十连(800)、无道具十连(500)\n", "tip_item")

        t.insert(tk.END, "技术巅峰\n", "h3")
        t.insert(tk.END, "• 清心寡欲(500)、终极无道具5(1200)、省步高手(320)\n", "tip_item")
        t.insert(tk.END, "• 速通：普通(300)、终极(600)\n", "tip_item")
        t.insert(tk.END, "• 零失误：普通(666)、终极(6666)\n", "tip_item")
        t.insert(tk.END, "• 无双(零失误速通)：普通(666)、终极(6666)\n", "tip_item")

    def _content_tips(self, t):
        t.insert(tk.END, "💡 游戏核心技巧\n", "h1")

        t.insert(tk.END, "1. 记牌小窍门\n", "h2")
        t.insert(tk.END, "- 翻牌前3秒分区看（左上→右上→左下→右下），优先记红黑颜色和数字特征（比如10是两位数，或8/0这类形状独特的数字）\n", "tip_item")
        t.insert(tk.END, "- 用花色/数字关联记相邻牌（比如“♡5+♡6=红桃连号”“♡3+♢3=红色3兄弟”），减少记忆负担\n", "tip_item")
        t.insert(tk.END, "2. 道具不浪费\n", "h2")
        t.insert(tk.END, "- 时间胶囊：极限模式剩10秒内用，且已找到2对以上卡牌时\n", "tip_item")
        t.insert(tk.END, "- 透视眼：30秒没找到匹配或剩牌少卡顿时用，重点看边缘卡牌\n", "tip_item")
        t.insert(tk.END, "- 洗牌道具（需确认）：10张以上卡牌没思路时，洗牌后重新分区观察\n", "tip_item")

        t.insert(tk.END, "3. 模式进阶\n", "h2")
        t.insert(tk.END, "- 普通模式：先练准确率（≥80%），翻2次牌复盘1秒\n", "tip_item")
        t.insert(tk.END, "- 极限模式：开局10秒只看标记3对，优先翻标记卡牌省时间\n", "tip_item")

        t.insert(tk.END, "4. 福利快速拿\n", "h2")
        t.insert(tk.END, "- 连续登录3天领道具包，7天解锁限定皮肤\n", "tip_item")
        t.insert(tk.END, "- 先做简单成就（如“连配5对”），快速攒积分换道具\n", "tip_item")

        t.insert(tk.END, "5. 避坑提醒\n", "h2")
        t.insert(tk.END, "- 不频繁乱翻，每配1对停顿0.5秒巩固记忆\n", "tip_item")
        t.insert(tk.END, "- 前期少用道具，20分钟后累了就休息5分钟\n", "tip_item")

        t.insert(tk.END, "\n祝您游戏愉快！有问题随时反馈～\n", "italic_footer")

    def show(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()