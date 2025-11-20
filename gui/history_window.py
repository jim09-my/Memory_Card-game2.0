"""
历史记录窗口
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class HistoryWindow:
    """历史记录窗口"""

    def __init__(self, master, player):
        self.master = master
        self.player = player

        self.window = tk.Toplevel(master)
        self.window.title("记忆翻牌游戏 - 历史记录")
        self.window.geometry("780x600")
        self.window.resizable(True, True)
        self.window.transient(master)
        self.window.grab_set()
        # 居中窗口
        try:
            self.window.update_idletasks()
            w = self.window.winfo_width() or 780
            h = self.window.winfo_height() or 600
            x = (self.window.winfo_screenwidth() // 2) - (w // 2)
            y = (self.window.winfo_screenheight() // 2) - (h // 2)
            self.window.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

        self.refresh_symbols = ['⟳', '⟲', '⟰', '⟱']
        self.refresh_index = 0
        self.is_refreshing = False

        self._create_widgets()
        self._populate_summary()
        self._populate_records()
        # 监听玩家变化，实时刷新记录与统计
        if hasattr(self.player, 'add_change_listener'):
            try:
                self.player.add_change_listener(self._on_player_change)
            except Exception:
                pass

        # 窗口关闭时清理监听器
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_player_change(self):
        try:
            self.window.after(0, lambda: (self._populate_summary(), self._populate_records()))
        except Exception:
            pass

    def _on_close(self):
        if hasattr(self.player, 'remove_change_listener'):
            try:
                self.player.remove_change_listener(self._on_player_change)
            except Exception:
                pass
        self.window.destroy()

    # ------------------------------ UI ------------------------------
    def _create_widgets(self):
        header = tk.Frame(self.window, bg='#34495E', height=100, padx=20)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📊 游戏历史记录",
            font=('Arial', 24, 'bold'),
            bg='#34495E',
            fg='white'
        ).pack(anchor=tk.W, pady=(15, 0))

        controls = tk.Frame(header, bg='#34495E')
        controls.pack(fill=tk.X, pady=(5, 0))

        self.refresh_btn = tk.Button(
            controls,
            text="🔄 刷新记录",
            font=('Arial', 12, 'bold'),
            command=self._handle_refresh
        )
        self.refresh_btn.pack(side=tk.RIGHT)

        summary = tk.Frame(self.window, padx=20, pady=10)
        summary.pack(fill=tk.X)
        self.summary_frame = summary

        # 记录表格
        table_frame = tk.Frame(self.window, padx=20, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('mode', 'result', 'time', 'moves', 'reward', 'date')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=15
        )

        headings = {
            'mode': '模式',
            'result': '结果',
            'time': '用时',
            'moves': '步数',
            'reward': '奖励',
            'date': '时间'
        }
        widths = [80, 80, 100, 80, 80, 180]

        for col, width in zip(columns, widths):
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=width, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ------------------------------ 数据填充 ------------------------------
    def _populate_summary(self):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        stats = self.player.get_statistics()
        cards = [
            ("总场次", stats['total_games']),
            ("完成场次", stats['completed_games']),
            ("胜率", f"{stats['win_rate']:.1f}%"),
            ("普通最佳", self._format_time(stats['best_time_normal'])),
            ("终极最佳", self._format_time(stats['best_time_ultimate'])),
            ("平均用时", self._format_time(stats['average_time']))
        ]

        for title, value in cards:
            box = tk.Frame(self.summary_frame, bd=1, relief=tk.GROOVE, padx=15, pady=10)
            box.pack(side=tk.LEFT, padx=6, expand=True, fill=tk.X)
            tk.Label(box, text=title, font=('Arial', 11), fg='#7F8C8D').pack()
            tk.Label(box, text=value, font=('Arial', 16, 'bold')).pack()

    def _populate_records(self):
        # 清空
        for row in self.tree.get_children():
            self.tree.delete(row)

        records = sorted(
            self.player.game_records,
            key=lambda r: r.get('timestamp', 0),
            reverse=True
        )[:50]

        for record in records:
            mode = "普通" if record.get('mode') == 'normal' else "终极"
            result = "通关" if record.get('completed') else "失败"
            time_used = self._format_time(record.get('time_used'))
            moves = record.get('moves', '-')
            reward = record.get('reward', 0)
            date = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M')

            self.tree.insert('', tk.END, values=(mode, result, time_used, moves, reward, date))

    # ------------------------------ 刷新逻辑 ------------------------------
    def _handle_refresh(self):
        if self.is_refreshing:
            return
        self.is_refreshing = True
        self.refresh_btn.config(state=tk.DISABLED)
        self._animate_refresh()
        self.window.after(700, self._finish_refresh)

    def _animate_refresh(self):
        if not self.is_refreshing:
            self.refresh_btn.config(text="🔄 刷新记录")
            return

        symbol = self.refresh_symbols[self.refresh_index % len(self.refresh_symbols)]
        self.refresh_btn.config(text=f"{symbol} 刷新中")
        self.refresh_index += 1
        self.window.after(120, self._animate_refresh)

    def _finish_refresh(self):
        self._populate_summary()
        self._populate_records()
        self.is_refreshing = False
        self.refresh_btn.config(state=tk.NORMAL, text="🔄 刷新记录")

    # ------------------------------ 工具方法 ------------------------------
    @staticmethod
    def _format_time(seconds):
        if not seconds and seconds != 0:
            return "-"
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"


# ============== 测试代码 ==============
if __name__ == '__main__':
    from core.player import Player
    import random
    import time

    root = tk.Tk()
    root.withdraw()

    p = Player("Tester")
    for i in range(20):
        p.add_game_record({
            'mode': 'normal' if i % 2 == 0 else 'ultimate',
            'completed': i % 3 != 0,
            'time_used': random.randint(60, 300),
            'moves': random.randint(15, 40),
            'reward': random.randint(100, 500),
            'timestamp': time.time() - i * 3600
        })

    HistoryWindow(root, p).window.mainloop()

