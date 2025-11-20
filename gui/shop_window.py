"""
道具商城窗口
"""

import tkinter as tk
from tkinter import messagebox
from functools import partial

from config import ItemConfig
from managers.shop_manager import ShopManager
from managers.data_manager import save_player


class ShopWindow:
    """商城窗口"""

    def __init__(self, master, player, on_close_callback=None):
        self.master = master
        self.player = player
        self.on_close_callback = on_close_callback

        self.window = tk.Toplevel(master)
        self.window.title("记忆翻牌游戏 - 道具商城")
        # 增大默认窗口尺寸并允许用户调整大小，便于在较小屏幕上仍可滚动查看
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        self.window.transient(master)
        self.window.grab_set()
        # 居中窗口
        try:
            self.window.update_idletasks()
            w = self.window.winfo_width() or 900
            h = self.window.winfo_height() or 700
            x = (self.window.winfo_screenwidth() // 2) - (w // 2)
            y = (self.window.winfo_screenheight() // 2) - (h // 2)
            self.window.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

        self.refresh_symbols = ['⟳', '⟲', '⟰', '⟱']
        self.refresh_index = 0
        self.is_refreshing = False

        self.shop_manager = ShopManager()

        self._create_widgets()
        self._render_items()

        # 监听玩家数据变化以更新积分/库存显示
        if hasattr(self.player, 'add_change_listener'):
            try:
                self.player.add_change_listener(self._on_player_change)
            except Exception:
                pass

        self.window.protocol("WM_DELETE_WINDOW", self._close)

    def _on_player_change(self):
        try:
            self.window.after(0, lambda: (self._update_points(), self._render_items()))
        except Exception:
            pass

    # ------------------------------ UI 构建 ------------------------------
    def _create_widgets(self):
        # 顶部
        header = tk.Frame(self.window, bg='#4A90E2', height=110, padx=20)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🛒 道具商城",
            font=('Arial', 26, 'bold'),
            bg='#4A90E2',
            fg='white'
        ).pack(anchor=tk.W, pady=(15, 5))

        info_bar = tk.Frame(header, bg='#4A90E2')
        info_bar.pack(fill=tk.X)

        self.points_label = tk.Label(
            info_bar,
            text=f"当前积分：{self.player.points}",
            font=('Arial', 14),
            bg='#4A90E2',
            fg='#FEE08B'
        )
        self.points_label.pack(side=tk.LEFT)

        self.refresh_btn = tk.Button(
            info_bar,
            text="🔄 刷新",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            relief=tk.GROOVE,
            command=self._handle_refresh
        )
        self.refresh_btn.pack(side=tk.RIGHT)

        # 提示栏
        bonus_text = "新手福利：注册7天内首次兑换提示道具免费"
        tk.Label(
            self.window,
            text=bonus_text,
            font=('Arial', 11),
            fg='#F39C12',
            pady=6
        ).pack(fill=tk.X)

        # 列表区域（使用 Canvas + 滚动条，确保所有商品可见）
        container = tk.Frame(self.window, padx=10, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Canvas + vertical scrollbar
        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.v_scroll = tk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 内部 frame（放在 canvas 中）
        self.items_frame = tk.Frame(self.canvas)
        self.items_window = self.canvas.create_window((0, 0), window=self.items_frame, anchor='nw')

        # 绑定尺寸变化以更新滚动区域和宽度
        def _on_frame_config(event):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))

        def _on_canvas_config(event):
            # 将内部 frame 宽度与 canvas 宽度保持一致
            canvas_width = event.width
            try:
                self.canvas.itemconfig(self.items_window, width=canvas_width)
            except Exception:
                pass

        self.items_frame.bind('<Configure>', _on_frame_config)
        self.canvas.bind('<Configure>', _on_canvas_config)

    def _render_items(self):
        """渲染商品卡片"""
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        # 优先使用 manager 中加载的商品（可能来自 data/shop_items.json）
        items = self.shop_manager.get_items() or ItemConfig.ITEMS
        for idx, (item_id, item) in enumerate(items.items()):
            card = tk.Frame(
                self.items_frame,
                bd=2,
                relief=tk.GROOVE,
                padx=15,
                pady=10
            )
            card.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky='nsew')

            icon = tk.Label(card, text=item.get('icon', '🎲'), font=('Arial', 28))
            icon.pack(anchor=tk.W)

            tk.Label(
                card,
                text=item['name'],
                font=('Arial', 16, 'bold')
            ).pack(anchor=tk.W)

            tk.Label(
                card,
                text=item['description'],
                font=('Arial', 11),
                fg='#555555',
                wraplength=240,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(2, 6))

            owned = self.player.get_item_count(item_id)
            tk.Label(
                card,
                text=f"库存：{owned} 个",
                font=('Arial', 11),
                fg='#2C3E50'
            ).pack(anchor=tk.W)

            price = self._get_price(item_id, item['price'])
            price_text = "限时免费" if price == 0 else f"{price} 积分"
            price_color = '#27AE60' if price == 0 else '#E74C3C'

            tk.Label(
                card,
                text=f"价格：{price_text}",
                font=('Arial', 12, 'bold'),
                fg=price_color
            ).pack(anchor=tk.W, pady=(6, 4))

            btn = tk.Button(
                card,
                text="兑换",
                font=('Arial', 12, 'bold'),
                bg='#4A90E2',
                fg='white',
                width=12,
                command=partial(self._purchase_item, item_id)
            )
            btn.pack(anchor=tk.E, pady=(5, 0))

        # 调整列权重
        for col in range(2):
            self.items_frame.grid_columnconfigure(col, weight=1)

    # ------------------------------ 功能逻辑 ------------------------------
    def _handle_refresh(self):
        if self.is_refreshing:
            return
        self.is_refreshing = True
        self.refresh_btn.config(state=tk.DISABLED)
        self._animate_refresh()
        # 模拟数据刷新
        self.window.after(600, self._finish_refresh)

    def _animate_refresh(self):
        if not self.is_refreshing:
            self.refresh_btn.config(text="🔄 刷新")
            return

        symbol = self.refresh_symbols[self.refresh_index % len(self.refresh_symbols)]
        self.refresh_btn.config(text=f"{symbol} 刷新中")
        self.refresh_index += 1
        self.window.after(120, self._animate_refresh)

    def _finish_refresh(self):
        self._render_items()
        self._update_points()
        self.is_refreshing = False
        self.refresh_btn.config(state=tk.NORMAL, text="🔄 刷新")

    def _get_price(self, item_id, base_price):
        """根据福利计算价格"""
        if item_id == 'hint' and self.player.can_claim_free_hint():
            return 0
        return base_price

    def _purchase_item(self, item_id):
        # 使用 ShopManager 处理购买与持久化
        success, msg = self.shop_manager.purchase_item(self.player, item_id)
        if not success:
            messagebox.showwarning("提示", msg)
            return

        # 刷新界面并保存（ShopManager.purchase_item 已尝试保存）
        item = self.shop_manager.get_item(item_id) or ItemConfig.ITEMS.get(item_id, {})
        messagebox.showinfo("成功", f"已获得：{item.get('name', item_id)}")
        # 确保玩家数据持久化（冗余保存，保证一致性）
        try:
            save_player(self.player)
        except Exception:
            pass

        self._update_points()
        self._render_items()

        if self.on_close_callback:
            self.on_close_callback()

    def _update_points(self):
        self.points_label.config(text=f"当前积分：{self.player.points}")

    def _close(self):
        # 移除监听器
        if hasattr(self.player, 'remove_change_listener'):
            try:
                self.player.remove_change_listener(self._on_player_change)
            except Exception:
                pass

        if self.on_close_callback:
            self.on_close_callback()
        self.window.destroy()


# ============== 测试代码 ==============
if __name__ == '__main__':
    from core.player import Player

    root = tk.Tk()
    root.withdraw()

    p = Player("Tester")
    p.points = 1500
    ShopWindow(root, p).window.mainloop()

