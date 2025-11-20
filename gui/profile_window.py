"""
个人资料窗口
"""

import tkinter as tk
from datetime import datetime

from config import ItemConfig


class ProfileWindow:
    """个人资料窗口"""

    def __init__(self, master, player):
        self.master = master
        self.player = player
        self.window = tk.Toplevel(master)
        self.window.title("记忆翻牌游戏 - 个人资料")
        self.window.geometry("720x520")
        self.window.resizable(True, True)
        self.window.transient(master)
        self.window.grab_set()

        # 居中窗口
        try:
            self.window.update_idletasks()
            w = self.window.winfo_width() or 720
            h = self.window.winfo_height() or 520
            x = (self.window.winfo_screenwidth() // 2) - (w // 2)
            y = (self.window.winfo_screenheight() // 2) - (h // 2)
            self.window.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

        self._create_widgets()
        # 监听玩家变化，实时刷新界面
        if hasattr(self.player, 'add_change_listener'):
            try:
                self.player.add_change_listener(self._on_player_change)
            except Exception:
                pass

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_player_change(self):
        try:
            self.window.after(0, self._refresh)
        except Exception:
            pass

    def _refresh(self):
        # 重新填充所有可变部分
        for widget in self.window.winfo_children():
            pass
        # 重新创建 widgets content
        # 简单做法：销毁并重建内容区域
        try:
            # 保留 header（first child），重建 content 区
            # 为保证安全，直接调用 _create_widgets 的刷新路径
            for child in self.window.winfo_children():
                child.destroy()
        except Exception:
            pass
        self._create_widgets()

    def _on_close(self):
        if hasattr(self.player, 'remove_change_listener'):
            try:
                self.player.remove_change_listener(self._on_player_change)
            except Exception:
                pass
        self.window.destroy()

    def _create_widgets(self):
        header = tk.Frame(self.window, bg='#2C3E50', height=110, padx=20)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="👤 个人资料",
            font=('Arial', 26, 'bold'),
            bg='#2C3E50',
            fg='white'
        ).pack(anchor=tk.W, pady=(15, 5))

        info = tk.Frame(header, bg='#2C3E50')
        info.pack(fill=tk.X)

        tk.Label(info, text=f"用户名：{self.player.username}", font=('Arial', 13), bg='#2C3E50', fg='white').pack(
            side=tk.LEFT, padx=10)
        tk.Label(info, text=f"等级：Lv.{self.player.level}", font=('Arial', 13), bg='#2C3E50', fg='white').pack(
            side=tk.LEFT, padx=10)
        tk.Label(info, text=f"积分：{self.player.points}", font=('Arial', 13), bg='#2C3E50', fg='#F0AD4E').pack(
            side=tk.LEFT, padx=10)

        tk.Label(
            header,
            text="信息实时同步，无需手动刷新",
            font=('Arial', 10),
            bg='#2C3E50',
            fg='#BDC3C7'
        ).pack(anchor=tk.W)

        content = tk.Frame(self.window, padx=20, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        # 左侧统计
        stats_frame = tk.LabelFrame(content, text="基础统计", padx=15, pady=10)
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self._populate_stats(stats_frame)

        # 右侧道具/成就
        right_frame = tk.Frame(content)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        inventory_frame = tk.LabelFrame(right_frame, text="道具库存", padx=15, pady=10)
        inventory_frame.pack(fill=tk.BOTH, expand=True)
        self._populate_inventory(inventory_frame)

        achievements_frame = tk.LabelFrame(right_frame, text="成就", padx=15, pady=10)
        achievements_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self._populate_achievements(achievements_frame)

    def _populate_stats(self, frame):
        stats = self.player.get_statistics()
        entries = [
            ("邮箱", self.player.email or "-"),
            ("注册时间", self._format_datetime(self.player.created_at)),
            ("最近登录", self._format_datetime(self.player.last_login)),
            ("连续登录", f"{self.player.consecutive_days} 天"),
            ("总游戏", stats['total_games']),
            ("完成游戏", stats['completed_games']),
            ("胜率", f"{stats['win_rate']:.1f}%"),
            ("平均用时", self._format_duration(stats['average_time'])),
            ("普通最佳", self._format_duration(stats['best_time_normal'])),
            ("终极最佳", self._format_duration(stats['best_time_ultimate'])),
            ("累计积分获取", stats['total_points_earned'])
        ]

        for title, value in entries:
            row = tk.Frame(frame)
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=f"{title}：", font=('Arial', 11), fg='#7F8C8D', width=12, anchor=tk.E).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=('Arial', 12), anchor=tk.W).pack(side=tk.LEFT, fill=tk.X)

    def _populate_inventory(self, frame):
        if not self.player.items:
            tk.Label(frame, text="暂无道具", font=('Arial', 12), fg='#95A5A6').pack()
            return

        for item_id, qty in self.player.items.items():
            cfg = ItemConfig.ITEMS.get(item_id, {})
            icon = cfg.get('icon', '🎲')
            name = cfg.get('name', item_id)
            row = tk.Frame(frame)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=f"{icon} {name}", font=('Arial', 12)).pack(side=tk.LEFT)
            tk.Label(row, text=f"x{qty}", font=('Arial', 12, 'bold'), fg='#2C3E50').pack(side=tk.RIGHT)

    def _populate_achievements(self, frame):
        if not self.player.achievements:
            tk.Label(frame, text="尚未解锁成就，加油！", font=('Arial', 12), fg='#95A5A6').pack()
            return

        for ach in self.player.achievements:
            row = tk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"🏅 {ach}", font=('Arial', 12)).pack(anchor=tk.W)

    @staticmethod
    def _format_datetime(timestamp):
        if not timestamp:
            return "-"
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def _format_duration(seconds):
        if seconds is None or seconds == 0:
            return "-"
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"


# ============== 测试代码 ==============
if __name__ == '__main__':
    from core.player import Player

    root = tk.Tk()
    root.withdraw()
    p = Player("Tester", "test@example.com")
    p.add_item('hint', 3)
    p.add_item('time_extend', 1)
    p.achievements = ['first_game', 'normal_master']
    ProfileWindow(root, p).window.mainloop()

