"""Canvas chart drawing. Pure drawing: takes data, knows nothing about the database."""
import calendar
from . import theme

def donut(canvas, parts, size=190, width=26, center=None):
    """parts: [{'amount': float, ...}]. center: (caption, value) text."""
    canvas.delete("all")
    pad = width // 2 + 4
    box = (pad, pad, size - pad, size - pad)
    total = sum(p["amount"] for p in parts)
    if total <= 0:
        canvas.create_arc(*box, start=0, extent=359.9, style="arc", width=width, outline=theme.BORDER)
    else:
        start = 90
        for i, p in enumerate(parts):
            extent = -360 * p["amount"] / total
            if abs(extent) > 0.1:
                canvas.create_arc(*box, start=start, extent=extent, style="arc",
                                  width=width, outline=theme.PALETTE[i % len(theme.PALETTE)])
            start += extent
    if center:
        canvas.create_text(size / 2, size / 2 - 9, text=center[0], fill=theme.MUTED,
                           font=(theme.FONT, 9))
        canvas.create_text(size / 2, size / 2 + 9, text=center[1], fill=theme.TEXT,
                           font=(theme.FONT, 11, "bold"))

def bars(canvas, months, w=340, h=190):
    """months: [{'month': 'YYYY-MM', 'income': x, 'spending': y}]"""
    canvas.delete("all")
    if not months:
        canvas.create_text(w / 2, h / 2, text="No activity yet", fill=theme.MUTED,
                           font=(theme.FONT, 10))
        return
    peak = max(max(m["income"], m["spending"]) for m in months) or 1
    slot, base, top = w / len(months), h - 24, 10
    bw = min(18, slot / 3)
    for i, m in enumerate(months):
        x = slot * i + slot / 2
        for dx, key, color in ((-bw - 1, "income", theme.PRIMARY), (1, "spending", theme.PRIMARY_LT2)):
            bh = (base - top) * m[key] / peak
            canvas.create_rectangle(x + dx, base - bh, x + dx + bw, base, fill=color, width=0)
        canvas.create_text(x, h - 10, fill=theme.MUTED, font=(theme.FONT, 9),
                           text=calendar.month_abbr[int(m["month"][5:])])