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
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.content = ttk.Frame(self.canvas)
        self.window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", self._update_scrollregion)
        self.canvas.bind("<Configure>", self._resize_content)
        self._layout = None
        events.subscribe(self.refresh)
        self.refresh()

    def _update_scrollregion(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)
        self._arrange(event.width)

    def refresh(self):
        for w in self.content.winfo_children():
            w.destroy()
        self._layout = None
        s = stats.summary()
        self.hero = self._hero(s)
        self.highlights = self._highlights(s)
        self.allocation = self._allocation(s)
        self.monthly = self._monthly()
        self.recent = self._recent()
        self._arrange(self.canvas.winfo_width())

    def _hero(self, s):
        card = Card(self.content, bg=theme.PRIMARY, pad=22)
        b = card.body
        lbl(b, "YOUR MONEY", 9, True, theme.PRIMARY_LT, theme.PRIMARY).pack(anchor="w")
        lbl(b, "Money on hand", 12, True, "white", theme.PRIMARY).pack(anchor="w", pady=(5, 0))
        lbl(b, money(s["total"]), 32, True, "white", theme.PRIMARY).pack(anchor="w", pady=(0, 16))
        row = tk.Frame(b, bg=theme.PRIMARY)
        row.pack(fill="x")
        self.metric_boxes = []
        for label, key in (("In the bank", "bank"), ("Cash on hand", "cash"), ("Spent so far", "spent")):
            box = tk.Frame(row, bg=theme.PRIMARY_MID, highlightthickness=1,
                           highlightbackground=theme.PRIMARY_LT)
            self.metric_boxes.append(box)
            lbl(box, label, 9, fg=theme.PRIMARY_LT, bg=theme.PRIMARY_MID).pack(anchor="w", padx=12, pady=(8, 0))
            lbl(box, money(s[key]), 13, True, "white", theme.PRIMARY_MID).pack(anchor="w", padx=12, pady=(0, 8))
        return card

    def _highlights(self, s):
        """The chosen money (both / bank / cash), split: guilt-free, investing, emergency fund, bills."""
        wrap = ttk.Frame(self.content)
        base, avail = s["base"], s["available"]
        head = (f"Plan based on {BASE_TEXT[base]}: {money(avail)}" if avail > 0
                else f"Nothing available in {BASE_TEXT[base]} yet. Add money to see your plan.")
        self.plan_heading = tk.Label(wrap, text=head, font=(theme.FONT, 11, "bold"),
                                     fg=theme.TEXT, bg=theme.BG, justify="left", anchor="w")
        ctrl = tk.Frame(wrap, bg=theme.BG)
        self.plan_controls = ctrl
        lbl(ctrl, "Calculate from", 9, fg=theme.MUTED, bg=theme.BG).pack(side="left", padx=(0, 8))
        Segmented(ctrl, BASES, base, lambda v: settings.put("calc_base", v)).pack(side="left")
        by_label = {p["label"]: p for p in s["allocation"]}
        self.highlight_cards = []
        for i, (key, title, caption, accent) in enumerate(HIGHLIGHTS):
            p = by_label[key]
            accent = (theme.PRIMARY if accent == "primary" else
                      theme.PRIMARY_DK if accent == "primary_dark" else
                      theme.MUTED if accent == "muted" else accent)
            card = Card(wrap, pad=0)
            self.highlight_cards.append(card)
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
        card = Card(self.content)
        b = card.body
        lbl(b, "Allocation", 12, True).pack(anchor="w")
        lbl(b, "Your money by category", 9, fg=theme.MUTED).pack(anchor="w", pady=(2, 8))
        canvas = tk.Canvas(b, width=190, height=190, bg=theme.CARD, highlightthickness=0)
        canvas.pack(anchor="center")
        self.allocation_parts = s["allocation"]
        self.allocation_amount = max(s["available"], 0)
        self.donut_canvas = canvas
        b.bind("<Configure>", self._resize_donut)
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
        card = Card(self.content)
        b = card.body
        lbl(b, "Cash flow", 12, True).pack(anchor="w")
        lbl(b, "Money added vs spending", 9, fg=theme.MUTED).pack(anchor="w", pady=(2, 8))
        canvas = tk.Canvas(b, width=340, height=190, bg=theme.CARD, highlightthickness=0)
        canvas.pack(fill="x", expand=True)
        self.monthly_canvas = canvas
        self.monthly_data = stats.monthly()
        canvas.bind("<Configure>", self._resize_bars)
        legend = tk.Frame(b, bg=theme.CARD)
        legend.pack(pady=8)
        for text, color in (("Money added", theme.PRIMARY), ("Spending", theme.PRIMARY_LT2)):
            tk.Frame(legend, bg=color, width=10, height=10).pack(side="left", padx=(8, 4))
            lbl(legend, text, 9, fg=theme.MUTED).pack(side="left")
        return card

    def _recent(self):
        card = Card(self.content)
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

    def _arrange(self, width):
        if width <= 1:
            return
        main_columns = 3 if width >= 1050 else 2 if width >= 680 else 1
        highlight_columns = 4 if width >= 1000 else 2 if width >= 560 else 1
        metric_columns = 3 if width >= 600 else 1
        self.plan_heading.configure(wraplength=max(width - (340 if highlight_columns == 4 else 24),
                                                  180))
        layout = (main_columns, highlight_columns, metric_columns)
        if layout == self._layout:
            return
        self._layout = layout

        for col in range(3):
            self.content.columnconfigure(col, weight=1 if col < main_columns else 0,
                                         uniform="dashboard" if col < main_columns else "")
        self.hero.grid(row=0, column=0, columnspan=main_columns, sticky="nsew", pady=(0, 8))
        self.highlights.grid(row=1, column=0, columnspan=main_columns, sticky="nsew", pady=(0, 8))
        stacked_header = highlight_columns < 4
        for col in range(4):
            self.highlights.columnconfigure(
                col, weight=1 if col < highlight_columns else 0,
                uniform="highlights" if col < highlight_columns else "")
        for col, card in enumerate(self.highlight_cards):
            row = (2 if stacked_header else 1) + col // highlight_columns
            card.grid(row=row, column=col % highlight_columns, sticky="nsew",
                      padx=(0, 8) if col % highlight_columns < highlight_columns - 1 else 0,
                      pady=(0, 8))
        if stacked_header:
            self.plan_heading.grid(row=0, column=0, columnspan=highlight_columns,
                                   sticky="ew", pady=(0, 6))
            self.plan_controls.grid(row=1, column=0, columnspan=highlight_columns,
                                    sticky="w", pady=(0, 8))
        else:
            self.plan_heading.grid(row=0, column=0, columnspan=highlight_columns - 1,
                                   sticky="w", pady=(0, 8))
            self.plan_controls.grid(row=0, column=highlight_columns - 1,
                                    columnspan=1, sticky="e", pady=(0, 6))

        if main_columns == 3:
            self.allocation.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
            self.monthly.grid(row=2, column=1, sticky="nsew", padx=(0, 8))
            self.recent.grid(row=2, column=2, sticky="nsew")
        elif main_columns == 2:
            self.allocation.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
            self.monthly.grid(row=2, column=1, sticky="nsew")
            self.recent.grid(row=3, column=0, columnspan=2, sticky="nsew")
        else:
            self.allocation.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
            self.monthly.grid(row=3, column=0, sticky="nsew", pady=(0, 8))
            self.recent.grid(row=4, column=0, sticky="nsew")

        for col in range(3):
            self.metric_boxes[col].grid(row=0 if metric_columns == 3 else col,
                                        column=col if metric_columns == 3 else 0,
                                        sticky="nsew",
                                        padx=(0, 8) if metric_columns == 3 and col < 2 else 0,
                                        pady=1)
        for col in range(metric_columns):
            self.metric_boxes[0].master.columnconfigure(col, weight=1)
        self._resize_donut()
        self._resize_bars()

    def _resize_donut(self, _event=None):
        if not hasattr(self, "donut_canvas"):
            return
        width = self.donut_canvas.master.winfo_width()
        size = max(140, min(190, width - 32))
        self.donut_canvas.configure(width=size, height=size)
        charts.donut(self.donut_canvas, self.allocation_parts, size=size,
                     center=("Money", money(self.allocation_amount)))

    def _resize_bars(self, _event=None):
        if not hasattr(self, "monthly_canvas"):
            return
        width = max(self.monthly_canvas.winfo_width(), 240)
        charts.bars(self.monthly_canvas, self.monthly_data, w=width, h=190)