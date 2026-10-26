import tkinter as tk
from tkinter import ttk
from core import events, settings, stats
from core.allocation import REST_LABEL
from . import charts
from . import theme
from .widgets import Card, Segmented, lbl, money

SIGN = {"bank": 1, "cash": 1, "spending": -1}

BASES = [("both", "Both"), ("bank", "Bank"), ("cash", "Cash on hand")]
BASE_TEXT = {"both": "your bank + cash on hand", "bank": "your bank", "cash": "your cash on hand"}

# (allocation label, title, caption, accent)
HIGHLIGHTS = [
    ("Guilt-free", "Guilt-free money", "you can spend right now", "#60A5FA"),
    ("Investment", "Money to invest", "available to invest", "primary"),
    ("Emergency fund", "Emergency fund", "to put in your emergency fund", "primary_dark"),
    (REST_LABEL, "Needs & bills", "for bills & essentials", "muted"),
]

class DashboardTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        for c in range(3):
            self.columnconfigure(c, weight=1, uniform="col")
        self.rowconfigure(2, weight=1)
        events.subscribe(self.refresh)
        self.refresh()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        s = stats.summary()
        self._hero(s).grid(row=0, column=0, columnspan=3, sticky="nsew", pady=(0, 8))
        self._highlights(s).grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(0, 8))
        self._allocation(s).grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        self._monthly().grid(row=2, column=1, sticky="nsew", padx=(0, 8))
        self._recent().grid(row=2, column=2, sticky="nsew")

    def _hero(self, s):
        card = Card(self, bg=theme.PRIMARY, pad=22)
        b = card.body
        lbl(b, "YOUR MONEY", 9, True, theme.PRIMARY_LT, theme.PRIMARY).pack(anchor="w")
        lbl(b, "Money on hand", 12, True, "white", theme.PRIMARY).pack(anchor="w", pady=(5, 0))
        lbl(b, money(s["total"]), 32, True, "white", theme.PRIMARY).pack(anchor="w", pady=(0, 16))
        row = tk.Frame(b, bg=theme.PRIMARY)
        row.pack(fill="x")
        for label, key in (("In the bank", "bank"), ("Cash on hand", "cash"), ("Spent so far", "spent")):
            box = tk.Frame(row, bg=theme.PRIMARY_MID, highlightthickness=1,
                           highlightbackground=theme.PRIMARY_LT)
            box.pack(side="left", expand=True, fill="x", padx=(0, 9), pady=1)
            lbl(box, label, 9, fg=theme.PRIMARY_LT, bg=theme.PRIMARY_MID).pack(anchor="w", padx=12, pady=(8, 0))
            lbl(box, money(s[key]), 13, True, "white", theme.PRIMARY_MID).pack(anchor="w", padx=12, pady=(0, 8))
        return card

    def _highlights(self, s):
        """The chosen money (both / bank / cash), split: guilt-free, investing, emergency fund, bills."""
        wrap = ttk.Frame(self)
        base, avail = s["base"], s["available"]
        head = (f"Plan based on {BASE_TEXT[base]}: {money(avail)}" if avail > 0
                else f"Nothing available in {BASE_TEXT[base]} yet. Add money to see your plan.")
        lbl(wrap, head, 11, True, theme.TEXT, theme.BG).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ctrl = tk.Frame(wrap, bg=theme.BG)
        ctrl.grid(row=0, column=2, columnspan=2, sticky="e", pady=(0, 6))
        lbl(ctrl, "Calculate from", 9, fg=theme.MUTED, bg=theme.BG).pack(side="left", padx=(0, 8))
        Segmented(ctrl, BASES, base, lambda v: settings.put("calc_base", v)).pack(side="left")
        by_label = {p["label"]: p for p in s["allocation"]}
        for i, (key, title, caption, accent) in enumerate(HIGHLIGHTS):
            wrap.columnconfigure(i, weight=1, uniform="hl")
            p = by_label[key]
            accent = (theme.PRIMARY if accent == "primary" else
                      theme.PRIMARY_DK if accent == "primary_dark" else
                      theme.MUTED if accent == "muted" else accent)
            card = Card(wrap, pad=0)
            card.grid(row=1, column=i, sticky="nsew", padx=(0, 8) if i < len(HIGHLIGHTS) - 1 else 0)
            tk.Frame(card.body, bg=accent, height=4).pack(fill="x")
            inner = tk.Frame(card.body, bg=theme.CARD)
            inner.pack(fill="both", padx=14, pady=10)
            top = tk.Frame(inner, bg=theme.CARD)
            top.pack(fill="x")
            lbl(top, title, 10, True).pack(side="left")
            tk.Label(top, text=f"{p['percent']:g}%", bg=theme.PRIMARY_LT, fg=theme.TEXT,
                     font=("Segoe UI", 9, "bold"), padx=9, pady=3).pack(side="right")
            lbl(inner, money(p["amount"]), 18, True, accent).pack(anchor="w", pady=(10, 1))
            lbl(inner, caption, 9, fg=theme.MUTED).pack(anchor="w")
            if key == "Emergency fund":
                lo, hi = stats.emergency_target()
                note = (f"Goal: {money(lo)} to {money(hi)} (3 to 6 months of spending)"
                        if hi else "Add spending to see your 3 to 6 month goal")
                tk.Label(inner, text=note, bg=theme.CARD, fg=theme.MUTED, font=("Segoe UI", 9),
                         wraplength=190, justify="left").pack(anchor="w", pady=(6, 0))
        return wrap

    def _allocation(self, s):
        card = Card(self)
        b = card.body
        lbl(b, "Allocation", 12, True).pack(anchor="w")
        lbl(b, "Your money by category", 9, fg=theme.MUTED).pack(anchor="w", pady=(2, 8))
        canvas = tk.Canvas(b, width=190, height=190, bg=theme.CARD, highlightthickness=0)
        canvas.pack()
        charts.donut(canvas, s["allocation"], center=("Money", money(max(s["available"], 0))))
        for i, p in enumerate(s["allocation"]):
            row = tk.Frame(b, bg=theme.SURFACE_ALT)
            row.pack(fill="x", pady=3)
            dot = tk.Canvas(row, width=12, height=12, bg=theme.SURFACE_ALT, highlightthickness=0)
            dot.pack(side="left", padx=(10, 8), pady=8)
            dot.create_oval(2, 2, 10, 10, fill=theme.PALETTE[i % len(theme.PALETTE)], outline="")
            lbl(row, p["label"], 9, True).pack(side="left", pady=7)
            lbl(row, f"{p['percent']:g}%  ·  {money(p['amount'])}", 9,
                fg=theme.MUTED, bg=theme.SURFACE_ALT).pack(side="right", padx=10)
        return card

    def _monthly(self):
        card = Card(self)
        b = card.body
        lbl(b, "Cash flow", 12, True).pack(anchor="w")
        lbl(b, "Money added vs spending", 9, fg=theme.MUTED).pack(anchor="w", pady=(2, 8))
        canvas = tk.Canvas(b, width=340, height=190, bg=theme.CARD, highlightthickness=0)
        canvas.pack()
        charts.bars(canvas, stats.monthly())
        legend = tk.Frame(b, bg=theme.CARD)
        legend.pack(pady=8)
        for text, color in (("Money added", theme.PRIMARY), ("Spending", theme.PRIMARY_LT2)):
            tk.Frame(legend, bg=color, width=10, height=10).pack(side="left", padx=(8, 4))
            lbl(legend, text, 9, fg=theme.MUTED).pack(side="left")
        return card

    def _recent(self):
        card = Card(self)
        b = card.body
        lbl(b, "Recent transactions", 12, True).pack(anchor="w", pady=(0, 8))
        rows = stats.recent(4)
        if not rows:
            lbl(b, "Nothing yet. Add a transaction.", 10, fg=theme.MUTED).pack(anchor="w")
        for t in rows:
            sign = SIGN[t["type"]]
            row = tk.Frame(b, bg=theme.CARD)
            row.pack(fill="x", pady=4)
            left = tk.Frame(row, bg=theme.CARD)
            left.pack(side="left")
            lbl(left, t["account"], 10, True).pack(anchor="w")
            lbl(left, t["date"], 8, fg=theme.MUTED).pack(anchor="w")
            lbl(row, f"{'+' if sign > 0 else '-'}{money(t['amount'])}", 10, True,
                theme.GOOD if sign > 0 else theme.BAD).pack(side="right")
        return card