"""
历史记录窗口 - v4.1 优化版
优化：单行列表、减少留白、标题位置
"""

import tkinter as tk
import math
from datetime import datetime
from config import UIConfig

class HistoryWindow:
    def __init__(self, master, player):
        self.player = player
        self.window = tk.Toplevel(master)
        self.window.title("我的战绩")
        self.window.geometry("600x700")
        self.window.config(bg='#E0F7FA')
        self.window.transient(master)
        self.window.grab_set()
        self._center_window()
        
        self.bg_canvas = tk.Canvas(self.window, bg='#E0F7FA', highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._draw_bg_decorations()
        self._draw_title()
        self._create_back_button()
        self._create_history_list()

    def _center_window(self):
        self.window.update_idletasks()
        w, h = 600, 700
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _draw_bg_decorations(self):
        self.bg_canvas.create_oval(-80, 500, 150, 730, fill='#B2DFDB', outline="") 
        self.bg_canvas.create_oval(500, -50, 650, 100, fill='#F0F4C3', outline="")

    def _draw_title(self):
        center_x = 300
        # 修改1：标题下移 (50 -> 65)
        y_pos = 65
        text = "我的战绩"
        font = ("Arial Rounded MT Bold", 32, "bold")
        
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            self.bg_canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill='white')
        
        self.bg_canvas.create_text(center_x, y_pos, text=text, font=font, fill='#B39DDB')

    def _create_back_button(self):
        btn = tk.Button(self.window, text="✖", command=self.window.destroy, 
                        bg='#B2DFDB', fg='white', font=('Arial', 10, 'bold'),
                        relief=tk.FLAT, bd=0)
        btn.place(x=560, y=15, width=25, height=25)

    def _create_history_list(self):
        container = tk.Frame(self.window, bg='#E0F7FA')
        # 修改2：列表区域宽度增加 (540 -> 580)，高度调整
        container.place(relx=0.5, rely=0.58, anchor=tk.CENTER, width=580, height=560)
        
        canvas = tk.Canvas(container, bg='#E0F7FA', highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg='#E0F7FA')
        
        # 让内部frame宽度自适应canvas
        canvas.bind('<Configure>', lambda e: canvas.itemconfig('inner', width=e.width))
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", tags='inner')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        records = sorted(self.player.game_records, key=lambda r: r.get('timestamp', 0), reverse=True)
        
        if not records:
            tk.Label(scrollable, text="暂无战绩", font=('Arial', 14), bg='#E0F7FA', fg='#90A4AE').pack(pady=50)
            return

        for r in records:
            self._draw_one_line_row(scrollable, r)

    def _draw_one_line_row(self, parent, record):
        # 修改3：单行布局，长条形
        is_win = record.get('completed', False)
        bg_col = '#F1F8E9' if is_win else '#FFEBEE'
        
        # 长条形 Frame
        row = tk.Frame(parent, bg=bg_col, pady=10, padx=10)
        row.pack(fill=tk.X, pady=10, padx=50) # 极小的左右边距
        
        # 1. 图标
        icon = "🏆" if is_win else "❌"
        tk.Label(row, text=icon, font=('Segoe UI Emoji', 12), bg=bg_col, width=3).pack(side=tk.LEFT)
        
        # 2. 模式
        mode = "普通" if record.get('mode') == 'normal' else "终极"
        tk.Label(row, text=mode, font=('Arial', 11, 'bold'), fg='#455A64', bg=bg_col, width=6, anchor='w').pack(side=tk.LEFT)
        
        # 3. 日期 (灰色小字)
        date = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%m-%d %H:%M')
        tk.Label(row, text=date, font=('Arial', 10), fg='#90A4AE', bg=bg_col).pack(side=tk.LEFT, padx=5)
        
        # 4. 用时 (靠右侧前)
        time_s = self._fmt_time(record.get('time_used'))
        tk.Label(row, text=f"⏱ {time_s}", font=('Arial', 10), fg='#78909C', bg=bg_col).pack(side=tk.LEFT, padx=10)
        
        # 5. 积分 (最右侧，加粗)
        score = record.get('reward', 0)
        score_col = '#FFA726' if score > 0 else '#9E9E9E'
        tk.Label(row, text=f"+{score}", font=('Arial', 12, 'bold'), fg=score_col, bg=bg_col).pack(side=tk.RIGHT, padx=5)

    def _fmt_time(self, s):
        if not s: return "--"
        return f"{int(s)}s"