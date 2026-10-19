# LiteParse — LlamaIndex 开源文档解析器

> **来源**：run-llama/liteparse · GitHub · 2026-02-09 创建
> **原文**：https://github.com/run-llama/liteparse
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

LiteParse 是 LlamaIndex 团队推出的开源文档解析工具，用 Rust 编写，专注**快速轻量**的 PDF 及多格式文档解析。核心能力：基于 PDFium 的空间文本提取 + Tesseract 内置 OCR + 多语言绑定（Python/Node/WASM/Rust CLI）。6.4K Star，Apache 2.0 许可。不依赖云服务，全部本地运行。定位是 LlamaParse（云端付费版）的开源轻量替代。

## 核心内容

### 1. 架构设计

Rust 核心引擎 + 多语言绑定架构：

1. **格式转换层**：LibreOffice（Office 文档）+ ImageMagick（图片）→ 统一转 PDF
2. **文本提取层**：PDFium C 库（Google 的 PDF 渲染引擎）
3. **OCR 层**：Tesseract 内置（零配置）/ HTTP OCR 服务器（EasyOCR、PaddleOCR、自定义）
4. **合并层**：原生文本 + OCR 结果智能合并
5. **空间投影层**：Grid Projection 重建空间布局，保留 bounding box 信息

### 2. 多格式输入支持

| 类别 | 格式 | 依赖 |
|------|------|------|
| PDF | .pdf | 内置 |
| Word | .doc/.docx/.docm/.odt/.rtf/.pages | LibreOffice |
| PPT | .ppt/.pptx/.pptm/.odp/.key | LibreOffice |
| 表格 | .xls/.xlsx/.xlsm/.ods/.csv/.numbers | LibreOffice |
| 图片 | .jpg/.png/.gif/.bmp/.tiff/.webp/.svg | ImageMagick |

### 3. 多语言绑定

| 语言 | 包名 | 绑定技术 |
|------|------|---------|
| Rust | liteparse | 原生 |
| Python | pip install liteparse | PyO3 |
| Node.js | npm i @llamaindex/liteparse | napi-rs |
| Browser | npm i @llamaindex/liteparse-wasm | wasm-bindgen |

所有安装方式共享同一个 `lit` CLI。

### 4. 关键 CLI 命令

```
# 基础解析
lit parse document.pdf

# JSON 格式 + 指定页
lit parse doc.pdf --format json --target-pages "1-5,10" -o output.json

# 批量解析
lit batch-parse ./input ./output

# 生成截图（供 LLM 视觉分析）
lit screenshot doc.pdf -o ./screenshots --dpi 300

# 指定 OCR 服务器
lit parse doc.pdf --ocr-server-url http://localhost:8000/ocr

# 管道输入
curl -sL https://example.com/report.pdf | lit parse -
```

### 5. OCR 灵活架构

三种模式可选：

1. **Tesseract 内置**：零配置开箱即用，适合大多数场景
2. **HTTP OCR 服务器**：接入 EasyOCR/PaddleOCR，更高中文识别精度
3. **自定义 OCR**：实现简单 API 规范即可（POST /ocr，接收 file + language，返回 text + bbox + confidence）

## 关键概念

- **PDFium**：Google Chrome 内置的 PDF 渲染引擎，C 库，高性能文本提取
- **Grid Projection**：空间布局重建算法，将提取的文本元素按位置映射到网格，保留阅读顺序
- **Bounding Box**：每个文本元素的精确坐标 (x1, y1, x2, y2)，支持空间定位
- **napi-rs / PyO3 / wasm-bindgen**：Rust FFI 框架，分别用于 Node.js / Python / 浏览器绑定
- **Selective OCR**：仅对 PDFium 无法提取文本的区域执行 OCR，减少处理时间

## 能力边界

**适用场景**：
- 文本型 PDF 的快速结构化提取
- 需要本地/离线运行的文档处理管道
- 需要多语言（Python/Node/WASM）集成的项目
- LLM Agent 的文档预处理（截图 + 文本双通道）

**局限性**：
- 复杂表格、多栏布局、手写体效果有限（官方推荐用付费 LlamaParse）
- 扫描件依赖 OCR 质量，Tesseract 中文效果不如 PaddleOCR
- Office 文档需额外安装 LibreOffice（服务器部署增加依赖）
- 无云端模式，大文件处理受本地资源限制

## 最佳实践

1. **中文文档**：外接 PaddleOCR HTTP 服务器替代 Tesseract，识别精度显著提升
2. **Agent 集成**：利用 screenshot 功能生成视觉输入，text + image 双通道喂给 LLM
3. **批量处理**：`batch-parse` 支持目录递归，配合 `--num-workers` 并行加速
4. **离线环境**：预下载 `.traineddata` 文件，设置 `TESSDATA_PREFIX` 环境变量
5. **Agent Skill**：`npx skills add run-llama/llamaparse-agent-skills --skill liteparse` 可直接作为 AI Agent 技能使用

## 项目数据

| 指标 | 值 |
|------|-----|
| Star | 6,433 |
| Fork | 411 |
| 语言 | Rust |
| 许可 | Apache 2.0 |
| 创建时间 | 2026-02-09 |
| 最近更新 | 2026-05-28 |
| 绑定语言 | Rust/Python/Node.js/WASM |

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | Rust 核心 + 多语言绑定 | 用 PyO3/napi-rs/wasm-bindgen 一次实现多端分发 | Hermes 的 Skill 系统可借鉴此模式，核心逻辑 Rust 化提升性能 | 无立即行动，但未来如需高性能解析可参考此架构 |
| 2 | OCR 可插拔架构 | Tesseract 内置 + HTTP OCR 服务器 + 自定义 API 规范 | 与 Hermes image-gen 降级链模式类似，可提炼为通用"可插拔能力层"模式 | 验证 current skills 中类似模式是否已文档化 |
| 3 | Agent Skill 集成 | 提供 SKILL.md 供 AI Agent 直接调用 | 直接将 liteparse 集成为 Hermes Skill，用于本地 PDF/文档解析任务 | pip install liteparse 后创建 liteparse skill |
| 4 | Screenshot + Text 双通道 | 为 LLM Agent 同时生成文本和截图 | Hermes 处理文档任务时可采用此双通道策略，text 提取 + vision 分析互补 | 在 ocr-and-documents skill 中加入双通道建议 |
| 5 | Grid Projection 空间布局 | 将文本元素映射到网格保持阅读顺序 | 笔记系统处理 PDF 内容时可利用 bounding box 信息重建文档结构 | 暂无直接行动，笔记系统当前不需要 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- Wiki KB 已有文档处理相关 Skill（ocr-and-documents）
- RAG 索引已建立，可检索笔记
- Memory 记录了搜索降级链模式

### 改进方案
1. liteparse 可作为 ocr-and-documents skill 的底层引擎替代 pymupdf/marker-pdf
2. 中文 OCR 场景下，liteparse + PaddleOCR 服务器组合优于 Tesseract

### 已执行操作
- ✅ 笔记已写入 ~/uclaw/bookmarks/notes/
- ⏳ 待评估是否安装 liteparse 并创建专用 Skill


## 相关笔记
<!-- 待关联：新笔记暂无关联 -->
