"""
主窗口
游戏主菜单界面 - v3.6 像素级复刻版
核心修改：
1. 标题重构：严格复刻截图样式——超厚白边 + 橙色立体层 + 亮黄表面，使用高密度圆周算法消除毛刺。
2. 按钮保持：保留你满意的 v3.5 糖果风格（黄/蓝/紫/绿）。
"""

import tkinter as tk
from tkinter import messagebox
import math 
from gui.game_window import GameWindow
from gui.shop_window import ShopWindow
from gui.career_window import CareerWindow
from gui.profile_window import ProfileWindow
from config import UIConfig

# --- 自定义组件：糖果风格按钮 (保持不变) ---
class CandyButton(tk.Canvas):
    """
    糖果/果冻风格按钮
    特点：圆润、有高光、立体阴影、文字描边
    """
    def __init__(self, master, text, command=None, width=260, height=75, theme='yellow'):
        super().__init__(master, width=width, height=height, 
                         bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.text = text
        self._command = command
        self.btn_width = width
        self.btn_height = height
        self.theme = theme
        
        # 颜色配置库 (主体色, 阴影色, 高光色, 文字色, 文字描边色)
        self.colors = {
            'yellow': ('#FFD54F', '#FFA000', '#FFE082', '#FFFFFF', '#795548'), 
            'blue':   ('#4FC3F7', '#0288D1', '#81D4FA', '#FFFFFF', '#01579B'),
            'purple': ('#CE93D8', '#8E24AA', '#F3E5F5', '#FFFFFF', '#4A148C'),
            'green':  ('#A5D6A7', '#388E3C', '#E8F5E9', '#FFFFFF', '#1B5E20'),
        }
        
        self._state = 'normal'
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        self._draw()

    def _draw(self):
        self.delete('all')
        cx, cy = self.btn_width / 2, self.btn_height / 2
        
        scale = 1.0
        if self._state == 'hover': scale = 1.05
        if self._state == 'active': scale = 0.95
        
        w = (self.btn_width - 10) * scale
        h = (self.btn_height - 10) * scale
        
        theme_cols = self.colors.get(self.theme, self.colors['yellow'])
        body_col, shadow_col, gloss_col, text_col, stroke_col = theme_cols
        
        offset_y = 4 if self._state != 'active' else 0
        shadow_depth = 8 if self._state != 'active' else 3
        
        x1 = cx - w/2
        y1 = cy - h/2
        x2 = cx + w/2
        y2 = cy + h/2
        r = h / 2 

        self._draw_capsule(x1, y1 + offset_y + shadow_depth, x2, y2 + offset_y + shadow_depth, r, fill=shadow_col)
        self._draw_capsule(x1, y1 + offset_y, x2, y2 + offset_y, r, fill=body_col)
        
        gloss_h = h * 0.4
        gloss_w = w * 0.6
        gloss_x1 = x1 + 10
        gloss_y1 = y1 + offset_y + 5
        self.create_arc(gloss_x1, gloss_y1, gloss_x1 + gloss_w, gloss_y1 + gloss_h * 2, 
                        start=90, extent=100, style=tk.CHORD, fill=gloss_col, outline="")

        text_y = cy + offset_y
        font = ('Arial Rounded MT Bold', 20, 'bold')
        self._draw_smooth_text(cx, text_y, self.text, font, stroke_col, text_col)

    def _draw_capsule(self, x1, y1, x2, y2, r, fill):
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=180, fill=fill, outline="")
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=270, extent=180, fill=fill, outline="")
        self.create_rectangle(x1+r, y1, x2-r, y2+1, fill=fill, outline="")

    def _draw_smooth_text(self, x, y, text, font, stroke_color, fill_color):
        radius = 2
        steps = 12
        for i in range(steps):
            angle = i * (2 * math.pi) / steps
            dx = radius * math.cos(angle)
            dy = radius * math.sin(angle)
            self.create_text(x + dx, y + dy, text=text, font=font, fill=stroke_color)
        self.create_text(x, y, text=text, font=font, fill=fill_color)

    def _on_enter(self, e):
        self._state = 'hover'
        self.config(cursor='hand2')
        self._draw()

    def _on_leave(self, e):
        self._state = 'normal'
        self.config(cursor='')
        self._draw()

    def _on_press(self, e):
        self._state = 'active'
        self._draw()

    def _on_release(self, e):
        if self._state == 'active':
            self._state = 'hover'
            self._draw()
            if self._command:
                self.after(50, self._command)

# --- 主窗口类 ---
class MainWindow:
    def __init__(self, player):
        self.player = player
        
        if hasattr(self.player, 'add_change_listener'):
            try: self.player.add_change_listener(self._save_player)
            except: pass

        self.window = tk.Tk()
        self.window.title("SCAU 记忆翻牌")
        self.window.geometry("1000x750")
        self.window.config(bg=UIConfig.COLORS['primary'])
        
        self._center_window()
        self.window.resizable(False, False)
        
        # 1. 背景层
        self.canvas = tk.Canvas(self.window, bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self._create_background_decorations()
        self._create_title()

        # 2. 按钮层
        self._create_menu_buttons()
        
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_background_decorations(self):
        """绘制背景装饰"""
        self.canvas.create_oval(-50, -50, 250, 250, fill='#4DB6AC', outline="")
        w, h = 1000, 750
        self.canvas.create_oval(w-200, h-200, w+100, h+100, fill='#FFCA28', outline="")
        self.canvas.create_oval(100, h-150, 220, h-30, fill='#FFF176', outline="")

    def _create_title(self):
        """
        严格复刻截图样式
        算法：多层高密度圆周堆叠
        """
        center_x = 500
        y_pos = 160
        
        text = "SCAU 记忆翻牌"
        # 使用系统中最圆润的粗体
        font = ("Arial Rounded MT Bold", 64, "bold")
        
        # --- 配色方案 (取自截图) ---
        # 1. 外层超厚白边
        stroke_color = '#FFFFFF' 
        # 2. 内部立体阴影 (深橙色/金色) - 模拟截图文字里的深色部分
        inner_shadow_color = '#F9A825' # Dark Yellow/Orange
        # 3. 表面亮黄色 - 模拟截图文字的最亮部分
        face_color = '#FFEB3B' # Bright Yellow
        
        # --- 绘制逻辑 ---
        
        # 第1层：超厚白边 (模拟贴纸效果)
        # 截图里的白边非常厚，我们需要堆叠一个半径很大的圆
        # 为了绝对光滑无毛刺，steps 设置为 72 (每5度画一次)
        stroke_radius = 10 # 边框厚度
        steps = 72 
        
        for i in range(steps):
            angle = i * (2 * math.pi) / steps
            dx = stroke_radius * math.cos(angle)
            dy = stroke_radius * math.sin(angle)
            self.canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill=stroke_color)
        
        # 第1.5层：填补白边内部缝隙 (防止半径太大导致中间有空洞)
        fill_radius = 5
        for i in range(36):
            angle = i * (2 * math.pi) / 36
            dx = fill_radius * math.cos(angle)
            dy = fill_radius * math.sin(angle)
            self.canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill=stroke_color)

        # 第2层：内部立体阴影 (向右下偏移)
        # 模拟文字厚度
        shadow_offset = 5
        self.canvas.create_text(center_x, y_pos+shadow_offset, text=text, font=font, fill=inner_shadow_color)
        # 为了让立体感更强，稍微横向也偏移一点点
        self.canvas.create_text(center_x+2, y_pos+shadow_offset, text=text, font=font, fill=inner_shadow_color)

        # 第3层：文字表面 (亮黄色)
        self.canvas.create_text(center_x, y_pos, text=text, font=font, fill=face_color)
        
        # 4. 欢迎语 (保持原样)
        self.canvas.create_text(center_x, y_pos + 90, 
                                text=f"✨ 欢迎回来，{self.player.username} ✨", 
                                font=("Arial", 16, "bold"), fill='white')

    def _create_menu_buttons(self):
        """创建糖果风格按钮"""
        btn_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        btn_frame.place(relx=0.5, rely=0.62, anchor=tk.CENTER)

        buttons_config = [
            ("开始游戏", self._start_game, 'yellow'),
            ("道具商城", self._open_shop, 'blue'),
            ("游戏生涯", self._open_career, 'purple'), # 葡萄紫
            ("个人主页", self._open_profile, 'green')   # 薄荷绿
        ]

        for text, cmd, theme in buttons_config:
            btn = CandyButton(btn_frame, text=text, command=cmd, 
                              width=280, height=75, theme=theme)
            btn.pack(pady=10)

    # --- 交互回调 ---
    def _start_game(self):
        self.window.withdraw()
        def on_close():
            self.window.deiconify()
        GameWindow(self.window, self.player, on_close)

    def _open_shop(self):
        ShopWindow(self.window, self.player)
        
    def _open_career(self):
        CareerWindow(self.window, self.player)

    def _open_profile(self):
        ProfileWindow(self.window, self.player)

    def _save_player(self):
        from config import DataConfig
        import json
        import os
        try:
            if os.path.exists(DataConfig.PLAYERS_FILE):
                with open(DataConfig.PLAYERS_FILE, 'r', encoding='utf-8') as f:
                    db = json.load(f)
            else:
                db = {}
            db[self.player.username] = self.player.to_dict()
            with open(DataConfig.PLAYERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
        except: pass

    def _on_closing(self):
        if messagebox.askokcancel("退出", "确定要退出游戏吗？"):
            if hasattr(self.player, 'remove_change_listener'):
                try: self.player.remove_change_listener(self._save_player)
                except: pass
            self._save_player()
            self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    from core.player import Player
    p = Player("TestUser")
    MainWindow(p).run()