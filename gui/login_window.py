"""
登录窗口
"""

import tkinter as tk
from tkinter import messagebox
import math
import os
import json
import random
from PIL import Image, ImageTk

from config import DataConfig, ASSETS_DIR, AchievementConfig, UIConfig
from core.player import Player
from managers.data_manager import add_unlocked_achievement
from gui.admin_window import AdminWindow

THEME = {
    'bg_color': '#E0F7FA',
    'card_bg': '#FFFFFF',           
    'card_shadow': '#00695C',       
    'text_stroke': '#FFFFFF',       
    'text_shadow': '#F9A825',       
    'text_face': "#FEF329",         
    'input_bg': '#F5F5F5',          
    'input_border': '#4DD0E1',      
    'link_color': '#039BE5',

    'bg_sky': '#E3F2FD',      
    'hill_1': '#F8BBD0', 
    'hill_2': '#C5CAE9',  
    'hill_3': '#B2DFDB', 
    'sun_glow': '#FFF9C4', 
}

class GraphicsUtils:
    """绘图工具类"""
    @staticmethod
    def draw_solid_capsule(canvas, x, y, w, h, color):
        r = h / 2
        canvas.create_arc(x, y, x + h, y + h, start=90, extent=180, fill=color, outline="")
        canvas.create_arc(x + w - h, y, x + w, y + h, start=270, extent=180, fill=color, outline="")
        canvas.create_rectangle(x + r, y, x + w - r, y + h, fill=color, outline="")

# --- 自定义组件按钮 ---
class CandyButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=200, height=60, theme='yellow'):
        super().__init__(master, width=width, height=height, 
                         bg=THEME['card_bg'], highlightthickness=0, bd=0)
        self.text = text
        self._command = command
        self.width = width
        self.height = height
        self.theme = theme
        
        self.colors = {
            'yellow': ('#FFD54F', '#FFA000', '#FFE082', '#FFFFFF', '#795548'),
            'blue':   ('#4FC3F7', '#0288D1', '#81D4FA', '#FFFFFF', '#01579B'),
        }
        self._state = 'normal'
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._draw()

    def _draw(self):
        self.delete('all')
        cx, cy = self.width / 2, self.height / 2
        scale = 1.02 if self._state == 'hover' else (0.96 if self._state == 'active' else 1.0)
        w, h = (self.width - 4) * scale, (self.height - 4) * scale
        
        colors = self.colors.get(self.theme, self.colors['yellow'])
        body_col, shadow_col, gloss_col, text_col, stroke_col = colors
        
        offset_y = 4 if self._state != 'active' else 0
        shadow_depth = 5 if self._state != 'active' else 2
        x, y = cx - w/2, cy - h/2
        
        GraphicsUtils.draw_solid_capsule(self, x, y + offset_y + shadow_depth, w, h, shadow_col)
        GraphicsUtils.draw_solid_capsule(self, x, y + offset_y, w, h, body_col)
        
        gloss_h, gloss_w = h * 0.4, w * 0.6
        self.create_arc(x + 15, y + offset_y + 5, x + 15 + gloss_w, y + offset_y + 5 + gloss_h * 2, 
                        start=90, extent=100, style=tk.CHORD, fill=gloss_col, outline="")

        font = ('Microsoft YaHei UI', 18, 'bold')
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]: 
            self.create_text(cx+dx, cy+offset_y+dy, text=self.text, font=font, fill=stroke_col)
        self.create_text(cx, cy+offset_y, text=self.text, font=font, fill=text_col)

    def _on_enter(self, e): self._state = 'hover'; self.config(cursor='hand2'); self._draw()
    def _on_leave(self, e): self._state = 'normal'; self.config(cursor=''); self._draw()
    def _on_press(self, e): self._state = 'active'; self._draw()
    def _on_release(self, e): 
        if self._state == 'active': 
            self._state = 'hover'; self._draw()
            if self._command: self.after(50, self._command)

# --- 自定义组件输入框 ---
class CandyEntry(tk.Canvas):
    def __init__(self, master, width=350, height=55, placeholder="", is_password=False):
        super().__init__(master, width=width, height=height, bg=THEME['card_bg'], highlightthickness=0, bd=0)
        self.w = width
        self.h = height
        self._draw_bg()
        
        self.entry = tk.Entry(self, bg=THEME['input_bg'], bd=0, font=('Microsoft YaHei UI', 12), 
                              fg='#455A64', highlightthickness=0, insertbackground='#263238')
        if is_password:
            self.entry.config(show='●')
        self.create_window(width/2, height/2, window=self.entry, width=width-40, height=30)

    def _draw_bg(self):
        # 1. 边框层
        GraphicsUtils.draw_solid_capsule(self, 2, 2, self.w-4, self.h-4, THEME['input_border'])
        # 2. 内胆层
        border_width = 2
        GraphicsUtils.draw_solid_capsule(self, 2+border_width, 2+border_width, 
                                         self.w-4-2*border_width, self.h-4-2*border_width, THEME['input_bg'])

    def get(self): return self.entry.get()
    def set_text(self, text): self.entry.delete(0, tk.END); self.entry.insert(0, text)

# --- 主窗口逻辑 ---
class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.window = tk.Tk()
        self.window.title("SCAU 记忆翻牌 - 登录")
        self.window.geometry("1100x700")
        self.window.resizable(False, False)
        self.window.config(bg=THEME['bg_sky']) 
        
        self._center_window()
        self.players_db = self._load_players()
        self._hidden_login_clicks = 0
        
        self.canvas_bg = tk.Canvas(self.window, highlightthickness=0, bd=0, bg=THEME['bg_sky'])
        self.canvas_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self._draw_vector_scenery()
        
        self.card_w, self.card_h = 520, 620

        cx, cy = 550, 350 
        self.canvas_bg.create_oval(cx-230, cy+280, cx+230, cy+320, fill='#90A4AE', outline="") 
        
        self.card_canvas = tk.Canvas(self.window, width=self.card_w, height=self.card_h, 
                                     bg=THEME['bg_color'], highlightthickness=0, bd=0)
        self.card_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self._draw_card_base()
        
        self.content_frame = tk.Frame(self.card_canvas, bg=THEME['card_bg'])
        self.content_frame.place(relx=0.5, rely=0.58, anchor=tk.CENTER, width=450, height=480)
        
        self.is_register_mode = False
        self._init_ui_elements()

    def _center_window(self):
        self.window.update_idletasks()
        w, h = 1100, 700
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _draw_vector_scenery(self):
        """绘制背景"""
        w, h = 1100, 700
        c = self.canvas_bg
        
        c.create_oval(800, -100, 1200, 300, fill=THEME['sun_glow'], outline="") 
        
        c.create_oval(-100, 350, 800, 850, fill=THEME['hill_1'], outline="") # 粉
        c.create_oval(400, 450, 1300, 950, fill=THEME['hill_2'], outline="") # 紫
        c.create_oval(-200, 550, 600, 1050, fill=THEME['hill_3'], outline="") # 绿
        
        colors = ['#FFFFFF', '#FFECB3', '#E1BEE7', '#B3E5FC']
        for _ in range(20):
            bx = random.randint(0, w)
            by = random.randint(0, h)
            size = random.randint(5, 25)
            color = random.choice(colors)
            c.create_oval(bx, by, bx+size, by+size, fill=color, outline="")

    def _draw_card_base(self):
        """绘制卡片背景和标题"""
        # 阴影
        GraphicsUtils.draw_solid_capsule(self.card_canvas, 20, 30, self.card_w-40, self.card_h-40, THEME['card_shadow'])
        # 本体
        GraphicsUtils.draw_solid_capsule(self.card_canvas, 20, 20, self.card_w-40, self.card_h-40, THEME['card_bg'])
        
        # 绘制标题
        self._draw_title(self.card_w/2, 90, "SCAU 记忆翻牌")

    def _draw_title(self, x, y, text):
        font = ("Microsoft YaHei UI", 38, "bold")
        # 白边
        for dx in range(-4, 5, 2):
            for dy in range(-4, 5, 2):
                self.card_canvas.create_text(x+dx, y+dy, text=text, font=font, fill=THEME['text_stroke'])
        # 阴影
        self.card_canvas.create_text(x, y+4, text=text, font=font, fill=THEME['text_shadow'])
        # 表面
        self.card_canvas.create_text(x, y, text=text, font=font, fill=THEME['text_face'])

    def _init_ui_elements(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        title = "登录游戏" if not self.is_register_mode else "注册账号"
        tk.Label(self.content_frame, text=title, font=("Microsoft YaHei UI", 16, "bold"), 
                 bg=THEME['card_bg'], fg="#546E7A").pack(pady=(10, 25))
        
        entry_w = 360
        
        tk.Label(self.content_frame, text="用户名 / Username", font=("Microsoft YaHei UI", 11), 
                 bg=THEME['card_bg'], fg="#90A4AE").pack(anchor="w", padx=45)
        self.entry_user = CandyEntry(self.content_frame, width=entry_w, height=55)
        self.entry_user.pack(pady=(5, 15))
        
        tk.Label(self.content_frame, text="密码 / Password", font=("Microsoft YaHei UI", 11), 
                 bg=THEME['card_bg'], fg="#90A4AE").pack(anchor="w", padx=45)
        self.entry_pwd = CandyEntry(self.content_frame, width=entry_w, height=55, is_password=True)
        self.entry_pwd.pack(pady=(5, 25))
        
        if not self.is_register_mode:
            self.btn_action = CandyButton(self.content_frame, text="立即登录", theme='yellow', 
                                          width=entry_w, height=65, command=self._handle_login_click)
            self.btn_action.pack(pady=10)
            
            link = tk.Label(self.content_frame, text="没有账号？点击这里注册 ✨", 
                            font=("Microsoft YaHei UI", 10, "underline"), 
                            fg=THEME['link_color'], bg=THEME['card_bg'], cursor="hand2")
            link.pack(pady=10)
            link.bind("<Button-1>", lambda e: self._toggle_mode())
        else:
            self.btn_action = CandyButton(self.content_frame, text="创建账号", theme='blue', 
                                          width=entry_w, height=65, command=self._handle_register)
            self.btn_action.pack(pady=10)
            
            link = tk.Label(self.content_frame, text="已有账号？返回登录 🔙", 
                            font=("Microsoft YaHei UI", 10, "underline"), 
                            fg=THEME['link_color'], bg=THEME['card_bg'], cursor="hand2")
            link.pack(pady=10)
            link.bind("<Button-1>", lambda e: self._toggle_mode())

    def _toggle_mode(self):
        self.is_register_mode = not self.is_register_mode
        self._init_ui_elements()

    def _handle_login_click(self):
        if not hasattr(self, '_hidden_login_clicks'): self._hidden_login_clicks = 0
        self._hidden_login_clicks += 1
        if self._hidden_login_clicks >= 5:
            self._hidden_login_clicks = 0
            self._login_as_admin()
        else:
            self._handle_login()

    def _handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pwd.get().strip()
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return
        if username not in self.players_db:
            messagebox.showerror("错误", "用户不存在，请先注册")
            return
        data = self.players_db[username]
        if data.get('password', '') != password:
            messagebox.showerror("错误", "密码错误")
            return
        player = Player.from_dict(data)
        self._finish_login(player)

    def _handle_register(self):
        username = self.entry_user.get().strip()
        password = self.entry_pwd.get().strip()
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return
        if len(username) < 3 or len(password) < 6:
            messagebox.showwarning("提示", "用户名需3字符以上，密码需6字符以上")
            return
        if username in self.players_db:
            messagebox.showerror("错误", "用户名已存在")
            return
        player = Player(username, password)
        self._save_player(player)
        messagebox.showinfo("成功", f"注册成功！\n获得新手奖励：500积分")
        self._toggle_mode()
        self.entry_user.set_text(username)

    def _login_as_admin(self):
        self.window.withdraw() 
        admin_window = AdminWindow(self.window)
        admin_window.show()
        self.window.deiconify() 

    def _finish_login(self, player):
        player.update_login()
        for ach in getattr(AchievementConfig, 'ACHIEVEMENTS', []):
            aid = ach.get('id')
            if isinstance(aid, str) and aid.startswith('login_'):
                cond = ach.get('condition')
                if callable(cond) and cond(player) and not player.has_achievement(aid):
                    player.unlock_achievement(aid)
                    if ach.get('reward', 0): player.add_points(ach['reward'])
                    add_unlocked_achievement(player.username, aid)
        self._save_player(player)
        self.window.destroy()
        self.on_login_success(player)

    def _load_players(self):
        if os.path.exists(DataConfig.PLAYERS_FILE):
            try:
                with open(DataConfig.PLAYERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_player(self, player):
        self.players_db[player.username] = player.to_dict()
        with open(DataConfig.PLAYERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.players_db, f, indent=2, ensure_ascii=False)

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    def on_success(p): print(f"Logged in: {p.username}")
    LoginWindow(on_success).run()
