import tkinter as tk
from tkinter import messagebox
import math 
from gui.game_window import GameWindow
from gui.shop_window import ShopWindow
from gui.career_window import CareerWindow
from gui.profile_window import ProfileWindow
from config import UIConfig
from managers.data_manager import save_player

# --- 辅助：圆角矩形绘制 ---
def draw_rounded_rect(canvas, x, y, w, h, r, fill, outline=""):
    canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline=outline)
    canvas.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline=outline)
    canvas.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline=outline)

# --- 自定义退出弹窗 (优化版) ---
class ExitDialog(tk.Toplevel):
    def __init__(self, parent, on_confirm):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.configure(bg=UIConfig.COLORS['primary'])
        self.overrideredirect(True) # 去除系统边框
        self.attributes('-topmost', True)
        
        # 窗口尺寸
        w, h = 400, 240 # 高度稍微减小
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self.canvas = tk.Canvas(self, width=w, height=h, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 1. 绘制阴影
        draw_rounded_rect(self.canvas, 8, 8, w-16, h-16, 25, fill='#B0BEC5')
        
        # 2. 绘制白色主体
        draw_rounded_rect(self.canvas, 4, 4, w-16, h-16, 25, fill='white')
        
        # 3. 内容 (优化排版)
        # 表情缩小，位置上移
        self.canvas.create_text(w/2, 75, text="🥺", font=("Segoe UI Emoji", 36)) # 字体改小
        
        # 标题居中
        self.canvas.create_text(w/2, 125, text="这就走了吗？", 
                                font=("Arial Rounded MT Bold", 18, "bold"), fill='#455A64')
        
        # 4. 按钮区域 (上移)
        btn_frame = tk.Frame(self, bg='white')
        btn_frame.place(relx=0.5, rely=0.80, anchor=tk.CENTER)
        
        # 再玩一会 (绿色)
        self._create_mini_btn(btn_frame, "再玩一会", '#A5D6A7', '#2E7D32', self.destroy).pack(side=tk.LEFT, padx=15)
        
        # 狠心离开 (粉色)
        self._create_mini_btn(btn_frame, "狠心离开", '#FFAB91', '#D84315', self._confirm_exit).pack(side=tk.LEFT, padx=15)
        
        self.grab_set()

    def _create_mini_btn(self, parent, text, bg_col, text_col, cmd):
        btn = tk.Canvas(parent, width=110, height=40, bg='white', highlightthickness=0)
        
        def draw():
            btn.delete('all')
            draw_rounded_rect(btn, 0, 0, 110, 40, 20, bg_col)
            btn.create_text(55, 20, text=text, font=('Arial Rounded MT Bold', 11, 'bold'), fill=text_col)

        draw()
        btn.bind('<Enter>', lambda e: btn.config(cursor='hand2'))
        btn.bind('<Leave>', lambda e: btn.config(cursor=''))
        btn.bind('<Button-1>', lambda e: cmd())
        return btn

    def _confirm_exit(self):
        self.destroy()
        self.on_confirm()


class CandyButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=260, height=75, theme='yellow'):
        super().__init__(master, width=width, height=height, 
                         bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.text = text
        self._command = command
        self.btn_width = width
        self.btn_height = height
        self.theme = theme
        
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
        
        self.canvas = tk.Canvas(self.window, bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self._create_background_decorations()
        self._create_title()
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
        self.canvas.create_oval(-50, -50, 250, 250, fill='#4DB6AC', outline="")
        w, h = 1000, 750
        self.canvas.create_oval(w-200, h-200, w+100, h+100, fill='#FFCA28', outline="")
        self.canvas.create_oval(100, h-150, 220, h-30, fill='#FFF176', outline="")

    def _create_title(self):
        center_x = 500
        y_pos = 160
        text = "SCAU 记忆翻牌"
        font = ("Arial Rounded MT Bold", 64, "bold")
        stroke_color = '#FFFFFF' 
        inner_shadow_color = '#F9A825'
        face_color = '#FFEB3B'
        
        stroke_radius = 10
        steps = 72 
        for i in range(steps):
            angle = i * (2 * math.pi) / steps
            dx = stroke_radius * math.cos(angle)
            dy = stroke_radius * math.sin(angle)
            self.canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill=stroke_color)
        
        fill_radius = 5
        for i in range(36):
            angle = i * (2 * math.pi) / 36
            dx = fill_radius * math.cos(angle)
            dy = fill_radius * math.sin(angle)
            self.canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill=stroke_color)

        shadow_offset = 5
        self.canvas.create_text(center_x, y_pos+shadow_offset, text=text, font=font, fill=inner_shadow_color)
        self.canvas.create_text(center_x+2, y_pos+shadow_offset, text=text, font=font, fill=inner_shadow_color)

        self.canvas.create_text(center_x, y_pos, text=text, font=font, fill=face_color)
        
        self.canvas.create_text(center_x, y_pos + 90, 
                                text=f"✨ 欢迎回来，{self.player.username} ✨", 
                                font=("Arial", 16, "bold"), fill='white')

    def _create_menu_buttons(self):
        btn_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        btn_frame.place(relx=0.5, rely=0.62, anchor=tk.CENTER)

        buttons_config = [
            ("开始游戏", self._start_game, 'yellow'),
            ("道具商城", self._open_shop, 'blue'),
            ("游戏生涯", self._open_career, 'purple'),
            ("个人主页", self._open_profile, 'green') 
        ]

        for text, cmd, theme in buttons_config:
            btn = CandyButton(btn_frame, text=text, command=cmd, 
                              width=280, height=75, theme=theme)
            btn.pack(pady=10)

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
        try: save_player(self.player)
        except: pass

    def _on_closing(self):
        def perform_exit():
            if hasattr(self.player, 'remove_change_listener'):
                try: self.player.remove_change_listener(self._save_player)
                except: pass
            self._save_player()
            self.window.destroy()
        ExitDialog(self.window, perform_exit)

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    from core.player import Player
    p = Player("TestUser")
    MainWindow(p).run()