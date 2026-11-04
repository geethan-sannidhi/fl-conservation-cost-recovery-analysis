"""Minimal static SVG bar charts (no plotting dependency).

Static images in a Markdown report can't have hover, so every bar carries a value
label and each chart has a table in the report. Colors are the reference palette's
first three categorical slots, validated all-pairs (CVD dE >= 9.2, normal-vision
dE >= 24.0); aqua is below 3:1 contrast on the surface, which is why labels are always shown.
"""
import math
from html import escape

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"


def _svg(w, h, body, title, desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="t d" font-family="{FONT}">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>{body}</svg>\n')


def _text(x, y, s, size=12, fill=TEXT, anchor="start", weight="normal", halo=False):
    h = f' stroke="{SURFACE}" stroke-width="4" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{h}>{escape(s)}</text>')


def _bar(x, y, w, h, color):
    """Horizontal bar with 4px rounded data-end, square at the baseline."""
    w = max(w, 0.5)
    r = min(4, w, h / 2)
    return (f'<path d="M{x:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} '
            f'a{r},{r} 0 0 1 -{r},{r} h-{w - r:.1f} z" fill="{color}"/>')


def hbar(items, title, desc, value_fmt, x_max=None, ref_line=None, ref_label="", log=False,
         ticks=None, legend=None, label_w=300, width=820):
    """items: list of (label, value, color_index)."""
    row, top = 26, 58
    plot_w = width - label_w - 90
    h = top + row * len(items) + 44
    vmax = x_max or max(v for _, v, _ in items) * 1.1
    vmin = min(v for _, v, _ in items if v > 0) if log else 0
    lo = 10 ** math.floor(math.log10(vmin)) if log else 0

    def sx(v):
        if log:
            return plot_w * (math.log10(max(v, lo)) - math.log10(lo)) / (math.log10(vmax) - math.log10(lo))
        return plot_w * v / vmax

    b = [_text(16, 24, title, 15, weight="600")]
    if legend:
        lx = 16
        for i, name in enumerate(legend):
            b.append(f'<rect x="{lx}" y="36" width="10" height="10" rx="2" fill="{SERIES[i]}"/>')
            b.append(_text(lx + 15, 45, name, 12, TEXT_2))
            lx += 22 + 7.2 * len(name)
    x0 = label_w
    for t in (ticks or []):
        x = x0 + sx(t)
        b.append(f'<line x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{top + row * len(items)}" stroke="{GRID}"/>')
        b.append(_text(x, top + row * len(items) + 16, value_fmt(t), 11, TEXT_2, "middle"))
    if ref_line is not None:
        x = x0 + sx(ref_line)
        b.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{top + row * len(items)}" '
                 f'stroke="{TEXT}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        b.append(_text(x + 4, top - 12, ref_label, 11, TEXT_2))
    for i, (label, v, ci) in enumerate(items):
        y = top + i * row
        b.append(_text(x0 - 10, y + 15, label, 12, TEXT, "end"))
        w = sx(v)
        b.append(_bar(x0, y + 4, w, row - 8, SERIES[ci]))
        b.append(_text(x0 + w + 6, y + 15, value_fmt(v), 12, TEXT, halo=True))
    b.append(f'<line x1="{x0}" y1="{top - 6}" x2="{x0}" y2="{top + row * len(items)}" stroke="{TEXT_2}"/>')
    return _svg(width, h, "".join(b), title, desc)


def stacked100(items, title, desc, segment_names, label_w=200, width=820):
    """items: list of (label, [part values]). Bars normalized to 100%, 2px surface gap between segments."""
    row, top = 40, 62
    plot_w = width - label_w - 40
    h = top + row * len(items) + 20
    b = [_text(16, 24, title, 15, weight="600")]
    lx = 16
    for i, name in enumerate(segment_names):
        b.append(f'<rect x="{lx}" y="38" width="10" height="10" rx="2" fill="{SERIES[i]}"/>')
        b.append(_text(lx + 15, 47, name, 12, TEXT_2))
        lx += 26 + 6.8 * len(name)
    for i, (label, parts) in enumerate(items):
        y = top + i * row
        total = sum(parts)
        b.append(_text(label_w - 10, y + 20, label, 12, TEXT, "end"))
        x = label_w
        for j, p in enumerate(parts):
            w = plot_w * p / total
            gap = 2 if j < len(parts) - 1 else 0
            b.append(f'<rect x="{x:.1f}" y="{y + 6}" width="{max(w - gap, 0.5):.1f}" height="{row - 14}" '
                     f'rx="{4 if j == len(parts) - 1 else 0}" fill="{SERIES[j]}"/>')
            share = p / total
            if w > 46:
                b.append(_text(x + 6, y + 24, f"{share:.0%}", 12, "#ffffff" if j == 0 else TEXT, weight="600"))
            else:
                b.append(_text(x + w + 4, y + 24, f"{share:.0%}", 12, TEXT))
            x += w
    return _svg(width, h, "".join(b), title, desc)
