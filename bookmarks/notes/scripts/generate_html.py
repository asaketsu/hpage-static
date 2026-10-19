#!/usr/bin/env python3
"""Generate HTML version of markdown notes with proper styling."""

import markdown
import re
import sys
import os

def md_to_html(md_path, html_path, template_name, title, emoji, background_color, primary_color):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract body (skip YAML frontmatter if any)
    body_lines = md_content.split('\n')
    if body_lines[0] == '---':
        # Skip YAML frontmatter
        end_idx = body_lines.index('---', 1) + 1
        body_lines = body_lines[end_idx:]
    
    body_md = '\n'.join(body_lines)
    
    # Convert markdown to HTML
    html_body = markdown.markdown(body_md, extensions=['tables', 'fenced_code', 'toc', 'attr_list'])
    
    # Verify conversion
    h2_count = len(re.findall(r'<h2[^>]*>', html_body))
    if h2_count == 0:
        print(f"⚠️ Warning: No <h2> tags found in converted HTML for {md_path}")
    
    # Generate full HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, "SF Pro Display", "Microsoft YaHei", "PingFang SC", sans-serif;
            background-color: {background_color};
            color: #1a2332;
            line-height: 1.7;
            padding: 20px;
        }}
        .container {{
            max-width: 680px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            padding: 40px;
        }}
        h1 {{
            color: {primary_color};
            font-size: 1.8rem;
            margin-bottom: 12px;
            line-height: 1.3;
        }}
        .header-info {{
            border-left: 4px solid {primary_color};
            padding-left: 16px;
            margin-bottom: 24px;
            font-size: 0.9rem;
            color: #64748b;
        }}
        .header-info a {{ color: {primary_color}; }}
        .tag {{
            display: inline-block;
            background: {primary_color}15;
            color: {primary_color};
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 8px;
            margin-top: 8px;
        }}
        h2 {{
            color: {primary_color};
            font-size: 1.3rem;
            margin-top: 32px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid {primary_color}20;
        }}
        h3 {{
            color: #334155;
            font-size: 1.1rem;
            margin-top: 20px;
            margin-bottom: 12px;
        }}
        p {{ margin-bottom: 16px; }}
        blockquote {{
            border-left: 4px solid {primary_color};
            padding-left: 16px;
            margin: 16px 0;
            padding: 12px 16px;
            background: {primary_color}08;
            border-radius: 0 8px 8px 0;
        }}
        blockquote p {{ margin-bottom: 0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 0.9rem;
        }}
        th {{
            background: {primary_color};
            color: #ffffff;
            padding: 10px 12px;
            text-align: left;
        }}
        td {{
            padding: 8px 12px;
            border-bottom: 1px solid #e2e8f0;
        }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        code {{
            background: #edf2f7;
            color: #e53e3e;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "SF Mono", "Fira Code", monospace;
            font-size: 0.85rem;
        }}
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 16px 0;
        }}
        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}
        ul, ol {{
            margin-left: 24px;
            margin-bottom: 16px;
        }}
        li {{ margin-bottom: 8px; }}
        a {{
            color: {primary_color};
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}
        .insight-box {{
            background: {primary_color}08;
            border: 1px solid {primary_color}30;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
        }}
        .related {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px dashed #e2e8f0;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
            font-size: 0.8rem;
            color: #94a3b8;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .container {{ padding: 24px; }}
            h1 {{ font-size: 1.5rem; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>{emoji} {title}</h1>
    <div class="header-info">
        来源：{title.split('：')[0] if '：' in title else title} · 2026-05-23
    </div>
    <div class="content">
        {html_body}
    </div>
    <div class="related">
        <strong>📎 相关笔记</strong>
        <p>参见同目录下的其他 2026-05-23 笔记</p>
    </div>
    <div class="footer">猫仔 bookmarks/notes · 2026-05-23</div>
</div>
</body>
</html>'''
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ {md_path} → {html_path} ({template_name})")
    return html_path

if __name__ == '__main__':
    notes_dir = os.path.expanduser('~/uclaw/bookmarks/notes')
    
    # Define notes to convert
    notes = [
        {
            'md': '2026-05-23-Anthropic-Project-Glasswing-初始更新-AI安全防御新范式.md',
            'html': '2026-05-23-Anthropic-Project-Glasswing-初始更新-AI安全防御新范式_deep-blue.html',
            'title': 'Anthropic Project Glasswing 初始更新：AI 安全防御新范式',
            'emoji': '🛡️',
            'template': 'deep-blue',
            'bg': '#f0f4ff',
            'color': '#4338ca'
        },
        {
            'md': '2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md',
            'html': '2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力_tech-blue.html',
            'title': 'Antigravity 2.0 与 OpenSCAD LLM Benchmark：AI 编程工具的 3D 建模能力',
            'emoji': '🏛️',
            'template': 'tech-blue',
            'bg': '#f7fafc',
            'color': '#00d4ff'
        },
        {
            'md': '2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md',
            'html': '2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测_deep-blue.html',
            'title': 'Domain-Camouflaged Injection Attacks：域伪装注入绕过多 Agent LLM 检测',
            'emoji': '🔐',
            'template': 'deep-blue',
            'bg': '#f0f4ff',
            'color': '#4338ca'
        }
    ]
    
    for note in notes:
        md_path = os.path.join(notes_dir, note['md'])
        html_path = os.path.join(notes_dir, note['html'])
        md_to_html(md_path, html_path, note['template'], note['title'], note['emoji'], note['bg'], note['color'])
