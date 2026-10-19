#!/usr/bin/env python3
"""Convert Open Design analysis MD to tech-blue styled HTML."""

import markdown
import re

SRC = "/home/ubot/uclaw/bookmarks/notes/2026-05-03-open-design-analysis.md"
DST = "/home/ubot/uclaw/bookmarks/notes/2026-05-03-open-design-analysis_tech-blue.html"

# ---------- read source ----------
with open(SRC, "r", encoding="utf-8") as f:
    raw = f.read()

# ---------- strip leading ideographic spaces (全角空格) from each line ----------
lines = raw.split("\n")
cleaned_lines = [re.sub(r"^\u3000+", "", line) for line in lines]
md_text = "\n".join(cleaned_lines)

# ---------- extract front-matter (title / meta) ----------
title_match = re.search(r"^# (.+)$", md_text, re.M)
title = title_match.group(1).strip() if title_match else "Open Design Analysis"

date_match = re.search(r"\*\*日期\*\*[：:]\s*(.+)", md_text)
type_match = re.search(r"\*\*类型\*\*[：:]\s*(.+)", md_text)
rel_match  = re.search(r"\*\*关联\*\*[：:]\s*(.+)", md_text)

date_val = date_match.group(1).strip() if date_match else ""
type_val = type_match.group(1).strip() if type_match else ""
rel_val  = rel_match.group(1).strip() if rel_match else ""

# ---------- build body MD (skip h1 + meta + first ---) ----------
# Find body start: after the first --- separator
parts = re.split(r"\n---\n", md_text, maxsplit=1)
if len(parts) > 1:
    body_md = parts[1]
else:
    body_md = md_text

# Remove trailing --- and source lines at bottom
body_md = re.sub(r"\n---\s*\n\*分析来源.*$", "", body_md, flags=re.DOTALL)

# ---------- convert with Python markdown ----------
html_body = markdown.markdown(body_md, extensions=["extra", "nl2br"])

# ---------- post-process: wrap **① 有利进化（已落实）** style headings in divs ----------
# Add insight-box class to specific patterns
# Wrap bold lines that act as sub-headers inside h2 sections
def add_insight_boxes(html):
    # Wrap "①" "②" "③" sub-headings
    html = re.sub(
        r"<p><strong>([①②③][^<]*)</strong></p>",
        r'<p class="sub-heading">\1</p>',
        html
    )
    # Wrap "短期" "中期" "长期" bold labels
    html = re.sub(
        r"<p><strong>(短|中|长)期（[^）]+）</strong>[：:]?\s*(.*?)</p>",
        r'<p class="sub-heading">\1（\2）</p>\n<p>\3</p>',
        html
    )
    # Also handle lines like **短期（1 个月）**：xxx
    # Fix: handle bold label + colon + text all in one <p>
    def _forecast_repl(m):
        period = m.group(1)
        timeframe = m.group(2)
        rest = m.group(3)
        return f'<p class="sub-heading">{period}期（{timeframe}）</p>\n<p>{rest}</p>'
    html = re.sub(
        r"<p><strong>(短|中|长)期（([^）]+)）</strong>[：:](.*?)</p>",
        _forecast_repl,
        html
    )
    return html

html_body = add_insight_boxes(html_body)

# ---------- also convert the source/footer text ----------
footer_text_match = re.search(r"\*分析来源：(.+?)\*\s*\n\*下次更新：(.+?)\*", raw)
footer_source = footer_text_match.group(1).strip() if footer_text_match else ""
footer_update = footer_text_match.group(2).strip() if footer_text_match else ""

# ---------- build full HTML ----------
# Parse relation links for tags
rel_tags = re.findall(r"\[\[([^\]]+)\]\]", rel_val)

tags_html = ""
for t in rel_tags:
    tags_html += f'<span class="tag">{t}</span>\n            '

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
/* ===== tech-blue global ===== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ font-size: 15px; }}
body {{
    background: #0a0e1a;
    color: #c8d6e5;
    font-family: "SF Mono", "Fira Code", "Microsoft YaHei", monospace;
    line-height: 1.75;
    padding: 2rem 1rem;
}}
.wrap {{
    max-width: 680px;
    margin: 0 auto;
}}

/* ===== h1 ===== */
h1 {{
    color: #00d4ff;
    font-size: 1.65rem;
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: .02em;
    border-bottom: 2px solid #1a2744;
    padding-bottom: .6rem;
}}

/* ===== h2 ===== */
h2 {{
    color: #00d4ff;
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 2.2rem;
    margin-bottom: .7rem;
    padding-left: .55rem;
    border-left: 3px solid #00d4ff;
}}

/* ===== header-info ===== */
.header-info {{
    border-left: 3px solid #00d4ff;
    background: linear-gradient(135deg, rgba(0,212,255,.08) 0%, rgba(0,212,255,.02) 100%);
    padding: .75rem 1rem;
    margin-bottom: 1.8rem;
    border-radius: 0 6px 6px 0;
    font-size: .88rem;
    color: #8fa8c8;
    line-height: 1.9;
}}
.header-info strong {{ color: #a0c4e8; }}

/* ===== tags ===== */
.tag {{
    display: inline-block;
    background: rgba(0,212,255,.12);
    color: #00d4ff;
    border: 1px solid rgba(0,212,255,.25);
    border-radius: 12px;
    padding: 2px 10px;
    font-size: .78rem;
    margin-right: 6px;
    margin-top: 4px;
}}

/* ===== paragraph ===== */
p {{
    margin-bottom: .85rem;
    color: #b8c9dc;
}}
p.sub-heading {{
    color: #00d4ff;
    font-weight: 600;
    margin-top: 1.2rem;
    margin-bottom: .4rem;
    font-size: .95rem;
}}

/* ===== quote ===== */
.quote {{
    border-left: 3px solid #00d4ff;
    background: rgba(0,212,255,.05);
    padding: .6rem 1rem;
    margin: 1rem 0 1.2rem;
    border-radius: 0 6px 6px 0;
    color: #d0e4f5;
    font-style: italic;
}}

/* ===== insight-box ===== */
.insight-box {{
    border: 1px solid rgba(0,212,255,.2);
    background: rgba(0,212,255,.04);
    border-radius: 6px;
    padding: .7rem 1rem;
    margin: 1rem 0 1.2rem;
    color: #c8ddf0;
}}

/* ===== em ===== */
em {{ color: #7faed4; }}

/* ===== strong ===== */
strong {{ color: #e0ecf8; }}

/* ===== hr ===== */
hr {{
    border: none;
    border-top: 1px dashed #1a2744;
    margin: 1.8rem 0;
}}

/* ===== footer ===== */
.footer {{
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px dashed #1a2744;
    font-size: .8rem;
    color: #5a7a9a;
    line-height: 1.9;
}}

/* ===== code ===== */
code {{
    background: rgba(0,212,255,.1);
    color: #00d4ff;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: .88em;
}}

/* ===== responsive ===== */
@media (max-width: 768px) {{
    html {{ font-size: 14px; }}
    body {{ padding: 1.2rem .6rem; }}
    h1 {{ font-size: 1.35rem; }}
    h2 {{ font-size: 1.05rem; }}
    .header-info {{ padding: .6rem .8rem; }}
}}
</style>
</head>
<body>
<div class="wrap">

<h1>{title}</h1>

<div class="header-info">
    <strong>日期</strong>：{date_val}<br>
    <strong>类型</strong>：{type_val}<br>
    <strong>关联</strong>：{tags_html}
</div>

{html_body}

<div class="footer">
    分析来源：{footer_source}<br>
    下次更新：{footer_update}
</div>

</div>
</body>
</html>
"""

with open(DST, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Written to {DST}")
