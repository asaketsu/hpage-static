#!/usr/bin/env python3
"""Convert Markdown note to styled HTML with inline CSS."""

import markdown
import sys

MD_PATH = sys.argv[1]
HTML_PATH = sys.argv[2]

with open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

# Convert markdown → HTML body
# extensions: tables, fenced_code, toc
html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "toc", "nl2br"],
)

# Build full HTML with inline CSS
html_full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>扩散模型（Diffusion Model）深度研究笔记</title>
<style>
/* ── Reset & Base ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html {{
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
}}

body {{
  background-color: #f8f9fa;
  color: #2c3e50;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
               "Noto Sans SC", system-ui, -apple-system, "Segoe UI",
               sans-serif;
  line-height: 1.8;
  padding: 2rem 1rem;
}}

/* ── Layout ── */
.container {{
  max-width: 800px;
  margin: 0 auto;
  background: #ffffff;
  padding: 2.5rem 3rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}}

@media (max-width: 640px) {{
  body {{ padding: 0.5rem; }}
  .container {{ padding: 1.25rem 1rem; border-radius: 0; }}
}}

/* ── Typography ── */
h1 {{
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a2e;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 3px solid #e74c3c;
}}

h2 {{
  font-size: 1.4rem;
  font-weight: 700;
  color: #1a1a2e;
  padding-bottom: 0.35rem;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #dee2e6;
}}

h3 {{
  font-size: 1.15rem;
  font-weight: 600;
  color: #34495e;
  margin-top: 1.8rem;
  margin-bottom: 0.6rem;
}}

p {{
  margin-bottom: 0.9rem;
}}

strong {{
  color: #c0392b;
  font-weight: 600;
}}

a {{
  color: #2980b9;
  text-decoration: none;
}}
a:hover {{
  text-decoration: underline;
}}

/* ── Lists ── */
ul, ol {{
  padding-left: 1.6rem;
  margin-bottom: 0.9rem;
}}
li {{
  margin-bottom: 0.3rem;
}}

/* ── Code ── */
code {{
  background: #f1f3f5;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
  font-family: "SF Mono", "Fira Code", "JetBrains Mono", Consolas,
               "Liberation Mono", Menlo, monospace;
  color: #d63384;
}}

pre {{
  background: #f1f3f5;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem 1.25rem;
  overflow-x: auto;
  margin-bottom: 1rem;
  line-height: 1.5;
}}

pre code {{
  background: none;
  padding: 0;
  border-radius: 0;
  font-size: 0.85rem;
  color: #2c3e50;
}}

/* ── Tables ── */
table {{
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.2rem;
  font-size: 0.92rem;
}}

th, td {{
  border: 1px solid #dee2e6;
  padding: 0.55rem 0.75rem;
  text-align: left;
  vertical-align: top;
}}

th {{
  background: #e9ecef;
  font-weight: 600;
  color: #1a1a2e;
}}

/* zebra stripes */
tbody tr:nth-child(even) {{
  background: #f8f9fa;
}}
tbody tr:nth-child(odd) {{
  background: #ffffff;
}}

tbody tr:hover {{
  background: #eef5ff;
}}

/* ── Blockquote ── */
blockquote {{
  border-left: 4px solid #2980b9;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
  background: #f0f7ff;
  color: #34495e;
}}

/* ── HR ── */
hr {{
  border: none;
  border-top: 1px solid #dee2e6;
  margin: 2rem 0;
}}

/* ── Metadata line (first block after h1) ── */
</style>
</head>
<body>
<div class="container">
{html_body}
</div>
</body>
</html>"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_full)

print(f"✅ HTML written to {HTML_PATH}")
