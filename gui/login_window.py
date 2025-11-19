"""
登录窗口
"""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from config import DataConfig
from core.player import Player

class LoginWindow:
    """登录/注册窗口"""

    def __init__(self, on_login_success):
        """
        初始化登录窗口
        :param on_login_success: 登录成功回调函数
        """
        self.on_login_success = on_login_success
        self.window = tk.Tk()
        self.window.title("记忆翻牌游戏 - 登录")
        self.window.geometry("400x500")
        self.window.resizable(False, False)

        # 居中显示
        self._center_window()

        # 创建界面
        self._create_widgets()

        # 加载玩家数据库
        self.players_db = self._load_players()

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
        # 标题
        title_frame = tk.Frame(self.window, bg='#4A90E2', height=100)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🎮 记忆翻牌游戏",
            font=('Arial', 24, 'bold'),
            bg='#4A90E2',
            fg='white'
        )
        title_label.pack(expand=True)

        # 主内容区
        content_frame = tk.Frame(self.window, padx=40, pady=30)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 标签页
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 登录标签页
        login_frame = tk.Frame(self.notebook)
        self.notebook.add(login_frame, text="登录")
        self._create_login_tab(login_frame)

        # 注册标签页
        register_frame = tk.Frame(self.notebook)
        self.notebook.add(register_frame, text="注册")
        self._create_register_tab(register_frame)

    def _create_login_tab(self, parent):
        """创建登录标签页"""
        # 用户名
        tk.Label(parent, text="用户名:", font=('Arial', 12)).pack(pady=(20, 5))
        self.login_username = tk.Entry(parent, font=('Arial', 12), width=25)
        self.login_username.pack(pady=5)

        # 登录按钮
        login_btn = tk.Button(
            parent,
            text="登录",
            font=('Arial', 14, 'bold'),
            bg='#5CB85C',
            fg='white',
            width=20,
            height=2,
            command=self._handle_login
        )
        login_btn.pack(pady=30)

        # 提示信息
        tip_label = tk.Label(
            parent,
            text="提示：首次使用请先注册账号",
            font=('Arial', 10),
            fg='gray'
        )
        tip_label.pack(pady=10)

    def _create_register_tab(self, parent):
        """创建注册标签页"""
        # 用户名
        tk.Label(parent, text="用户名:", font=('Arial', 12)).pack(pady=(20, 5))
        self.register_username = tk.Entry(parent, font=('Arial', 12), width=25)
        self.register_username.pack(pady=5)

        # 邮箱
        tk.Label(parent, text="邮箱 (可选):", font=('Arial', 12)).pack(pady=(10, 5))
        self.register_email = tk.Entry(parent, font=('Arial', 12), width=25)
        self.register_email.pack(pady=5)

        # 注册按钮
        register_btn = tk.Button(
            parent,
            text="注册",
            font=('Arial', 14, 'bold'),
            bg='#4A90E2',
            fg='white',
            width=20,
            height=2,
            command=self._handle_register
        )
        register_btn.pack(pady=30)

        # 新手福利提示
        bonus_label = tk.Label(
            parent,
            text="🎁 新手福利：注册即送500积分！",
            font=('Arial', 11, 'bold'),
            fg='#F0AD4E'
        )
        bonus_label.pack(pady=10)

    def _handle_login(self):
        """处理登录"""
        username = self.login_username.get().strip()

        if not username:
            messagebox.showwarning("提示", "请输入用户名")
            return

        # 检查用户是否存在
        if username not in self.players_db:
            messagebox.showerror("错误", "用户不存在，请先注册")
            return

        # 加载玩家数据
        player = Player.from_dict(self.players_db[username])
        player.update_login()

        # 保存更新后的登录信息
        self._save_player(player)

        messagebox.showinfo("成功", f"欢迎回来，{username}！")

        # 关闭登录窗口，调用成功回调
        self.window.destroy()
        self.on_login_success(player)

    def _handle_register(self):
        """处理注册"""
        username = self.register_username.get().strip()
        email = self.register_email.get().strip()

        if not username:
            messagebox.showwarning("提示", "请输入用户名")
            return

        # 检查用户名长度
        if len(username) < 3:
            messagebox.showwarning("提示", "用户名至少3个字符")
            return

        # 检查用户是否已存在
        if username in self.players_db:
            messagebox.showerror("错误", "用户名已存在")
            return

        # 创建新玩家
        player = Player(username, email)

        # 保存玩家数据
        self._save_player(player)

        messagebox.showinfo("成功", f"注册成功！欢迎 {username}！\n获得新手奖励：500积分")

        # 切换到登录标签页
        self.notebook.select(0)
        self.login_username.delete(0, tk.END)
        self.login_username.insert(0, username)

    def _load_players(self):
        """加载玩家数据库"""
        if os.path.exists(DataConfig.PLAYERS_FILE):
            try:
                with open(DataConfig.PLAYERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_player(self, player):
        """保存玩家数据"""
        self.players_db[player.username] = player.to_dict()

        with open(DataConfig.PLAYERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.players_db, f, indent=2, ensure_ascii=False)

    def run(self):
        """运行窗口"""
        self.window.mainloop()


# ============== 测试代码 ==============
if __name__ == '__main__':
    def on_success(player):
        print(f"登录成功: {player}")

    app = LoginWindow(on_success)
    app.run()
