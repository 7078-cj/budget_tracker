"""Reusable building blocks: lbl(), Card, Form, Table, money()."""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BORDER, CARD, FONT, MUTED, TEXT

def money(v):
    return f"₱{v:,.2f}"

def lbl(parent, text, size=10, bold=False, fg=TEXT, bg=CARD):
    return tk.Label(parent, text=text, bg=bg, fg=fg,
                    font=(FONT, size, "bold" if bold else "normal"))

class Card(tk.Frame):
    """A bordered panel. Put children in `card.body`."""
    def __init__(self, master, bg=CARD, pad=16):
        super().__init__(master, bg=bg, bd=0, highlightthickness=1,
                         highlightbackground=BORDER if bg == CARD else bg)
        self.body = tk.Frame(self, bg=bg)
        self.body.pack(fill="both", expand=True, padx=pad, pady=pad)

class Form(tk.Frame):
    """fields: [(key, label, choices|None, default)]"""
    def __init__(self, master, fields, on_submit, button="Add"):
        super().__init__(master, bg=CARD)
        self.vars, self.widgets, self.on_submit = {}, {}, on_submit
        for i, (key, label, choices, default) in enumerate(fields):
            cell = tk.Frame(self, bg=CARD)
            cell.grid(row=0, column=i, padx=(0, 12))
            lbl(cell, label, 9, fg=MUTED).pack(anchor="w")
            var = self.vars[key] = tk.StringVar(value=default)
            w = self.widgets[key] = (
                ttk.Combobox(cell, textvariable=var, values=choices, state="readonly", width=18)
                if choices is not None else ttk.Entry(cell, textvariable=var, width=18))
            w.pack(fill="x")
        ttk.Button(self, text=button, style="Primary.TButton",
                   command=self._submit).grid(row=0, column=len(fields), sticky="s")

    def set_choices(self, key, choices):
        self.widgets[key]["values"] = choices
        if choices and self.vars[key].get() not in choices:
            self.vars[key].set(choices[0])

    def _submit(self):
        try:
            self.on_submit({k: v.get().strip() for k, v in self.vars.items()})
        except (ValueError, sqlite3.IntegrityError) as e:
            messagebox.showerror("Can't save", str(e))

class Table(ttk.Treeview):
    """columns: [(key, heading, width)]. Rows are dicts with an 'id'."""
    def __init__(self, master, columns):
        super().__init__(master, columns=[c[0] for c in columns], show="headings")
        for key, heading, width in columns:
            self.heading(key, text=heading, anchor="w")
            self.column(key, width=width, anchor="w")

    def load(self, rows):
        self.delete(*self.get_children())
        for r in rows:
            self.insert("", "end", iid=str(r["id"]), values=[r[c] for c in self["columns"]])

    def selected_id(self):
        sel = self.selection()
        return int(sel[0]) if sel else None