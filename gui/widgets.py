"""
自定义控件
基于 Canvas 绘制
"""

import tkinter as tk
from config import UIConfig, PokerConfig

class PlayingCard(tk.Canvas):
    def __init__(self, master, width=90, height=128, corner_radius=14, command=None, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bd=0, bg=UIConfig.COLORS['primary'],** kwargs)
        self._cw = width
        self._ch = height
        self._cr = corner_radius
        self._command = command
        self._state = 'normal'
        
        self._front = False
        self._rank = None
        self._suit = None
        self._highlighted = False # 是否处于高亮状态 (配对成功)

        # 绑定事件
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._hover_in)
        self.bind('<Leave>', self._hover_out)
        
        # 初始绘制
        self._render_back()

    def config(self, **kwargs):
        if 'state' in kwargs:
            self._state = kwargs.pop('state')
        super().config(**kwargs)

    configure = config

    def set_face(self, rank, suit):
        self._rank = str(rank)
        self._suit = str(suit)

    # --- 核心交互 ---
    def _on_click(self, e):
        if self._state == 'disabled': return
        if callable(self._command): self._command()

    def _hover_in(self, e=None):
        if self._state == 'disabled' or self._highlighted: return
        # 鼠标悬停轻微放大效果
        self._render_current(scale=1.05)

    def _hover_out(self, e=None):
        if self._highlighted: return
        self._render_current(scale=1.0)

    # --- 绘图辅助函数 ---
    def _draw_round_rect(self, x, y, w, h, r, fill, outline=None, width=0, tag='card'):
        """绘制圆角矩形"""
        points = [
            x+r, y, x+w-r, y,
            x+w, y, x+w, y+r,
            x+w, y+h-r, x+w, y+h,
            x+w-r, y+h, x+r, y+h,
            x, y+h, x, y+h-r,
            x, y+r, x, y
        ]
        
        self.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline="", tags=(tag,))
        self.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline="", tags=(tag,))
        self.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline="", tags=(tag,))
        self.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline="", tags=(tag,))
        
        self.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline="", tags=(tag,))
        self.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline="", tags=(tag,))
        
        if outline and width > 0:
            pass

    def _draw_cartoon_icon(self, cx, cy, size):
        """绘制卡背上的图标"""
        color = UIConfig.COLORS['card_back_icon']

        self.create_oval(cx-size, cy-size, cx+size, cy+size, outline=color, width=3, tags=('card',))
        icon_sz = size * 0.6
        self.create_oval(cx-icon_sz, cy-icon_sz + 5, cx+icon_sz, cy+icon_sz + 5, fill=color, outline="", tags=('card',))
        self.create_line(cx, cy-icon_sz+5, cx+icon_sz, cy-size, fill=color, width=3, capstyle=tk.ROUND, tags=('card',))

    # --- 渲染逻辑 ---
    def _pip_layout(self):
        center = 0.5
        top = 0.2
        bot = 0.8
        mid = 0.5
        upper = 0.35
        lower = 0.65
        left = 0.25
        right = 0.75
        return {
            '2': [(center, top), (center, bot)],
            '3': [(center, top), (center, mid), (center, bot)],
            '4': [(left, top), (right, top), (left, bot), (right, bot)],
            '5': [(left, top), (right, top), (center, mid), (left, bot), (right, bot)],
            '6': [(left, top), (right, top), (left, mid), (right, mid), (left, bot), (right, bot)],
            '7': [(left, top), (right, top), (left, mid), (right, mid), (left, bot), (right, bot), (center, upper)],
            '8': [(left, top), (right, top), (left, mid), (right, mid), (left, bot), (right, bot), (center, upper), (center, lower)],
            '9': [(left, top), (right, top), (left, mid), (right, mid), (left, bot), (right, bot), (center, upper), (center, lower), (center, mid)],
            '10': [(left, top), (right, top), (left, upper), (right, upper), (left, lower), (right, lower), (left, bot), (right, bot), (center, upper), (center, lower)]
        }

    def _draw_pips(self, positions, col, x_offset, y_offset, w, h, scale):
        pip_font = (UIConfig.FONTS['card_corner'][0], max(10, int(h * 0.16 * scale)), 'bold')
        for x_rel, y_rel in positions:
            x = x_offset + w * x_rel
            y = y_offset + h * y_rel
            self.create_text(x, y, text=self._suit, fill=col, font=pip_font, tags=('card',))

    def _render_current(self, scale=1.0):
        if self._front:
            self._render_front(scale)
        else:
            self._render_back(scale)

    def _render_back(self, scale=1.0):
        self.delete('all')
        
        cx, cy = self._cw / 2, self._ch / 2
        w = self._cw * scale
        h = self._ch * scale
        x = (self._cw - w) / 2
        y = (self._ch - h) / 2
        r = self._cr * scale

        # 1. 绘制发光层
        if self._highlighted:
            glow_color = UIConfig.COLORS['success_glow']
            glow_width = 6
            self._draw_round_rect(x-glow_width, y-glow_width, w+glow_width*2, h+glow_width*2, r+4, fill=glow_color, tag='glow')

        # 2. 绘制白色外边框
        self._draw_round_rect(x, y, w, h, r, fill=UIConfig.COLORS['card_border_white'], tag='card')
        
        # 3. 绘制黄色内芯
        inset = 4 * scale
        self._draw_round_rect(x+inset, y+inset, w-inset*2, h-inset*2, r-2, fill=UIConfig.COLORS['card_back_bg'], tag='card')

        # 4. 绘制中心图案
        self._draw_cartoon_icon(cx, cy, w * 0.25)

        self._front = False

    def _render_front(self, scale=1.0):
        """
        绘制卡牌正面
        """
        self.delete('all')
        
        # 基础尺寸
        w = self._cw * scale
        h = self._ch * scale
        x_offset = (self._cw - w) / 2
        y_offset = (self._ch - h) / 2
        r = self._cr * scale

        # 1. 发光层
        if self._highlighted:
            glow_color = UIConfig.COLORS['success_glow']
            glow_width = 6
            self._draw_round_rect(x_offset-glow_width, y_offset-glow_width, 
                                  w+glow_width*2, h+glow_width*2, r+4, 
                                  fill=glow_color, tag='glow')

        # 2. 白色底面
        self._draw_round_rect(x_offset, y_offset, w, h, r, 
                              fill=UIConfig.COLORS['card_front'], tag='card')
        
        if not (self._rank and self._suit):
            return

        col = PokerConfig.suit_color(self._suit)
        pip_layouts = self._pip_layout()
        

        safe_margin_x = max(6, int(w * 0.14)) 
        safe_margin_y = max(8, int(h * 0.01)) 

        corner_font_size = int(h * 0.11)
        center_font_size = int(h * 0.40)
        
        font_corner = (UIConfig.FONTS['card_corner'][0], corner_font_size, 'bold')
        font_main = (UIConfig.FONTS['card_main'][0], center_font_size, 'bold')

        tl_x = x_offset + safe_margin_x
        tl_y = y_offset + safe_margin_y
        
        # 数字
        self.create_text(tl_x, tl_y,
                         text=self._rank,
                         fill=col, font=font_corner, anchor=tk.N, tags=('card',))

        br_x = x_offset + w - safe_margin_x
        br_y = y_offset + h - safe_margin_y
        
        try:
            self.create_text(br_x, br_y,
                             text=self._rank,
                             fill=col, font=font_corner, 
                             anchor=tk.N, angle=180, tags=('card',)) 
                             
        except Exception:
            self.create_text(br_x, br_y,
                             text=self._rank,
                             fill=col, font=font_corner, anchor=tk.SE, tags=('card',))


        cx = x_offset + w / 2
        cy = y_offset + h / 2
        
        if self._rank in ['J', 'Q', 'K', 'A']:
            text_content = self._rank if self._rank in ['J', 'Q', 'K'] else self._suit
            self.create_text(cx, cy, text=text_content, fill=col, font=font_main, tags=('card',))
        else:
            layout = pip_layouts.get(self._rank)
            if layout:
                self._draw_pips(layout, col, x_offset, y_offset, w, h, scale)
            else:
                self.create_text(cx, cy, text=self._suit, fill=col, font=font_main, tags=('card',))

        self._front = True

    # --- 外部调用接口 ---
    def show_front(self, rank, suit):
        self.set_face(rank, suit)
        self._render_front()
    
    def animate_vanish(self):
        """
        配对成功的消失动画
        """

        self._highlighted = True
        self._render_front()
        
        steps = 10
        duration = 300
        step_time = duration // steps
        
        def _shrink(step):
            if step <= steps:
                scale = 1.0 - (step / steps)

                self._render_front(scale=scale)
                
                self.after(step_time, lambda: _shrink(step + 1))
            else:
                # 动画结束
                self.delete('all')
                self.config(state='disabled')
                self._highlighted = False 
                # 标记为已隐藏
                self._is_vanished = True 

        # 开始动画
        _shrink(0)

    def _render_current(self, scale=1.0):
        if getattr(self, '_is_vanished', False):
            return
            
        if self._front:
            self._render_front(scale)
        else:
            self._render_back(scale)
            
    def _hover_in(self, e=None):
        if self._state == 'disabled' or self._highlighted or getattr(self, '_is_vanished', False): 
            return
        self._render_current(scale=1.05)

    def show_back(self):
        self._render_back()
        
    def set_highlight(self, active=True):
        self._highlighted = active
        self._render_current()

    def animate_flip_to_front(self, rank, suit):
        self.set_face(rank, suit)
        # 简单缩放动画模拟翻转
        steps = 6
        ms = 20
        
        def _anim(step):
            if step < steps:
                scale_x = 1.0 - (step / steps)
                self.delete('all')
                w = self._cw * scale_x
                x = (self._cw - w) / 2
                self._draw_round_rect(x, 0, w, self._ch, self._cr, fill=UIConfig.COLORS['card_back_bg'])
                self.after(ms, lambda: _anim(step + 1))
            elif step == steps:
                self._front = True
                _anim_out(0)
                
        def _anim_out(step):
            if step <= steps:
                scale_x = (step / steps)
                self._render_front(scale=scale_x) 
                if step == steps:
                    self._render_front()
                else:
                    self.after(ms, lambda: _anim_out(step + 1))

        _anim(0)

    def __getattr__(self, item):
        if item.startswith('_'):
            return self.__dict__.get(item, None)
        raise AttributeError(item)


class ItemButton(tk.Canvas):
    """
    自定义道具按钮
    """
    def __init__(self, master, item_id, icon, name, count=0, command=None, width=100, height=90):
        super().__init__(master, width=width, height=height, 
                         bg=UIConfig.COLORS['primary'], highlightthickness=0, bd=0)
        self.item_id = item_id
        self.icon = icon
        self.name = name
        self.count = count
        self._command = command
        self._width = width
        self._height = height
        self._state = 'normal' if count > 0 else 'disabled'
        self._hover = False
        
        # 绑定事件
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        self._draw()

    def _draw(self):
        self.delete('all')
        
        # 颜色定义
        if self._state == 'disabled':
            bg_color = '#CFD8DC'
            fg_color = '#90A4AE'
            border_color = '#B0BEC5'
        else:
            bg_color = '#FFFFFF'
            fg_color = UIConfig.COLORS['text_dark']
            border_color = '#B2DFDB' if not self._hover else '#FFCD3C'
            
        # 悬停时浮起
        offset_y = 0 if (self._state == 'disabled' or not self._hover) else -4
        shadow_offset = 4 if (self._state == 'disabled' or not self._hover) else 8
        
        # 1. 绘制阴影
        if self._state != 'disabled':
            self._draw_round_rect(2, 2 + shadow_offset, self._width-4, self._height-4, 12, 
                                  fill='#00695C', alpha=0.3) # 半透明深青色阴影
            
        # 2. 绘制按钮主体
        self._draw_round_rect(2, 2 + offset_y, self._width-4, self._height-4, 12, 
                              fill=bg_color, outline=border_color, width=2)
        
        # 3. 绘制图标
        self.create_text(self._width/2, self._height/2 - 10 + offset_y, 
                         text=self.icon, font=("Segoe UI Emoji", 28), fill=fg_color)
        
        # 4. 绘制名称
        self.create_text(self._width/2, self._height - 22 + offset_y,
                         text=self.name, font=("Arial Rounded MT Bold", 10), fill=fg_color)
        
        # 5. 绘制数量角标
        if self.count > 0:
            badge_x = self._width - 18
            badge_y = 18 + offset_y
            self.create_oval(badge_x-10, badge_y-10, badge_x+10, badge_y+10, 
                             fill='#FF5252', outline='white', width=2)
            self.create_text(badge_x, badge_y, text=str(self.count), 
                             fill='white', font=('Arial', 9, 'bold'))

    def _draw_round_rect(self, x, y, w, h, r, fill, outline="", width=0, alpha=None):
        self.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline=outline, width=width)
        self.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline=outline, width=width)
        self.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline=outline, width=width)
        self.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline=outline, width=width)
        self.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline="", width=0)
        self.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline="", width=0)
        
        if width > 0:
           self.create_line(x+r, y, x+w-r, y, fill=outline, width=width)
           self.create_line(x+r, y+h, x+w-r, y+h, fill=outline, width=width)
           self.create_line(x, y+r, x, y+h-r, fill=outline, width=width)
           self.create_line(x+w, y+r, x+w, y+h-r, fill=outline, width=width)

    def set_count(self, count):
        self.count = count
        self._state = 'normal' if count > 0 else 'disabled'
        self._draw()

    def _on_click(self, event):
        if self._state == 'normal' and self._command:
            self._command(self.item_id)

    def _on_enter(self, event):
        if self._state != 'disabled':
            self._hover = True
            self._draw()

    def _on_leave(self, event):
        self._hover = False
        self._draw()

class RoundButton(tk.Canvas):
    """
    通用圆角文字按钮
    """
    def __init__(self, master, text, command=None, width=100, height=40, 
                 bg_color='#FF7043', hover_color='#FF8A65', 
                 text_color='white', parent_bg=None, font=None):
        if parent_bg is None:
            parent_bg = UIConfig.COLORS['primary_dark'] 
            
        super().__init__(master, width=width, height=height, 
                         bg=parent_bg, highlightthickness=0, bd=0)
        
        self.text = text
        self._command = command
        self._width = width
        self._height = height
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font or ('Arial Rounded MT Bold', 12)
        self._hover = False
        
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        self._draw()

    def _draw(self):
        self.delete('all')
        
        fill_color = self.hover_color if self._hover else self.bg_color
        
        # 绘制圆角矩形背景
        self._draw_round_rect(0, 0, self._width, self._height, 20, fill=fill_color)
        
        # 绘制文字
        self.create_text(self._width/2, self._height/2, text=self.text, 
                         fill=self.text_color, font=self.font)

    def _draw_round_rect(self, x, y, w, h, r, fill):
        self.create_arc(x, y, x+2*r, y+2*r, start=90, extent=90, fill=fill, outline="")
        self.create_arc(x+w-2*r, y, x+w, y+2*r, start=0, extent=90, fill=fill, outline="")
        self.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, fill=fill, outline="")
        self.create_arc(x, y+h-2*r, x+2*r, y+h, start=180, extent=90, fill=fill, outline="")
        self.create_rectangle(x+r, y, x+w-r, y+h, fill=fill, outline="")
        self.create_rectangle(x, y+r, x+w, y+h-r, fill=fill, outline="")

    def _on_click(self, event):
        if self._command:
            self._command()

    def _on_enter(self, event):
        self._hover = True
        self._draw()
        # 鼠标变手型
        self.config(cursor='hand2')

    def _on_leave(self, event):
        self._hover = False
        self._draw()
        self.config(cursor='')

