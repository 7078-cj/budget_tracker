"""Single source of truth for colors, fonts and ttk styling."""
from tkinter import ttk

BG, CARD, BORDER = "#EEF3FB", "#FFFFFF", "#E2E8F0"
TEXT, MUTED = "#0F172A", "#64748B"
PRIMARY, PRIMARY_DK, PRIMARY_MID = "#2563EB", "#1E40AF", "#3B82F6"
PRIMARY_LT, PRIMARY_LT2 = "#DBEAFE", "#93C5FD"
GOOD, BAD, BAD_LT = "#16A34A", "#DC2626", "#FEE2E2"
FONT = "Segoe UI"
PALETTE = ["#1E40AF", "#2563EB", "#60A5FA", "#93C5FD", "#CBD5E1"]

def apply(root):
    root.configure(bg=BG)
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=TEXT, font=(FONT, 10))
    s.configure("TFrame", background=BG)
    s.configure("Primary.TButton", background=PRIMARY, foreground="white",
                borderwidth=0, padding=(16, 8), font=(FONT, 10, "bold"))
    s.map("Primary.TButton", background=[("active", PRIMARY_DK)])
    s.configure("Danger.TButton", background=BAD_LT, foreground=BAD,
                borderwidth=0, padding=(14, 7), font=(FONT, 10, "bold"))
    s.map("Danger.TButton", background=[("active", "#FECACA")])
    s.configure("TEntry", fieldbackground="white", bordercolor=BORDER, padding=6)
    s.configure("TCombobox", fieldbackground="white", bordercolor=BORDER,
                padding=6, arrowcolor=PRIMARY)
    s.map("TCombobox", fieldbackground=[("readonly", "white")])
    s.configure("Treeview", background=CARD, fieldbackground=CARD, rowheight=36,
                borderwidth=0, font=(FONT, 10))
    s.configure("Treeview.Heading", background=PRIMARY_LT, foreground=PRIMARY_DK,
                relief="flat", font=(FONT, 10, "bold"), padding=8)
    s.map("Treeview.Heading", background=[("active", PRIMARY_LT)])
    s.map("Treeview", background=[("selected", PRIMARY_LT)],
          foreground=[("selected", TEXT)])