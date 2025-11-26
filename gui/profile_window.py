"""
个人档案窗口 - v4.3 修复版
"""

import tkinter as tk
import math
from datetime import datetime
from config import UIConfig

# --- 绘图辅助 ---
def draw_rounded_rect(canvas, x, y, w, h, r, fill, outline=""):
    canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline=outline)
    canvas.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline=outline)
    canvas.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline=outline)

class ProfileWindow:
    def __init__(self, master, player):
        self.player = player
        self.window = tk.Toplevel(master)
        self.window.title("我的数据")
        self.window.geometry("650x750") 
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
        
        # === Top 5 展示 (Heap 可视化，移除技术性文字) ===
        self._create_heap_display()

    def _center_window(self):
        self.window.update_idletasks()
        w, h = 650, 750
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _draw_bg_decorations(self):
        self.canvas.create_oval(-100, 500, 100, 700, fill='#C8E6C9', outline="")
        self.canvas.create_oval(500, -50, 650, 100, fill='#B2DFDB', outline="")

    def _create_header_area(self):
        center_x = 325
        y_pos = 60
        text = "我的数据"
        font = ("Arial Rounded MT Bold", 32, "bold")
        
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            self.canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill='white')
        self.canvas.create_text(center_x, y_pos, text=text, font=font, fill='#A5D6A7')
        
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
        btn.place(x=610, y=15, width=25, height=25)

    def _create_stats_grid(self):
        container = tk.Frame(self.window, bg='#E0F7FA')
        container.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
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
            f = tk.Frame(container, bg='white', width=190, height=65, padx=10, pady=8)
            f.grid(row=r, column=c, padx=8, pady=8)
            f.pack_propagate(False)
            
            tk.Frame(f, bg=color, width=4).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
            tk.Label(f, text=title, font=('Arial', 10), fg='#90A4AE', bg='white').pack(anchor='w')
            tk.Label(f, text=val, font=('Arial Rounded MT Bold', 13), fg='#455A64', bg='white').pack(anchor='w')
            c += 1
            if c >= 2: c = 0; r += 1

    def _create_heap_display(self):
        frame = tk.Frame(self.window, bg='#E0F7FA')
        frame.place(relx=0.5, rely=0.75, anchor=tk.CENTER, width=580, height=280)
        
        # 移除 "(基于堆结构)"，保留核心标题
        tk.Label(frame, text="🏆 个人巅峰记录", font=('Arial Rounded MT Bold', 14, 'bold'), 
                 bg='#E0F7FA', fg='#00796B').pack(pady=(0, 10))
        
        content = tk.Frame(frame, bg='#E0F7FA')
        content.pack(fill=tk.BOTH, expand=True)
        
        self._draw_top_n_column(content, "普通模式 Top 5", self.player.best_records_normal.get_top_n(), tk.LEFT, '#FFF9C4')
        self._draw_top_n_column(content, "终极模式 Top 5", self.player.best_records_ultimate.get_top_n(), tk.RIGHT, '#FFCCBC')

    def _draw_top_n_column(self, parent, title, records, side, bg_col):
        col = tk.Canvas(parent, width=270, height=220, bg='#E0F7FA', highlightthickness=0)
        col.pack(side=side, padx=10)
        
        draw_rounded_rect(col, 0, 0, 270, 220, 15, 'white')
        col.create_text(135, 20, text=title, font=('Arial', 11, 'bold'), fill='#546E7A')
        col.create_line(20, 35, 250, 35, fill='#ECEFF1')
        
        if not records:
            col.create_text(135, 110, text="暂无数据", fill='#B0BEC5', font=('Arial', 10))
            return
            
        y = 55
        for i, (time_val, data) in enumerate(records):
            rank_color = '#FFD700' if i == 0 else ('#C0C0C0' if i == 1 else ('#CD7F32' if i == 2 else '#90A4AE'))
            col.create_text(35, y, text=f"#{i+1}", font=('Arial Rounded MT Bold', 12, 'bold'), fill=rank_color)
            col.create_text(100, y, text=f"{int(time_val)} 秒", font=('Arial', 11), fill='#455A64', anchor='w')
            ts = data.get('timestamp', 0)
            date_str = datetime.fromtimestamp(ts).strftime('%m/%d')
            col.create_text(240, y, text=date_str, font=('Arial', 9), fill='#CFD8DC', anchor='e')
            y += 32
    
    def _fmt_time(self, s):
        if s is None: return "--"
        return f"{int(s)}s"