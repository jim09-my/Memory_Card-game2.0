import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Any
from config import DataConfig
from managers.data_manager import load_players
from core.player import Player


class AdminWindow:
    def __init__(self, master=None):
        # 创建新窗口或使用提供的master
        if master:
            self.window = tk.Toplevel(master)
            self.window.title("管理员面板")
        else:
            self.window = tk.Tk()
            self.window.title("管理员面板")
        
        self.window.geometry("1000x700")
        self.window.configure(bg='#E0F7FA')
        
        # 设置窗口居中
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"1000x700+{x}+{y}")
        
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        # 标题
        title_label = tk.Label(
            self.window,
            text="管理员面板",
            font=('Arial Rounded MT Bold', 24, 'bold'),
            bg='#E0F7FA',
            fg='#2896A0'
        )
        title_label.pack(pady=20)
        
        # 创建选项卡
        tab_control = ttk.Notebook(self.window)
        
        # 用户管理选项卡
        self.user_tab = ttk.Frame(tab_control)
        tab_control.add(self.user_tab, text='用户管理')
        
        # 数据导出选项卡
        self.export_tab = ttk.Frame(tab_control)
        tab_control.add(self.export_tab, text='数据导出')
        
        tab_control.pack(expand=1, fill="both", padx=20, pady=10)
        
        # 用户管理界面
        self.setup_user_management_tab()
        
        # 数据导出界面
        self.setup_export_tab()
        
    def setup_user_management_tab(self):
        # 创建框架用于放置用户列表和详细信息
        main_frame = tk.Frame(self.user_tab, bg='#E0F7FA')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧用户列表
        left_frame = tk.Frame(main_frame, bg='#E0F7FA')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 用户列表标签
        list_label = tk.Label(
            left_frame,
            text="用户列表",
            font=('Arial Rounded MT Bold', 16, 'bold'),
            bg='#E0F7FA',
            fg='#2896A0'
        )
        list_label.pack(pady=(0, 10))
        
        # 用户列表框
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.user_listbox = tk.Listbox(
            list_frame,
            width=30,
            height=20,
            font=('Arial', 12),
            yscrollcommand=scrollbar.set
        )
        self.user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.user_listbox.yview)
        
        self.user_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        # 右侧详细信息
        right_frame = tk.Frame(main_frame, bg='#E0F7FA')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 详细信息标签
        detail_label = tk.Label(
            right_frame,
            text="用户详细信息",
            font=('Arial Rounded MT Bold', 16, 'bold'),
            bg='#E0F7FA',
            fg='#2896A0'
        )
        detail_label.pack(pady=(0, 10))
        
        # 详细信息文本框
        detail_frame = tk.Frame(right_frame)
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        detail_scrollbar = tk.Scrollbar(detail_frame)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(
            detail_frame,
            font=('Arial', 11),
            wrap=tk.WORD,
            yscrollcommand=detail_scrollbar.set
        )
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.config(command=self.detail_text.yview)
        
        # 操作按钮
        button_frame = tk.Frame(right_frame, bg='#E0F7FA')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        reset_password_btn = tk.Button(
            button_frame,
            text="重置密码",
            font=('Arial Rounded MT Bold', 12),
            bg='#2896A0',
            fg='white',
            command=self.reset_user_password
        )
        reset_password_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(
            button_frame,
            text="刷新列表",
            font=('Arial Rounded MT Bold', 12),
            bg='#1E7882',
            fg='white',
            command=self.load_users
        )
        refresh_btn.pack(side=tk.LEFT)
        
    def setup_export_tab(self):
        # 导出界面
        export_frame = tk.Frame(self.export_tab, bg='#E0F7FA')
        export_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        export_label = tk.Label(
            export_frame,
            text="数据导出",
            font=('Arial Rounded MT Bold', 18, 'bold'),
            bg='#E0F7FA',
            fg='#2896A0'
        )
        export_label.pack(pady=(0, 30))
        
        # 导出选项
        options_frame = tk.Frame(export_frame, bg='#E0F7FA')
        options_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            options_frame,
            text="选择导出格式:",
            font=('Arial Rounded MT Bold', 14),
            bg='#E0F7FA',
            fg='#263238'
        ).pack(anchor=tk.W)
        
        self.export_format = tk.StringVar(value="json")
        format_frame = tk.Frame(options_frame, bg='#E0F7FA')
        format_frame.pack(fill=tk.X, pady=10)
        
        tk.Radiobutton(
            format_frame,
            text="JSON格式",
            variable=self.export_format,
            value="json",
            font=('Arial', 12),
            bg='#E0F7FA'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Radiobutton(
            format_frame,
            text="CSV格式",
            variable=self.export_format,
            value="csv",
            font=('Arial', 12),
            bg='#E0F7FA'
        ).pack(side=tk.LEFT)
        
        # 导出按钮
        export_btn = tk.Button(
            export_frame,
            text="导出所有用户数据",
            font=('Arial Rounded MT Bold', 14),
            bg='#2896A0',
            fg='white',
            command=self.export_user_data,
            height=2
        )
        export_btn.pack(pady=30)
        
        # 导出状态标签
        self.export_status_label = tk.Label(
            export_frame,
            text="",
            font=('Arial', 12),
            bg='#E0F7FA',
            fg='#2896A0'
        )
        self.export_status_label.pack()
        
    def load_users(self):
        """加载所有用户信息"""
        try:
            self.users_data = load_players()
            self.user_listbox.delete(0, tk.END)
            
            for username in self.users_data:
                self.user_listbox.insert(tk.END, username)
                
            # 如果有用户，选中第一个
            if self.user_listbox.size() > 0:
                self.user_listbox.selection_set(0)
                self.display_user_details(self.user_listbox.get(0))
        except Exception as e:
            messagebox.showerror("错误", f"加载用户数据失败: {str(e)}")
            
    def on_user_select(self, event):
        """当用户选择一个用户时显示详细信息"""
        selection = self.user_listbox.curselection()
        if selection:
            username = self.user_listbox.get(selection[0])
            self.display_user_details(username)
            
    def display_user_details(self, username):
        """显示用户详细信息"""
        if username not in self.users_data:
            return
            
        user_data = self.users_data[username]
        self.detail_text.delete(1.0, tk.END)
        
        # 格式化显示用户信息
        details = f"""用户名: {user_data.get('username', 'N/A')}
邮箱: {user_data.get('email', 'N/A')}
密码: {user_data.get('password', 'N/A')}
积分: {user_data.get('points', 0)}
等级: {user_data.get('level', 1)}
总获得积分: {user_data.get('total_points_earned', 0)}
总游戏次数: {user_data.get('total_games', 0)}
完成游戏次数: {user_data.get('completed_games', 0)}
总移动次数: {user_data.get('total_moves', 0)}
总游戏时间: {user_data.get('total_time', 0)}

创建时间: {self.format_timestamp(user_data.get('created_at', 0))}
最后登录: {self.format_timestamp(user_data.get('last_login', 0))}
连续登录天数: {user_data.get('consecutive_days', 0)}

成就数量: {len(user_data.get('achievements', []))}
道具数量: {len(user_data.get('items', {}))}
游戏记录数量: {len(user_data.get('game_records', []))}

--- 成就列表 ---
"""
        
        for achievement in user_data.get('achievements', []):
            details += f"- {achievement}\n"
            
        details += "\n--- 道具列表 ---\n"
        for item_id, quantity in user_data.get('items', {}).items():
            details += f"- {item_id}: {quantity}\n"
            
        details += "\n--- 最佳记录 ---\n"
        details += "普通模式:\n"
        for record in user_data.get('best_records_normal', []):
            details += f"  - 时间: {record[0]}s\n"
            
        details += "终极模式:\n"
        for record in user_data.get('best_records_ultimate', []):
            details += f"  - 时间: {record[0]}s\n"
            
        details += "\n--- 游戏记录 ---\n"
        for i, record in enumerate(user_data.get('game_records', [])):
            if i >= 10:  # 只显示前10条记录
                details += "... (更多记录)\n"
                break
            mode = record.get('mode', '未知')
            time_used = record.get('time_used', 'N/A')
            moves = record.get('moves', 'N/A')
            completed = "完成" if record.get('completed', False) else "未完成"
            details += f"- 模式: {mode}, 时间: {time_used}s, 步数: {moves}, 状态: {completed}\n"
            
        self.detail_text.insert(tk.END, details)
        
    def format_timestamp(self, timestamp):
        """格式化时间戳"""
        if not timestamp:
            return "N/A"
        try:
            import datetime
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(timestamp)
            
    def reset_user_password(self):
        """重置用户密码"""
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
            
        username = self.user_listbox.get(selection[0])
        if username.lower() == "root":
            messagebox.showwarning("警告", "不能重置管理员账户密码")
            return
            
        # 弹出输入框让用户输入新密码
        new_password = tk.simpledialog.askstring(
            "重置密码",
            f"请输入 {username} 的新密码:",
            parent=self.window
        )
        
        if new_password is None:  # 用户取消
            return
            
        if not new_password:
            messagebox.showwarning("警告", "密码不能为空")
            return
            
        try:
            # 更新用户密码
            self.users_data[username]['password'] = new_password
            
            # 保存到文件
            from managers.data_manager import save_players
            save_players(self.users_data)
            
            messagebox.showinfo("成功", f"用户 {username} 的密码已重置")
            
            # 刷新显示
            self.display_user_details(username)
        except Exception as e:
            messagebox.showerror("错误", f"重置密码失败: {str(e)}")
            
    def export_user_data(self):
        """导出用户数据"""
        try:
            # 让用户选择保存位置
            file_format = self.export_format.get()
            if file_format == "json":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )
            else:  # CSV
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
                
            if not file_path:
                return
                
            if file_format == "json":
                self.export_to_json(file_path)
            else:
                self.export_to_csv(file_path)
                
            self.export_status_label.config(text=f"数据已导出到: {file_path}")
            messagebox.showinfo("成功", "数据导出成功")
        except Exception as e:
            self.export_status_label.config(text=f"导出失败: {str(e)}")
            messagebox.showerror("错误", f"数据导出失败: {str(e)}")
            
    def export_to_json(self, file_path):
        """导出为JSON格式"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.users_data, f, indent=2, ensure_ascii=False)
            
    def export_to_csv(self, file_path):
        """导出为CSV格式"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                '用户名', '邮箱', '密码', '积分', '等级', '总获得积分',
                '总游戏次数', '完成游戏次数', '总移动次数', '总游戏时间',
                '创建时间', '最后登录', '连续登录天数', '成就数量', '道具数量'
            ])
            
            # 写入用户数据
            for username, user_data in self.users_data.items():
                writer.writerow([
                    user_data.get('username', ''),
                    user_data.get('email', ''),
                    user_data.get('password', ''),
                    user_data.get('points', 0),
                    user_data.get('level', 1),
                    user_data.get('total_points_earned', 0),
                    user_data.get('total_games', 0),
                    user_data.get('completed_games', 0),
                    user_data.get('total_moves', 0),
                    user_data.get('total_time', 0),
                    self.format_timestamp(user_data.get('created_at', 0)),
                    self.format_timestamp(user_data.get('last_login', 0)),
                    user_data.get('consecutive_days', 0),
                    len(user_data.get('achievements', [])),
                    len(user_data.get('items', {}))
                ])

    def show(self):
        """显示窗口"""
        self.window.mainloop()


if __name__ == "__main__":
    # 测试代码
    app = AdminWindow()
    app.show()