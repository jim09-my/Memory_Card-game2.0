import tkinter as tk
from tkinter import messagebox
from config import ItemConfig, UIConfig
from managers.shop_manager import ShopManager
from managers.data_manager import save_player
from data_structures.sort_algorithms import merge_sort
from data_structures.sort_algorithms import merge_sort

# --- 辅助绘图函数---
def draw_rounded_rect(canvas, x, y, w, h, r, fill, outline=""):
    canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline=outline)
    canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline=outline)
    canvas.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline=outline)
    canvas.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline=outline)

class FlatBuyButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=90, height=32, state='normal'):
        super().__init__(master, width=width, height=height, bg='white', highlightthickness=0, bd=0)
        self.text = text
        self._command = command
        self.w, self.h = width, height
        self._state = state
        self.bg_color = '#FFF59D' if state == 'normal' else '#EEEEEE'
        self.text_color = '#5D4037' if state == 'normal' else '#9E9E9E'
        if self._state != 'disabled':
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
        r = h/2
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2
        col = '#FFF176' if self._state == 'hover' else self.bg_color
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=180, fill=col, outline="")
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=270, extent=180, fill=col, outline="")
        self.create_rectangle(x1+r, y1, x2-r, y2+1, fill=col, outline="")
        self.create_text(cx, cy, text=self.text, font=('Arial Rounded MT Bold', 11), fill=self.text_color)
    def _on_enter(self, e): self._state = 'hover'; self.config(cursor='hand2'); self._draw()
    def _on_leave(self, e): self._state = 'normal'; self.config(cursor=''); self._draw()
    def _on_press(self, e): self._state = 'active'; self._draw()
    def _on_release(self, e): 
        if self._state == 'active': 
            self._state = 'hover'; self._draw()
            if self._command: self.after(50, self._command)

class ShopWindow:
    def __init__(self, master, player):
        self.master = master
        self.player = player
        self.shop_manager = ShopManager()
        self.window = tk.Toplevel(master)
        self.window.title("道具商城")
        self.window.geometry("500x650")
        self.window.config(bg='#E0F7FA')
        self.window.transient(master)
        self.window.grab_set()
        self._center_window()
        
        self.sort_mode = 0 # 0: 默认, 1: 价格升序, 2: 价格降序
        
        self.canvas = tk.Canvas(self.window, bg='#E0F7FA', highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._draw_bg_decorations()
        self._draw_title()
        
        self._create_points_display()
        self._create_back_button()
        
        # === 添加排序按钮 ===
        self._create_sort_controls()
        
        self._create_items_area()
        
        if hasattr(self.player, 'add_change_listener'):
            self.player.add_change_listener(self._on_player_change)
        self.window.protocol("WM_DELETE_WINDOW", self._close)

    def _center_window(self):
        self.window.update_idletasks()
        w, h = 500, 650
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _draw_bg_decorations(self):
        self.canvas.create_oval(-50, -50, 150, 150, fill='#B2DFDB', outline="")
        self.canvas.create_oval(400, 500, 550, 650, fill='#F0F4C3', outline="")

    def _draw_title(self):
        center_x = 250
        y_pos = 60
        text = "道具商城"
        font = ("Arial Rounded MT Bold", 32, "bold")
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            self.canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill='white')
        self.canvas.create_text(center_x, y_pos, text=text, font=font, fill='#FBC02D')

    def _create_points_display(self):
        tk.Label(self.window, text=f"当前积分: {self.player.points}", font=('Arial', 12, 'bold'), 
                 bg='#E0F7FA', fg='#00796B').place(relx=0.5, y=110, anchor=tk.CENTER)

    def _create_back_button(self):
        btn = tk.Button(self.window, text="✖", command=self._close, 
                        bg='#B2DFDB', fg='white', font=('Arial', 10, 'bold'),
                        relief=tk.FLAT, bd=0)
        btn.place(x=460, y=15, width=25, height=25)

    def _create_sort_controls(self):
        frame = tk.Frame(self.window, bg='#E0F7FA')
        frame.place(relx=0.5, y=145, anchor=tk.CENTER)
        
        self.sort_btn = tk.Button(frame, text="⇅ 价格排序", command=self._toggle_sort,
                                  bg='#FFF59D', fg='#5D4037', font=('Arial', 10, 'bold'),
                                  relief=tk.FLAT)
        self.sort_btn.pack()

    def _toggle_sort(self):
        self.sort_mode = (self.sort_mode + 1) % 3
        texts = ["⇅ 价格排序 (默认)", "↑ 价格排序 (低到高)", "↓ 价格排序 (高到低)"]
        self.sort_btn.config(text=texts[self.sort_mode])
        self._render_items()

    def _create_items_area(self):
        container = tk.Frame(self.window, bg='#E0F7FA')
        container.place(relx=0.5, rely=0.62, anchor=tk.CENTER, width=460, height=420)
        
        canvas = tk.Canvas(container, bg='#E0F7FA', highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#E0F7FA')

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((230, 0), window=self.scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.item_canvas = canvas
        self._render_items()

    def _render_items(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 获取原始字典数据
        raw_items = self.shop_manager.get_items() or ItemConfig.ITEMS

        items_list = []
        for k, v in raw_items.items():
            item_copy = v.copy()
            item_copy['id'] = k
            items_list.append(item_copy)
            
        # === 使用归并排序进行排序 ===
        if self.sort_mode == 1: # 升序
            items_list = merge_sort(items_list, lambda x: x['price'], reverse=False)
        elif self.sort_mode == 2: # 降序
            items_list = merge_sort(items_list, lambda x: x['price'], reverse=True)

        col_count = 0
        row_count = 0
        
        for item in items_list:
            item_id = item['id']
            card_w, card_h = 180, 190
            card = tk.Canvas(self.scrollable_frame, bg='#E0F7FA', width=card_w, height=card_h, highlightthickness=0)
            card.grid(row=row_count, column=col_count, padx=15, pady=15)
            
            draw_rounded_rect(card, 0, 0, card_w, card_h, 20, fill='white', outline="")
            
            content = tk.Frame(card, bg='white')
            card.create_window(card_w/2, card_h/2, window=content, width=card_w-20, height=card_h-20)

            tk.Label(content, text=item.get('icon', '🎁'), font=('Segoe UI Emoji', 32), bg='white').pack(pady=(10, 5))
            tk.Label(content, text=item['name'], font=('Arial Rounded MT Bold', 12), bg='white', fg='#455A64').pack()
            
            price = item['price']
            tk.Label(content, text=f"{price} 积分", font=('Arial', 10, 'bold'), bg='white', fg='#FFB74D').pack(pady=(2, 5))
            
            btn_state = 'normal' if self.player.points >= price else 'disabled'
            
            btn = FlatBuyButton(content, text="购买", width=80, height=28, state=btn_state,
                          command=lambda i=item_id: self._purchase(i))
            btn.pack(pady=5)
            
            owned = self.player.get_item_count(item_id)
            card.create_text(card_w-15, card_h-15, text=f"持有: {owned}", font=('Arial', 9), fill='#B0BEC5', anchor='se')

            col_count += 1
            if col_count >= 2:
                col_count = 0
                row_count += 1

    def _purchase(self, item_id):
        success, msg = self.shop_manager.purchase_item(self.player, item_id)
        if success:
            item_name = (self.shop_manager.get_items() or ItemConfig.ITEMS)[item_id]["name"]
            messagebox.showinfo("成功", f"{item_name}\n购买成功！")
            save_player(self.player)
            self._update_ui()
        else:
            messagebox.showwarning("提示", msg)

    def _update_ui(self):
        self._render_items()
        self._create_points_display()

    def _on_player_change(self):
        self.window.after(0, self._update_ui)

    def _close(self):
        if hasattr(self.player, 'remove_change_listener'):
            try: self.player.remove_change_listener(self._on_player_change)
            except: pass
        self.window.destroy()