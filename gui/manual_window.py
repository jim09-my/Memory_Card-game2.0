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
            ("interface", "📱 主界面功能"),
            ("account", "🎁 道具商城"), 
            ("gameplay", "🎯 游戏玩法"),
            ("achievements", "🏆 成就系统"),
            ("points", "💎 积分指南"),
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
        text_widget.tag_configure("h1", font=("Microsoft YaHei UI", 16, "bold"), foreground="#00897B", spacing3=10)
        
        # 修改：h2 (小标题) 的 spacing1 (段前距) 稍微调大一点，代替换行符，但不要太大
        text_widget.tag_configure("h2", font=("Microsoft YaHei UI", 13, "bold"), foreground="#00695C", 
                                  spacing1=15, # 段前距，代替 \n
                                  spacing3=3)
        
        text_widget.tag_configure("body", font=("Microsoft YaHei UI", 11), foreground="#37474F")
        text_widget.tag_configure("highlight", foreground="#EF6C00", font=("Microsoft YaHei UI", 11, "bold"))
        
        text_widget.tag_configure("tip_item", 
                                  font=("Microsoft YaHei UI", 11), 
                                  foreground="#37474F",
                                  lmargin1=30,
                                  lmargin2=52,
                                  spacing1=1, 
                                  spacing2=0, 
                                  spacing3=1)
                                  
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

    # --- 内容填充方法 ---

    def _content_intro(self, t):
        t.insert(tk.END, "🎮 游戏简介\n", "h1")
        t.insert(tk.END, "欢迎来到 SCAU 记忆翻牌游戏！\n", "body")
        t.insert(tk.END, "这是一款考验记忆力、反应力与策略的经典卡牌翻牌游戏。通过翻牌配对来锻炼您的记忆力，解锁成就，提升等级，成为记忆大师！\n\n", "body")
        t.insert(tk.END, "游戏特色：\n", "h2")
        t.insert(tk.END, "• 多种游戏模式，满足不同挑战需求\n", "body")
        t.insert(tk.END, "• 丰富的成就系统，记录您的成长历程\n", "body")
        t.insert(tk.END, "• 道具系统，提供更多策略选择\n", "body")
        t.insert(tk.END, "• 积分奖励机制，激励持续游戏\n\n", "body")
        t.insert(tk.END, "祝您玩得开心~\n", "body")

    def _content_interface(self, t):
        t.insert(tk.END, "📱 主界面功能说明\n", "h1")
        t.insert(tk.END, "主界面包含以下核心功能区：\n", "h2")
        items = [
            ("1. 开始游戏", "进入游戏模式选择界面，可以选择不同难度和挑战模式开始游戏。"),
            ("2. 道具商城", "在商城中，您可以使用游戏积分购买各种实用道具。"),
            ("3. 游戏生涯", "查看您的游戏记录、成就和进步历程。"),
            ("4. 个人主页", "展示您的个人信息和详细统计数据。")
        ]
        for title, desc in items:
            t.insert(tk.END, f"{title} - ", "highlight")
            t.insert(tk.END, f"{desc}\n", "body")

    def _content_shop(self, t):
        t.insert(tk.END, "🎁 道具商城\n", "h1")
        t.insert(tk.END, "游戏提供丰富的道具可以使用：\n", "body")
        items = [
            ("· 提示道具", "价值200积分，帮助您找到一对未配对的卡片位置。"),
            ("· 时间延长道具", "价值300积分，增加30秒游戏时间，适用于限时模式。"),
            ("· 防洗牌道具", "价值400积分，防止下一次因连续失败触发的洗牌。"),
            ("· 时间静止道具", "价值500积分，冻结计时10秒，适用于终极挑战模式。")
        ]
        for title, desc in items:
            t.insert(tk.END, f"\n{title}：", "highlight")
            t.insert(tk.END, f"{desc}", "body")
        t.insert(tk.END, "\n注意事项：\n", "h2") # h2 自带上边距
        notes = [
            "• 提示道具在各个模式均可使用，帮助您更轻松找到配对。",
            "• 时间延长道具仅适用于终极挑战模式，帮助您争取更多时间完成挑战。",
            "• 防洗牌道具仅在洗牌模式生效，防止因连续失败触发的洗牌。",
            "• 时间静止道具仅适用于终极挑战模式，冻结倒计时10秒。"
        ]
        for n in notes: t.insert(tk.END, f"{n}\n", "body")

    def _content_gameplay(self, t):
        t.insert(tk.END, "🎯 游戏玩法\n", "h1")
        t.insert(tk.END, "一、三种游戏模式\n", "h2")
        modes = [
            "1. 普通模式 ：默认4x4网格，无时间限制，适合休闲体验。",
            "2. 终极挑战模式 ：4x9网格，仅120秒时间限制，需快速完成配对。",
            "3. 洗牌模式：同4x9网格，180秒时间限制；连续7次匹配失误会打乱未配对卡片。"
        ]
        for m in modes: t.insert(tk.END, f"{m}\n", "body")
        t.insert(tk.END, "二、核心规则\n", "h2")
        rules = [
            "1. 翻牌配对：每次点击两张卡片，图案/数值相同则消除，不同则翻回。",
            "2. 胜负判定：找出所有配对即通关；限时模式下时间耗尽则失败。"
        ]
        for r in rules: t.insert(tk.END, f"{r}\n", "body")

    def _content_achievements(self, t):
        t.insert(tk.END, "🏆 成就系统\n", "h1")
        t.insert(tk.END, "游戏内置29项成就，达成即领奖励！\n", "body")
        sections = [
            ("一、新手必备", ["完成1场游戏", "首次通关任意模式", "首次使用任意道具"]),
            ("二、进阶挑战", ["累计游玩50局", "累计积分达5000分", "终极模式通关5次"]),
            ("三、高手专属", ["无道具通关10次", "普通模式零失误通关", "终极模式80秒内通关"]),
            ("四、连胜&活跃", ["连胜3/5/7/10场", "单日完成10局游戏", "连续登录奖励"])
        ]
        for title, subs in sections:
            t.insert(tk.END, f"{title}\n", "h2")
            for s in subs: t.insert(tk.END, f"• {s}\n", "body")

    def _content_points(self, t):
        t.insert(tk.END, "💎 积分获取指南\n", "h1")
        t.insert(tk.END, "一、初始登录福利\n", "h2")
        t.insert(tk.END, "新注册即得500初始积分，连续登录有额外奖励。\n", "body")
        t.insert(tk.END, "二、游戏通关积分\n", "h2")
        modes = [
            ("普通模式", "基础分：200分 | 加分：限时/零失误"),
            ("终极模式", "基础分：1200分 | 加分：限时/零失误")
        ]
        for m, desc in modes:
            t.insert(tk.END, f"{m}\n", "highlight")
            t.insert(tk.END, f"{desc}\n", "body")

    def _content_tips(self, t):
        t.insert(tk.END, "🎮 游戏核心技巧\n", "h1")

        sections = [
            ("1. 记牌小窍门", [
                "翻牌前3秒分区看（左上→右上→左下→右下），优先记颜色/形状特别的卡牌",
                "用简单联想记相邻卡牌（比如“月亮+星星=夜空”），减少记忆负担"
            ]),
            ("2. 道具不浪费", [
                "时间延长：极限模式剩10秒内用，且已找到2对以上卡牌时",
                "提示道具：30秒没找到匹配或剩牌少卡顿时用，重点看边缘卡牌",
                "洗牌道具：10张以上卡牌没思路时，洗牌后重新分区观察"
            ]),
            ("3. 模式进阶", [
                "普通模式：先练准确率（≥80%），翻2次牌复盘1秒",
                "极限模式：开局10秒只看标记3对，优先翻标记卡牌省时间"
            ]),
            ("4. 福利快速拿", [
                "连续登录3天领道具包，7天解锁限定皮肤",
                "先做简单成就（如“连配5对”），快速攒积分换道具"
            ]),
            ("5. 避坑提醒", [
                "不频繁乱翻，每配1对停顿0.5秒巩固记忆",
                "前期少用道具，20分钟后累了就休息5分钟"
            ])
        ]

        # 修改：不再使用 \n 强制换行，而是依赖 h2 的 spacing1=15 实现更紧凑的间距
        for title, items in sections:
            t.insert(tk.END, f"{title}\n", "h2")
            for item in items:
                t.insert(tk.END, f"• {item}\n", "tip_item")
            
        t.insert(tk.END, "\n祝您游戏愉快！有问题随时反馈～\n", "italic_footer")

    def show(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()