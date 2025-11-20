"""
游戏窗口
核心游戏界面
"""

import tkinter as tk
from tkinter import messagebox
import random
from core.game import Game
from config import GameConfig, UIConfig, PointsConfig, ItemConfig
from managers.data_manager import save_player

class GameWindow:
    """游戏窗口类"""

    def __init__(self, parent, player, on_close=None):
        """
        初始化游戏窗口
        :param parent: 父窗口
        :param player: 玩家对象
        :param on_close: 关闭回调
        """
        self.parent = parent
        self.player = player
        self.on_close = on_close
        self.game = None

        # 注册玩家变更监听（用于道具/积分等即时刷新）
        if hasattr(self.player, 'add_change_listener'):
            try:
                self.player.add_change_listener(self._on_player_change)
            except Exception:
                pass

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("记忆翻牌游戏")
        # 使用 1000x800 的窗口大小，适配大部分屏幕
        self.window.geometry("1000x800")
        # 窗口居中
        try:
            self._center_window()
        except Exception:
            pass
        self.window.resizable(False, False)

        # 卡牌按钮
        self.card_buttons = []

        # 动画状态
        self.animating = False
        self.selected_cards = []
        self.pending_resolution_task = None
        self.pending_mismatch = False

        # 更新任务ID
        self.update_task = None

        # 结束处理标志，防止重复弹窗或重复销毁
        self._end_handled = False

        # 创建界面
        self._create_widgets()

        # 显示模式选择
        self._show_mode_selection()

        # 窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部信息栏
        self._create_top_bar()

        # 游戏区域
        self._create_game_area()

        # 底部面板（包含控制和道具）
        self.bottom_panel = tk.Frame(self.window, bg='#ECF0F1')
        self.bottom_panel.pack(fill=tk.X, side=tk.BOTTOM)

        # 控制按钮区
        self._create_control_panel(self.bottom_panel)

        # 道具栏
        self._create_item_panel(self.bottom_panel)

    def _center_window(self):
        """把当前窗口居中到屏幕中央"""
        try:
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            # 如果尚未得到尺寸，使用默认值
            if not width or width <= 1:
                width = 1000
            if not height or height <= 1:
                height = 800
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

    def _create_top_bar(self):
        """创建顶部信息栏"""
        top_frame = tk.Frame(self.window, bg='#34495E', height=80)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)

        # 左侧：玩家信息
        left_frame = tk.Frame(top_frame, bg='#34495E')
        left_frame.pack(side=tk.LEFT, padx=20)

        self.player_label = tk.Label(
            left_frame,
            text=f"👤 {self.player.username}",
            font=('Arial', 14, 'bold'),
            bg='#34495E',
            fg='white'
        )
        self.player_label.pack(anchor=tk.W)

        self.points_label = tk.Label(
            left_frame,
            text=f"💰 积分: {self.player.points}",
            font=('Arial', 12),
            bg='#34495E',
            fg='#F0AD4E'
        )
        self.points_label.pack(anchor=tk.W)

        # 中间：游戏信息
        center_frame = tk.Frame(top_frame, bg='#34495E')
        center_frame.pack(side=tk.LEFT, expand=True)

        self.mode_label = tk.Label(
            center_frame,
            text="模式: 未开始",
            font=('Arial', 14, 'bold'),
            bg='#34495E',
            fg='white'
        )
        self.mode_label.pack()

        info_frame = tk.Frame(center_frame, bg='#34495E')
        info_frame.pack()

        self.time_label = tk.Label(
            info_frame,
            text="⏱ 00:00",
            font=('Arial', 12),
            bg='#34495E',
            fg='white'
        )
        self.time_label.pack(side=tk.LEFT, padx=10)

        self.moves_label = tk.Label(
            info_frame,
            text="🔄 步数: 0",
            font=('Arial', 12),
            bg='#34495E',
            fg='white'
        )
        self.moves_label.pack(side=tk.LEFT, padx=10)

        self.pairs_label = tk.Label(
            info_frame,
            text="✓ 配对: 0/0",
            font=('Arial', 12),
            bg='#34495E',
            fg='white'
        )
        self.pairs_label.pack(side=tk.LEFT, padx=10)

        # 右侧：进度条
        right_frame = tk.Frame(top_frame, bg='#34495E')
        right_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(
            right_frame,
            text="进度:",
            font=('Arial', 11),
            bg='#34495E',
            fg='white'
        ).pack()

        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = tk.Scale(
            right_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            length=150,
            state='disabled',
            bg='#34495E',
            fg='white',
            troughcolor='#2C3E50',
            highlightthickness=0
        )
        self.progress_bar.pack()

    def _create_game_area(self):
        """创建游戏区域"""
        self.game_frame = tk.Frame(self.window, bg='#ECF0F1', relief=tk.SUNKEN, bd=2)
        self.game_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=(24, 10))

    def _create_control_panel(self, parent=None):
        """创建控制面板"""
        parent = parent or self.window
        control_frame = tk.Frame(parent, bg='#ECF0F1', height=60)
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        control_frame.pack_propagate(False)

        # 按钮样式
        btn_config = {
            'font': ('Arial', 11, 'bold'),
            'width': 12,
            'height': 2
        }

        # 开始/重新开始按钮
        self.start_btn = tk.Button(
            control_frame,
            text="🎮 开始游戏",
            bg='#5CB85C',
            fg='white',
            command=self._show_mode_selection,
            **btn_config
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # 暂停/继续按钮
        self.pause_btn = tk.Button(
            control_frame,
            text="⏸ 暂停",
            bg='#F0AD4E',
            fg='white',
            command=self._toggle_pause,
            state=tk.DISABLED,
            **btn_config
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        # 返回按钮
        back_btn = tk.Button(
            control_frame,
            text="🏠 返回主菜单",
            bg='#D9534F',
            fg='white',
            command=self._on_closing,
            **btn_config
        )
        back_btn.pack(side=tk.RIGHT, padx=5)

    def _create_item_panel(self, parent=None):
        """创建道具栏"""
        parent = parent or self.window
        item_frame = tk.Frame(parent, bg='#2C3E50', height=90, bd=1, relief=tk.SUNKEN)
        item_frame.pack(fill=tk.X, padx=16, pady=(0, 10))
        item_frame.pack_propagate(False)

        tk.Label(
            item_frame,
            text="🎒 道具栏",
            font=('Arial', 12, 'bold'),
            bg='#2C3E50',
            fg='white'
        ).pack(pady=(6, 2))

        items_container = tk.Frame(item_frame, bg='#2C3E50')
        items_container.pack(fill=tk.X, padx=10)

        # 动态创建道具按钮
        self.item_buttons = {}
        item_btn_config = {
            'font': ('Arial', 10),
            'width': 15,
            'bg': '#4A90E2',
            'fg': 'white'
        }

        for item_id, item in ItemConfig.ITEMS.items():
            btn = tk.Button(
                items_container,
                text=f"{item.get('icon','')} {item.get('name','')} (0)",
                command=lambda i=item_id: self._use_item(i),
                state=tk.DISABLED,
                **item_btn_config
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.item_buttons[item_id] = btn

        # 更新道具数量显示
        self._update_item_display()

    def _show_mode_selection(self):
        """显示模式选择对话框"""
        selection_window = tk.Toplevel(self.window)
        selection_window.title("选择游戏模式")
        selection_window.geometry("400x300")
        selection_window.resizable(False, False)
        selection_window.transient(self.window)
        selection_window.grab_set()

        # 居中显示
        selection_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 300) // 2
        selection_window.geometry(f"400x300+{x}+{y}")

        tk.Label(
            selection_window,
            text="选择游戏模式",
            font=('Arial', 18, 'bold'),
            fg='#34495E'
        ).pack(pady=20)

        # 普通模式按钮
        normal_btn = tk.Button(
            selection_window,
            text="🎮 普通模式\n4x4 网格 | 无时间限制\n奖励: 200积分",
            font=('Arial', 12, 'bold'),
            bg='#5CB85C',
            fg='white',
            width=25,
            height=4,
            command=lambda: self._start_game('normal', selection_window)
        )
        normal_btn.pack(pady=10)

        # 终极模式按钮
        ultimate_btn = tk.Button(
            selection_window,
            text="⚡ 终极挑战\n6x6 网格 | 8分钟限时\n奖励: 1200积分",
            font=('Arial', 12, 'bold'),
            bg='#D9534F',
            fg='white',
            width=25,
            height=4,
            command=lambda: self._start_game('ultimate', selection_window)
        )
        ultimate_btn.pack(pady=10)

    def _start_game(self, mode, selection_window):
        """
        开始游戏
        :param mode: 游戏模式
        :param selection_window: 模式选择窗口
        """
        selection_window.destroy()

        # 停止之前的更新任务
        if self.update_task:
            self.window.after_cancel(self.update_task)

        # 创建新游戏
        self.game = Game(mode=mode, player=self.player)
        self.game.start_game()

        # 更新UI
        mode_text = "普通模式 (4x4)" if mode == 'normal' else "终极挑战 (6x6)"
        self.mode_label.config(text=f"模式: {mode_text}")

        # 创建卡牌网格
        self._create_card_grid()

        # 启用控制按钮
        self.start_btn.config(text="🔄 重新开始")
        self.pause_btn.config(state=tk.NORMAL)

        # 更新道具按钮状态
        self._update_item_display()

        # 开始更新循环
        self._update_game_state()

    def _create_card_grid(self):
        """创建卡牌网格"""
        # 清空之前的卡牌
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.card_buttons = []

        grid_size = self.game.grid_size

        # 获取游戏区域的实际大小
        self.window.update_idletasks()
        self.game_frame.update_idletasks()
        available_width = self.game_frame.winfo_width()
        available_height = self.game_frame.winfo_height()

        # 如果还没有实际大小，使用估算值（根据窗口大小和布局计算）
        # 窗口1000x800，减去顶部80，控制面板60，道具栏70，padding 40
        if available_width <= 1:
            available_width = 960
        if available_height <= 1:
            available_height = 590

        # 计算卡牌大小（考虑间距），让所有卡牌在可视区域内完全显示
        padding = 1
        container_pad_x = 16
        container_pad_y = 12
        usable_width = max(available_width - container_pad_x * 2, grid_size)
        usable_height = max(available_height - container_pad_y * 2, grid_size)
        max_card_width = (usable_width - (grid_size + 1) * padding) // grid_size
        max_card_height = (usable_height - (grid_size + 1) * padding) // grid_size

        # 控制目标大小，保证所有卡片可以显示并略小
        target_size = 60 if grid_size <= 4 else 44
        min_size = 28 if grid_size <= 4 else 22
        card_size = max(min_size, min(target_size, max_card_width, max_card_height))

        # 计算按钮的字符宽度和高度（tkinter Button的width/height是字符单位）
        # 粗略估算：1字符宽度≈8像素，1字符高度≈16像素
        btn_width = max(2, int(card_size / 10))
        btn_height = max(2, int(card_size / 20))

        # 字体大小根据卡牌大小调整（确保文字清晰可见）
        if grid_size <= 4:
            font_size = max(10, min(16, int(card_size * 0.28)))
        else:
            font_size = max(8, min(14, int(card_size * 0.26)))

        # 单一容器，卡片从 game_frame 顶部开始铺满，避免上下裁切
        container = tk.Frame(self.game_frame, bg='#ECF0F1')
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # 创建卡牌按钮
        for row in range(grid_size):
            row_buttons = []
            for col in range(grid_size):
                card_index = row * grid_size + col

                btn = tk.Button(
                    container,
                    text="?",
                    font=('Arial', font_size, 'bold'),
                    width=btn_width,
                    height=btn_height,
                    bg='#3498DB',
                    fg='white',
                    relief=tk.RAISED,
                    bd=2,
                    command=lambda idx=card_index: self._on_card_click(idx)
                )
                btn.grid(row=row, column=col, padx=padding//2, pady=padding//2, sticky='nsew')
                # 标记为未隐藏（用于后续隐藏保护）
                try:
                    btn._hidden = False
                except Exception:
                    pass
                row_buttons.append(btn)

            self.card_buttons.extend(row_buttons)

        # 配置grid权重，使按钮能够均匀拉伸填满容器
        for i in range(grid_size):
            container.grid_rowconfigure(i, weight=1)
            container.grid_columnconfigure(i, weight=1)

    def _on_card_click(self, card_index):
        """
        卡牌点击事件
        :param card_index: 卡牌索引
        """
        if not self.game or self.game.is_paused:
            return

        if self.animating and self.pending_resolution_task:
            self.window.after_cancel(self.pending_resolution_task)
            self.pending_resolution_task = None
            self.pending_mismatch = False
            self.animating = False
            self._handle_match_result()

        if self.animating:
            return

        # 检查是否可以翻牌
        card = self.game.get_card_by_index(card_index)
        if not card or not card.can_flip():
            return

        if self.game.flip_card(card_index):
            self._update_card_display(card_index)

            if len(self.game.flipped_cards) == 2:
                self.animating = True
                self.pending_resolution_task = self.window.after(1000, self._handle_match_result)
                self.pending_mismatch = True

    def _handle_match_result(self):
        """处理配对结果"""
        if not self.game:
            return

        # 检查是否匹配
        if self.pending_resolution_task:
            self.pending_resolution_task = None
        pair, matched = self.game.get_last_pair()
        if pair:
            idx1, idx2 = pair
            if matched:
                # 同步隐藏两张已配对卡牌，确保视觉同时消失
                self._hide_matched_cards([idx1, idx2])
            else:
                self.game.flip_back_cards(pair)
                self._update_card_display(idx1)
                self._update_card_display(idx2)
        self.game.clear_last_pair()
        self.game.clear_flipped_cards()

        self.animating = False
        self.pending_mismatch = False

        # 检查游戏是否完成
        if self.game.is_completed:
            self._on_game_complete()
        elif self.game.is_failed:
            self._on_game_failed()

    def _update_card_display(self, card_index):
        """
        更新卡牌显示
        :param card_index: 卡牌索引
        """
        if card_index >= len(self.card_buttons):
            return

        card = self.game.get_card_by_index(card_index)
        btn = self.card_buttons[card_index]
        # 如果该位置已经被标记为匹配占位，直接返回，防止后续状态覆盖样式
        try:
            if getattr(btn, '_matched_placeholder', False):
                return
        except Exception:
            pass

        # 如果该卡牌已配对，设置占位样式并返回
        try:
            if card.is_matched:
                self._set_matched_placeholder(card_index)
                return
        except Exception:
            pass

        # 其他状态处理继续（已在上方处理匹配状态）

        if card.is_flipped:
            btn.config(
                text=str(card.value),
                bg='white',
                fg='#34495E',
                relief=tk.SUNKEN
            )
            return

        if card.is_revealed:
            btn.config(
                text="💡",
                bg='#F0AD4E',
                fg='white',
                relief=tk.RAISED
            )
            return

        btn.config(
            text="?",
            bg='#3498DB',
            fg='white',
            relief=tk.RAISED
        )

    def _hide_matched_card(self, card_index):
        """让已配对的按钮视觉上消失"""
        if card_index >= len(self.card_buttons):
            return

        btn = self.card_buttons[card_index]
        # 只清空显示并禁用交互，但保留在 grid 中作为占位，防止布局重排
        try:
            # 将已配对卡牌保持为翻开状态，但显示问号并置白底，以便与未翻牌卡形成对比
            try:
                btn.config(text='?', image='', bg='white', fg='#34495E', disabledforeground='#34495E', activebackground='white', relief=tk.RAISED, state=tk.DISABLED)
            except Exception:
                try:
                    btn.config(bg='white', state=tk.DISABLED)
                except Exception:
                    pass
            try:
                btn._matched_placeholder = True
            except Exception:
                pass
            try:
                self.window.update_idletasks()
            except Exception:
                pass
        except Exception:
            pass

    def _hide_matched_cards(self, indices):
        """一次性隐藏多张已配对卡牌并刷新界面"""
        try:
            for card_index in indices:
                if 0 <= card_index < len(self.card_buttons):
                    btn = self.card_buttons[card_index]
                    # 将已配对卡牌保持为翻开状态，但显示问号并置白底，以便与未翻牌卡形成对比
                    try:
                        btn.config(text='?', image='', bg='white', fg='#34495E', disabledforeground='#34495E', activebackground='white', relief=tk.RAISED, state=tk.DISABLED)
                    except Exception:
                        try:
                            btn.config(bg='white', state=tk.DISABLED)
                        except Exception:
                            pass
                    try:
                        btn._matched_placeholder = True
                    except Exception:
                        pass
            # 立即刷新 UI
            try:
                self.window.update_idletasks()
            except Exception:
                pass
        except Exception:
            pass

    def _set_matched_placeholder(self, card_index):
        """把单张已配对卡牌设置为占位问号样式并禁用交互"""
        try:
            if 0 <= card_index < len(self.card_buttons):
                widget = self.card_buttons[card_index]
                # If it's a Button, configure to white background and disable it
                if isinstance(widget, tk.Button):
                    try:
                        widget.config(text='', bg='white', fg='#34495E', relief=tk.FLAT, state=tk.DISABLED, disabledforeground='#34495E')
                    except Exception:
                        try:
                            widget.config(bg='white', state=tk.DISABLED)
                        except Exception:
                            pass
                # If it's a Canvas, fill background white and remove items
                elif isinstance(widget, tk.Canvas):
                    try:
                        widget.config(bg='white')
                        widget.delete('all')
                        w = widget.winfo_width() or widget['width'] if 'width' in widget.keys() else 60
                        h = widget.winfo_height() or widget['height'] if 'height' in widget.keys() else 40
                        try:
                            widget.create_rectangle(0, 0, w, h, fill='white', outline='white')
                        except Exception:
                            pass
                    except Exception:
                        pass
                # If it's a Label or other, set bg to white
                else:
                    try:
                        widget.config(bg='white', fg='#34495E', text='')
                    except Exception:
                        try:
                            widget.config(bg='white')
                        except Exception:
                            pass

                try:
                    widget._matched_placeholder = True
                except Exception:
                    pass
        except Exception:
            pass

    def _update_game_state(self):
        """更新游戏状态（定时调用）"""
        if not self.game or not self.game.is_started:
            return

        # 如果游戏在外部被标记为完成或失败，优先处理结束逻辑
        if self.game.is_completed:
            # 在主线程中调度完成回调，保证 UI 更新
            try:
                self._on_game_complete()
            except Exception:
                pass
            return
        if self.game.is_failed:
            try:
                self._on_game_failed()
            except Exception:
                pass
            return

        # 更新时间
        self.time_label.config(text=f"⏱ {self.game.timer.get_time_display()}")

        # 更新步数
        self.moves_label.config(text=f"🔄 步数: {self.game.moves}")

        # 更新配对数
        self.pairs_label.config(
            text=f"✓ 配对: {self.game.matched_pairs}/{self.game.get_total_pairs()}"
        )

        # 更新进度
        self.progress_var.set(int(self.game.get_progress()))

        # 更新积分显示
        self.points_label.config(text=f"💰 积分: {self.player.points}")

        # 检查超时
        if self.game.timer.is_time_up() and not self.game.is_completed:
            self.game.fail_game()
            self._on_game_failed()
            return

        # 继续更新
        if not self.game.is_paused and not self.game.is_completed:
            self.update_task = self.window.after(100, self._update_game_state)

    def _toggle_pause(self):
        """暂停/继续游戏"""
        if not self.game:
            return

        if self.game.is_paused:
            self.game.resume_game()
            self.pause_btn.config(text="⏸ 暂停")
            self._update_game_state()
        else:
            self.game.pause_game()
            self.pause_btn.config(text="▶ 继续")

    def _use_hint(self):
        """使用提示道具"""
        if not self.game or not self.player.has_item('hint'):
            messagebox.showwarning("提示", "没有提示道具！\n请前往商城购买。")
            return

        if self.game.use_hint():
            # 更新卡牌显示
            for idx in self.game.hint_cards:
                self._update_card_display(idx)

            # 3秒后隐藏提示
            self.window.after(3000, self._hide_hint)

            # 更新道具显示
            self._update_item_display()

            # 持久化玩家道具变化
            try:
                save_player(self.player)
            except Exception:
                pass

    def _hide_hint(self):
        """隐藏提示"""
        if self.game:
            hint_cards = self.game.hint_cards.copy()
            self.game.hide_hint()
            for idx in hint_cards:
                self._update_card_display(idx)

    def _use_time_extend(self):
        """使用延时道具"""
        if not self.game or not self.player.has_item('time_extend'):
            messagebox.showwarning("提示", "没有延时道具！\n请前往商城购买。")
            return

        if self.game.extend_time(30):
            messagebox.showinfo("成功", "⏰ 时间延长30秒！")
            self._update_item_display()
            try:
                save_player(self.player)
            except Exception:
                pass
        else:
            messagebox.showinfo("提示", "当前模式无时间限制")

    def _use_undo(self):
        """使用撤销道具"""
        if not self.game or not self.player.has_item('undo'):
            messagebox.showwarning("提示", "没有撤销道具！\n请前往商城购买。")
            return

        if self.game.undo_move():
            # 更新所有卡牌显示
            for i in range(len(self.card_buttons)):
                self._update_card_display(i)

            messagebox.showinfo("成功", "↩️ 已撤销上一步操作！")
            self._update_item_display()
            try:
                save_player(self.player)
            except Exception:
                pass
        else:
            messagebox.showinfo("提示", "没有可撤销的操作")

    def _update_item_display(self):
        """更新道具显示（动态根据 ItemConfig）"""
        # 如果没有动态按钮（兼容旧逻辑），直接返回
        if not hasattr(self, 'item_buttons') or not self.item_buttons:
            return

        for item_id, btn in self.item_buttons.items():
            item = ItemConfig.ITEMS.get(item_id, {})
            icon = item.get('icon', '')
            name = item.get('name', item_id)
            count = self.player.get_item_count(item_id)

            btn.config(text=f"{icon} {name} ({count})")

            # 只有在游戏进行中且拥有数量时才可用
            usable = (count > 0 and self.game and getattr(self.game, 'is_started', False))
            btn.config(state=tk.NORMAL if usable else tk.DISABLED)

        return

    def _use_item(self, item_id):
        """通用道具使用路由：根据 item_id 调用对应方法"""
        if item_id == 'hint':
            self._use_hint()
            return

        if item_id == 'time_extend':
            self._use_time_extend()
            return

        if item_id == 'undo':
            self._use_undo()
            return

        # 其他道具（如果尚未实现）给出提示
        messagebox.showinfo("提示", f"当前道具暂未实现：{item_id}")

    def _on_player_change(self):
        """玩家数据变化回调（由 Player 调用），在主线程调度 UI 刷新。"""
        try:
            if hasattr(self, 'window') and self.window:
                self.window.after(0, self._update_item_display)
        except Exception:
            pass

    def _on_game_complete(self):
        """游戏完成"""
        # 防止重复处理（由不同路径重复触发）
        if getattr(self, '_end_handled', False):
            return
        self._end_handled = True

        # 停止定时刷新任务，防止再次触发结束逻辑
        if self.update_task:
            try:
                self.window.after_cancel(self.update_task)
            except Exception:
                pass

        self.pause_btn.config(state=tk.DISABLED)

        # 显示结果
        result_text = f"""
🎉 恭喜通关！

⏱ 用时: {self.game.timer.format_time(self.game.timer.get_elapsed_time())}
🔄 步数: {self.game.moves}
❌ 失误: {self.game.mistakes}
💯 得分: {self.game.score}

🎁 获得积分: {self.game._calculate_reward(int(self.game.timer.get_elapsed_time()))}
        """

        messagebox.showinfo("完成", result_text)

        # 更新积分显示
        self.points_label.config(text=f"💰 积分: {self.player.points}")

        # 结束游戏后关闭并销毁本窗口
        try:
            self._on_closing()
        except Exception:
            pass

    def _on_game_failed(self):
        """游戏失败"""
        # 防止重复处理（由不同路径重复触发）
        if getattr(self, '_end_handled', False):
            return
        self._end_handled = True

        # 停止定时刷新任务，防止再次触发结束逻辑
        if self.update_task:
            try:
                self.window.after_cancel(self.update_task)
            except Exception:
                pass

        self.pause_btn.config(state=tk.DISABLED)

        messagebox.showwarning(
            "失败",
            f"⏰ 时间到！\n\n已完成: {self.game.matched_pairs}/{self.game.get_total_pairs()}"
        )

        # 失败后也关闭游戏窗口
        try:
            self._on_closing()
        except Exception:
            pass

    def _on_closing(self):
        """窗口关闭"""
        if self.update_task:
            self.window.after_cancel(self.update_task)
        # 移除玩家监听器
        if hasattr(self.player, 'remove_change_listener'):
            try:
                self.player.remove_change_listener(self._on_player_change)
            except Exception:
                pass
        self.window.destroy()

        if self.on_close:
            self.on_close()


# ============== 测试代码 ==============
if __name__ == '__main__':
    from core.player import Player

    root = tk.Tk()
    root.withdraw()

    # 创建测试玩家
    player = Player("TestPlayer")
    player.add_item('hint', 5)
    player.add_item('time_extend', 3)
    player.add_item('undo', 2)

    def on_close():
        root.quit()

    game_window = GameWindow(root, player, on_close)
    root.mainloop()
