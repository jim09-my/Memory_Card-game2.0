"""
自定义控件：RoundButton
基于 Canvas 绘制圆角矩形 + 文字/图片，并提供简单的 `config` 接口与 `command` 回调，目的是在不依赖平台主题的情况下获得一致外观。
"""

import tkinter as tk
from typing import Optional
from config import UIConfig, PokerConfig

class RoundButton(tk.Canvas):
    def __init__(self, master, width=80, height=80, corner_radius=10, bg='#FFE66D', fg='#333333',
                 text='?', image=None, command=None, font=None, **kwargs):
        # 使用 Canvas 以便绘制圆角矩形
        super().__init__(master, width=width, height=height, highlightthickness=0, bd=0, **kwargs)
        self._width = width
        self._height = height
        self._corner = max(1, corner_radius)
        self._bg = bg
        self._fg = fg
        self._text = text
        self._image = image
        self._font = font or ('Arial', 12, 'bold')
        self._command = command
        self._state = 'normal'

        self._items = {}
        self._mode = 'back'  # 'back' or 'front'
        self._shadow_offset = 0
        self._hovered = False
        self._draw()
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_hover_enter)
        self.bind('<Leave>', self._on_hover_leave)

    def _draw(self):
        self.delete('all')
        w, h, r = self._width, self._height, self._corner
        # draw rounded rectangle by drawing arcs and rectangles
        try:
            if self._shadow_offset:
                so = self._shadow_offset
                self._draw_round_rect(so, so, w, h, r, fill='#2C3E50')
            self._draw_round_rect(0, 0, w, h, r, fill=self._bg)
        except Exception:
            # fallback: plain rectangle
            self.create_rectangle((0,0,w,h), outline=self._bg, fill=self._bg)

        # draw image or text
        if self._image:
            try:
                self._items['image'] = self.create_image(w//2, h//2, image=self._image, tags=('content',))
            except Exception:
                # fallback to text
                self._items['text'] = self.create_text(w//2, h//2, text=str(self._text), fill=self._fg, font=self._font, tags=('content',))
        else:
            self._items['text'] = self.create_text(w//2, h//2, text=str(self._text), fill=self._fg, font=self._font, tags=('content',))

    def _draw_round_rect(self, x, y, w, h, r, fill):
        try:
            self.create_arc((x, y, x+r*2, y+r*2), start=90, extent=90, outline=fill, fill=fill)
            self.create_arc((x+w-2*r, y, x+w, y+r*2), start=0, extent=90, outline=fill, fill=fill)
            self.create_arc((x, y+h-2*r, x+r*2, y+h), start=180, extent=90, outline=fill, fill=fill)
            self.create_arc((x+w-2*r, y+h-2*r, x+w, y+h), start=270, extent=90, outline=fill, fill=fill)
            self.create_rectangle((x+r, y, x+w-r, y+h), outline=fill, fill=fill)
            self.create_rectangle((x, y+r, x+w, y+h-r), outline=fill, fill=fill)
        except Exception:
            self.create_rectangle((x, y, x+w, y+h), outline=fill, fill=fill)

    def config(self, **kwargs):
        # 支持常用属性：text, bg, fg, image, state, font
        if 'text' in kwargs:
            self._text = kwargs.pop('text')
        if 'bg' in kwargs:
            self._bg = kwargs.pop('bg')
        if 'fg' in kwargs:
            self._fg = kwargs.pop('fg')
        if 'image' in kwargs:
            self._image = kwargs.pop('image')
        if 'state' in kwargs:
            self._state = kwargs.pop('state')
        if 'font' in kwargs:
            self._font = kwargs.pop('font')
        # apply redraw
        self._draw()

    # alias to be compatible with tk widgets
    configure = config

    def _on_click(self, event):
        if self._state != 'disabled' and callable(self._command):
            try:
                self._command()
            except Exception:
                pass

    def _on_hover_enter(self, event=None):
        if self._state == 'disabled':
            return
        self._hovered = True
        self._shadow_offset = 6
        try:
            self.move('content', 0, -6)
        except Exception:
            pass
        self._draw()

    def _on_hover_leave(self, event=None):
        self._hovered = False
        try:
            self.move('content', 0, 6)
        except Exception:
            pass
        self._shadow_offset = 0
        self._draw()

    def animate_flip_to_front(self, rank, suit, face_color=None):
        try:
            self.scale('content', self._width/2, self._height/2, 0.01, 1.0)
        except Exception:
            pass
        self._render_front(rank, suit, face_color)
        try:
            steps = 8
            for i in range(steps):
                sx = 1.0 - (steps - 1 - i) / steps
                self.scale('content', self._width/2, self._height/2, 1.1, 1.0)
                self.update_idletasks()
        except Exception:
            pass
        self._mode = 'front'

    def animate_flip_to_back(self):
        try:
            self.scale('content', self._width/2, self._height/2, 0.01, 1.0)
        except Exception:
            pass
        self._render_back()
        try:
            steps = 8
            for i in range(steps):
                self.scale('content', self._width/2, self._height/2, 1.1, 1.0)
                self.update_idletasks()
        except Exception:
            pass
        self._mode = 'back'

    def _render_front(self, rank, suit, face_color=None):
        self._bg = UIConfig.COLORS['card_front']
        self._fg = face_color or UIConfig.COLORS['text_dark']
        self.delete('all')
        w, h, r = self._width, self._height, self._corner
        self._draw_round_rect(0, 0, w, h, r, fill=self._bg)
        try:
            col = PokerConfig.suit_color(suit)
            self.create_text(10, 10, anchor=tk.NW, text=f"{rank}{suit}", fill=col, font=UIConfig.FONTS['card_corner'], tags=('content','card'))
            self.create_text(w-10, h-10, anchor=tk.SE, text=f"{rank}{suit}", fill=col, font=UIConfig.FONTS['card_corner'], tags=('content','card'))
            if rank in ('J','Q','K'):
                self.create_text(w//2, h//2, text=rank, fill=col, font=('Times New Roman', int(h*0.5), 'bold'), tags=('content','card'))
                self.create_text(w//2, h//2 + int(h*0.22), text=suit, fill=col, font=('Times New Roman', int(h*0.22), 'bold'), tags=('content','card'))
            elif rank == 'A':
                self.create_text(w//2, h//2, text=suit, fill=col, font=('Times New Roman', int(h*0.6), 'bold'), tags=('content','card'))
            else:
                for px, py in PlayingCard.pip_positions_static(rank, w, h):
                    self.create_text(px, py, text=suit, fill=col, font=('Times New Roman', int(h*0.14), 'bold'), tags=('content','card'))
        except Exception:
            self.create_text(w//2, h//2, text=f"{rank}{suit}", fill=self._fg, font=self._font, tags=('content','card'))

    def _render_back(self):
        self._bg = UIConfig.COLORS['card_back']
        self._fg = '#FFFFFF'
        self.delete('all')
        w, h, r = self._width, self._height, self._corner
        self._draw_round_rect(0, 0, w, h, r, fill=self._bg)
        try:
            step = 10
            for x in range(step, w, step):
                self.create_line(x, 0, x, h, fill='#FFECB3', tags=('content','card'))
            for y in range(step, h, step):
                self.create_line(0, y, w, y, fill='#FFECB3', tags=('content','card'))
        except Exception:
            pass
        self.create_text(w//2, h//2, text='?', fill=self._fg, font=self._font, tags=('content','card'))

class PlayingCard(tk.Canvas):
    def __init__(self, master, width=90, height=128, corner_radius=14, command=None, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bd=0, **kwargs)
        self._cw = width
        self._ch = height
        self._cr = corner_radius
        self._command = command
        self._state = 'normal'
        self._shadow = 6
        self._front = False
        self._rank = None
        self._suit = None
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._hover_in)
        self.bind('<Leave>', self._hover_out)
        self._render_back()

    def config(self, **kwargs):
        if 'state' in kwargs:
            self._state = kwargs.pop('state')
        super().config(**kwargs)

    configure = config

    def set_face(self, rank, suit):
        self._rank = str(rank)
        self._suit = str(suit)

    def _on_click(self, e):
        if self._state == 'disabled':
            return
        if callable(self._command):
            try:
                self._command()
            except Exception:
                pass

    def _hover_in(self, e=None):
        if self._state == 'disabled':
            return
        self._hover = True
        self._shadow = 14
        try:
            self.move('card', 0, -2)
            self.move('shadow', 0, 6)
        except Exception:
            pass
        self._redraw_current()

    def _hover_out(self, e=None):
        self._hover = False
        self._shadow = 6
        try:
            self.move('card', 0, 2)
            self.move('shadow', 0, -2)
        except Exception:
            pass
        self._redraw_current()

    def _draw_round_rect(self, x, y, w, h, r, fill, outline=None, width=1, tag='card'):
        try:
            self.create_arc((x, y, x+r*2, y+r*2), start=90, extent=90, outline=fill, fill=fill, tags=(tag,))
            self.create_arc((x+w-2*r, y, x+w, y+r*2), start=0, extent=90, outline=fill, fill=fill, tags=(tag,))
            self.create_arc((x, y+h-2*r, x+r*2, y+h), start=180, extent=90, outline=fill, fill=fill, tags=(tag,))
            self.create_arc((x+w-2*r, y+h-2*r, x+w, y+h), start=270, extent=90, outline=fill, fill=fill, tags=(tag,))
            self.create_rectangle((x+r, y, x+w-r, y+h), outline=fill, fill=fill, tags=(tag,))
            self.create_rectangle((x, y+r, x+w, y+h-r), outline=fill, fill=fill, tags=(tag,))
        except Exception:
            self.create_rectangle((x, y, x+w, y+h), outline=fill, fill=fill, tags=(tag,))
        if outline:
            try:
                self.create_rectangle((x+2, y+2, x+w-2, y+h-2), outline=outline, width=width, tags=(tag,))
            except Exception:
                pass

    def _render_back(self):
        self.delete('all')
        w, h, r = self._cw, self._ch, self._cr
        if self._shadow:
            self._draw_drop_shadow(w, h, r, dx=4, dy=8 if self._hover else 4)
        outline_w = 2 if not self._hover else 3
        self._draw_round_rect(0, 0, w, h, r, fill=UIConfig.COLORS['card_back'], outline=UIConfig.COLORS['card_border'], width=outline_w, tag='card')
        self.create_text(w//2, h//2, text='?', fill='#FFFFFF', font=UIConfig.FONTS['card_main'], tags=('card',))
        self._front = False
        if self._hover:
            try:
                self.scale('card', w/2, h/2, 1.12, 1.12)
            except Exception:
                pass

    def _render_front(self):
        self.delete('all')
        w, h, r = self._cw, self._ch, self._cr
        if self._shadow:
            self._draw_drop_shadow(w, h, r, dx=4, dy=8 if self._hover else 4)
        outline_w = 2 if not self._hover else 3
        self._draw_round_rect(0, 0, w, h, r, fill=UIConfig.COLORS['card_front'], outline=UIConfig.COLORS['card_border'], width=outline_w, tag='card')
        if not (self._rank and self._suit):
            self.create_text(w//2, h//2, text='?', fill=UIConfig.COLORS['text_dark'], font=UIConfig.FONTS['card_main'], tags=('card',))
        else:
            col = PokerConfig.suit_color(self._suit)
            pad = int(min(w, h) * 0.12)
            num_sz = int(h * (0.12 if len(str(self._rank)) == 1 else 0.10))
            num_font = ('Arial', num_sz, 'bold')
            self.create_text(pad, pad, anchor=tk.NW, text=f"{self._rank}", fill=col, font=num_font, tags=('card','corner'))
            self.create_text(w - pad, h - pad, anchor=tk.SE, text=f"{self._rank}", fill=col, font=num_font, tags=('card','corner'))
            if self._rank == 'A':
                self.create_text(w//2, h//2, text=self._suit, fill=col, font=('Times New Roman', int(h*0.55), 'bold'), tags=('card',))
            else:
                pip_font = ('Times New Roman', int(h*0.14), 'bold')
                for px, py in PlayingCard.pip_positions_static(self._rank, w, h):
                    self.create_text(px, py, text=self._suit, fill=col, font=pip_font, tags=('card','pip'))
        self._front = True
        if self._hover:
            try:
                self.scale('card', w/2, h/2, 1.12, 1.12)
            except Exception:
                pass

    @staticmethod
    def pip_positions_static(rank, w, h):
        cx = int(w * 0.50)
        left = int(w * 0.30)
        right = int(w * 0.70)
        top = int(h * 0.20)
        upper = int(h * 0.35)
        middle = int(h * 0.50)
        lower = int(h * 0.65)
        bottom = int(h * 0.80)
        if rank == '2':
            return [(cx, top), (cx, bottom)]
        if rank == '3':
            return [(cx, top), (cx, middle), (cx, bottom)]
        if rank == '4':
            return [(left, top), (right, top), (left, bottom), (right, bottom)]
        if rank == '5':
            return [(left, top), (right, top), (cx, middle), (left, bottom), (right, bottom)]
        if rank == '6':
            return [(left, top), (right, top), (left, middle), (right, middle), (left, bottom), (right, bottom)]
        if rank == '7':
            return [(left, top), (right, top), (left, upper), (right, upper), (left, bottom), (right, bottom), (cx, upper)]
        if rank == '8':
            return [(left, top), (right, top), (left, upper), (right, upper), (left, lower), (right, lower), (left, bottom), (right, bottom)]
        if rank == '9':
            return [(left, top), (right, top), (left, upper), (right, upper), (cx, middle), (left, lower), (right, lower), (left, bottom), (right, bottom)]
        if rank == '10':
            rows = [top, upper, middle, lower, bottom]
            return [(left, y) for y in rows] + [(right, y) for y in rows]
        return [(cx, middle)]

    def _draw_drop_shadow(self, w, h, r, dx=4, dy=6):
        colors = ['#263238', '#2C3E50', '#37474F', '#455A64']
        for i, c in enumerate(colors):
            offx = dx + i
            offy = dy + i
            try:
                self._draw_round_rect(offx, offy, w, h, r, fill=c, tag='shadow')
            except Exception:
                pass

    def show_front(self, rank, suit):
        self.set_face(rank, suit)
        self._render_front()

    def show_back(self):
        self._render_back()

    def _redraw_current(self):
        if self._front:
            self._render_front()
        else:
            self._render_back()

    def animate_flip_to_front(self, rank, suit):
        self.set_face(rank, suit)
        w, h = self._cw, self._ch
        try:
            steps = 10
            for i in range(steps):
                sx = max(0.08, 1 - i / steps)
                self.scale('card', w/2, h/2, sx, 1)
                self.update_idletasks()
            self._render_front()
            for i in range(steps):
                sx = 0.08 + i / steps
                self.scale('card', w/2, h/2, sx, 1)
                self.update_idletasks()
        except Exception:
            self._render_front()

    def animate_flip_to_back(self):
        w, h = self._cw, self._ch
        try:
            steps = 10
            for i in range(steps):
                sx = max(0.08, 1 - i / steps)
                self.scale('card', w/2, h/2, sx, 1)
                self.update_idletasks()
            self._render_back()
            for i in range(steps):
                sx = 0.08 + i / steps
                self.scale('card', w/2, h/2, sx, 1)
                self.update_idletasks()
        except Exception:
            self._render_back()

    def set_disabled_placeholder(self):
        self._state = 'disabled'
        self.delete('all')
        w, h, r = self._cw, self._ch, self._cr
        self._draw_round_rect(0, 0, w, h, r, fill='#FFFFFF', outline='#DDDDDD', width=1, tag='card')

    def set_command(self, cmd):
        self._command = cmd

    # keep compatibility with old code that uses btn._hidden etc.
    def __getattr__(self, item):
        # allow reading arbitrary attributes like _hidden
        if item.startswith('_'):
            return self.__dict__.get(item, None)
        raise AttributeError(item)

    # ensure widget reports width/height
    def winfo_width(self):
        try:
            return int(super().winfo_width()) or self._cw
        except Exception:
            return self._cw

    def winfo_height(self):
        try:
            return int(super().winfo_height()) or self._ch
        except Exception:
            return self._ch
