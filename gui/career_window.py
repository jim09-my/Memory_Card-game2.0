import tkinter as tk
import math
from datetime import datetime
from config import UIConfig, AchievementConfig
from managers.data_manager import load_records
# === 引入数据结构 ===
from data_structures.binary_tree import Leaderboard  # <--- 新增：使用 AVL 树进行排序

# --- 绘图辅助函数 (保持不变) ---
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

def draw_shadow_card(canvas, x, y, w, h, r, bg_color, shadow_color='#CFD8DC', offset=4):
    draw_rounded_rect(canvas, x+offset, y+offset, w, h, r, shadow_color)
    draw_rounded_rect(canvas, x, y, w, h, r, bg_color)

# --- 组件类 (保持不变) ---
class CandyTabButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=130, height=50, theme='yellow', active=False):
        super().__init__(master, width=width, height=height, 
                         bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.text = text
        self._command = command
        self.width = width
        self.height = height
        self.theme = theme
        self._active_state = active
        
        self.colors = {
            'yellow': ('#FFD54F', '#EF6C00'), 
            'blue':   ('#4FC3F7', '#0277BD'),
            'green':  ('#A5D6A7', '#2E7D32'),
        }
        
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', lambda e: self.config(cursor='hand2'))
        self.bind('<Leave>', lambda e: self.config(cursor=''))
        self._draw()

    def set_active(self, is_active):
        self._active_state = is_active
        self._draw()

    def _draw(self):
        self.delete('all')
        w, h = self.width, self.height
        theme_cols = self.colors.get(self.theme, self.colors['yellow'])
        body_col, shadow_col = theme_cols
        
        if self._active_state:
             if self.theme == 'yellow': body_col = '#FFF59D'
             elif self.theme == 'blue': body_col = '#B3E5FC'
             elif self.theme == 'green': body_col = '#C8E6C9'

        shadow_h = 6
        offset_y = 4 if not self._active_state else 6
        r = (h - shadow_h) / 2
        
        if not self._active_state:
            self._draw_capsule(0, shadow_h, w, h, r, shadow_col)
        
        draw_y = 0 if not self._active_state else 4
        self._draw_capsule(0, draw_y, w, h - shadow_h + draw_y, r, body_col)
        
        font = ('Arial Rounded MT Bold', 12, 'bold')
        text_col = 'white'
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
             self.create_text(w/2+dx, (h-shadow_h)/2 + draw_y + dy, text=self.text, font=font, fill=shadow_col)
        self.create_text(w/2, (h-shadow_h)/2 + draw_y, text=self.text, font=font, fill=text_col)

    def _draw_capsule(self, x1, y1, x2, y2, r, fill):
        canvas = self
        canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=180, fill=fill, outline="")
        canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=270, extent=180, fill=fill, outline="")
        canvas.create_rectangle(x1+r, y1, x2-r, y2+1, fill=fill, outline="")

    def _on_click(self, e):
        if self._command: self._command()

class CategoryTag(tk.Canvas):
    def __init__(self, master, text, selected=False, command=None):
        super().__init__(master, width=80, height=32, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        self.text = text
        self.selected = selected
        self.command = command
        self.bind('<Button-1>', lambda e: command(text) if command else None)
        self.bind('<Enter>', lambda e: self.config(cursor='hand2'))
        self._draw()

    def set_selected(self, selected):
        self.selected = selected
        self._draw()

    def _draw(self):
        self.delete('all')
        w, h = 80, 32
        bg_col = '#00796B' if self.selected else '#E0E0E0'
        fg_col = 'white' if self.selected else '#757575'
        draw_rounded_rect(self, 0, 0, w, h, 16, bg_col)
        self.create_text(w/2, h/2, text=self.text, fill=fg_col, font=('Arial', 10, 'bold' if self.selected else 'normal'))


class CareerWindow:
    def __init__(self, master, player):
        self.master = master
        self.player = player
        self.window = tk.Toplevel(master)
        self.window.title("游戏生涯")
        self.window.geometry("900x750")
        self.window.config(bg=UIConfig.COLORS['primary'])
        self._center_window()
        self.window.transient(master)
        self.window.grab_set()
        self.window.resizable(False, False)

        self._filtered_records = []
        self.tab_buttons = {}
        self.ach_tags = {} 
        self.current_ach_cat = "全部"

        self._create_header()
        self._create_nav_tabs()
        self._create_pages()
        self._show_page('overview')

    def _center_window(self):
        self.window.update_idletasks()
        w, h = 900, 750
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _create_header(self):
        canvas = tk.Canvas(self.window, bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        canvas.place(x=0, y=0, relwidth=1, height=110)
        
        center_x = 450
        y_pos = 55
        text = "我的生涯"
        font = ("Arial Rounded MT Bold", 36, "bold")
        
        for dx, dy in [(-2,2)]:
            canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill='#F9A825')
        canvas.create_text(center_x, y_pos, text=text, font=font, fill='white')

        btn = tk.Button(self.window, text="✖", command=self.window.destroy,
                        bg='#B2DFDB', fg='white', font=('Arial', 12, 'bold'),
                        relief=tk.FLAT, bd=0)
        btn.place(x=860, y=15, width=30, height=30)

    def _create_nav_tabs(self):
        bar = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        bar.place(x=0, y=100, relwidth=1, height=70)

        container = tk.Frame(bar, bg=UIConfig.COLORS['primary'])
        container.pack()

        self.tab_buttons['overview'] = CandyTabButton(container, "总览", command=lambda: self._show_page('overview'), theme='yellow')
        self.tab_buttons['records'] = CandyTabButton(container, "战绩", command=lambda: self._show_page('records'), theme='blue')
        self.tab_buttons['achievements'] = CandyTabButton(container, "成就", command=lambda: self._show_page('achievements'), theme='green')

        self.tab_buttons['overview'].pack(side=tk.LEFT, padx=20)
        self.tab_buttons['records'].pack(side=tk.LEFT, padx=20)
        self.tab_buttons['achievements'].pack(side=tk.LEFT, padx=20)

    def _create_pages(self):
        self.pages = {}
        container = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        container.place(x=0, y=180, relwidth=1, relheight=1)

        self.pages['overview'] = tk.Frame(container, bg=UIConfig.COLORS['primary'])
        self.pages['records'] = tk.Frame(container, bg=UIConfig.COLORS['primary'])
        self.pages['achievements'] = tk.Frame(container, bg=UIConfig.COLORS['primary'])

        self._build_overview(self.pages['overview'])
        self._build_records(self.pages['records'])
        self._build_achievements(self.pages['achievements'])

    def _show_page(self, key):
        for k, f in self.pages.items():
            f.place_forget()
        page = self.pages.get(key)
        if page:
            page.place(x=0, rely=0.02, relwidth=0.98, relheight=0.76)
        
        for k, btn in self.tab_buttons.items():
            btn.set_active(k == key)

    def _build_overview(self, parent):
        stats = self.player.get_statistics()
        
        bg = tk.Canvas(parent, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        bg.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        w, h = 820, 480
        bg.create_rectangle(0, 0, w, h, fill='white', outline="")
        
        content = tk.Frame(bg, bg='white')
        bg.create_window(w/2, h/2, window=content, width=w-40, height=h-40)
        
        tk.Label(content, text=f"✨ {stats['username']} 的数据概览 ✨", font=('Arial Rounded MT Bold', 18), 
                 fg='#546E7A', bg='white').pack(pady=(5, 20))
        
        grid = tk.Frame(content, bg='white')
        grid.pack()
        
        items = [
            ("💎", "现有积分", str(self.player.points), '#FFF8E1'),
            ("🌟", "累计积分", str(stats['total_points_earned']), '#FFF8E1'),
            ("🎮", "总局数", str(stats['total_games']), '#E1F5FE'),
            ("🏆", "通关数", str(stats['completed_games']), '#E1F5FE'),
            ("🔥", "胜率", f"{int(stats['win_rate'])}%", '#FFEBEE'),
            
            ("⚡", "普通最佳", self._fmt_time(stats['best_time_normal']), '#FFEBEE'),
            ("🚀", "终极最佳", self._fmt_time(stats['best_time_ultimate']), '#E0F2F1'),
            ("📆", "连续登录", f"{stats['consecutive_days']}天", '#E0F2F1'),
            ("🏅", "解锁成就", f"{stats['achievement_count']}", '#F3E5F5'),
            ("👣", "平均步数", f"{int(stats['average_moves'])}", '#F3E5F5')
        ]
        
        for i, (icon, label, val, color) in enumerate(items):
            r, c = i // 5, i % 5
            card_w, card_h = 130, 110
            card = tk.Canvas(grid, bg='white', width=card_w, height=card_h, highlightthickness=0)
            card.grid(row=r, column=c, padx=8, pady=12)
            
            draw_shadow_card(card, 2, 2, card_w-6, card_h-6, 15, color, shadow_color='#B0BEC5', offset=4)
            
            cx = card_w / 2
            card.create_text(cx, 35, text=icon, font=('Segoe UI Emoji', 26))
            card.create_text(cx, 68, text=label, font=('Arial', 9), fill='#78909C')
            card.create_text(cx, 88, text=val, font=('Arial Rounded MT Bold', 13), fill='#37474F')

    def _build_records(self, parent):
        list_container = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        self.records_canvas = tk.Canvas(list_container, bg=UIConfig.COLORS['primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient='vertical', command=self.records_canvas.yview)
        self.scrollable_records = tk.Frame(self.records_canvas, bg=UIConfig.COLORS['primary'])
        
        self.records_canvas.bind('<Configure>', lambda e: self.records_canvas.itemconfig('inner', width=e.width))
        self.scrollable_records.bind('<Configure>', lambda e: self.records_canvas.configure(scrollregion=self.records_canvas.bbox('all')))
        self.records_canvas.create_window((0,0), window=self.scrollable_records, anchor='nw', tags='inner')
        self.records_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.records_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self._apply_filters()

    def _apply_filters(self):
        # 1. 修复：调用 get_all_records() 获取列表，而不是直接访问 Queue
        raw_records = self.player.get_all_records()
        
        # 2. 应用高级数据结构：Leaderboard (AVL 树) 进行排序
        # 虽然列表只有50条，sort很快，但为了演示 AVL 树的应用：
        # 我们创建一个临时 Leaderboard，按时间戳将所有记录插入，然后按序读取
        
        leaderboard = Leaderboard(mode='time') # 这里的mode仅影响add_record时的key策略，我们手动指定
        
        # 将记录插入 AVL 树，Key 为时间戳 (取负实现降序，即最近的时间在前)
        for i, rec in enumerate(raw_records):
            # 为了防止时间戳完全相同导致覆盖，加一点微小偏移
            timestamp = rec.get('timestamp', 0)
            # AVL树默认中序遍历是升序。
            # 我们希望最近的时间(timestamp大)排在前面。
            # 所以我们用 -timestamp 作为key。
            key = -timestamp + (i * 0.00001) 
            leaderboard.add_record(str(i), key, real_record=rec)
            
        # 从 AVL 树中获取排序后的记录
        # get_all_records() 返回的是按 Key 升序排列的 list
        # Key 是 -timestamp，所以升序就是 timestamp 降序 (最近的在前)
        sorted_data = leaderboard.get_all_records()
        records = [item['real_record'] for item in sorted_data]
        
        for w in self.scrollable_records.winfo_children(): w.destroy()
        
        if not records:
            tk.Label(self.scrollable_records, text='暂无战绩', font=('Arial', 14), 
                     bg=UIConfig.COLORS['primary'], fg='#90A4AE').pack(pady=50)
            return
            
        for r in records:
            self._draw_record_capsule(self.scrollable_records, r)

    def _draw_record_capsule(self, parent, record):
        h = 75
        is_win = record.get('completed', False)
        mode = record.get('mode', 'normal')
        
        if is_win:
            if mode == 'normal':
                bg_col = '#DCEDC8' 
                status_icon = "🎉"
            else:
                bg_col = '#FFF59D'
                status_icon = "👑"
        else:
            bg_col = '#FFCDD2' 
            status_icon = "💨"
            
        row = tk.Canvas(parent, bg=UIConfig.COLORS['primary'], height=h, highlightthickness=0)
        row.pack(fill=tk.X, pady=6, padx=20)
        
        def _draw_bg(event):
            w = event.width
            row.delete('bg')
            r = 35
            draw_rounded_rect(row, 0, 0, w, 2*r+5, r, bg_col)
            row.tag_lower('bg')
            
            row.delete('content')
            
            # 1. 左
            row.create_text(40, 38, text=status_icon, font=('Segoe UI Emoji', 22), anchor='w', tags='content')
            mode_txt = "普通模式" if mode == 'normal' else "终极挑战"
            mode_fg = '#33691E' if is_win and mode=='normal' else ('#F57F17' if is_win else '#C62828')
            row.create_text(90, 38, text=mode_txt, font=('Arial Rounded MT Bold', 13), fill=mode_fg, anchor='w', tags='content')
            
            # 2. 中
            cx = w / 2
            date = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%m-%d %H:%M')
            time_s = self._fmt_time(record.get('time_used'))
            center_text = f"{date}   |   耗时 {time_s}"
            row.create_text(cx, 38, text=center_text, font=('Arial', 11), fill='#546E7A', anchor='center', tags='content')
            
            # 3. 右
            score = record.get('score', 0)
            reward = record.get('reward', 0)
            score_col = '#EF6C00' if score > 0 else '#9E9E9E'
            reward_col = UIConfig.COLORS.get('danger', '#FF5252') if reward > 0 else '#9E9E9E'
            row.create_text(w-40, 38, text=f"+{reward}分", font=('Arial Rounded MT Bold', 16), fill=reward_col, anchor='e', tags='content')
            row.create_text(w-150, 38, text=f"{score}分", font=('Arial Rounded MT Bold', 16), fill=score_col, anchor='e', tags='content')
            row.create_text(w-40, 58, text="奖励", font=('Arial', 9), fill='#78909C', anchor='e', tags='content')
            row.create_text(w-150, 58, text="得分", font=('Arial', 9), fill='#78909C', anchor='e', tags='content')

        row.bind('<Configure>', _draw_bg)

    def _build_achievements(self, parent):
        self.tag_frame = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
        self.tag_frame.pack(fill=tk.X, pady=(0, 15), padx=40)
        self._refresh_tags()

        list_container = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
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
        
        self._render_achievements_list()

    def _refresh_tags(self):
        for w in self.tag_frame.winfo_children(): w.destroy()
        
        cats = sorted(list({a.get('category','其他') for a in getattr(AchievementConfig, 'ACHIEVEMENTS', []) if not a.get('hidden')}))
        cats = ['全部'] + cats
        
        for cat in cats:
            is_selected = (cat == self.current_ach_cat)
            tag = CategoryTag(self.tag_frame, text=cat, selected=is_selected, 
                              command=self._on_tag_click)
            tag.pack(side=tk.LEFT, padx=6)

    def _on_tag_click(self, cat):
        if self.current_ach_cat != cat:
            self.current_ach_cat = cat
            self._refresh_tags()
            self._render_achievements_list()

    def _render_achievements_list(self):
        for w in self.ach_scrollable.winfo_children(): w.destroy()
        
        defs = getattr(AchievementConfig, 'ACHIEVEMENTS', [])
        cat = self.current_ach_cat
        items = defs if cat == '全部' else [a for a in defs if a.get('category') == cat]
        items.sort(key=lambda a: (a.get('id') not in self.player.achievements, -(a.get('reward', 0))))

        r, c = 0, 0
        for a in items:
            card_w, card_h = 250, 160
            card = tk.Canvas(self.ach_scrollable, bg=UIConfig.COLORS['primary'], width=card_w, height=card_h, highlightthickness=0)
            card.grid(row=r, column=c, padx=15, pady=15)
            
            unlocked = a.get('id') in self.player.achievements
            
            if unlocked:
                draw_rounded_rect(card, 2, 2, card_w-4, card_h-4, 18, fill='white')
                draw_clean_border(card, 2, 2, card_w-4, card_h-4, 18, color="#FFD54F", width=3)
            else:
                draw_rounded_rect(card, 4, 4, card_w-8, card_h-8, 18, fill='#F5F5F5')
            
            cx = card_w / 2
            icon = a.get('icon', '🏅')
            card.create_text(cx, 40, text=icon, font=('Segoe UI Emoji', 28))
            
            name_col = '#37474F' if unlocked else '#9E9E9E'
            card.create_text(cx, 75, text=a.get('name'), font=('Arial Rounded MT Bold', 12, 'bold'), fill=name_col)
            
            desc_col = '#78909C' if unlocked else '#BDBDBD'
            desc = a.get('description', '')
            card.create_text(cx, 98, text=desc, font=('Arial', 9), fill=desc_col, width=220, justify='center')
            
            if unlocked:
                card.create_text(cx, 135, text="✨ 已解锁 ✨", font=('Arial', 10, 'bold'), fill='#FFA000')
            else:
                cur, target = self._ach_progress(a)
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

            c += 1
            if c >= 3: c=0; r+=1

    def _fmt_time(self, s):
        if s is None:
            return "--"
        return f"{int(s)}s"

    def _ach_progress(self, a):
        aid = a.get('id')
        p = self.player
        # 修复：获取记录列表而不是直接用 Queue
        records = p.get_all_records()
        
        if aid == 'normal_master':
            cur = sum(1 for r in records if r.get('mode')=='normal' and r.get('completed'))
            return cur, 10
        if aid == 'ultimate_conqueror':
            cur = sum(1 for r in records if r.get('mode')=='ultimate' and r.get('completed'))
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
            return p.consecutive_days, 3
        if aid == 'login_streak_7':
            return p.consecutive_days, 7
        return 0, 0