"""
游戏窗口 - v4.2 完整重制版
包含：
1. 游戏主界面 (Teal/Yellow 配色, 居中布局, 胶囊数据栏, 可爱道具栏)
2. 模式选择弹窗 (清新扁平风格, 圆润按钮)
3. 配对消失动画
"""

import tkinter as tk
from tkinter import messagebox
import math
import time
from core.game import Game
from config import GameConfig, UIConfig, ItemConfig, AchievementConfig
from managers.data_manager import save_player
# 引入通用组件
from gui.widgets import PlayingCard, ItemButton, RoundButton

# --- 内部类：模式选择按钮 (清新扁平风格) ---
class ModeButton(tk.Canvas):
    def __init__(self, master, text, sub_text, command=None, width=220, height=80, theme='yellow'):
        super().__init__(master, width=width, height=height, bg='#E0F7FA', highlightthickness=0, bd=0)
        self.text = text
        self.sub_text = sub_text
        self._command = command
        self.w, self.h = width, height
        self.theme = theme
        self._state = 'normal'
        
        # 配色方案
        self.colors = {
            'yellow': ('#FFF59D', '#FBC02D', '#5D4037'), # 普通模式: 柔黄 + 深黄阴影 + 深褐字
            'red':    ('#FFCCBC', '#FF7043', '#BF360C')   # 终极模式: 淡红 + 深红阴影 + 深红字
        }
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._draw()

    def _draw(self):
        self.delete('all')
        scale = 0.96 if self._state == 'active' else 1.0
        w, h = self.w * scale, self.h * scale
        cx, cy = self.w/2, self.h/2
        
        bg_col, shadow_col, text_col = self.colors.get(self.theme, self.colors['yellow'])
        if self._state == 'hover':
            # 悬停变亮逻辑
            if self.theme == 'yellow': bg_col = '#FFF9C4'
            else: bg_col = '#FFAB91'

        offset_y = 0 if self._state == 'active' else -4
        shadow_h = 0 if self._state == 'active' else 4
        
        # 绘制圆角矩形 (胶囊)
        r = h/2
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2
        
        # 阴影
        self._draw_capsule(x1, y1 + offset_y + shadow_h, x2, y2 + offset_y + shadow_h, r, shadow_col)
        # 主体
        self._draw_capsule(x1, y1 + offset_y, x2, y2 + offset_y, r, bg_col)
        
        # 文字
        self.create_text(cx, cy + offset_y - 8, text=self.text, font=('Arial Rounded MT Bold', 14, 'bold'), fill=text_col)
        self.create_text(cx, cy + offset_y + 12, text=self.sub_text, font=('Arial', 10), fill=text_col)

    def _draw_capsule(self, x1, y1, x2, y2, r, fill):
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=180, fill=fill, outline="")
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=270, extent=180, fill=fill, outline="")
        self.create_rectangle(x1+r, y1, x2-r, y2+1, fill=fill, outline="")

    def _on_enter(self, e): self._state = 'hover'; self.config(cursor='hand2'); self._draw()
    def _on_leave(self, e): self._state = 'normal'; self.config(cursor=''); self._draw()
    def _on_press(self, e): self._state = 'active'; self._draw()
    def _on_release(self, e): 
        if self._state == 'active': 
            self._state = 'hover'; self._draw()
            if self._command: self.after(50, self._command)

# --- 游戏主窗口类 ---
class GameWindow:
    def __init__(self, parent, player, on_close=None):
        self.parent = parent
        self.player = player
        self.on_close = on_close
        self.game = None

        self.window = tk.Toplevel(parent)
        self.window.title("记忆翻牌")
        self.window.geometry(f"{UIConfig.WINDOW_WIDTH}x{UIConfig.WINDOW_HEIGHT}")
        self.window.config(bg=UIConfig.COLORS['primary']) 
        
        self._center_window()
        self.window.resizable(False, False)

        self.card_buttons = []
        self.animating = False
        self.update_task = None
        self._end_handled = False
        self._time_freeze_task = None
        self._time_freeze_remaining = 0
        self._time_frozen = False
        self._shuffle_warning_label = None  # 洗牌警告标签（居中）
        self._shuffle_side_hint_label = None  # 洗牌侧边浅色提示文字
        self._shuffle_warning_animation = None  # 洗牌警告动画任务
        self._shuffle_flash_done = False       # 是否已完成本轮闪烁
        self._shuffle_flash_count = 0          # 本轮闪烁计数
        # 统一的洗牌提示字体，确保闪烁前后样式一致
        self._shuffle_warning_font = ('Arial Rounded MT Bold', 16, 'bold')
        self._shuffle_side_font = ('Arial Rounded MT Bold', 12, 'bold')
        
        self._create_ui()
        
        if hasattr(self.player, 'add_change_listener'):
            self.player.add_change_listener(self._on_player_change)
        
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 延迟显示模式选择
        self.window.after(100, self._show_mode_selection)

    def _center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """UI 结构"""
        # 1. 顶部状态栏
        top_bar = tk.Frame(self.window, bg=UIConfig.COLORS['primary_dark'], height=70, pady=5)
        top_bar.pack(fill=tk.X)
        top_bar.grid_columnconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=2)
        top_bar.grid_columnconfigure(2, weight=1)
        
        # 左侧玩家
        p_frame = tk.Frame(top_bar, bg=UIConfig.COLORS['primary_dark'])
        p_frame.grid(row=0, column=0, sticky='w', padx=20)
        tk.Label(p_frame, text=f"👤 {self.player.username}", font=('Arial Rounded MT Bold', 14), 
                 bg=UIConfig.COLORS['primary_dark'], fg='white').pack(anchor='w')
        
        # 中间数据
        stats_c = tk.Frame(top_bar, bg=UIConfig.COLORS['primary_dark'])
        stats_c.grid(row=0, column=1)
        self._create_pill_label(stats_c, "⏱ 00:00", '#26A69A', 'time_label')
        tk.Frame(stats_c, bg=UIConfig.COLORS['primary_dark'], width=20).pack(side=tk.LEFT)
        self._create_pill_label(stats_c, "⭐ 分数: 0", '#FFA726', 'score_label')
        tk.Frame(stats_c, bg=UIConfig.COLORS['primary_dark'], width=20).pack(side=tk.LEFT)
        self.pause_button = RoundButton(
            stats_c, text="⏸ 暂停", command=self._toggle_pause,
            width=100, height=40, bg_color='#42A5F5', hover_color='#64B5F6', text_color='white'
        )
        self.pause_button.pack(side=tk.LEFT)

        # 右侧退出
        exit_c = tk.Frame(top_bar, bg=UIConfig.COLORS['primary_dark'])
        exit_c.grid(row=0, column=2, sticky='e', padx=20)
        RoundButton(exit_c, text="🚪 退出", command=self._on_closing, 
                    width=100, height=40, bg_color='#FF7043', hover_color='#FF8A65').pack()

        # 2. 游戏区
        self.game_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        self.game_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # 洗牌警告标签（初始隐藏）
        self._shuffle_warning_label = tk.Label(
            self.game_frame,
            text="",
            font=self._shuffle_warning_font,
            bg=UIConfig.COLORS['primary'],
            fg='#FF5252',
            pady=10
        )

        # 洗牌侧边浅色提示文字（初始隐藏）
        self._shuffle_side_hint_label = tk.Label(
            self.game_frame,
            text="",
            font=self._shuffle_side_font,
            bg=UIConfig.COLORS['primary'],
            fg='#FFFDE7'  # 浅色字体，避免太抢眼
        )
        
        # 3. 底部道具
        bottom_bar = tk.Frame(self.window, bg=UIConfig.COLORS['primary'], height=110, pady=10)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.items_container = tk.Frame(bottom_bar, bg=UIConfig.COLORS['primary'])
        self.items_container.pack(anchor=tk.CENTER)
        self._create_item_buttons(self.items_container)

    def _create_pill_label(self, parent, text, color, attr_name):
        canvas = tk.Canvas(parent, width=140, height=40, bg=UIConfig.COLORS['primary_dark'], highlightthickness=0, bd=0)
        canvas.pack(side=tk.LEFT)
        r = 20
        w, h = 140, 40
        canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline="")
        canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline="")
        canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline="")
        canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline="")
        canvas.create_rectangle(r, 0, w-r, h, fill=color, outline="")
        canvas.create_rectangle(0, r, w, h-r, fill=color, outline="")
        
        t_id = canvas.create_text(w/2, h/2, text=text, fill='white', font=('Arial Rounded MT Bold', 13))
        
        class LabelWrapper:
            def config(self, text): canvas.itemconfig(t_id, text=text)
        setattr(self, attr_name, LabelWrapper())

    def _create_item_buttons(self, parent):
        self.item_buttons = {}
        for item_id, item in ItemConfig.ITEMS.items():
            count = self.player.get_item_count(item_id)
            btn = ItemButton(parent, item_id, item['icon'], item['name'], count, 
                             command=self._use_item, width=90, height=80)
            btn.pack(side=tk.LEFT, padx=15)
            self.item_buttons[item_id] = btn

    # --- 核心修改：模式选择弹窗 ---
    def _show_mode_selection(self):
        """
        v4.2 清新风格模式选择弹窗
        """
        win = tk.Toplevel(self.window)
        win.title("模式选择")
        win.geometry("500x450") # 增加高度以容纳复选框
        win.config(bg='#E0F7FA') # 统一背景
        win.transient(self.window)
        win.grab_set()
        
        # 居中
        self.window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 500) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 450) // 2
        win.geometry(f"+{x}+{y}")
        
        # 画布背景 + 标题
        canvas = tk.Canvas(win, bg='#E0F7FA', highlightthickness=0, bd=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 1. 背景装饰 (淡黄/淡青圆圈)
        canvas.create_oval(-50, -50, 150, 150, fill='#B2DFDB', outline="")
        canvas.create_oval(400, 300, 550, 450, fill='#F0F4C3', outline="")
        
        # 2. 标题：模式选择 (细白边 + 深青色填充)
        center_x = 250
        y_pos = 80
        title = "模式选择"
        font = ("Arial Rounded MT Bold", 32, "bold")
        
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            canvas.create_text(center_x+dx, y_pos+dy, text=title, font=font, fill='white')
        canvas.create_text(center_x, y_pos, text=title, font=font, fill='#00796B')
        
        # 3. 副标题
        canvas.create_text(center_x, y_pos + 50, text="准备好挑战记忆力了吗？", 
                           font=("Arial", 12), fill='#546E7A')

        # 4. 按钮区域 (使用 place 居中)
        shuffle_enabled = tk.BooleanVar(value=False)
        
        def start(mode):
            # 如果选择了终极模式且勾选了洗牌，则使用ultimate_shuffle模式
            if mode == 'ultimate' and shuffle_enabled.get():
                mode = 'ultimate_shuffle'
            win.destroy()
            self._start_game(mode)
        
        # 按钮容器
        btn_frame = tk.Frame(win, bg='#E0F7FA')
        btn_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        # 普通模式 (黄色 - 轻松)
        ModeButton(btn_frame, text="普通模式", sub_text="4x4 网格 | 轻松休闲",
                   theme='yellow', command=lambda: start('normal')).pack(pady=10)
        
        # 终极挑战 (淡红 - 挑战)
        ultimate_btn_frame = tk.Frame(btn_frame, bg='#E0F7FA')
        ultimate_btn_frame.pack(pady=10)
        
        ModeButton(ultimate_btn_frame, text="终极挑战", sub_text="4x9 网格 | 限时挑战",
                   theme='red', command=lambda: start('ultimate')).pack()
        
        # 洗牌选项复选框（仅终极模式）
        checkbox_frame = tk.Frame(ultimate_btn_frame, bg='#E0F7FA')
        checkbox_frame.pack(pady=5)
        
        checkbox = tk.Checkbutton(
            checkbox_frame, 
            text="启用洗牌模式", 
            variable=shuffle_enabled,
            bg='#E0F7FA',
            fg='#546E7A',
            font=('Arial', 10),
            activebackground='#E0F7FA',
            activeforeground='#546E7A',
            selectcolor='#E0F7FA'
        )
        checkbox.pack()

    def _start_game(self, mode):
        self.game = Game(mode=mode, player=self.player)
        self.game.start_game()
        self._prev_achievements = set(self.player.achievements)
        if mode in ('ultimate', 'ultimate_shuffle'): 
            self.window.geometry("1200x800")
        else: 
            self.window.geometry("1000x750")
        self._create_card_grid()
        self._update_loop()

    def _create_card_grid(self):
        # 仅销毁卡牌网格相关控件，保留洗牌警告标签和侧边提示等其他UI元素
        for widget in self.game_frame.winfo_children():
            if widget is self._shuffle_warning_label or widget is self._shuffle_side_hint_label:
                continue
            widget.destroy()
        self.card_buttons = []
        rows, cols = self._get_grid_dims()
        
        grid_container = tk.Frame(self.game_frame, bg=UIConfig.COLORS['primary'])
        grid_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        total_cards = len(self.game.cards)
        for i in range(total_cards):
            r, c = i // cols, i % cols
            card = PlayingCard(grid_container, width=85, height=120, corner_radius=12,
                               command=lambda idx=i: self._on_card_click(idx))
            card.grid(row=r, column=c, padx=8, pady=8)
            self.card_buttons.append(card)

    def _get_grid_dims(self):
        if self.game.mode in ('ultimate', 'ultimate_shuffle'): return 4, 9
        return 4, 4

    def _on_card_click(self, idx):
        if not self.game or self.game.is_paused or self.animating: 
            return
        if self.game.resolving_pair:
            return
        card = self.game.get_card_by_index(idx)
        if not card or card.is_matched or card.is_flipped: 
            return
        if not self.game.flip_card(idx):
            return
        r, s = card.value
        self.card_buttons[idx].animate_flip_to_front(r, s)
        if len(self.game.flipped_cards) == 2:
            self.animating = True
            self.window.after(GameConfig.MATCH_DELAY, self._check_match)

    def _check_match(self):
        pair, matched = self.game.get_last_pair()
        if pair:
            idx1, idx2 = pair
            btn1, btn2 = self.card_buttons[idx1], self.card_buttons[idx2]
            if matched:
                self.game.resolve_current_pair()
                btn1.animate_vanish()
                btn2.animate_vanish()
            else:
                # 先更新游戏状态，将卡牌翻回
                self.game.resolve_current_pair()
                # 然后更新UI显示 - 确保卡牌翻回背面
                btn1.show_back()
                btn2.show_back()
                # 检查是否触发洗牌（_check_shuffle_trigger会在匹配失败时自动调用）
                # 如果触发了洗牌，需要重新渲染卡牌
                if self.game.shuffle_enabled:
                    # 延迟检查，确保洗牌逻辑已执行
                    self.window.after(100, self._check_and_render_shuffle)
                else:
                    # 如果没有洗牌，确保所有卡牌状态正确同步
                    self.window.after(50, self._sync_cards_state)
        else:
            # 如果没有配对信息，确保重置状态
            if self.game:
                self.game.resolving_pair = False
                self.game.clear_flipped_cards()
        self.animating = False
        if self.game and self.game.is_completed: 
            self.window.after(500, self._on_game_complete)
    
    def _sync_cards_state(self):
        """同步卡牌状态，确保UI和游戏状态一致"""
        if not self.game:
            return
        # 确保重置 resolving_pair 状态，防止卡住
        self.game.resolving_pair = False
        for i, card in enumerate(self.game.cards):
            if i >= len(self.card_buttons):
                continue
            # 如果卡牌未匹配且未翻转，确保显示背面
            if not card.is_matched and not card.is_flipped and not card.is_revealed:
                self.card_buttons[i].show_back()
    
    def _check_and_render_shuffle(self):
        """检查是否需要重新渲染卡牌（洗牌后）"""
        if not self.game or not self.game.shuffle_enabled:
            return
        # 检查是否刚刚发生了洗牌（通过检查连续失败计数是否被重置）
        # 这里我们通过检查卡牌位置是否改变来判断，但更简单的方法是直接重新渲染
        # 实际上，洗牌后卡牌的值会改变，但位置索引不变，所以需要重新显示所有卡牌
        # 由于洗牌会重置所有卡牌状态，我们需要重新渲染
        # 确保重置 resolving_pair 状态，防止卡住
        if self.game:
            self.game.resolving_pair = False
        # 重新渲染卡牌状态
        self._render_cards_state()

        # 额外步骤：有时 PlayingCard 会保留动画结束后的 _is_vanished 标记，
        # 导致洗牌后未匹配卡牌仍然不可点击或不可绘制。
        # 因此在洗牌后强制清理未匹配卡牌的消失标记并恢复为可用状态。
        try:
            for i, btn in enumerate(self.card_buttons):
                if i >= len(self.game.cards):
                    continue
                card = self.game.cards[i]
                # 未匹配的卡牌应当可交互并显示背面
                if not card.is_matched:
                    # 删除内部消失标记（如果存在）
                    if getattr(btn, '_is_vanished', False):
                        try:
                            delattr(btn, '_is_vanished')
                        except Exception:
                            try:
                                del btn._is_vanished
                            except Exception:
                                pass
                    # 确保可点击并显示背面
                    try:
                        btn.config(state='normal')
                    except Exception:
                        pass
                    btn.show_back()
                else:
                    # 匹配的卡牌保持禁用/正面显示
                    try:
                        btn.config(state='disabled')
                    except Exception:
                        pass
        except Exception:
            pass

        # 如果游戏对象上记录了 shuffle_status，清理它，避免重复处理
        try:
            if hasattr(self.game, 'shuffle_status'):
                delattr(self.game, 'shuffle_status')
        except Exception:
            try:
                self.game.shuffle_status = None
            except Exception:
                pass

    def _update_loop(self):
        """定期更新游戏状态和时间显示"""
        if not self.game or self._end_handled: 
            return
        
        # 确保计时器已启动（如果游戏已开始但计时器未启动）
        if self.game.is_started and not self.game.timer.is_running and not self.game.is_paused:
            self.game.timer.start()
        
        # 更新时间显示
        time_str = f"冻结中 {self._time_freeze_remaining}s" if self._time_frozen else self.game.timer.get_time_display()
        try:
            self.time_label.config(text=f"⏱ {time_str}")
        except Exception:
            # 如果时间标签已被销毁，忽略异常，避免打断更新循环
            pass
        try:
            self.score_label.config(text=f"⭐ 分数: {self.game.score}")
        except Exception:
            # 如果分数标签已被销毁，忽略异常，避免打断更新循环
            pass
        
        # 检查洗牌警告
        self._update_shuffle_warning()
        
        # 检查超时（仅限有时间限制的模式）
        if self.game.timer.time_limit is not None and self.game.timer.is_time_up():
            self._on_game_failed()
            return

        # 如果游戏对象标记了已洗牌状态，重建卡牌网格并重渲染
        # 注意：需要保持已经匹配并执行过“消失”的卡牌在洗牌后依然不可见
        try:
            if getattr(self.game, 'shuffle_status', None) == 'shuffled':
                # 重新创建卡牌按钮（彻底重置控件状态）
                self._create_card_grid()

                # 对已经匹配完成的卡牌重新应用“消失”效果，避免它们在洗牌后重新出现
                try:
                    for i, card in enumerate(self.game.cards):
                        if i >= len(self.card_buttons):
                            break
                        if getattr(card, 'is_matched', False):
                            try:
                                # 使用已有的 vanish 动画接口，让按钮保持隐藏状态
                                self.card_buttons[i].animate_vanish()
                            except Exception:
                                # 如果动画不可用，至少禁用按钮，避免被点击
                                try:
                                    self.card_buttons[i].config(state='disabled')
                                except Exception:
                                    pass
                except Exception:
                    pass

                # 然后根据当前游戏状态整体同步一次 UI
                self._render_cards_state()

                # 给玩家一个明确提示：已经发生洗牌
                try:
                    messagebox.showinfo("洗牌提示", "⚠️ 由于连续配对失败，牌局已重新洗牌，请重新观察牌面！")
                except Exception:
                    pass
                # 清理标志
                try:
                    delattr(self.game, 'shuffle_status')
                except Exception:
                    try:
                        self.game.shuffle_status = None
                    except Exception:
                        pass
        except Exception:
            pass
        
        # 继续循环更新（100ms刷新一次）
        self.update_task = self.window.after(100, self._update_loop)

    def _toggle_pause(self):
        if not self.game or not self.game.is_started:
            return
        if self.game.is_paused:
            self.game.resume_game()
            try:
                self.pause_button.text = "⏸ 暂停"
                self.pause_button._draw()
            except Exception:
                pass
        else:
            self.game.pause_game()
            try:
                self.pause_button.text = "▶ 继续"
                self.pause_button._draw()
            except Exception:
                pass

    def _on_game_complete(self):
        if self._end_handled: return
        self._end_handled = True
        try:
            last = self.player.game_records[-1] if getattr(self.player, 'game_records', None) else None
            reward = last.get('reward', 0) if (last and last.get('completed')) else self.game._calculate_reward(int(self.game.timer.get_elapsed_time()))
        except Exception:
            reward = self.game._calculate_reward(int(self.game.timer.get_elapsed_time()))
        messagebox.showinfo("恭喜", f"通关成功！\n获得积分: {reward}")
        if hasattr(self.player, 'achievements'):
            prev = getattr(self, '_prev_achievements', set())
            current = set(self.player.achievements)
            diff = current - prev
            if diff:
                defs = {a.get('id'): a for a in getattr(AchievementConfig, 'ACHIEVEMENTS', [])}
                lines = []
                for aid in diff:
                    a = defs.get(aid, {})
                    name = a.get('name', aid)
                    icon = a.get('icon', '')
                    reward = a.get('reward', 0)
                    lines.append(f"{icon} {name} (+{reward}积分)")
                messagebox.showinfo("成就解锁", "\n".join(lines))
        self.on_close() if self.on_close else self.window.destroy()

    def _on_game_failed(self):
        if self._end_handled: return
        self._end_handled = True
        messagebox.showinfo("遗憾", "时间到了，挑战失败！")
        self.on_close() if self.on_close else self.window.destroy()

    def _on_closing(self):
        if self.update_task: self.window.after_cancel(self.update_task)
        if self._shuffle_warning_animation: 
            self.window.after_cancel(self._shuffle_warning_animation)
            self._shuffle_warning_animation = None
        if hasattr(self.player, 'remove_change_listener'):
            try: self.player.remove_change_listener(self._on_player_change)
            except: pass
        self.window.destroy()
        if self.on_close: self.on_close()

    def _on_player_change(self):
        self.window.after(0, self._update_item_display)

    def _update_item_display(self):
        for item_id, btn in self.item_buttons.items():
            btn.set_count(self.player.get_item_count(item_id))

    def _use_item(self, item_id):
        if not self.game or not self.game.is_started or self._time_frozen: return
        if self.player.get_item_count(item_id) <= 0: return
        if item_id == 'hint':
            self.game.use_hint()
            for idx in self.game.hint_cards:
                r, s = self.game.cards[idx].value
                self.card_buttons[idx].show_front(r, s)
            self.window.after(1000, lambda: self._restore_hint())
        elif item_id == 'time_extend':
            self.game.extend_time(30)
            messagebox.showinfo("道具", "时间延长 30 秒！")
        elif item_id == 'shuffle_prevent':
            # 防洗牌道具：仅在洗牌模式下可用
            if not self.game.shuffle_enabled:
                messagebox.showwarning("道具", "防洗牌道具仅在洗牌模式下可用！")
                return
            if self.game.activate_shuffle_prevent():
                messagebox.showinfo("道具", "🛡️ 防洗牌道具已激活！下次洗牌将被阻止。")
                save_player(self.player)
        elif item_id == 'undo':
            # 时间静止道具：仅在终极模式中可用，冻结时间10秒但允许正常翻牌配对
            if self.game.mode not in ('ultimate', 'ultimate_shuffle'):
                messagebox.showwarning("道具", "时间静止仅在终极模式中可用！")
                return
            if self._trigger_time_freeze(10):
                # 消耗道具并记录使用次数
                if self.player:
                    self.player.use_item('undo')
                if hasattr(self.game, 'items_used'):
                    self.game.items_used['undo'] = self.game.items_used.get('undo', 0) + 1
                messagebox.showinfo("道具", "⏸ 时间静止启动：10 秒内时间不流逝！")
        save_player(self.player)

    def _trigger_time_freeze(self, duration):
        if self._time_frozen: return False
        self._time_frozen = True
        self._time_freeze_remaining = duration
        self._time_freeze_task = self.window.after(1000, self._update_time_freeze)
        self.game.timer.pause()
        return True

    def _update_time_freeze(self):
        self._time_freeze_remaining -= 1
        if self._time_freeze_remaining <= 0:
            self._time_frozen = False
            self.game.timer.resume()
            if self._time_freeze_task:
                self.window.after_cancel(self._time_freeze_task)
                self._time_freeze_task = None
        else:
            self._time_freeze_task = self.window.after(1000, self._update_time_freeze)

    def _restore_hint(self):
        for idx in self.game.hint_cards:
            if not self.game.cards[idx].is_matched: self.card_buttons[idx].show_back()
        self.game.hide_hint()

    def _update_shuffle_warning(self):
        """更新洗牌警告显示"""
        # 不需要警告或游戏已结束时，隐藏所有相关 UI，并重置状态
        if not self.game or not self.game.shuffle_enabled or self.game.is_completed or self.game.is_failed:
            if self._shuffle_warning_label:
                try:
                    self._shuffle_warning_label.place_forget()
                except Exception:
                    pass
            if self._shuffle_side_hint_label:
                try:
                    self._shuffle_side_hint_label.place_forget()
                except Exception:
                    pass
            if self._shuffle_warning_animation:
                try:
                    self.window.after_cancel(self._shuffle_warning_animation)
                except Exception:
                    pass
                self._shuffle_warning_animation = None
            # 重置闪烁状态
            self._shuffle_flash_done = False
            self._shuffle_flash_count = 0
            # 恢复背景色
            if hasattr(self, 'game_frame'):
                self.game_frame.config(bg=UIConfig.COLORS['primary'])
            return

        warning_needed, remaining = self.game.get_shuffle_warning()

        if warning_needed and remaining > 0:
            # 中间红色警告文字
            warning_text = f"⚠️ 警告：再失败 {remaining} 次将触发洗牌！"
            if self._shuffle_warning_label:
                try:
                    self._shuffle_warning_label.config(text=warning_text, font=self._shuffle_warning_font)
                    self._shuffle_warning_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
                except Exception:
                    pass

            # 如果尚未完成本轮闪烁，则启动闪烁动画序列
            if not self._shuffle_flash_done and not self._shuffle_warning_animation:
                self._shuffle_flash_count = 0
                self._animate_shuffle_warning()

            # 闪烁完成后，仅显示右侧竖排浅色提示文字（居中显示）
            if self._shuffle_flash_done and self._shuffle_side_hint_label:
                try:
                    vertical_text = "再\n失\n败\n一\n次\n将\n会\n重\n新\n洗\n牌\n，\n\n请\n注\n意\n记\n忆\n牌\n面\n位\n置"
                    self._shuffle_side_hint_label.config(text=vertical_text, justify=tk.CENTER, anchor='center', font=self._shuffle_side_font)
                    # 右侧居中显示（垂直居中）
                    self._shuffle_side_hint_label.place(relx=0.98, rely=0.5, anchor=tk.E)
                except Exception:
                    pass
        else:
            # 当前不需要警告：隐藏并重置状态
            if self._shuffle_warning_label:
                try:
                    self._shuffle_warning_label.place_forget()
                except Exception:
                    pass
            if self._shuffle_side_hint_label:
                try:
                    self._shuffle_side_hint_label.place_forget()
                except Exception:
                    pass
            if self._shuffle_warning_animation:
                try:
                    self.window.after_cancel(self._shuffle_warning_animation)
                except Exception:
                    pass
                self._shuffle_warning_animation = None
            self._shuffle_flash_done = False
            self._shuffle_flash_count = 0
            if hasattr(self, 'game_frame'):
                self.game_frame.config(bg=UIConfig.COLORS['primary'])
    
    def _animate_shuffle_warning(self):
        """洗牌警告闪烁动画"""
        if not self.game or not self._shuffle_warning_label:
            return

        try:
            # 立即切换为提示色与背景（一次性闪烁）
            try:
                self._shuffle_warning_label.config(fg='#FF1744', font=self._shuffle_warning_font)
            except Exception:
                pass

            if hasattr(self, 'game_frame'):
                try:
                    self.game_frame.config(bg='#FFEBEE')
                except Exception:
                    pass

            # 在短延迟后恢复并标记闪烁完成，由内部函数完成恢复工作
            def _end_flash():
                try:
                    try:
                        self._shuffle_warning_label.config(fg='#FF5252', font=self._shuffle_warning_font)
                    except Exception:
                        pass
                    if hasattr(self, 'game_frame'):
                        try:
                            self.game_frame.config(bg=UIConfig.COLORS['primary'])
                        except Exception:
                            pass
                    # 隐藏中间大警告，侧边提示由 _update_shuffle_warning 接管显示
                    try:
                        self._shuffle_warning_label.place_forget()
                    except Exception:
                        pass
                    self._shuffle_warning_animation = None
                    self._shuffle_flash_done = True
                except Exception:
                    self._shuffle_warning_animation = None

            # 安排一次性的恢复操作（500ms）
            self._shuffle_warning_animation = self.window.after(500, _end_flash)
        except Exception:
            self._shuffle_warning_animation = None

    def _render_cards_state(self):
        if not self.game: return
        # 确保重置 resolving_pair 状态，防止卡住
        self.game.resolving_pair = False
        for i, card in enumerate(self.game.cards):
            r, s = card.value
            # 如果卡牌已经匹配且执行过消失动画（_is_vanished 标记存在），
            # 则保持消失状态，不再强制绘制出来
            if card.is_matched and getattr(self.card_buttons[i], '_is_vanished', False):
                try: self.card_buttons[i].config(state='disabled')
                except: pass
                continue
            if card.is_matched:
                self.card_buttons[i].show_front(r, s)
                try: self.card_buttons[i].config(state='disabled')
                except: pass
            elif card.is_flipped or card.is_revealed:
                self.card_buttons[i].show_front(r, s)
                try: self.card_buttons[i].config(state='normal')
                except: pass
            else:
                self.card_buttons[i].show_back()
                try: self.card_buttons[i].config(state='normal')
                except: pass
            if not card.is_matched:
                try: delattr(self.card_buttons[i], '_is_vanished')
                except: pass
        self.animating = False
