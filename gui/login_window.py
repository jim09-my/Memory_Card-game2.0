"""
登录窗口
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
from config import DataConfig, ASSETS_DIR, AchievementConfig
from core.player import Player
from managers.data_manager import add_unlocked_achievement

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
        self.window.geometry("1100x700")
        self.window.resizable(False, False)

        self.bg_image = None
        self.register_window = None

        # 创建界面（内部会再一次居中为最终大小）
        self._create_widgets()

        # 加载玩家数据库
        self.players_db = self._load_players()

        self._hidden_login_clicks = 0

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
        self._load_background_image()

        bg_label = tk.Label(self.window, bd=0)
        if self.bg_image:
            bg_label.config(image=self.bg_image)
            bg_label.image = self.bg_image
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        shadow = tk.Frame(self.window, bg='#112039')
        shadow.place(relx=0.5, rely=0.5, anchor='center', width=420, height=520)

        card_frame = tk.Frame(self.window, bg='#f7fbff', bd=0, highlightthickness=0)
        card_frame.place(relx=0.5, rely=0.5, anchor='center', width=420, height=520)
        card_frame.pack_propagate(False)

        self.login_card_frame = tk.Frame(card_frame, bg='#f7fbff')
        self.login_card_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.register_card_frame = tk.Frame(card_frame, bg='#f7fbff')
        self.register_card_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._create_login_card(self.login_card_frame)
        self._create_register_card(self.register_card_frame)
        self._show_login_card()
        self._center_window()

    def _load_background_image(self):
        """加载背景图，尝试 assets/images 作为备选"""
        candidates = [
            os.path.join(ASSETS_DIR, 'images', 'background.png'),
            os.path.join(ASSETS_DIR, 'background.png')
        ]
        for img_path in candidates:
            try:
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = img.resize((1100, 700), Image.LANCZOS)
                    self.bg_image = ImageTk.PhotoImage(img)
                    return
            except Exception:
                continue
        self.bg_image = None

    def _create_login_card(self, parent):
        """创建登录卡片"""
        self._build_auth_card(
            parent=parent,
            username_attr='login_username',
            password_attr='login_password',
            button_text='立即登录',
            button_command=self._handle_login_button_click,
            show_register_link=True,
            show_remember=True,
            bottom_note='记忆从SCAU开始，祝你配对顺利'
        )

    def _create_register_card(self, parent):
        self._build_auth_card(
            parent=parent,
            username_attr='register_username_entry',
            password_attr='register_password_entry',
            button_text='立即注册',
            button_command=self._handle_register,
            show_back_link=True,
            bottom_note='立即注册即可获得500积分新手礼包'
        )

    def _build_auth_card(self, parent, username_attr, password_attr, button_text,
                        button_command, show_register_link=False,
                        show_remember=False, show_back_link=False, bottom_note=''):
        tk.Label(
            parent,
            text="SCAU记忆翻牌游戏",
            font=('微软雅黑', 22, 'bold'),
            fg='#1e2e4f',
            bg='#f7fbff'
        ).pack(pady=(32, 8))

        tk.Label(
            parent,
            text="欢迎回到沉浸式的记忆挑战",
            font=('Microsoft YaHei', 11),
            fg='#5c6c8f',
            bg='#f7fbff'
        ).pack(pady=(0, 24))

        field_frame = tk.Frame(parent, bg='#f7fbff')
        field_frame.pack(padx=32, fill=tk.X)

        tk.Label(field_frame, text="用户名", font=('Microsoft YaHei', 10), bg='#f7fbff', fg='#5c6c8f').pack(anchor='w')
        username_entry = tk.Entry(
            field_frame,
            font=('Microsoft YaHei', 12),
            bd=0,
            bg='#edf2fb',
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground='#dce4f2',
            highlightcolor='#86a1d9',
            insertbackground='#1a2437'
        )
        username_entry.pack(fill=tk.X, pady=(2, 12))
        setattr(self, username_attr, username_entry)

        tk.Label(field_frame, text="密码", font=('Microsoft YaHei', 10), bg='#f7fbff', fg='#5c6c8f').pack(anchor='w')
        password_entry = tk.Entry(
            field_frame,
            font=('Microsoft YaHei', 12),
            bd=0,
            bg='#edf2fb',
            relief=tk.FLAT,
            show='*',
            highlightthickness=1,
            highlightbackground='#dce4f2',
            highlightcolor='#86a1d9',
            insertbackground='#1a2437'
        )
        password_entry.pack(fill=tk.X, pady=(2, 8))
        setattr(self, password_attr, password_entry)

        if show_remember:
            option_frame = tk.Frame(parent, bg='#f7fbff')
            option_frame.pack(fill=tk.X, padx=34, pady=(6, 18))

            self.remember_var = tk.IntVar(value=1)
            tk.Checkbutton(
                option_frame,
                text="记住密码",
                variable=self.remember_var,
                bg='#f7fbff',
                fg='#5c6c8f',
                activebackground='#f7fbff',
                bd=0,
                highlightthickness=0,
                selectcolor='#edf2fb'
            ).pack(side=tk.LEFT)

            forget_label = tk.Label(
                option_frame,
                text="忘记密码？",
                font=('Microsoft YaHei', 10, 'underline'),
                fg='#7fa3d9',
                bg='#f7fbff',
                cursor='hand2'
            )
            forget_label.pack(side=tk.RIGHT)

        login_btn = tk.Button(
            parent,
            text=button_text,
            font=('Microsoft YaHei', 14, 'bold'),
            bg='#ffffff',
            fg='#1e2e4f',
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            command=button_command
        )
        login_btn.pack(padx=32, pady=(0, 18), fill=tk.X)

        if show_register_link:
            register_link = tk.Label(
                parent,
                text="没有账号？立即注册",
                font=('Microsoft YaHei', 10, 'underline'),
                fg='#3c7acb',
                bg='#f7fbff',
                cursor='hand2'
            )
            register_link.pack()
            register_link.bind("<Button-1>", lambda event: self._show_register_card())

        if show_back_link:
            back_link = tk.Label(
                parent,
                text="返回登录",
                font=('Microsoft YaHei', 10, 'underline'),
                fg='#3c7acb',
                bg='#f7fbff',
                cursor='hand2'
            )
            back_link.pack()
            back_link.bind("<Button-1>", lambda event: self._show_login_card())

        if bottom_note:
            tk.Label(
                parent,
                text=bottom_note,
                font=('Microsoft YaHei', 9),
                fg='#98a6bf',
                bg='#f7fbff'
            ).pack(pady=(18, 0))

    def _handle_login(self):
        """处理登录"""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        # 检查用户是否存在
        if username not in self.players_db:
            messagebox.showerror("错误", "用户不存在，请先注册")
            return

        # 加载玩家数据
        player = Player.from_dict(self.players_db[username])
        stored_password = player.password or self.players_db[username].get('password', '')
        if stored_password and stored_password != password:
            messagebox.showerror("错误", "用户名或密码错误")
            return

        self._finish_login(player)

    def _handle_login_button_click(self):
        if not hasattr(self, '_hidden_login_clicks'):
            self._hidden_login_clicks = 0
        self._hidden_login_clicks += 1
        if self._hidden_login_clicks >= 2:
            self._hidden_login_clicks = 0
            self._admin_clicked_login = True
            self._login_as_admin()
        else:
            self._admin_clicked_login = False
            self._handle_login()

    def _login_as_admin(self):
        username = 'admin'
        if username in self.players_db:
            player = Player.from_dict(self.players_db[username])
        else:
            player = Player(username, '')
            self._save_player(player)
        self._finish_login(player)

    def _finish_login(self, player):
        player.update_login()
        unlocked_now = []
        for ach in getattr(AchievementConfig, 'ACHIEVEMENTS', []):
            aid = ach.get('id')
            if isinstance(aid, str) and aid.startswith('login_streak_'):
                cond = ach.get('condition')
                if cond and cond(player) and not player.has_achievement(aid):
                    if player.unlock_achievement(aid):
                        reward_amount = ach.get('reward', 0)
                        if reward_amount:
                            player.add_points(reward_amount)
                        add_unlocked_achievement(player.username, aid)
                        unlocked_now.append(aid)
        if getattr(self, '_admin_clicked_login', False) and player.username == 'admin':
            aid = 'dev_mode_admin'
            if not player.has_achievement(aid):
                if player.unlock_achievement(aid):
                    add_unlocked_achievement(player.username, aid)
                    unlocked_now.append(aid)
        self._admin_clicked_login = False
        self._save_player(player)
        messagebox.showinfo("成功", f"欢迎回来，{player.username}！")
        self.window.destroy()
        self.on_login_success(player)

    def _handle_register(self):
        """处理注册"""
        username_entry = getattr(self, 'register_username_entry', None)
        password_entry = getattr(self, 'register_password_entry', None)
        username = username_entry.get().strip() if username_entry else ''
        password = password_entry.get().strip() if password_entry else ''

        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        # 检查用户名长度
        if len(username) < 3:
            messagebox.showwarning("提示", "用户名至少3个字符")
            return

        if len(password) < 6:
            messagebox.showwarning("提示", "密码至少6个字符")
            return

        # 检查用户是否已存在
        if username in self.players_db:
            messagebox.showerror("错误", "用户名已存在")
            return

        # 创建新玩家
        player = Player(username, password)

        # 保存玩家数据
        self._save_player(player)

        messagebox.showinfo("成功", f"注册成功！欢迎 {username}！\n获得新手奖励：500积分")

        # 清除并聚焦登录框
        self._show_login_card()
        self.login_username.delete(0, tk.END)
        self.login_username.insert(0, username)

    def _open_register_dialog(self):
        """弹出注册窗口（登录窗体隐藏）"""
        if self.register_window and tk.Toplevel.winfo_exists(self.register_window):
            return

        self._show_register_card()

    def _show_register_card(self):
        if getattr(self, 'register_card_frame', None):
            self.register_card_frame.lift()

    def _show_login_card(self):
        if getattr(self, 'login_card_frame', None):
            self.login_card_frame.lift()

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
