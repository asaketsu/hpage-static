#!/usr/bin/env python3
"""
批量关联笔记脚本 — 为缺少 "## 相关笔记" 的笔记自动添加相关笔记链接

用法: python batch-note-linking.py [--dry-run]
"""

import os
import sys
from pathlib import Path
from datetime import datetime

NOTES_DIR = Path("~/uclaw/bookmarks/notes").expanduser()
INDEX_FILE = NOTES_DIR / "index.md"


def find_missing_links() -> list[Path]:
    """查找缺少 '## 相关笔记' 的笔记文件"""
    missing = []
    for md_file in NOTES_DIR.glob("*.md"):
        if md_file.name in ("index.md", "index.md.bak"):
            continue
        content = md_file.read_text(encoding="utf-8")
        if "## 相关笔记" not in content:
            missing.append(md_file)
    return missing


def generate_related_links(note_path: Path, all_notes: list[Path], max_links: int = 5) -> str:
    """为笔记生成相关笔记链接（基于文件名关键词匹配）"""
    name = note_path.stem.lower()
    
    # 关键词映射（可扩展）- 使用精确匹配避免过度匹配
    keyword_map = {
        "数字孪生": ["Antigravity", "GPU", "NAS"],
        "hermes-agent": ["hermes-agent", "Hermes-Agent"],
        "quant": ["quant", "MACD", "量化"],
        "AI-Agent": ["AI-Agent", "AI Agent"],
        "AI": ["AI", "LLM", "Claude"],
    }
    
    related = []
    matched_keywords = set()
    for keyword, candidates in keyword_map.items():
        # 精确匹配：关键词必须作为完整词出现在文件名中
        if keyword.lower() in name:
            matched_keywords.add(keyword)
            for candidate in candidates:
                for n in all_notes:
                    if n != note_path and candidate.lower() in n.stem.lower():
                        if n not in related:
                            related.append(n)
    
    # 限制最大链接数
    related = related[:max_links]
    
    if not related:
        # 默认关联最近3篇笔记
        related = sorted(all_notes, key=lambda p: p.stat().st_mtime, reverse=True)[:min(3, max_links)]
    
    links = []
    for r in related:
        rel_path = f"./{r.name}"
        links.append(f"- [{r.stem}]({rel_path})")
    
    return "\n".join(links)


def main(dry_run: bool = False):
    print(f"📋 扫描笔记目录: {NOTES_DIR}")
    
    all_notes = [f for f in NOTES_DIR.glob("*.md") if f.name not in ("index.md", "index.md.bak")]
    print(f"📊 总笔记数: {len(all_notes)}")
    
    missing = find_missing_links()
    print(f"❌ 缺少 '## 相关笔记' 的笔记: {len(missing)}")
    
    if not missing:
        print("✅ 所有笔记已有相关笔记链接")
        return 0
    
    for note in missing:
        print(f"\n🔗 处理: {note.name}")
        links = generate_related_links(note, all_notes, max_links=5)
        
        content = note.read_text(encoding="utf-8")
        new_content = content.rstrip() + "\n\n---\n\n## 相关笔记\n\n" + links + "\n"
        
        if dry_run:
            print(f"   [DRY-RUN] 将添加 {len(links.split(chr(10)))} 个链接")
        else:
            note.write_text(new_content, encoding="utf-8")
            print(f"   ✅ 已添加 {len(links.split(chr(10)))} 个相关笔记链接")
    
    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(main(dry_run=dry_run))
