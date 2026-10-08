"""Componentes visuales reutilizables, tablas y recursos locales."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path

BG = '#F3F7FA'
INK = '#173449'
MUTED = '#637C8D'
TEAL = '#087F83'
ASSETS = Path(__file__).resolve().parent / 'assets'


def label(parent, text, size=11, bold=False, color=INK, bg=None, **kw):
    return tk.Label(parent, text=text, font=('Segoe UI', size, 'bold' if bold else 'normal'),
                    fg=color, bg=bg or parent.cget('bg'), **kw)


def button(parent, text, command, secondary=False, **kw):
    return tk.Button(parent, text=text, command=command, font=('Segoe UI', 10, 'bold'),
                     bg='#E6F3F3' if secondary else TEAL, fg=TEAL if secondary else 'white',
                     activebackground='#BFE5E3' if secondary else '#066B70',
                     activeforeground=TEAL if secondary else 'white', bd=0, relief='flat',
                     cursor='hand2', padx=16, pady=9, **kw)


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.body = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window((0,0), window=self.body, anchor='nw')
        self.body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(self.window, width=e.width))
        self.bind('<Destroy>', self._cleanup, add='+')
        self._wheel_id = self.winfo_toplevel().bind('<MouseWheel>', self._wheel, add='+')

    def _wheel(self, event):
        widget = event.widget
        while widget is not None:
            if widget == self:
                self.canvas.yview_scroll(int(-event.delta/120), 'units'); break
            widget = getattr(widget, 'master', None)

    def _cleanup(self, event):
        if event.widget == self and self._wheel_id:
            self.winfo_toplevel().unbind('<MouseWheel>', self._wheel_id)


def table(parent, columns):
    frame = tk.Frame(parent, bg='white')
    frame.pack(fill='both', expand=True, pady=(12,0))
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show='headings', selectmode='browse')
    for key, title, width in columns:
        tree.heading(key, text=title)
        tree.column(key, width=width, minwidth=width, stretch=True)
    vs = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    hs = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
    tree.grid(row=0,column=0,sticky='nsew'); vs.grid(row=0,column=1,sticky='ns'); hs.grid(row=1,column=0,sticky='ew')
    frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
    tree.tag_configure('PROGRAMADA', foreground='#946000', background='#FFFAED')
    tree.tag_configure('ATENDIDA', foreground='#087A61', background='#EDFAF4')
    tree.tag_configure('CANCELADA', foreground='#A33E4F', background='#FFF1F3')
    return tree


def configure_style(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', font=('Segoe UI',10))
    style.configure('Treeview', rowheight=40, background='white', fieldbackground='white', foreground=INK, borderwidth=0)
    style.configure('Treeview.Heading', font=('Segoe UI',10,'bold'), background='#E7EFF4', foreground=INK, padding=10)
    style.map('Treeview', background=[('selected','#C6E9E7')], foreground=[('selected',INK)])
    style.configure('TCombobox', padding=7)
    style.configure('TEntry', padding=7)