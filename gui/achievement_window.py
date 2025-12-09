"""
成就窗口 - 集成 Trie 树搜索版 (修复搜索框显示问题)
"""

import tkinter as tk
from config import UIConfig, AchievementConfig
# 引入 Trie
from data_structures.trie import Trie

# --- 局部绘图辅助函数 (避免导入错误) ---
def draw_rounded_rect(canvas, x, y, w, h, r, fill, outline="", width=0):
    canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline=outline, width=width)
    canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline=outline, width=width)
    canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline=outline, width=width)
    canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline=outline, width=width)
    canvas.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline=outline, width=width)
    canvas.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline=outline, width=width)

def draw_clean_border(canvas, x, y, w, h, r, color, width=2):
    canvas.create_line(x+r, y, x+w-r, y, fill=color, width=width)
    canvas.create_line(x+r, y+h, x+w-r, y+h, fill=color, width=width)
    canvas.create_line(x, y+r, x, y+h-r, fill=color, width=width)
    canvas.create_line(x+w, y+r, x+w, y+h-r, fill=color, width=width)
    canvas.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, style=tk.ARC, outline=color, width=width)
    canvas.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, style=tk.ARC, outline=color, width=width)
    canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, style=tk.ARC, outline=color, width=width)
    canvas.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, style=tk.ARC, outline=color, width=width)

class AchievementWindow:
    def __init__(self, parent, player):
        self.parent = parent
        self.player = player
        self.window = tk.Toplevel(parent)
        self.window.title("游戏成就")
        self.window.geometry("1000x650") # 加宽窗口，确保一行能放下
        self.window.config(bg=UIConfig.COLORS['primary'])
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.current_category = '全部'
        self.search_query = ""
        
        # === 1. 初始化 Trie 并构建索引 ===
        self.trie = Trie()
        self._build_trie_index()
        
        self._create_ui()
        self._refresh_tags()
        self._render_achievements_list()
        
    def _build_trie_index(self):
        """将所有成就名称和描述关键词插入 Trie"""
        defs = getattr(AchievementConfig, 'ACHIEVEMENTS', [])
        for ach in defs:
            # 插入名字
            self.trie.insert(ach.get('name', ''), ach)
            # 也可以插入 ID 以支持搜 ID
            self.trie.insert(ach.get('id', ''), ach)

    def _create_ui(self):
        # 1. 标题区域
        title_frame = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        title_frame.pack(fill=tk.X, pady=15)
        tk.Label(title_frame, text="🏆 游戏成就", font=('Arial Rounded MT Bold', 24, 'bold'),
                 fg='white', bg=UIConfig.COLORS['primary']).pack()
        
        # 2. 筛选与搜索控制栏 (Container)
        control_container = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        control_container.pack(fill=tk.X, pady=(0, 15), padx=40)
        
        # === 关键修改：先创建并 Pack 右侧搜索框，确保它优先占据空间 ===
        
        # 2.1 右侧：搜索框 (样式复刻标签，但更长)
        # 注意：pack side=RIGHT 必须写在 side=LEFT 之前，或者保证空间足够
        self._create_styled_search_box(control_container)
        
        # 2.2 左侧：分类标签容器
        self.tag_frame = tk.Frame(control_container, bg=UIConfig.COLORS['primary'])
        self.tag_frame.pack(side=tk.LEFT, fill=tk.X)
        
        # 3. 列表区域
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

    def _create_styled_search_box(self, parent):
        """创建样式与标签一致但更长的搜索框"""
        # 尺寸定义
        w, h = 220, 32
        bg_color = 'white'
        
        # 容器 Canvas - Pack 到右侧
        search_canvas = tk.Canvas(parent, width=w, height=h, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        search_canvas.pack(side=tk.RIGHT)
        
        # 绘制圆角胶囊背景
        draw_rounded_rect(search_canvas, 0, 0, w, h, 16, fill=bg_color)
        
        # 绘制搜索图标
        search_canvas.create_text(20, h/2, text="🔍", font=('Segoe UI Emoji', 12), fill='#90A4AE')
        
        # 嵌入 Entry 控件
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        
        entry = tk.Entry(search_canvas, textvariable=self.search_var, 
                         bd=0, bg=bg_color, fg='#546E7A',
                         font=('Arial Rounded MT Bold', 11), width=18)
        
        # 将 Entry 放置在 Canvas 中央偏右
        search_canvas.create_window(w/2 + 10, h/2, window=entry, width=w-50, height=20)

    def _on_search_change(self, *args):
        query = self.search_var.get().strip()
        self.search_query = query
        self._render_achievements_list()

    def _refresh_tags(self):
        for w in self.tag_frame.winfo_children(): w.destroy()
        categories = sorted(list({a.get('category','其他') for a in getattr(AchievementConfig, 'ACHIEVEMENTS', []) if not a.get('hidden')}))
        categories = ['全部'] + categories
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
        for w in self.ach_scrollable.winfo_children(): w.destroy()
        
        # === 核心逻辑：结合分类筛选 + Trie 搜索 ===
        
        # 第一步：获取基础列表（根据搜索框）
        if self.search_query:
            # 使用 Trie 进行前缀搜索
            base_items = self.trie.search_prefix(self.search_query)
            # 去重
            seen_ids = set()
            unique_items = []
            for item in base_items:
                if item['id'] not in seen_ids:
                    unique_items.append(item)
                    seen_ids.add(item['id'])
            items = unique_items
        else:
            items = getattr(AchievementConfig, 'ACHIEVEMENTS', [])

        # 第二步：根据分类筛选
        if self.current_category != '全部':
            items = [a for a in items if a.get('category') == self.current_category]
            
        # 排序
        items.sort(key=lambda a: (a.get('id') not in self.player.achievements, -(a.get('reward', 0))))

        row, col = 0, 0
        for achievement in items:
            card_w, card_h = 250, 160
            card = tk.Canvas(self.ach_scrollable, bg=UIConfig.COLORS['primary'], width=card_w, height=card_h, highlightthickness=0)
            card.grid(row=row, column=col, padx=15, pady=15)
            
            unlocked = achievement.get('id') in self.player.achievements
            
            if unlocked:
                draw_rounded_rect(card, 2, 2, card_w-4, card_h-4, 18, fill='white')
                draw_clean_border(card, 2, 2, card_w-4, card_h-4, 18, color="#FFD54F", width=3)
            else:
                draw_rounded_rect(card, 4, 4, card_w-8, card_h-8, 18, fill='#F5F5F5')
            
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
        aid = achievement.get('id')
        player = self.player
        records = player.get_all_records()
        
        if aid == 'normal_master':
            cur = sum(1 for r in records if r.get('mode')=='normal' and r.get('completed'))
            return cur, 10
        if aid == 'ultimate_conqueror':
            cur = sum(1 for r in records if r.get('mode') in ('ultimate','ultimate_shuffle') and r.get('completed'))
            return cur, 5
        if aid == 'persistent_50':
            return len(records), 50
        if aid == 'item_user_10':
            cur = 0
            for r in records:
                iu = r.get('items_used', {})
                cur += sum(iu.values()) if isinstance(iu, dict) else 0
            return cur, 10
        if aid == 'no_item_10':
            cur = sum(1 for r in records if r.get('completed') and all((r.get('items_used',{}).get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo']))
            return cur, 10
        if aid == 'login_streak_3':
            return player.consecutive_days, 3
        if aid == 'login_streak_7':
            return player.consecutive_days, 7
        return 0, 0

class CategoryTag(tk.Canvas):
    def __init__(self, master, text, selected=False, command=None, **kwargs):
        super().__init__(master, width=80, height=30, highlightthickness=0, bg=UIConfig.COLORS['primary'], **kwargs)
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
        draw_rounded_rect(self, 0, 0, w, h, 15, self.bg_color)
        font = ('Arial Rounded MT Bold', 10, 'bold')
        self.create_text(w/2, h/2, text=self.text, font=font, fill=self.text_color)
    def _on_click(self, event):
        if self.command: self.command(self.text)
    def _on_enter(self, event):
        if not self.selected:
            self.bg_color = '#CFD8DC'
            self._draw()
    def _on_leave(self, event):
        if not self.selected:
            self.bg_color = '#B0BEC5'
            self._draw()
