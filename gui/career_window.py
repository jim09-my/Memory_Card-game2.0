import tkinter as tk
from tkinter import messagebox
import csv
import math
import os
from datetime import datetime
from config import UIConfig, DataConfig, AchievementConfig
from managers.data_manager import load_records, add_unlocked_achievement
from gui.game_window import GameWindow

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

        self._records_source = 'player'
        self._filtered_records = []
        self._current_category = None
        self._newly_unlocked = []

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
        canvas.place(x=0, y=0, relwidth=1, height=120)
        center_x = 450
        y_pos = 60
        text = "游戏生涯"
        font = ("Arial Rounded MT Bold", 32, "bold")
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            canvas.create_text(center_x+dx, y_pos+dy, text=text, font=font, fill='white')
        canvas.create_text(center_x, y_pos, text=text, font=font, fill='#FFEB3B')

        canvas.create_text(center_x, y_pos+40, text=f"{self.player.username}", font=("Arial", 13, 'bold'), fill='white')

        btn = tk.Button(self.window, text="✖", command=self.window.destroy,
                        bg='#B2DFDB', fg='white', font=('Arial', 10, 'bold'),
                        relief=tk.FLAT, bd=0)
        btn.place(x=860, y=15, width=25, height=25)

    def _create_nav_tabs(self):
        bar = tk.Frame(self.window, bg=UIConfig.COLORS['primary'])
        bar.place(x=0, y=120, relwidth=1, height=70)

        def tab_btn(text, key):
            btn = tk.Button(bar, text=text, command=lambda: self._show_page(key),
                            font=('Arial Rounded MT Bold', 12), bg='#B2DFDB', fg=UIConfig.COLORS['text_dark'],
                            activebackground='#FFCD3C', activeforeground='#2C3E50',
                            relief=tk.FLAT, bd=0, padx=18, pady=10)
            return btn

        tabs = tk.Frame(bar, bg=UIConfig.COLORS['primary'])
        tabs.pack(fill=tk.X)
        buttons_row = tk.Frame(tabs, bg=UIConfig.COLORS['primary'])
        buttons_row.pack(pady=8)
        b1 = tab_btn('总览', 'overview'); b1.pack(in_=buttons_row, side=tk.LEFT, padx=16)
        b2 = tab_btn('战绩', 'records'); b2.pack(in_=buttons_row, side=tk.LEFT, padx=16)
        b3 = tab_btn('成就', 'achievements'); b3.pack(in_=buttons_row, side=tk.LEFT, padx=16)
        self._nav_buttons = {'overview': b1, 'records': b2, 'achievements': b3}

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
            page.place(x=0, rely=0.02, relwidth=0.98, relheight=0.71)
        self._update_nav_styles(key)

    def _update_nav_styles(self, active_key):
        for k, btn in getattr(self, '_nav_buttons', {}).items():
            if k == active_key:
                btn.configure(bg='#FFCD3C', fg='#2C3E50')
            else:
                btn.configure(bg='#B2DFDB', fg=UIConfig.COLORS['text_dark'])

    def _build_overview(self, parent):
        stats = self.player.get_statistics()
        container = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)
        form_card = tk.Frame(container, bg='#FFFFFF')
        form_card.pack(side='left', fill='both', expand=True)
        header = tk.Label(form_card, text='生涯记录', font=('Arial Rounded MT Bold', 18), fg=UIConfig.COLORS['text_dark'], bg='#FFFFFF')
        header.grid(row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(18, 8))
        def field(r, label_text, value_text):
            tk.Label(form_card, text=label_text, font=('Arial', 12), fg='#455A64', bg='#FFFFFF').grid(row=r, column=0, sticky='e', padx=(20,8), pady=6)
            tk.Label(form_card, text=value_text, font=('Arial', 12, 'bold'), fg='#2C3E50', bg='#FFFFFF').grid(row=r, column=1, sticky='w', padx=(8,20), pady=6)
        field(1, '用户名', stats['username'])
        field(2, '等级', f"Lv.{stats['level']}")
        field(3, '积分', f"{self.player.points}")
        field(4, '累计积分', f"{stats['total_points_earned']}")
        field(5, '总局数', f"{stats['total_games']}")
        field(6, '通关局数', f"{stats['completed_games']}")
        field(7, '胜率', f"{int(stats['win_rate'])}%")
        field(8, '平均用时', self._fmt_time(stats['average_time']))
        field(9, '平均步数', f"{int(stats['average_moves'])}")
        field(10, '普通最佳', self._fmt_time(stats['best_time_normal']))
        field(11, '终极最佳', self._fmt_time(stats['best_time_ultimate']))
        field(12, '连续登录天数', f"{stats['consecutive_days']}")
        field(13, '成就数量', f"{stats['achievement_count']}")
        pen_canvas = tk.Canvas(form_card, width=360, height=320, bg='#FFFFFF', highlightthickness=0, bd=0)
        pen_canvas.place(relx=1.0, x=-360, rely=0.02)
        self._draw_pen(pen_canvas, 60, 260, -60, 2.0)

    def _pill(self, parent, text, color, width=180, height=42):
        canvas = tk.Canvas(parent, width=width, height=height, bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        r = height//2
        w, h = width, height
        canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline="")
        canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline="")
        canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline="")
        canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline="")
        canvas.create_rectangle(r, 0, w-r, h, fill=color, outline="")
        canvas.create_rectangle(0, r, w, h-r, fill=color, outline="")
        canvas.create_text(w/2, h/2, text=text, fill='white', font=('Arial Rounded MT Bold', 12))
        return canvas

    def _draw_pen(self, c, tip_x, tip_y, angle_deg, scale=1.0):
        rad = math.radians(angle_deg)
        L, W = 112*scale, 18*scale
        ca, sa = math.cos(rad), math.sin(rad)
        def rot(px, py):
            return (tip_x + px*ca - py*sa, tip_y + px*sa + py*ca)
        def fl(arr):
            o = []
            for x, y in arr:
                o.extend([x, y])
            return o
        c.create_polygon(*fl([rot(0,0), rot(L,0), rot(L,-W), rot(0,-W)]), fill='#546E7A', outline='')
        c.create_polygon(*fl([rot(4*scale,-2*scale), rot(L-10*scale,-2*scale), rot(L-10*scale,-W+2*scale), rot(4*scale,-W+2*scale)]), fill='#607D8B', outline='')
        c.create_polygon(*fl([rot(-12*scale,-W/2), rot(0,0), rot(0,-W)]), fill='#CFD8DC', outline='')
        cx, cy = rot(L+10*scale, -W/2)
        c.create_line(tip_x-10*scale, tip_y+3*scale, tip_x-4*scale, tip_y+6*scale, tip_x-12*scale, tip_y+12*scale, smooth=True, width=max(2, int(2*scale)), fill='#2C3E50')

    def _build_records(self, parent):
        toolbar = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
        toolbar.pack(fill=tk.X, pady=(0, 8))

        self.summary_label = tk.Label(parent, text='', bg=UIConfig.COLORS['primary'], fg='white', font=('Arial', 12))
        self.summary_label.pack(fill=tk.X)

        list_container = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
        list_container.pack(fill=tk.BOTH, expand=True)
        self.records_canvas = tk.Canvas(list_container, bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(list_container, orient='vertical', command=self.records_canvas.yview)
        self.scrollable_records = tk.Frame(self.records_canvas, bg=UIConfig.COLORS['primary'])
        self.records_canvas.bind('<Configure>', lambda e: self.records_canvas.itemconfig('inner', width=e.width-16))
        self.scrollable_records.bind('<Configure>', lambda e: self.records_canvas.configure(scrollregion=self.records_canvas.bbox('all')))
        self.records_canvas.create_window((0,0), window=self.scrollable_records, anchor='nw', tags='inner')
        self.records_canvas.configure(yscrollcommand=scrollbar.set)
        self.records_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self._apply_filters()



    def _apply_filters(self):
        records = list(self.player.game_records)
        filtered = list(records)
        filtered.sort(key=lambda r: r.get('timestamp', 0), reverse=True)
        self._filtered_records = filtered
        self._render_records()
        self._update_summary()

    def _render_records(self):
        for w in self.scrollable_records.winfo_children():
            w.destroy()
        if not self._filtered_records:
            tk.Label(self.scrollable_records, text='暂无战绩', font=('Arial', 14), bg=UIConfig.COLORS['primary'], fg='#90A4AE').pack(pady=50)
            return
        for r in self._filtered_records:
            self._record_row(self.scrollable_records, r)

    def _record_row(self, parent, record):
        is_win = record.get('completed', False)
        bg_col = '#F1F8E9' if is_win else '#FFEBEE'
        row = tk.Frame(parent, bg=bg_col, pady=10, padx=10)
        row.pack(fill=tk.X, pady=14, padx=30)
        icon = "🏆" if is_win else "❌"
        tk.Label(row, text=icon, font=('Segoe UI Emoji', 18), bg=bg_col, width=4).pack(side=tk.LEFT)
        mode = "普通" if record.get('mode') == 'normal' else "终极"
        tk.Label(row, text=mode, font=('Arial', 12, 'bold'), fg='#455A64', bg=bg_col, width=6, anchor='w').pack(side=tk.LEFT)
        date = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%m-%d %H:%M')
        tk.Label(row, text=date, font=('Arial', 11), fg='#90A4AE', bg=bg_col).pack(side=tk.LEFT, padx=5)
        time_s = self._fmt_time(record.get('time_used'))
        tk.Label(row, text=f"⏱ {time_s}", font=('Arial', 11), fg='#78909C', bg=bg_col).pack(side=tk.LEFT, padx=10)
        tk.Label(row, text=f"🎯 {int(record.get('score', 0))}", font=('Arial', 11), fg='#AB47BC', bg=bg_col).pack(side=tk.LEFT, padx=10)
        score = record.get('reward', 0)
        score_col = '#FFA726' if score > 0 else '#9E9E9E'
        tk.Label(row, text=f"+{score}", font=('Arial', 13, 'bold'), fg=score_col, bg=bg_col).pack(side=tk.RIGHT, padx=5)

    def _update_summary(self):
        records = self._filtered_records
        if not records:
            self.summary_label.config(text='')
            return
        total = len(records)
        wins = sum(1 for r in records if r.get('completed'))
        avg_time = int(sum(r.get('time_used', 0) for r in records if r.get('completed'))/max(1, wins))
        avg_moves = int(sum(r.get('moves', 0) for r in records)/max(1, total))
        avg_score = int(sum(r.get('score', 0) for r in records)/max(1, total))
        win_rate = int(wins/max(1, total)*100)
        self.summary_label.config(text=f"场次 {total} | 通关率 {win_rate}% | 平均用时 {avg_time}s | 平均步数 {avg_moves} | 平均得分 {avg_score}")





    def _build_achievements(self, parent):
        cats = sorted(list({a.get('category','其他') for a in getattr(AchievementConfig, 'ACHIEVEMENTS', []) if not a.get('hidden')}))
        cats = ['全部'] + cats if cats else ['全部']
        tabs = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
        tabs.pack(fill=tk.X, pady=(0,8))
        self.ach_cat_var = tk.StringVar(value=cats[0])
        for c in cats:
            tk.Radiobutton(tabs, text=c, variable=self.ach_cat_var, value=c, bg=UIConfig.COLORS['primary'], fg='white', selectcolor=UIConfig.COLORS['primary'], command=self._render_achievements).pack(side=tk.LEFT, padx=8)


        grid_container = tk.Frame(parent, bg=UIConfig.COLORS['primary'])
        grid_container.pack(fill=tk.BOTH, expand=True)
        self.ach_canvas = tk.Canvas(grid_container, bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(grid_container, orient='vertical', command=self.ach_canvas.yview)
        self.ach_scrollable = tk.Frame(self.ach_canvas, bg=UIConfig.COLORS['primary'])
        self.ach_canvas.bind('<Configure>', lambda e: self.ach_canvas.itemconfig('inner', width=e.width-20))
        self.ach_scrollable.bind('<Configure>', lambda e: self.ach_canvas.configure(scrollregion=self.ach_canvas.bbox('all')))
        self.ach_canvas.create_window((0,0), window=self.ach_scrollable, anchor='nw', tags='inner')
        self.ach_canvas.configure(yscrollcommand=scrollbar.set)
        self.ach_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self._render_achievements()

    def _render_achievements(self):
        for w in self.ach_scrollable.winfo_children():
            w.destroy()
        defs = getattr(AchievementConfig, 'ACHIEVEMENTS', [])
        cat = self.ach_cat_var.get()
        items = defs if cat == '全部' else [a for a in defs if a.get('category') == cat]
        items.sort(key=lambda a: (
            a.get('id') not in self.player.achievements,
            (a.get('category') or ''),
            -(a.get('reward', 0) or 0),
            (a.get('name', '') or '')
        ))

        if not items:
            tk.Label(self.ach_scrollable, text='暂无成就', bg=UIConfig.COLORS['primary'], fg='#90A4AE').pack(pady=30)
            return
        r, c = 0, 0
        for a in items:
            unlocked = a.get('id') in self.player.achievements
            card_bg = 'white' if unlocked else '#F5F5F5'
            name_fg = '#455A64' if unlocked else '#B0BEC5'
            desc_fg = '#90A4AE' if unlocked else '#CFD8DC'
            reward_fg = '#FFA726' if unlocked else '#B0BEC5'
            status_fg = '#66BB6A' if unlocked else '#9E9E9E'
            f = tk.Frame(self.ach_scrollable, bg=card_bg, width=260, height=160, padx=10, pady=8)
            f.grid(row=r, column=c, padx=12, pady=12)
            f.pack_propagate(False)
            icon_box = tk.Frame(f, bg=card_bg, width=52, height=52)
            icon_box.pack(anchor='w')
            icon_box.pack_propagate(False)
            tk.Label(icon_box, text=a.get('icon','🏅'), font=("Segoe UI Emoji", 24), bg=card_bg).pack(expand=True)
            tk.Label(f, text=a.get('name',''), font=('Arial Rounded MT Bold', 13), fg=name_fg, bg=card_bg).pack(anchor='w')
            if a.get('hidden'):
                tk.Label(f, text='隐藏', font=('Arial', 10), fg='#9E9E9E', bg=card_bg).place(relx=1.0, x=-8, y=8, anchor='ne')
            else:
                cat_text = a.get('category','') or '其他'
                tk.Label(f, text=cat_text, font=('Arial', 10), fg='#00796B', bg=card_bg).place(relx=1.0, x=-8, y=8, anchor='ne')
            tk.Label(f, text=a.get('description',''), font=('Arial', 11), fg=desc_fg, bg=card_bg).pack(anchor='w')
            tk.Label(f, text=f"奖励 {a.get('reward',0)}", font=('Arial', 11, 'bold'), fg=reward_fg, bg=card_bg).pack(anchor='w', pady=(4,0))
            status = '已解锁' if unlocked else '未解锁'
            tk.Label(f, text=status, font=('Arial', 11), fg=status_fg, bg=card_bg).pack(anchor='w')
            cur, target = self._ach_progress(a)
            if target:
                pb = tk.Canvas(f, width=230, height=10, bg=card_bg, highlightthickness=0, bd=0)
                pb.create_rectangle(0,0,230,10, fill='#ECEFF1', outline='')
                w = int(230*min(1.0, (cur/target if target else 0)))
                pb.create_rectangle(0,0,w,10, fill=('#4FC3F7' if unlocked else '#B0BEC5'), outline='')
                pb.pack(anchor='w', pady=(4,0))
                tk.Label(f, text=f"{cur}/{target}", font=('Arial', 10), fg=('#78909C' if unlocked else '#B0BEC5'), bg=card_bg).pack(anchor='w')
            if not unlocked and not a.get('hidden'):
                tk.Button(f, text='去挑战', command=lambda aid=a.get('id'): self._go_challenge(aid), bg='#FFCD3C', fg='#2C3E50', relief=tk.FLAT).pack(anchor='e')
            c += 1
            if c >= 3:
                c = 0
                r += 1

    def _ach_progress(self, a):
        aid = a.get('id')
        p = self.player
        if aid == 'normal_master':
            cur = sum(1 for r in p.game_records if r.get('mode')=='normal' and r.get('completed'))
            return cur, 10
        if aid == 'ultimate_conqueror':
            cur = sum(1 for r in p.game_records if r.get('mode')=='ultimate' and r.get('completed'))
            return cur, 5
        if aid == 'persistent_50':
            return len(p.game_records), 50
        if aid == 'item_user_10':
            cur = 0
            for r in p.game_records:
                iu = r.get('items_used', {})
                cur += sum(iu.values()) if isinstance(iu, dict) else 0
            return cur, 10
        if aid == 'no_item_10':
            cur = sum(1 for r in p.game_records if r.get('completed') and all((r.get('items_used',{}).get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo']))
            return cur, 10
        if aid == 'win_streak_3':
            return self._current_streak(), 3
        if aid == 'win_streak_5':
            return self._current_streak(), 5
        if aid == 'login_streak_3':
            return self.player.consecutive_days, 3
        if aid == 'login_streak_7':
            return self.player.consecutive_days, 7
        return 0, 0

    def _current_streak(self):
        streak = 0
        for r in sorted(self.player.game_records, key=lambda x: x.get('timestamp',0), reverse=True):
            if r.get('completed'):
                streak += 1
            else:
                break
        return streak

    def _go_challenge(self, aid):
        mode = 'normal'
        if aid in ['ultimate_conqueror','flawless_ultimate','speedrunner_ultimate','no_item_ultimate','win_streak_5']:
            mode = 'ultimate'
        self.window.withdraw()
        def on_close():
            self.window.deiconify()
            self._render_achievements()
        GameWindow(self.window, self.player, on_close)
        self.window.after(0, lambda: None)

    def _fmt_time(self, s):
        if not s: return "--"
        return f"{int(s)}s"