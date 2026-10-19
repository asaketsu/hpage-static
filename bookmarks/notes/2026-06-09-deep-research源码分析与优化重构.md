# Deep-Research 深度调研引擎：源码分析与优化重构

> 来源：[hoolulu/deep-research](https://github.com/hoolulu/deep-research)  
> 分析日期：2026-06-09  
> 优化版本：`/home/jc/uclaw/project/deep-research-hermes/`

---

## 1. 项目概述

**deep-research** 是一个面向 OpenCode（类似 Claude Code 的终端 AI 编码工具）的 Skill，实现全自动深度调研报告生成。核心特性：

- **4 步 Agent 流水线**：主题分析 → 数据收集 → 章节撰写 → 装配验证
- **19 种语言**输出（含中日韩、阿语、印地语等非拉丁语系）
- **三级搜索引擎**级联：SearXNG → Exa → 免费源兜底
- **双抓取引擎**：Scrapling（反检测）→ webfetch（回退）
- **完整 QA 管线**：编码 / 标题 / 章编号 / 元数据 / 目录 / 引用 / 年份密度

---

## 2. 原始架构分析

### 2.1 文件结构

```
deep-research/
├── SKILL.md                    # 主控指令（~360行），Agent 编排核心
├── RULES.md                    # Agent 行为规范
├── VERSION                     # 版本号
├── profiles.json               # 调研模式配置（quick/standard/deep）
├── tools/
│   ├── dr_check.py             # QA 检查（编码/标题/章编号/元数据/目录/年份密度）
│   ├── dr_gen.py               # 报告生成（元数据/引用转换/装配）
│   └── lang_config.py          # 19 语言配置表（~540行）
├── prompts/
│   ├── task1_oracle.md         # Task 1 主题分析 prompt
│   ├── task2_data_collection.md # Task 2 数据收集 prompt
│   └── task3_chapter_agent.md  # Task 3 章节撰写 prompt
├── command/                    # slash command 注册
│   └── research.md
├── reports/                    # 输出报告（按语言分子目录）
└── scrapling-mcp-server.py     # MCP Server（可选抓取引擎）
```

### 2.2 四步流水线

| 步骤 | 任务 | 执行者 | 输出 |
|:-----|:-----|:-------|:-----|
| Task 1 | 主题分析 + 大纲生成 | oracle 子 agent | `outline.json` |
| Task 2 | 搜索 + 抓取 + 结构化数据池 | 子 agent（unspecified-high） | `data-pool.json` + `task2_manifest.json` |
| Task 3 | 并行章节撰写 | N 个子 agent 并行 | `chapters/chapter-{N}.md` |
| Task 4 | 验证 + 装配 + QA | 主 agent 直接执行 | 最终报告 `.md` |

### 2.3 核心设计亮点

1. **数据池协议**（`data-pool.json`）：标准化的 `{question, src[], facts[{src, yr, met, val, u, ctx, url, cur, conf}]}` 结构，实现搜索→撰写→验证全链路事实追踪
2. **引用编号预分配**：按首次出现顺序为 `(src, yr)` 分配 `[1], [2], [3]...`，章节写入时直接引用，最终装配时统一转换为 `[(N)](#refN)` 跳转锚点
3. **跨平台编码安全**：全链路 UTF-8，stdin 二进制读取 + 多编码回退，原子文件写入（write → tmp → replace）
4. **年份密度检查**：确保报告中 ≥50% 的年份数据来自目标年份（target_year ± 1），防止信息过时
5. **并行章节验证**：`ThreadPoolExecutor` 并行验证所有章节的编码、标题、段落、区块引用等

### 2.4 已识别问题

| # | 问题 | 严重度 | 说明 |
|:--|:-----|:-------|:-----|
| 1 | **OpenCode 强耦合** | P0 | 搜索/抓取依赖 OpenCode 的 `task()` 子 agent API，无法独立运行 |
| 2 | **Scrapling MCP 依赖** | P1 | 核心抓取依赖 Scrapling MCP Server 注册到 opencode.json，安装链路长 |
| 3 | **无 CLI 入口** | P1 | 纯 Skill 模式，无命令行工具可直接调用 |
| 4 | **Windows 特殊处理过多** | P2 | 大量 PowerShell 兼容代码，增加维护负担 |
| 5 | **dr_gen.py / dr_check.py 耦合** | P2 | 模块间直接 import（无包结构），全局可执行 |
| 6 | **无单元测试** | P2 | 零测试覆盖 |

---

## 3. 优化重构方案

### 3.1 架构变更

```
原: OpenCode Skill（SKILL.md + tools/ + prompts/）
↓
新: 独立 Python 包（deep_research/ + CLI + 可插拔搜索/抓取）
```

### 3.2 模块拆分

| 模块 | 职责 | 关键改进 |
|:-----|:-----|:---------|
| `deep_research/lang_config.py` | 19 语言配置表 | 保持原样，已验证完备 |
| `deep_research/dr_check.py` | QA 检查 | 解耦为包内导入，去除顶层入口 |
| `deep_research/dr_gen.py` | 报告生成 | 解耦为包内导入，去除 stdin 入口 |
| `deep_research/search/` | 搜索引擎抽象层 | **新增**，替代 OpenCode task() 搜索 |
| `deep_research/fetch/` | 网页抓取抽象层 | **新增**，urllib + Scrapling 可选 |
| `deep_research/qa/` | QA 聚合 | **新增**，聚合 dr_check 全部检查项 |
| `deep_research/pipeline/` | 报告装配管线 | **新增**，从 SKILL.md 流程提取 |
| `deep_research/cli.py` | CLI 入口 | **新增**，`dr` 命令 |

### 3.3 搜索引擎替换策略

原方案依赖 OpenCode 的 `task()` 子 agent 调用 `websearch_web_search_exa`，重构为：

```
Layer 1: SearXNG（自建，70+引擎含百度/搜狗）
    ↓ 不可用
Layer 2: Exa（付费 API）
    ↓ 不可用
Layer 3: DuckDuckGo Lite + Brave（免费兜底）
```

### 3.4 抓取引擎替换策略

原方案依赖 Scrapling MCP Server，重构为：

```
优先: Scrapling（如果已安装）
    ↓ 不可用
回退: urllib（零依赖，内置）
```

### 3.5 验证结果

```
✅ 全模块导入正常
✅ QA 检查在真实报告（2026年AI眼镜行业深度研究）上全部 passed
✅ CLI `dr check` 命令正常工作
✅ 19 语言配置表完整
✅ 字数统计: 8504 字
✅ 年份密度: 73.4%（>50% 阈值）
✅ 8 章编号检测正常
```

---

## 4. 进一步优化建议

| 优先级 | 建议 | 工作量 |
|:-------|:-----|:-------|
| P0 | 实现 Hermes Skill 适配（将 Task 1-3 编排为 Hermes delegate_task） | 2h |
| P0 | 添加 `pyproject.toml` 的 `scripts` 入口，支持 `pip install -e .` | 0.5h |
| P1 | 补充单元测试（至少覆盖 dr_check 全部检查函数） | 3h |
| P1 | 搜索引擎结果缓存（避免重复搜索） | 1h |
| P2 | 去除 Windows PowerShell 兼容代码（本机为 Linux） | 0.5h |
| P2 | 支持流式输出（边生成边推送） | 2h |

---

## 5. 关键代码模式

### 5.1 原子文件写入（跨平台安全）

```python
tmp = filepath + '.tmp'
with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
os.replace(tmp, filepath)  # 原子操作
```

### 5.2 引用编号预分配

```python
# 按首次出现顺序分配 [1], [2], [3]...
seen = set()
for rec in data:
    for fact in rec['facts']:
        key = (fact['src'], fact['yr'])
        if key not in seen:
            seen.add(key)
            ordered_refs.append(key)
ref_map = {pair: i + 1 for i, pair in enumerate(ordered_refs)}
```

### 5.3 并行章节验证

```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=min(chapter_count, 8)) as ex:
    futures = {}
    for i in range(1, chapter_count + 1):
        path = os.path.join(chapters_dir, f"chapter-{i}.md")
        futures[ex.submit(validate_chapter, path, expected)] = i
```

---

## 6. 数据流图

```
用户输入主题 + 模式(quick/standard/deep) + 语言(19种)
    │
    ▼
┌─ Task 1: Oracle ─────────────────────────────┐
│ 分析主题 → 生成 outline.json                  │
│ {title, depth_mode, chapters[{title, sections}]} │
└───────────────────────┬───────────────────────┘
                        ▼
┌─ Task 2: Data Collection ────────────────────┐
│ 搜索(SearXNG/Exa/DDG) → 抓取(Scrapling/urllib) │
│ → 结构化 data-pool.json + task2_manifest.json  │
└───────────────────────┬───────────────────────┘
                        ▼
┌─ Task 3: Chapter Writing (并行) ──────────────┐
│ N 个子 agent 各写一章 → chapter-{N}.md          │
│ 引用预分配的 [N] 编号，嵌入 facts                │
└───────────────────────┬───────────────────────┘
                        ▼
┌─ Task 4: Assemble + QA ──────────────────────┐
│ validate-all → assemble → convert-citations    │
│ → qa-report → 最终报告                          │
└───────────────────────────────────────────────┘
```

---

*分析完成于 2026-06-09 · 项目路径: `/home/jc/uclaw/project/deep-research-hermes/`*


## 相关笔记
- [[2026-06-05-A2A协议v1.0正式发布-三层架构-多绑定与Agent互联新范式]]
- [[hermesclaw-analysis]]
- [[2026-05-30-SQLite就是你需要的全部-持久工作流的极简架构]]
