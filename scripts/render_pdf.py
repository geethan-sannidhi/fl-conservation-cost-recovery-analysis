"""Render docs/recommendation.md to docs/recommendation.html (print-styled); the PDF is made with
headless Chromium (see scripts/render_pdf.js). Optional: requires `pip install markdown`."""
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parents[1]
md = (ROOT / "docs" / "recommendation.md").read_text()
body = markdown.markdown(md, extensions=["tables"])
css = """
@page { size: Letter; margin: 0.8in 0.75in; }
body { font: 10.5pt/1.45 Georgia, 'Times New Roman', serif; color: #111; background: #fff; max-width: 7in; margin: 0 auto; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 12pt; }
h2 { font-size: 13pt; margin: 20pt 0 6pt; border-bottom: 1px solid #999; padding-bottom: 2pt; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 16pt 0 4pt; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font: 8.5pt/1.3 system-ui, sans-serif; break-inside: auto; }
th, td { border-bottom: 1px solid #ccc; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #f1f1ef; }
tr { break-inside: avoid; }
img { max-width: 100%; display: block; margin: 8pt auto; break-inside: avoid; }
hr { border: 0; border-top: 1px solid #bbb; margin: 14pt 0; }
code { font-size: 8.5pt; }
"""
html = f'<!doctype html><html><head><meta charset="utf-8"><title>2025 Conservation Program Review</title><style>{css}</style></head><body>{body}</body></html>'
(ROOT / "docs" / "recommendation.html").write_text(html)
print("wrote docs/recommendation.html")
