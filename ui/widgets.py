"""Reusable building blocks: lbl, Card, Form, Segmented, Table, money()."""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from . import theme

def money(v):
    return f"₱{v:,.2f}"

def lbl(parent, text, size=10, bold=False, fg=None, bg=None):
    return tk.Label(parent, text=text, bg=bg or theme.CARD, fg=fg or theme.TEXT,
                    font=(theme.FONT, size, "bold" if bold else "normal"))


class Card(tk.Frame):
    """A bordered panel. Put children in `card.body`."""
    def __init__(self, master, bg=None, pad=16):
        bg = bg or theme.CARD
        super().__init__(master, bg=theme.SHADOW, bd=0, highlightthickness=0)
        self.surface = tk.Frame(self, bg=bg, bd=0, highlightthickness=1,
                                highlightbackground=theme.BORDER if bg == theme.CARD else theme.PRIMARY_MID)
        self.surface.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 3))
        tk.Frame(self.surface, bg=theme.PRIMARY_LT, height=1).pack(fill="x")
        self.body = tk.Frame(self.surface, bg=bg)
        self.body.pack(fill="both", expand=True, padx=pad, pady=pad)


class GlassSlider(tk.Canvas):
    """A compact, keyboard-accessible slider styled to match the glass surfaces."""
    def __init__(self, master, value, command, resolution=0.1):
        super().__init__(master, height=30, bg=theme.CARD, highlightthickness=0,
                         bd=0, cursor="hand2", takefocus=True)
        self.value = float(value)
        self.command = command
        self.resolution = resolution
        self.bind("<Configure>", lambda _event: self._draw())
        self.bind("<Button-1>", self._pointer_changed)
        self.bind("<B1-Motion>", self._pointer_changed)
        self.bind("<Left>", lambda _event: self._step(-1))
        self.bind("<Down>", lambda _event: self._step(-1))
        self.bind("<Right>", lambda _event: self._step(1))
        self.bind("<Up>", lambda _event: self._step(1))
        self.bind("<Home>", lambda _event: self.set(0, notify=True))
        self.bind("<End>", lambda _event: self.set(100, notify=True))
        self.bind("<FocusIn>", lambda _event: self._draw())
        self.bind("<FocusOut>", lambda _event: self._draw())
        self._draw()

    def set(self, value, notify=False):
        self.value = min(100.0, max(0.0, round(float(value) / self.resolution) * self.resolution))
        self._draw()
        if notify:
            self.command(self.value)

    def _step(self, direction):
        self.set(self.value + direction * self.resolution, notify=True)
        return "break"

    def _pointer_changed(self, event):
        self.focus_set()
        width = max(self.winfo_width() - 28, 1)
        value = (event.x - 14) / width * 100
        self.set(value, notify=True)

    def _draw(self):
        self.delete("all")
        width = max(self.winfo_width(), 80)
        height = max(self.winfo_height(), 30)
        left, right, center_y = 12, width - 12, height / 2
        knob_x = left + (right - left) * self.value / 100
        self.create_line(left, center_y, right, center_y, fill=theme.SURFACE_ALT,
                         width=8, capstyle="round")
        self.create_line(left, center_y, knob_x, center_y, fill=theme.PRIMARY,
                         width=8, capstyle="round")
        radius = 8
        if self.focus_get() == self:
            self.create_oval(knob_x - 11, center_y - 11, knob_x + 11, center_y + 11,
                             fill=theme.PRIMARY_LT, outline="")
        self.create_oval(knob_x - radius, center_y - radius, knob_x + radius, center_y + radius,
                         fill=theme.CARD, outline=theme.PRIMARY, width=3)

class Form(tk.Frame):
    """fields: [(key, label, choices|None, default)]"""
    def __init__(self, master, fields, on_submit, button="Add"):
        super().__init__(master, bg=theme.CARD)
        self.vars, self.widgets, self.labels, self.on_submit = {}, {}, {}, on_submit
        self.cells = []
        for i, (key, label, choices, default) in enumerate(fields):
            cell = tk.Frame(self, bg=theme.CARD)
            self.cells.append(cell)
            self.labels[key] = lbl(cell, label, 9, fg=theme.MUTED)
            self.labels[key].pack(anchor="w")
            var = self.vars[key] = tk.StringVar(value=default)
            w = self.widgets[key] = (
                ttk.Combobox(cell, textvariable=var, values=choices, state="readonly", width=18)
                if choices is not None else ttk.Entry(cell, textvariable=var, width=18))
            w.pack(fill="x")
        self.button = ttk.Button(self, text=button, style="Primary.TButton",
                                 command=self._submit)
        self._columns = None
        self.bind("<Configure>", self._arrange)
        self.after_idle(lambda: self._arrange())

    def _arrange(self, event=None):
        width = event.width if event else self.winfo_width()
        if width <= 1:
            return
        cell_width = max((cell.winfo_reqwidth() for cell in self.cells), default=160)
        columns = max(1, min(len(self.cells) + 1, width // (cell_width + 12)))
        if columns == self._columns:
            return
        self._columns = columns
        for col in range(len(self.cells) + 1):
            self.columnconfigure(col, weight=1 if col < columns else 0)
        for index, cell in enumerate(self.cells):
            cell.grid(row=index // columns, column=index % columns, sticky="ew",
                      padx=(0, 12), pady=(0, 6))
        button_index = len(self.cells)
        self.button.grid(row=button_index // columns, column=button_index % columns,
                         sticky="s", pady=(0, 6))

    def set_label(self, key, text):
        self.labels[key].config(text=text)

    def set_choices(self, key, choices):
        self.widgets[key]["values"] = choices
        if choices and self.vars[key].get() not in choices:
            self.vars[key].set(choices[0])

    def _submit(self):
        try:
            self.on_submit({k: v.get().strip() for k, v in self.vars.items()})
        except (ValueError, sqlite3.IntegrityError) as e:
            messagebox.showerror("Can't save", str(e))

class Segmented(tk.Frame):
    """Pill-style selector. options: [(value, label)]. Calls on_change(value) when clicked."""
    def __init__(self, master, options, value, on_change):
        super().__init__(master, bg=theme.SURFACE_ALT, highlightthickness=1,
                         highlightbackground=theme.BORDER)
        for val, text in options:
            on = val == value
            b = tk.Label(self, text=text, font=(theme.FONT, 9, "bold"), padx=12, pady=5, cursor="hand2",
                         bg=theme.PRIMARY if on else theme.SURFACE_ALT,
                         fg="white" if on else theme.MUTED)
            b.pack(side="left", padx=2, pady=2)
            b.bind("<Button-1>", lambda e, v=val: on_change(v))

class Table(ttk.Treeview):
    """columns: [(key, heading, width)]. Rows are dicts with an 'id'."""
    def __init__(self, master, columns):
        super().__init__(master, columns=[c[0] for c in columns], show="headings")
        self.tag_configure("row_even", background=theme.CARD)
        self.tag_configure("row_odd", background=theme.SURFACE_ALT)
        for key, heading, width in columns:
            self.heading(key, text=heading, anchor="w")
            self.column(key, width=width, anchor="w")

    def load(self, rows):
        self.delete(*self.get_children())
        self.tag_configure("row_even", background=theme.CARD)
        self.tag_configure("row_odd", background=theme.SURFACE_ALT)
        for index, r in enumerate(rows):
            self.insert("", "end", iid=str(r["id"]), values=[r[c] for c in self["columns"]],
                        tags=("row_even" if index % 2 == 0 else "row_odd",))

    def selected_id(self):
        sel = self.selection()
        return int(sel[0]) if sel else None