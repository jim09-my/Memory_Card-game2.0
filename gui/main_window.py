"""
主窗口
游戏主菜单界面
"""

import tkinter as tk
from tkinter import messagebox
from gui.game_window import GameWindow
from gui.shop_window import ShopWindow
from gui.history_window import HistoryWindow
from gui.profile_window import ProfileWindow
from config import UIConfig

class MainWindow:
    """主窗口类"""

    def __init__(self, player):
        """
        初始化主窗口
        :param player: 玩家对象
        """
        self.player = player
        self.window = tk.Tk()
        self.window.title("记忆翻牌游戏 - 主菜单")
        self.window.geometry("800x600")
        self.window.resizable(False, False)

        # 居中显示
        self._center_window()

        # 创建界面
        self._create_widgets()

        # 窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _center_window(self):
        """窗口居中"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部标题栏
        self._create_header()

        # 主菜单区域
        self._create_menu()

        # 底部信息栏
        self._create_footer()

    def _create_header(self):
        """创建顶部标题栏"""
        header_frame = tk.Frame(self.window, bg='#4A90E2', height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # 游戏标题
        title_label = tk.Label(
            header_frame,
            text="🎮 记忆翻牌游戏",
            font=('Arial', 32, 'bold'),
            bg='#4A90E2',
            fg='white'
        )
        title_label.pack(pady=10)

        # 玩家信息
        player_info_frame = tk.Frame(header_frame, bg='#4A90E2')
        player_info_frame.pack()

        tk.Label(
            player_info_frame,
            text=f"👤 {self.player.username}",
            font=('Arial', 14),
            bg='#4A90E2',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

        self.points_label = tk.Label(
            player_info_frame,
            text=f"💰 {self.player.points} 积分",
            font=('Arial', 14, 'bold'),
            bg='#4A90E2',
            fg='#F0AD4E'
        )
        self.points_label.pack(side=tk.LEFT, padx=20)

        tk.Label(
            player_info_frame,
            text=f"⭐ Lv.{self.player.level}",
            font=('Arial', 14),
            bg='#4A90E2',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

    def _create_menu(self):
        """创建主菜单"""
        menu_frame = tk.Frame(self.window, bg='#ECF0F1')
        menu_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)

        # 按钮配置
        btn_config = {
            'font': ('Arial', 16, 'bold'),
            'width': 25,
            'height': 2,
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 3
        }

        # 开始游戏按钮
        start_btn = tk.Button(
            menu_frame,
            text="🎮 开始游戏",
            bg='#5CB85C',
            command=self._open_game,
            **btn_config
        )
        start_btn.pack(pady=10)

        # 道具商城按钮
        shop_btn = tk.Button(
            menu_frame,
            text="🛒 道具商城",
            bg='#4A90E2',
            command=self._open_shop,
            **btn_config
        )
        shop_btn.pack(pady=10)

        # 游戏记录按钮
        history_btn = tk.Button(
            menu_frame,
            text="📊 游戏记录",
            bg='#F0AD4E',
            command=self._open_history,
            **btn_config
        )
        history_btn.pack(pady=10)

        # 个人资料按钮
        profile_btn = tk.Button(
            menu_frame,
            text="👤 个人资料",
            bg='#9B59B6',
            command=self._open_profile,
            **btn_config
        )
        profile_btn.pack(pady=10)

        # 退出游戏按钮
        quit_btn = tk.Button(
            menu_frame,
            text="🚪 退出游戏",
            bg='#D9534F',
            command=self._on_closing,
            **btn_config
        )
        quit_btn.pack(pady=10)

    def _create_footer(self):
        """创建底部信息栏"""
        footer_frame = tk.Frame(self.window, bg='#34495E', height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        # 统计信息
        stats = self.player.get_statistics()

        stats_frame = tk.Frame(footer_frame, bg='#34495E')
        stats_frame.pack(expand=True)

        tk.Label(
            stats_frame,
            text=f"总游戏: {stats['total_games']}",
            font=('Arial', 11),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            stats_frame,
            text=f"完成: {stats['completed_games']}",
            font=('Arial', 11),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            stats_frame,
            text=f"胜率: {stats['win_rate']:.1f}%",
            font=('Arial', 11),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            stats_frame,
            text=f"连续登录: {stats['consecutive_days']}天",
            font=('Arial', 11),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

    def _open_game(self):
        """打开游戏窗口"""
        GameWindow(self.window, self.player, self._on_child_window_close)

    def _open_shop(self):
        """打开商城窗口"""
        ShopWindow(self.window, self.player, self._on_child_window_close)

    def _open_history(self):
        """打开历史记录窗口"""
        HistoryWindow(self.window, self.player)

    def _open_profile(self):
        """打开个人资料窗口"""
        ProfileWindow(self.window, self.player)

    def _on_child_window_close(self):
        """子窗口关闭回调"""
        # 更新积分显示
        self.points_label.config(text=f"💰 {self.player.points} 积分")

        # 保存玩家数据
        self._save_player()

    def _save_player(self):
        """保存玩家数据"""
        from config import DataConfig
        import json
        import os

        # 加载所有玩家数据
        if os.path.exists(DataConfig.PLAYERS_FILE):
            with open(DataConfig.PLAYERS_FILE, 'r', encoding='utf-8') as f:
                players_db = json.load(f)
        else:
            players_db = {}

        # 更新当前玩家
        players_db[self.player.username] = self.player.to_dict()

        # 保存
        with open(DataConfig.PLAYERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(players_db, f, indent=2, ensure_ascii=False)

    def _on_closing(self):
        """窗口关闭"""
        if messagebox.askokcancel("退出", "确定要退出游戏吗？"):
            self._save_player()
            self.window.destroy()

    def run(self):
        """运行主窗口"""
        self.window.mainloop()


# ============== 测试代码 ==============
if __name__ == '__main__':
    from core.player import Player

    # 创建测试玩家
    player = Player("TestPlayer")
    player.add_points(1000)
    player.add_item('hint', 5)

    # 添加一些测试记录
    for i in range(5):
        player.add_game_record({
            'mode': 'normal',
            'completed': True,
            'time_used': 120 + i * 10,
            'moves': 20 + i
        })

    app = MainWindow(player)
    app.run()
