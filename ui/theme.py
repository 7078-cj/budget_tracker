"""Single source of truth for colors, fonts and ttk styling."""
import tkinter as tk
from tkinter import ttk

FONT = "Segoe UI"

PALETTES = {
    "light": {
        "BG": "#EAF0FB", "CARD": "#F8FAFF", "SURFACE_ALT": "#EEF3FC",
        "BORDER": "#D8E2F2", "SHADOW": "#DCE5F3",
        "TEXT": "#15213A", "MUTED": "#71809B",
        "PRIMARY": "#536DFE", "PRIMARY_DK": "#4056D8", "PRIMARY_MID": "#7188FF",
        "PRIMARY_LT": "#E4EAFE", "PRIMARY_LT2": "#A7B8FF",
        "GOOD": "#16A34A", "BAD": "#DC2626", "BAD_LT": "#FEE2E2",
        "PALETTE": ["#536DFE", "#29B6C8", "#9274F6", "#F1A55B", "#61B894"],
    },
    "night": {
        "BG": "#10172A", "CARD": "#1C2740", "SURFACE_ALT": "#202D49",
        "BORDER": "#344362", "SHADOW": "#0B1020",
        "TEXT": "#EDF2FF", "MUTED": "#9AA9C6",
        "PRIMARY": "#8194FF", "PRIMARY_DK": "#667AE8", "PRIMARY_MID": "#5269D1",
        "PRIMARY_LT": "#303B64", "PRIMARY_LT2": "#A7B8FF",
        "GOOD": "#4ADE80", "BAD": "#F87171", "BAD_LT": "#451A1A",
        "PALETTE": ["#8194FF", "#50D1D8", "#B19AFF", "#FFBD78", "#65D5A7"],
    },
}


def set_palette(mode):
    selected = PALETTES[mode if mode in PALETTES else "light"]
    globals().update(selected)


def apply(root, mode="light"):
    previous = {
        name: globals().get(name)
        for name in ("BG", "CARD", "SURFACE_ALT", "BORDER", "SHADOW", "TEXT", "MUTED",
                     "PRIMARY", "PRIMARY_DK", "PRIMARY_MID", "PRIMARY_LT", "PRIMARY_LT2",
                     "GOOD", "BAD", "BAD_LT", "PALETTE")
    }
    set_palette(mode)
    replacements = {
        value: globals()[name]
        for name, value in previous.items()
        if name != "PALETTE" and value is not None
    }
    replacements.update(zip(previous["PALETTE"] or [], PALETTE))

    def recolor(widget):
        for option in ("background", "foreground", "highlightbackground",
                       "highlightcolor", "troughcolor"):
            try:
                old_color = widget.cget(option)
                if old_color in replacements:
                    widget.configure(**{option: replacements[old_color]})
            except tk.TclError:
                continue
        for child in widget.winfo_children():
            recolor(child)

    recolor(root)
    root.configure(bg=BG)
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=TEXT, font=(FONT, 10))
    s.configure("TFrame", background=BG)
    s.configure("Primary.TButton", background=PRIMARY, foreground="white",
                borderwidth=0, padding=(16, 8), font=(FONT, 10, "bold"))
    s.map("Primary.TButton", background=[("active", PRIMARY_DK), ("pressed", PRIMARY_DK)])
    s.configure("Danger.TButton", background=BAD_LT, foreground=BAD,
                borderwidth=0, padding=(14, 7), font=(FONT, 10, "bold"))
    s.map("Danger.TButton", background=[("active", BORDER), ("pressed", BAD_LT)])
    s.configure("TEntry", fieldbackground=CARD, foreground=TEXT, bordercolor=BORDER,
                insertcolor=TEXT, padding=6)
    s.configure("TCombobox", fieldbackground=CARD, foreground=TEXT, bordercolor=BORDER,
                padding=6, arrowcolor=PRIMARY)
    s.map("TCombobox", fieldbackground=[("readonly", CARD)],
          foreground=[("readonly", TEXT)])
    s.configure("Treeview", background=CARD, fieldbackground=CARD, rowheight=36,
                foreground=TEXT, borderwidth=0, font=(FONT, 10))
    s.configure("Treeview.Heading", background=PRIMARY_LT, foreground=TEXT,
                relief="flat", font=(FONT, 10, "bold"), padding=8)
    s.map("Treeview.Heading", background=[("active", PRIMARY_LT)])
    s.map("Treeview", background=[("selected", PRIMARY_LT)],
          foreground=[("selected", TEXT)])