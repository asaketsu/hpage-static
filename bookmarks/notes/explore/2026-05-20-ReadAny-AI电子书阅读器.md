# ReadAny — AI 驱动的跨端电子书阅读器

- 📅 2026-05-20
- ⭐ 4/5 — 技术架构扎实，RAG 实现值得借鉴，但生态尚早期
- 🏷️ #开源项目 #RAG #电子书 #AI阅读器 #跨平台
- 📰 GitHub
- 🔗 https://github.com/codedogQBY/ReadAny

## 摘要

ReadAny 是一款 AI 驱动的跨端电子书阅读器（1.2k⭐，GPL-3.0），支持 EPUB/PDF/MOBI。核心亮点：**语义搜索（Hybrid RAG）** + **上下文感知 AI 对话** + **技能系统**。Monorepo 架构（pnpm workspace），桌面端 Tauri，移动端 Expo React Native，Core 层共享。LangChain + sqlite-vec 构建本地优先的 RAG 管线。

## 项目概况

- **Stars**: 1.2k | **Forks**: 95 | **Commits**: 604 | **License**: GPL-3.0
- **平台**: macOS / Windows / Linux / iOS / Android
- **格式**: EPUB, PDF, MOBI
- **同步**: WebDAV, S3, LAN
- **AI Provider**: OpenAI, Claude, Gemini, Ollama, DeepSeek, 任意 OpenAI 兼容 API
- **数据**: 全部本地存储

## 技术栈

| 层 | 技术 |
|---|---|
| Monorepo | pnpm workspace |
| 桌面端 | Tauri (Rust) + React 19 |
| 移动端 | Expo (React Native) |
| 前端 | React 19 + TypeScript + Tailwind CSS 4 + Radix UI |
| 构建 | Vite 7 + EAS |
| AI | LangChain (OpenAI/Anthropic/Google/DeepSeek) |
| 向量DB | sqlite-vec |
| 嵌入 | @huggingface/transformers (本地) + API |
| 状态管理 | Zustand |
| 测试 | Vitest |
| Lint | Biome |
| TTS | expo-speech / react-native-track-player |

## 核心架构

### Monorepo 结构
```
packages/
  app/          → Tauri 桌面端 (Vite + React)
  app-expo/     → 移动端 (Expo RN)
  core/         → 共享核心层 (@readany/core)
  feedback-worker/ → 反馈处理
  foliate-js/   → EPUB 渲染引擎
```

### Core 层模块
- **ai/** — LLM Provider, Streaming Chat, System Prompt, Semantic Context, Skills, Tools
- **rag/** — Chunker, Embedding, Vector DB (sqlite-vec), Hybrid Search, Tokenizer, Inverted Index
- **db/** — 数据库层
- **reader/** — 阅读器核心
- **sync/** — WebDAV/S3/LAN 同步
- **tts/** — 语音朗读
- **stats/** — 阅读统计
- **translation/** — 翻译
- **export/** — 笔记导出
- **feedback/** — 用户反馈

## 值得借鉴的设计

### 1. Semantic Reading Context (SRC) — 上下文感知
- 追踪用户当前操作类型：`reading | highlighting | searching | navigating`
- 生成上下文快照：当前章节、位置(CFI)、可见文本、最近标注
- AI 对话自动注入上下文，不是简单问答而是"读过这本书"的伙伴

### 2. Hybrid Search — Vector + BM25 融合
- **三种搜索模式**: Vector / BM25 / Hybrid
- **Vector**: sqlite-vec 优先，内存 cosine similarity 兜底
- **BM25**: 倒排索引 O(k*d)，支持 CJK bigram
- **Hybrid**: RRF (Reciprocal Rank Fusion, k=60) 合并排序
- **缓存**: 5分钟 TTL 内存缓存（chunk + 倒排索引）
- **优雅降级**: Vector 失败 → 内存搜索；两者都不可用 → BM25 only

### 3. 多语言 Tokenizer — CJK 支持
- 中日韩混合文本处理（如 "AI人工智能"）
- 中文：单字 + bigram（"人工智能" → ["人工", "智能"]）
- 日文：平假名/片假名 + 汉字
- 韩文：韩文字母
- 中英停用词表（各 50+）
- NFKC Unicode 标准化

### 4. Segment-aware Chunker — 精确 CFI 映射
- 每个 chunk 保留精确 CFI（Canonical Fragment Identifier）
- 按 token 数分组（默认 300 tokens，min 50，overlap 20%）
- 支持段落级导航定位

### 5. System Prompt 6 段式架构
1. Role & Persona — 阅读助手身份
2. Book Context — 书籍元数据 + 阅读进度
3. SRC — 语义阅读上下文
4. Available Tools — 按状态动态启用
5. Core Workflow — 强制引用工作流（addCitation）
6. Response Constraints — 语言/风格约束

### 6. AI Tool 系统
- **通用**: listBooks, searchAllHighlights, searchAllNotes, getReadingStats, getSkills, mindmap
- **阅读**: getCurrentChapter, getSelection, getSurroundingContext, getRecentHighlights
- **RAG**: ragSearch, ragToc, ragContext（需 vectorized）
- **分析**: summarize, extractEntities, analyzeArguments, findQuotes, compareSections
- **引用**: addCitation（强制注册来源，防幻觉）

### 7. 技能系统 (.claude/skills + .agents/skills)
- 项目内置 Claude Code Skills，AI 用 Claude 辅助开发
- 用户侧有动态 Skill 系统（getSkills tool）

## 🔍 借鉴点

### 可吸收到我们的体系

1. **Hybrid Search RRF 融合** → 可增强 `hybrid-search` Skill，当前我们只有向量+关键词并行，缺 RRF 排序融合
2. **Segment-aware Chunker + CFI** → 我们的 RAG 缺精确段落定位，CFI 模式可借鉴到 EPUB 处理
3. **6 段式 System Prompt** → 结构化 prompt 设计可参考到阅读/分析类 Skill
4. **强制 Citation 工作流** → addCitation 防幻觉机制，可用于我们的 deep-analysis Skill
5. **CJK Tokenizer bigram** → 我们的 search/tokenizer 可借鉴 CJK bigram 方案

### 不需要借鉴

- Tauri/Expo 技术栈 → 我们是 Python/CLI 体系
- WebDAV/S3 同步 → 我们已有 Cloudflare Tunnel
- TTS 系统 → 我们有 F5-TTS 本地方案

## 🔗 关联性

- [llm_wiki 分析与 Skill 进化](2026-05-20-llm_wiki分析与Skill进化.md) — 同日分析，知识管理方法论
- hybrid-search Skill — 可吸收 RRF 融合算法
- deep-analysis Skill — 可吸收 Citation 工作流
- scholar-assist Skill — 学术阅读工具链，ReadAny 是互补产品

## 💡 启发

- **"阅读助手"定位** → AI 不只是聊天，是理解上下文的伙伴。我们的 knowledge-query 可进化为上下文感知查询
- **本地优先** → 所有数据本地存储 + 多 Provider 支持，符合隐私趋势
- **CFI 定位** → 精确到段落的引用体系，比页码更灵活，适合电子书场景

## 🔮 预判

- ReadAny 会快速成长（已上阮一峰周刊），6个月内可能 3k+ star
- Hybrid RAG + 本地 embedding 会成为阅读类 App 的标配
- CJK Tokenizer 质量决定中文搜索体验，这是差异化关键

## 相关笔记
- [llm_wiki分析与Skill进化](explore/2026-05-20-llm_wiki分析与Skill进化.md)
- [Understand-Anything-源码精读](explore/2026-05-24-Understand-Anything-源码精读.md)
