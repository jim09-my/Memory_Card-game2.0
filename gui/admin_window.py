import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
from typing import Dict, Any
from config import UIConfig, DataConfig
from managers.data_manager import load_players, save_players
from core.player import Player

# --- 配置颜色 ---
BORDER_COLOR = "#B2DFDB"  # 主题浅色边框
SHADOW_COLOR = "#E0F2F1"  # 极浅阴影

# --- 绘图辅助函数 ---
def draw_shadow_panel(canvas, x, y, w, h, r, bg_color, border_color=BORDER_COLOR, shadow_color=SHADOW_COLOR, tags="panel"):
    canvas.delete(tags)
    _draw_rounded_path(canvas, x, y+3, w, h, r, fill=shadow_color, outline="", tags=tags)
    _draw_rounded_path(canvas, x, y, w, h, r, fill=bg_color, outline=border_color, width=1, tags=tags)

def _draw_rounded_path(canvas, x, y, w, h, r, **kwargs):
    x, y, w, h, r = map(int, (x, y, w, h, r))
    if 'outline' not in kwargs: kwargs['outline'] = ""
    
    canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, style=tk.PIESLICE, **kwargs)
    canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, style=tk.PIESLICE, **kwargs)
    canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, style=tk.PIESLICE, **kwargs)
    canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, style=tk.PIESLICE, **kwargs)
    
    fill_col = kwargs.get('fill', '')
    canvas.create_rectangle(x, y+r, x+w+1, y+h-r, outline="", fill=fill_col, tags=kwargs.get('tags'))
    canvas.create_rectangle(x+r, y, x+w-r, y+h+1, outline="", fill=fill_col, tags=kwargs.get('tags'))
    
    if kwargs.get('outline'):
        col = kwargs['outline']
        wd = kwargs.get('width', 1)
        tags = kwargs.get('tags')
        canvas.create_line(x+r, y, x+w-r, y, fill=col, width=wd, tags=tags)
        canvas.create_line(x+r, y+h, x+w-r, y+h, fill=col, width=wd, tags=tags)
        canvas.create_line(x, y+r, x, y+h-r, fill=col, width=wd, tags=tags)
        canvas.create_line(x+w, y+r, x+w, y+h-r, fill=col, width=wd, tags=tags)
        
        canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, style=tk.ARC, outline=col, width=wd, tags=tags)
        canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, style=tk.ARC, outline=col, width=wd, tags=tags)
        canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, style=tk.ARC, outline=col, width=wd, tags=tags)
        canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, style=tk.ARC, outline=col, width=wd, tags=tags)

# --- 自定义组件 ---
class CandyTabButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=140, height=45, selected=False):
        super().__init__(master, width=width, height=height, 
                         bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.text = text
        self.command = command
        self.btn_w = width
        self.btn_h = height
        self._selected = selected
        self._hover = False
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self._draw()

    def set_selected(self, val):
        self._selected = val
        self._draw()

    def _draw(self):
        self.delete('all')
        if self._selected:
            bg_col, fg_col, border_col = '#FFD54F', '#5D4037', '#FBC02D'
        elif self._hover:
            bg_col, fg_col, border_col = '#80DEEA', '#006064', '#4DD0E1'
        else:
            bg_col, fg_col, border_col = '#B2DFDB', '#455A64', '#80CBC4'
        
        r = self.btn_h / 2
        _draw_rounded_path(self, 1, 1, self.btn_w-2, self.btn_h-2, r, fill=bg_col, outline=border_col, width=1)
        self.create_text(self.btn_w/2, self.btn_h/2, text=self.text, font=("Microsoft YaHei UI", 11, "bold"), fill=fg_col)

    def _on_click(self, e):
        if self.command: self.command()
    def _on_enter(self, e):
        self._hover = True; self.config(cursor='hand2'); self._draw()
    def _on_leave(self, e):
        self._hover = False; self.config(cursor=''); self._draw()

class RoundButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=120, height=40, 
                 bg_color='#2896A0', hover_color='#4DB6AC', text_color='white', parent_bg='white'):
        super().__init__(master, width=width, height=height, bg=parent_bg, highlightthickness=0, bd=0) 
        self.text = text
        self.command = command
        self.w, self.h = width, height
        self.bg_color, self.hover_color, self.text_color = bg_color, hover_color, text_color
        self._hover = False
        self.bind('<Button-1>', lambda e: command() if command else None)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self._draw()

    def _draw(self):
        self.delete('all')
        fill = self.hover_color if self._hover else self.bg_color
        _draw_rounded_path(self, 1, 1, self.w-2, self.h-2, 8, fill=fill, outline=BORDER_COLOR, width=1)
        self.create_text(self.w/2, self.h/2, text=self.text, font=("Microsoft YaHei UI", 10, "bold"), fill=self.text_color)

    def _on_enter(self, e):
        self._hover = True; self.config(cursor='hand2'); self._draw()
    def _on_leave(self, e):
        self._hover = False; self.config(cursor=''); self._draw()

class AdminWindow:
    def __init__(self, master=None):
        if master: self.window = tk.Toplevel(master)
        else: self.window = tk.Tk()
        
        self.window.title("管理员面板")
        self.window.geometry("1000x750")
        self.window.configure(bg=UIConfig.COLORS['primary']) 
        self.window.resizable(True, True)
        self._center_window()
        self._configure_styles()
        
        self.tabs = {}
        self.current_tab = None
        self.setup_ui()
        self.window.after(100, self.load_users)
        
    def _center_window(self):
        self.window.update_idletasks()
        w, h = 1000, 750
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _configure_styles(self):
        style = ttk.Style()
        try: style.theme_use('clam')
        except: pass
        style.configure("Admin.Vertical.TScrollbar", gripcount=0, background='#B2DFDB', 
                        troughcolor='#FAFAFA', bordercolor='#FAFAFA', arrowsize=0)

    def setup_ui(self):
        # 1. 顶部
        header_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'], pady=25) 
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="管理员控制台", font=('Microsoft YaHei UI', 20, 'bold'),
                 bg=UIConfig.COLORS['primary'], fg='white').pack()

        # 2. 导航
        nav_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'], pady=15) 
        nav_frame.pack(fill=tk.X)
        center_nav = tk.Frame(nav_frame, bg=UIConfig.COLORS['primary'])
        center_nav.pack(anchor=tk.CENTER)
        
        self.user_tab_btn = CandyTabButton(center_nav, "用户管理", command=lambda: self._switch_tab('users'))
        self.user_tab_btn.pack(side=tk.LEFT, padx=16) 
        self.export_tab_btn = CandyTabButton(center_nav, "数据导出", command=lambda: self._switch_tab('export'))
        self.export_tab_btn.pack(side=tk.LEFT, padx=16)
        self.tabs = {'users': self.user_tab_btn, 'export': self.export_tab_btn}

        # 3. 内容容器
        self.container = tk.Frame(self.window, bg=UIConfig.COLORS['primary'], padx=20, pady=20)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.bg_canvas = tk.Canvas(self.container, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        self.content_area = tk.Frame(self.bg_canvas, bg='white')
        self.window_item = self.bg_canvas.create_window(0, 0, window=self.content_area, anchor='nw')
        self.bg_canvas.bind('<Configure>', self._on_bg_resize)
        self._switch_tab('users')

    def _on_bg_resize(self, event):
        w, h = event.width, event.height
        self.bg_canvas.delete('bg_rect')
        _draw_rounded_path(self.bg_canvas, 0, 0, w, h, 25, fill='white', outline="")
        self.bg_canvas.itemconfigure(self.window_item, width=w-50, height=h-50)
        self.bg_canvas.coords(self.window_item, 25, 25)

    def _switch_tab(self, tab_name):
        if self.current_tab: self.tabs[self.current_tab].set_selected(False)
        self.tabs[tab_name].set_selected(True)
        self.current_tab = tab_name
        for widget in self.content_area.winfo_children(): widget.destroy()
        if tab_name == 'users': self._build_user_mgmt()
        else: self._build_export()

    # --- 用户管理 ---
    def _build_user_mgmt(self):
        main_layout = tk.Frame(self.content_area, bg='white')
        main_layout.pack(fill=tk.BOTH, expand=True)
        
        # === 左侧：列表 ===
        left_panel = tk.Canvas(main_layout, bg='white', highlightthickness=0, width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16)) 
        
        def _draw_left_bg(event):
            draw_shadow_panel(left_panel, 5, 5, event.width-10, event.height-12, 10, bg_color='#FAFAFA')
        left_panel.bind('<Configure>', _draw_left_bg)
        
        left_content = tk.Frame(left_panel, bg='#FAFAFA')
        left_panel.create_window(15, 15, window=left_content, width=250, anchor='nw', tags='content')
        left_panel.bind('<Configure>', lambda e: left_panel.itemconfigure('content', width=e.width-30, height=e.height-30), add='+')

        # 标题
        lbl_frame = tk.Frame(left_content, bg='#FAFAFA')
        lbl_frame.pack(fill=tk.X, pady=(5, 10))
        tk.Label(lbl_frame, text="👥 用户列表", font=('Microsoft YaHei UI', 12, 'bold'), bg='#FAFAFA', fg='#455A64').pack(side=tk.LEFT, padx=10)
        
        # 列表
        list_container = tk.Frame(left_content, bg='white')
        list_container.pack(fill=tk.BOTH, expand=True)
        list_scroll = ttk.Scrollbar(list_container, orient="vertical", style="Admin.Vertical.TScrollbar")
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.user_listbox = tk.Listbox(
            list_container, font=('Microsoft YaHei UI', 11), bg='white', fg='#37474F',
            bd=0, highlightthickness=0, selectbackground=UIConfig.COLORS['primary'], 
            selectforeground='white', activestyle='none', yscrollcommand=list_scroll.set
        )
        self.user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        list_scroll.config(command=self.user_listbox.yview)
        self.user_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        # === 右侧：详情 ===
        right_panel = tk.Canvas(main_layout, bg='white', highlightthickness=0)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        def _draw_right_bg(event):
            draw_shadow_panel(right_panel, 5, 5, event.width-10, event.height-12, 10, bg_color='white')
        right_panel.bind('<Configure>', _draw_right_bg)
        
        right_content = tk.Frame(right_panel, bg='white')
        right_panel.create_window(15, 15, window=right_content, anchor='nw', tags='content')
        right_panel.bind('<Configure>', lambda e: right_panel.itemconfigure('content', width=e.width-30, height=e.height-30), add='+')
        
        # 详情标题
        r_lbl_frame = tk.Frame(right_content, bg='white')
        r_lbl_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 10))
        tk.Label(r_lbl_frame, text="📄 档案详情", font=('Microsoft YaHei UI', 12, 'bold'), bg='white', fg='#455A64').pack(side=tk.LEFT, padx=10)
        
        # --- 关键修改：按钮区 (先 pack BOTTOM，确保固定在底部) ---
        btn_bar = tk.Frame(right_content, bg='white')
        btn_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5))
        
        # 按钮：右对齐 (side=RIGHT)
        # 刷新列表
        RoundButton(btn_bar, "刷新列表", self.load_users, 
                    bg_color='#26A69A', hover_color='#4DB6AC').pack(side=tk.RIGHT, padx=10)
        
        # 重置密码
        RoundButton(btn_bar, "重置密码", self.reset_user_password, 
                    bg_color='#FF7043', hover_color='#FF8A65').pack(side=tk.RIGHT, padx=10)

        # --- 文本框 (填充剩余空间) ---
        text_container = tk.Frame(right_content, bg='white')
        # 放在标题下面，按钮上面
        text_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        text_scroll = ttk.Scrollbar(text_container, orient="vertical", style="Admin.Vertical.TScrollbar")
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(text_container, font=('Microsoft YaHei UI', 11),
            bg='white', fg='#37474F', bd=0, highlightthickness=0, wrap=tk.WORD,
            padx=10, pady=10, yscrollcommand=text_scroll.set)
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.detail_text.yview)

        if hasattr(self, 'users_data'): self._populate_listbox()

    # --- 导出界面 (保持不变) ---
    def _build_export(self):
        container = tk.Frame(self.content_area, bg='white')
        container.pack(expand=True, fill=tk.BOTH, padx=50, pady=30)
        center_canvas = tk.Canvas(container, width=500, height=400, bg='white', highlightthickness=0)
        center_canvas.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        draw_shadow_panel(center_canvas, 5, 5, 490, 390, 16, bg_color='#FAFAFA')
        content_frame = tk.Frame(center_canvas, bg='#FAFAFA')
        center_canvas.create_window(250, 200, window=content_frame, width=450, height=350)
        
        tk.Label(content_frame, text="📤 数据导出配置", font=('Microsoft YaHei UI', 16, 'bold'),
                 bg='#FAFAFA', fg='#263238').pack(pady=(30, 20))
        tk.Label(content_frame, text="请选择导出的文件格式:", font=('Microsoft YaHei UI', 11),
                 bg='#FAFAFA', fg='#546E7A').pack(anchor=tk.CENTER, pady=(0, 15))
        
        self.export_format = tk.StringVar(value="json")
        radio_frame = tk.Frame(content_frame, bg='#FAFAFA')
        radio_frame.pack(pady=10)
        tk.Radiobutton(radio_frame, text="JSON 格式", variable=self.export_format, value="json",
                       font=('Microsoft YaHei UI', 11), bg='#FAFAFA', activebackground='#FAFAFA', 
                       fg='#37474F', selectcolor='#FAFAFA').pack(side=tk.LEFT, padx=20)
        tk.Radiobutton(radio_frame, text="CSV 格式", variable=self.export_format, value="csv",
                       font=('Microsoft YaHei UI', 11), bg='#FAFAFA', activebackground='#FAFAFA', 
                       fg='#37474F', selectcolor='#FAFAFA').pack(side=tk.LEFT, padx=20)
        
        btn_frame = tk.Frame(content_frame, bg='#FAFAFA')
        btn_frame.pack(pady=40)
        RoundButton(btn_frame, "导出所有数据", self.export_user_data, 
                    width=220, height=50, bg_color='#039BE5', hover_color='#29B6F6', parent_bg='#FAFAFA').pack()
        self.export_status_label = tk.Label(content_frame, text="", font=('Microsoft YaHei UI', 10), bg='#FAFAFA', fg='#009688')
        self.export_status_label.pack()

    # --- 逻辑实现 ---
    def load_users(self):
        try:
            self.users_data = load_players()
            if self.current_tab == 'users' and hasattr(self, 'user_listbox'):
                self._populate_listbox()
        except Exception as e:
            messagebox.showerror("错误", f"加载用户数据失败: {str(e)}")

    def _populate_listbox(self):
        self.user_listbox.delete(0, tk.END)
        for username in self.users_data:
            self.user_listbox.insert(tk.END, username)
        if self.user_listbox.size() > 0:
            self.user_listbox.selection_set(0)
            self.display_user_details(self.user_listbox.get(0))

    def on_user_select(self, event):
        selection = self.user_listbox.curselection()
        if selection:
            username = self.user_listbox.get(selection[0])
            self.display_user_details(username)
            
    def display_user_details(self, username):
        if username not in self.users_data: return
        user_data = self.users_data[username]
        
        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)
        # 配置 Tag (样式)
        self.detail_text.tag_config('h_section', font=('Microsoft YaHei UI', 12, 'bold'), foreground='#2896A0', spacing1=20, spacing3=10)
        self.detail_text.tag_config('dashed_line', font=('Arial', 10), foreground='#E0E0E0', justify='center')
        self.detail_text.tag_config('key', font=('Microsoft YaHei UI', 11), foreground='#78909C', spacing1=5)
        self.detail_text.tag_config('val', font=('Microsoft YaHei UI', 11), foreground='#263238')
        self.detail_text.tag_config('val_bold', font=('Microsoft YaHei UI', 11, 'bold'), foreground='#00897B')
        self.detail_text.tag_config('time', font=('Arial', 10), foreground='#90A4AE')
        self.detail_text.tag_config('empty', font=('Microsoft YaHei UI', 11, 'italic'), foreground='#BDBDBD')

        self.detail_text.insert(tk.END, "📌 基础信息\n", 'h_section')
        basic_info = [
            ('用户名', user_data.get('username', 'N/A'), False),
            ('积分', str(user_data.get('points', 0)), True),
            ('等级', f"Lv.{user_data.get('level', 1)}", True),
            ('创建时间', self.format_timestamp(user_data.get('created_at', 0)), False, True),
            ('最后登录', self.format_timestamp(user_data.get('last_login', 0)), False, True),
        ]
        for item in basic_info:
            label, val, is_bold = item[0], item[1], item[2]
            is_time = len(item) > 3 and item[3]
            self.detail_text.insert(tk.END, f"{label}：", 'key')
            if is_time: self.detail_text.insert(tk.END, f"{val}\n", 'time')
            elif is_bold: self.detail_text.insert(tk.END, f"{val}\n", 'val_bold')
            else: self.detail_text.insert(tk.END, f"{val}\n", 'val')

        self.detail_text.insert(tk.END, "\n" + "- "*40 + "\n", 'dashed_line')
        self.detail_text.insert(tk.END, "📊 统计数据\n", 'h_section')
        stats = [('总场次', f"{user_data.get('total_games', 0)} 场"), ('通关数', f"{user_data.get('completed_games', 0)} 次"), ('总时长', f"{user_data.get('total_time', 0)} 秒"), ('连续登录', f"{user_data.get('consecutive_days', 0)} 天")]
        for k, v in stats:
            self.detail_text.insert(tk.END, f"{k}：", 'key'); self.detail_text.insert(tk.END, f"{v}\n", 'val_bold')

        self.detail_text.insert(tk.END, "\n" + "- "*40 + "\n", 'dashed_line')
        self.detail_text.insert(tk.END, "🎒 成就与道具\n", 'h_section')
        achievements = user_data.get('achievements', [])
        items = user_data.get('items', {})
        if not achievements and not items: self.detail_text.insert(tk.END, "暂无数据\n", 'empty')
        else:
            if achievements:
                self.detail_text.insert(tk.END, f"已解锁成就 ({len(achievements)}):\n", 'key')
                ach_str = "、".join(achievements[:5]) + (" 等..." if len(achievements) > 5 else "")
                self.detail_text.insert(tk.END, f"{ach_str}\n", 'val')
            if items:
                self.detail_text.insert(tk.END, f"道具库存:\n", 'key')
                for k, v in items.items():
                    self.detail_text.insert(tk.END, f" • {k}: ", 'val'); self.detail_text.insert(tk.END, f"{v}\n", 'val_bold')

        self.detail_text.config(state='disabled')
        
    def format_timestamp(self, timestamp):
        if not timestamp: return "N/A"
        try:
            import datetime
            return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
        except: return str(timestamp)
            
    # --- 修复后的重置密码逻辑 ---
    def reset_user_password(self):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        username = self.user_listbox.get(selection[0])
        
        # 保护管理员账号不被修改
        if username.lower() in ["root", "admin"]:
            messagebox.showwarning("警告", "不能重置管理员账户密码")
            return
            
        new_password = simpledialog.askstring("重置密码", f"请输入 {username} 的新密码:", parent=self.window)
        if new_password is None: return
        if not new_password:
            messagebox.showwarning("警告", "密码不能为空")
            return
            
        try:
            # 1. 修改内存数据
            self.users_data[username]['password'] = new_password
            
            # 2. 保存到文件
            save_players(self.users_data)
            
            messagebox.showinfo("成功", f"用户 {username} 的密码已重置")
            self.display_user_details(username) # 刷新详情显示
        except Exception as e:
            messagebox.showerror("错误", f"重置密码失败: {str(e)}")
            
    def export_user_data(self):
        try:
            file_format = self.export_format.get()
            ext = ".json" if file_format == "json" else ".csv"
            ft = [("JSON files", "*.json")] if file_format == "json" else [("CSV files", "*.csv")]
            
            file_path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=ft + [("All files", "*.*")])
            if not file_path: return
                
            if file_format == "json":
                self.export_to_json(file_path)
            else:
                self.export_to_csv(file_path)
            
            self.export_status_label.config(text=f"数据已导出到: {file_path}", fg='#2E7D32')
            messagebox.showinfo("成功", "数据导出成功")
        except Exception as e:
            self.export_status_label.config(text=f"导出失败: {str(e)}", fg='#C62828')
            messagebox.showerror("错误", f"数据导出失败: {str(e)}")
            
    def export_to_json(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.users_data, f, indent=2, ensure_ascii=False)
            
    def export_to_csv(self, file_path):
        import csv
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['用户名', '密码', '积分', '等级', '总获得积分'])
            for username, user_data in self.users_data.items():
                writer.writerow([
                    user_data.get('username', ''),
                    user_data.get('password', ''),
                    user_data.get('points', 0),
                    user_data.get('level', 1),
                    user_data.get('total_points_earned', 0)
                ])

    def show(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = AdminWindow()
    app.show()