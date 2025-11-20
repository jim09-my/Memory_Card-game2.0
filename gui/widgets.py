"""
自定义控件：RoundButton
基于 Canvas 绘制圆角矩形 + 文字/图片，并提供简单的 `config` 接口与 `command` 回调，目的是在不依赖平台主题的情况下获得一致外观。
"""

import tkinter as tk
from typing import Optional

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
        self._draw()
        self.bind('<Button-1>', self._on_click)

    def _draw(self):
        self.delete('all')
        w, h, r = self._width, self._height, self._corner
        # draw rounded rectangle by drawing arcs and rectangles
        try:
            # four corners
            self.create_arc((0, 0, r*2, r*2), start=90, extent=90, outline=self._bg, fill=self._bg)
            self.create_arc((w-2*r, 0, w, r*2), start=0, extent=90, outline=self._bg, fill=self._bg)
            self.create_arc((0, h-2*r, r*2, h), start=180, extent=90, outline=self._bg, fill=self._bg)
            self.create_arc((w-2*r, h-2*r, w, h), start=270, extent=90, outline=self._bg, fill=self._bg)
            # center rects
            self.create_rectangle((r, 0, w-r, h), outline=self._bg, fill=self._bg)
            self.create_rectangle((0, r, w, h-r), outline=self._bg, fill=self._bg)
        except Exception:
            # fallback: plain rectangle
            self.create_rectangle((0,0,w,h), outline=self._bg, fill=self._bg)

        # draw image or text
        if self._image:
            try:
                self._items['image'] = self.create_image(w//2, h//2, image=self._image)
            except Exception:
                # fallback to text
                self._items['text'] = self.create_text(w//2, h//2, text=str(self._text), fill=self._fg, font=self._font)
        else:
            self._items['text'] = self.create_text(w//2, h//2, text=str(self._text), fill=self._fg, font=self._font)

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
            return int(super().winfo_width()) or self._width
        except Exception:
            return self._width

    def winfo_height(self):
        try:
            return int(super().winfo_height()) or self._height
        except Exception:
            return self._height
