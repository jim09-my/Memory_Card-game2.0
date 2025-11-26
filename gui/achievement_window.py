"""
成就窗口
展示玩家已解锁和未解锁的成就
"""

import tkinter as tk
from tkinter import messagebox
from config import UIConfig, AchievementConfig
from gui.widgets import draw_rounded_rect, draw_clean_border
from datetime import datetime


class AchievementWindow:
    def __init__(self, parent, player):
        self.parent = parent
        self.player = player
        self.window = tk.Toplevel(parent)
        self.window.title("游戏成就")
        self.window.geometry("900x600")
        self.window.config(bg=UIConfig.COLORS['primary'])
        self.window.resizable(False, False)
        
        # 居中显示
        self.window.transient(parent)
        self.window.grab_set()
        
        # 当前选中的分类
        self.current_category = '全部'
        
        # 创建UI
        self._create_ui()
        
        # 初始渲染
        self._refresh_tags()
        self._render_achievements_list()
        
    def _create_ui(self):
        # 标题
        title_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        title_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(title_frame, text="🏆 游戏成就", font=('Arial Rounded MT Bold', 24, 'bold'),
                 fg='white', bg=UIConfig.COLORS['primary']).pack()
                 
        # 分类标签区域
        self.tag_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        self.tag_frame.pack(fill=tk.X, pady=(0, 15), padx=40)
        
        # 成就列表区域
        list_container = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)
        
        self.ach_canvas = tk.Canvas(list_container, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient='vertical', command=self.ach_canvas.yview)
        self.ach_scrollable = tk.Frame(self.ach_canvas, bg=UIConfig.COLORS['primary'])
        
        self.ach_canvas.bind('<Configure>', lambda e: self.ach_canvas.itemconfig('inner', width=e.width))
        self.ach_scrollable.bind('<Configure>', lambda e: self.ach_canvas.configure(scrollregion=self.ach_canvas.bbox('all')))
        self.ach_canvas.create_window((0,0), window=self.ach_scrollable, anchor='nw', tags='inner')
        self.ach_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.ach_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def _refresh_tags(self):
        for w in self.tag_frame.winfo_children(): 
            w.destroy()
        
        # 获取所有分类
        categories = sorted(list({a.get('category','其他') for a in getattr(AchievementConfig, 'ACHIEVEMENTS', []) if not a.get('hidden')}))
        categories = ['全部'] + categories
        
        # 创建分类标签
        for category in categories:
            is_selected = (category == self.current_category)
            tag = CategoryTag(self.tag_frame, text=category, selected=is_selected, 
                              command=lambda cat=category: self._on_tag_click(cat))
            tag.pack(side=tk.LEFT, padx=6)
            
    def _on_tag_click(self, category):
        if self.current_category != category:
            self.current_category = category
            self._refresh_tags()
            self._render_achievements_list()
            
    def _render_achievements_list(self):
        # 清空现有内容
        for w in self.ach_scrollable.winfo_children(): 
            w.destroy()
        
        # 获取成就定义
        defs = getattr(AchievementConfig, 'ACHIEVEMENTS', [])
        
        # 根据分类筛选
        if self.current_category == '全部':
            items = defs
        else:
            items = [a for a in defs if a.get('category') == self.current_category]
            
        # 排序：已解锁的在前，按奖励分值降序
        items.sort(key=lambda a: (a.get('id') not in self.player.achievements, -(a.get('reward', 0))))

        # 创建网格布局
        row, col = 0, 0
        for achievement in items:
            card_w, card_h = 250, 160
            card = tk.Canvas(self.ach_scrollable, bg=UIConfig.COLORS['primary'], width=card_w, height=card_h, highlightthickness=0)
            card.grid(row=row, column=col, padx=15, pady=15)
            
            unlocked = achievement.get('id') in self.player.achievements
            
            # 绘制卡片背景
            if unlocked:
                # 已解锁：白色背景 + 金色边框
                draw_rounded_rect(card, 2, 2, card_w-4, card_h-4, 18, fill='white')
                draw_clean_border(card, 2, 2, card_w-4, card_h-4, 18, color="#FFD54F", width=3)
            else:
                # 未解锁：灰色背景
                draw_rounded_rect(card, 4, 4, card_w-8, card_h-8, 18, fill='#F5F5F5')
            
            # 绘制内容
            cx = card_w / 2
            icon = achievement.get('icon', '🏅')
            card.create_text(cx, 40, text=icon, font=('Segoe UI Emoji', 28))
            
            name_col = '#37474F' if unlocked else '#9E9E9E'
            card.create_text(cx, 75, text=achievement.get('name'), font=('Arial Rounded MT Bold', 12, 'bold'), fill=name_col)
            
            desc_col = '#78909C' if unlocked else '#BDBDBD'
            desc = achievement.get('description', '')
            card.create_text(cx, 98, text=desc, font=('Arial', 9), fill=desc_col, width=220, justify='center')
            
            if unlocked:
                card.create_text(cx, 135, text="✨ 已解锁 ✨", font=('Arial', 10, 'bold'), fill='#FFA000')
            else:
                # 显示进度条
                cur, target = self._get_achievement_progress(achievement)
                if target > 0:
                    prog_text = f"进度: {cur}/{target}"
                    bar_w, bar_h = 120, 6
                    bx, by = cx - bar_w/2, 130
                    card.create_rectangle(bx, by, bx+bar_w, by+bar_h, fill='#E0E0E0', outline="")
                    pct = min(1.0, cur / target)
                    if pct > 0:
                        card.create_rectangle(bx, by, bx + bar_w*pct, by+bar_h, fill='#90A4AE', outline="")
                    card.create_text(cx, 145, text=prog_text, font=('Arial', 9), fill='#9E9E9E')
                else:
                    card.create_text(cx, 135, text="未解锁", font=('Arial', 9), fill='#BDBDBD')

            col += 1
            if col >= 3: 
                col = 0
                row += 1
                
    def _get_achievement_progress(self, achievement):
        """获取成就进度"""
        aid = achievement.get('id')
        player = self.player
        
        # 根据成就ID计算进度
        if aid == 'normal_master':
            cur = sum(1 for r in player.game_records if r.get('mode')=='normal' and r.get('completed'))
            return cur, 10
        if aid == 'ultimate_conqueror':
            cur = sum(1 for r in player.game_records if r.get('mode')=='ultimate' and r.get('completed'))
            return cur, 5
        if aid == 'persistent_50':
            return len(player.game_records), 50
        if aid == 'item_user_10':
            cur = 0
            for r in player.game_records:
                iu = r.get('items_used', {})
                cur += sum(iu.values()) if isinstance(iu, dict) else 0
            return cur, 10
        if aid == 'no_item_10':
            cur = sum(1 for r in player.game_records if r.get('completed') and all((r.get('items_used',{}).get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo']))
            return cur, 10
        if aid == 'login_streak_3':
            return player.consecutive_days, 3
        if aid == 'login_streak_7':
            return player.consecutive_days, 7
            
        return 0, 0


class CategoryTag(tk.Canvas):
    """分类标签按钮"""
    def __init__(self, master, text, selected=False, command=None, **kwargs):
        super().__init__(master, width=80, height=30, highlightthickness=0, **kwargs)
        self.text = text
        self.selected = selected
        self.command = command
        self.bg_color = '#FFD54F' if selected else '#B0BEC5'
        self.text_color = '#37474F' if selected else '#78909C'
        
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        self._draw()
        
    def _draw(self):
        self.delete('all')
        w, h = 80, 30
        r = 15
        
        # 绘制圆角矩形
        draw_rounded_rect(self, 0, 0, w, h, r, self.bg_color)
        
        # 绘制文字
        font = ('Arial Rounded MT Bold', 10, 'bold')
        self.create_text(w/2, h/2, text=self.text, font=font, fill=self.text_color)
        
    def _on_click(self, event):
        if self.command:
            self.command(self.text)
            
    def _on_enter(self, event):
        if not self.selected:
            self.bg_color = '#CFD8DC'
            self._draw()
            
    def _on_leave(self, event):
        if not self.selected:
            self.bg_color = '#B0BEC5'
            self._draw()