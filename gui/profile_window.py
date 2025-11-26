"""
个人档案窗口 - v4.1 优化版
优化：间距缩减、紧凑布局
"""

import tkinter as tk
import math
from datetime import datetime
from config import UIConfig

class ProfileWindow:
    def __init__(self, master, player):
        self.player = player
        self.window = tk.Toplevel(master)
        self.window.title("我的数据")
        self.window.geometry("600x700")
        self.window.config(bg='#E0F7FA')
        self.window.transient(master)
        self.window.grab_set()
        self._center_window()
        
        self.canvas = tk.Canvas(self.window, bg='#E0F7FA', highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._draw_bg_decorations()
        
        self._create_header_area()
        self._create_back_button()
        self._create_stats_grid()

    def _center_window(self):
        self.window.update_idletasks()
        w, h = 600, 700
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _draw_bg_decorations(self):
        self.canvas.create_oval(-100, 500, 100, 700, fill='#C8E6C9', outline="")
        self.canvas.create_oval(500, -50, 650, 100, fill='#B2DFDB', outline="")

    def _create_header_area(self):
        center_x = 300
        y_pos = 75
        text = "我的数据"
        font = ("Arial Rounded MT Bold", 32, "bold")
        
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            self.canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill='white')
        self.canvas.create_text(center_x, y_pos, text=text, font=font, fill='#A5D6A7')
        
        # 确保 statistics 获取正确
        stats = self.player.get_statistics()
        win_rate = int(stats['win_rate'])
        circle_x = center_x + 100
        circle_y = y_pos - 5
        r = 22
        self.canvas.create_oval(circle_x-r, circle_y-r, circle_x+r, circle_y+r, fill='#FFCC80', outline='white', width=2)
        self.canvas.create_text(circle_x, circle_y-5, text=f"{win_rate}%", font=('Arial', 10, 'bold'), fill='white')
        self.canvas.create_text(circle_x, circle_y+8, text="胜率", font=('Arial', 8), fill='white')
        
        self.canvas.create_text(center_x, y_pos + 55, 
                                text=f"玩家：{self.player.username}", 
                                font=('Arial', 12), fill='#546E7A')

    def _create_back_button(self):
        btn = tk.Button(self.window, text="✖", command=self.window.destroy, 
                        bg='#B2DFDB', fg='white', font=('Arial', 10, 'bold'),
                        relief=tk.FLAT, bd=0)
        btn.place(x=560, y=15, width=25, height=25)

    def _create_stats_grid(self):
        container = tk.Frame(self.window, bg='#E0F7FA')
        container.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        
        stats = self.player.get_statistics()
        
        items = [
            ("总场次", str(stats['total_games']), '#42A5F5'),
            ("通关数", str(stats['completed_games']), '#66BB6A'),
            ("当前积分", str(self.player.points), '#FFA726'),
            ("连续登录", f"{self.player.consecutive_days}天", '#EC407A'),
            ("最佳时间", self._fmt_time(stats['best_time_normal']), '#AB47BC'),
            ("注册日期", datetime.fromtimestamp(self.player.created_at).strftime('%y/%m/%d'), '#78909C')
        ]
        
        r, c = 0, 0
        for title, val, color in items:
            f = tk.Frame(container, bg='white', width=200, height=70, padx=10, pady=8)
            f.grid(row=r, column=c, padx=10, pady=10)
            f.pack_propagate(False)
            
            tk.Frame(f, bg=color, width=4).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
            
            tk.Label(f, text=title, font=('Arial', 10), fg='#90A4AE', bg='white').pack(anchor='w')
            tk.Label(f, text=val, font=('Arial Rounded MT Bold', 14), fg='#455A64', bg='white').pack(anchor='w')
            
            c += 1
            if c >= 2:
                c = 0
                r += 1
    
    def _fmt_time(self, s):
        if s is None:
            return "--"
        return f"{int(s)}s"