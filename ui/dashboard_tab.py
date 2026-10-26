import tkinter as tk
from tkinter import ttk
from core import events, settings, stats
from core.allocation import REST_LABEL
from . import charts
from .theme import (BAD, BG, CARD, GOOD, MUTED, PALETTE, PRIMARY, PRIMARY_DK,
                    PRIMARY_LT, PRIMARY_LT2, PRIMARY_MID, TEXT)
from .widgets import Card, Segmented, lbl, money

SIGN = {"bank": 1, "cash": 1, "spending": -1}

BASES = [("both", "Both"), ("bank", "Bank"), ("cash", "Cash on hand")]
BASE_TEXT = {"both": "your bank + cash on hand", "bank": "your bank", "cash": "your cash on hand"}

# (allocation label, title, caption, accent)
HIGHLIGHTS = [
    ("Guilt-free", "Guilt-free money", "you can spend right now", "#60A5FA"),
    ("Investment", "Money to invest", "available to invest", PRIMARY),
    ("Emergency fund", "Emergency fund", "to put in your emergency fund", PRIMARY_DK),
    (REST_LABEL, "Needs & bills", "for bills & essentials", "#64748B"),
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
        card = Card(self, bg=PRIMARY, pad=20)
        b = card.body
        lbl(b, "Money on hand (bank + cash)", 10, fg="#BFDBFE", bg=PRIMARY).pack(anchor="w")
        lbl(b, money(s["total"]), 30, True, "white", PRIMARY).pack(anchor="w", pady=(2, 14))
        row = tk.Frame(b, bg=PRIMARY)
        row.pack(fill="x")
        for label, key in (("In the bank", "bank"), ("Cash on hand", "cash"), ("Spent so far", "spent")):
            box = tk.Frame(row, bg=PRIMARY_MID)
            box.pack(side="left", expand=True, fill="x", padx=(0, 8))
            lbl(box, label, 9, fg="#DBEAFE", bg=PRIMARY_MID).pack(anchor="w", padx=12, pady=(8, 0))
            lbl(box, money(s[key]), 13, True, "white", PRIMARY_MID).pack(anchor="w", padx=12, pady=(0, 8))
        return card

    def _highlights(self, s):
        """The chosen money (both / bank / cash), split: guilt-free, investing, emergency fund, bills."""
        wrap = ttk.Frame(self)
        base, avail = s["base"], s["available"]
        head = (f"Plan based on {BASE_TEXT[base]}: {money(avail)}" if avail > 0
                else f"Nothing available in {BASE_TEXT[base]} yet. Add money to see your plan.")
        lbl(wrap, head, 11, True, TEXT, BG).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ctrl = tk.Frame(wrap, bg=BG)
        ctrl.grid(row=0, column=2, columnspan=2, sticky="e", pady=(0, 6))
        lbl(ctrl, "Calculate from", 9, fg=MUTED, bg=BG).pack(side="left", padx=(0, 8))
        Segmented(ctrl, BASES, base, lambda v: settings.put("calc_base", v)).pack(side="left")
        by_label = {p["label"]: p for p in s["allocation"]}
        for i, (key, title, caption, accent) in enumerate(HIGHLIGHTS):
            wrap.columnconfigure(i, weight=1, uniform="hl")
            p = by_label[key]
            card = Card(wrap, pad=0)
            card.grid(row=1, column=i, sticky="nsew", padx=(0, 8) if i < len(HIGHLIGHTS) - 1 else 0)
            tk.Frame(card.body, bg=accent, height=4).pack(fill="x")
            inner = tk.Frame(card.body, bg=CARD)
            inner.pack(fill="both", padx=14, pady=10)
            top = tk.Frame(inner, bg=CARD)
            top.pack(fill="x")
            lbl(top, title, 10, True).pack(side="left")
            tk.Label(top, text=f"{p['percent']:g}%", bg=PRIMARY_LT, fg=PRIMARY_DK,
                     font=("Segoe UI", 9, "bold"), padx=8).pack(side="right")
            lbl(inner, money(p["amount"]), 17, True, accent).pack(anchor="w", pady=(6, 0))
            lbl(inner, caption, 9, fg=MUTED).pack(anchor="w")
            if key == "Emergency fund":
                lo, hi = stats.emergency_target()
                note = (f"Goal: {money(lo)} to {money(hi)} (3 to 6 months of spending)"
                        if hi else "Add spending to see your 3 to 6 month goal")
                tk.Label(inner, text=note, bg=CARD, fg=MUTED, font=("Segoe UI", 9),
                         wraplength=190, justify="left").pack(anchor="w", pady=(6, 0))
        return wrap

    def _allocation(self, s):
        card = Card(self)
        b = card.body
        lbl(b, "How your money is split", 12, True).pack(anchor="w", pady=(0, 8))
        canvas = tk.Canvas(b, width=190, height=190, bg=CARD, highlightthickness=0)
        canvas.pack()
        charts.donut(canvas, s["allocation"], center=("Money", money(max(s["available"], 0))))
        for i, p in enumerate(s["allocation"]):
            row = tk.Frame(b, bg=CARD)
            row.pack(fill="x", pady=2)
            tk.Frame(row, bg=PALETTE[i % len(PALETTE)], width=10, height=10).pack(side="left", padx=(0, 8))
            lbl(row, p["label"], 9).pack(side="left")
            lbl(row, f"{p['percent']:g}%  ·  {money(p['amount'])}", 9, fg=MUTED).pack(side="right")
        return card

    def _monthly(self):
        card = Card(self)
        b = card.body
        lbl(b, "Money added vs spending", 12, True).pack(anchor="w", pady=(0, 8))
        canvas = tk.Canvas(b, width=340, height=190, bg=CARD, highlightthickness=0)
        canvas.pack()
        charts.bars(canvas, stats.monthly())
        legend = tk.Frame(b, bg=CARD)
        legend.pack(pady=8)
        for text, color in (("Money added", PRIMARY), ("Spending", PRIMARY_LT2)):
            tk.Frame(legend, bg=color, width=10, height=10).pack(side="left", padx=(8, 4))
            lbl(legend, text, 9, fg=MUTED).pack(side="left")
        return card

    def _recent(self):
        card = Card(self)
        b = card.body
        lbl(b, "Recent transactions", 12, True).pack(anchor="w", pady=(0, 8))
        rows = stats.recent(4)
        if not rows:
            lbl(b, "Nothing yet. Add a transaction.", 10, fg=MUTED).pack(anchor="w")
        for t in rows:
            sign = SIGN[t["type"]]
            row = tk.Frame(b, bg=CARD)
            row.pack(fill="x", pady=4)
            left = tk.Frame(row, bg=CARD)
            left.pack(side="left")
            lbl(left, t["account"], 10, True).pack(anchor="w")
            lbl(left, t["date"], 8, fg=MUTED).pack(anchor="w")
            lbl(row, f"{'+' if sign > 0 else '-'}{money(t['amount'])}", 10, True,
                GOOD if sign > 0 else BAD).pack(side="right")
        return card