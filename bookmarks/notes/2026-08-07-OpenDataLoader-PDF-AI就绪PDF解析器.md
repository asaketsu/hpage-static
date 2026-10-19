# OpenDataLoader PDF — AI 就绪的 PDF 解析器（基准测试 #1）

> **来源**：[github.com/opendataloader-project/opendataloader-pdf](https://github.com/opendataloader-project/opendataloader-pdf)
> **文档**：[opendataloader.org](https://opendataloader.org)
> **License**：Apache-2.0（2.0 前为 MPL 2.0）
> **Stars**：28,218 · **Forks**：2,693
> **语言**：Java（核心）+ Python/Node.js/Java SDK
> **Topics**：pdf, ocr, rag, markdown, json, html, accessibility, pdf-ua, tables, tagged-pdf

---

## 一句话定义

> PDF 解析器基准测试 **#1（0.907 总分）**——确定性本地模式 + AI 混合模式，从任何 PDF 提取 Markdown、JSON（带边界框）和 HTML。同时是**首个端到端开源的 PDF 自动标签化工具**（Tagged PDF / PDF/UA 无障碍合规）。

---

## 内容整理

### 解决的两大问题

| 问题 | 解决方案 | 状态 |
|------|---------|------|
| PDF 结构在解析时丢失（阅读顺序错、表格碎、无坐标） | 确定性本地解析 + XY-Cut++ 阅读顺序 + 边界框 | ✅ 发布 |
| 复杂表格/扫描件/公式/图表需要 AI 级理解 | 混合模式：复杂页路由到 AI 后端（基准 #1） | ✅ 发布 |
| 手动 PDF 无障碍修复成本 $50-200/文档 | 自动标签化 → Tagged PDF（Apache-2.0 免费） | ✅ 发布 |

### 基准测试结果（#1）

| 引擎 | 总分 | 阅读顺序 | 表格 | 标题 | 速度(s/页) | License |
|------|------|---------|------|------|-----------|---------|
| **opendataloader [hybrid]** | **0.907** | **0.934** | **0.928** | 0.821 | 0.463 | Apache-2.0 |
| nutrient | 0.885 | 0.925 | 0.708 | 0.819 | **0.008** | 商业 |
| docling | 0.882 | 0.898 | 0.887 | **0.824** | 0.762 | MIT |
| marker | 0.861 | 0.890 | 0.808 | 0.796 | 53.932 | GPL-3.0 |
| unstructured [hi_res] | 0.841 | 0.904 | 0.588 | 0.749 | 3.008 | Apache-2.0 |
| opendataloader (本地) | 0.831 | 0.902 | 0.489 | 0.739 | **0.015** | Apache-2.0 |
| mineru | 0.831 | 0.857 | 0.873 | 0.743 | 5.962 | AGPL-3.0 |
| pymupdf4llm | 0.732 | 0.885 | 0.401 | 0.412 | 0.091 | AGPL-3.0 |
| markitdown | 0.589 | 0.844 | 0.273 | 0.000 | 0.114 | MIT |

> 200+ 真实 PDF 测试（含多栏和科学论文）。混合模式表格准确率从本地 0.489 → 0.928（+90%）。

### 模式选择

| 文档类型 | 模式 | 安装 |
|---------|------|------|
| 标准数字 PDF | 快速（默认） | `pip install opendataloader-pdf` |
| 复杂/嵌套表格 | **混合** | `pip install "opendataloader-pdf[hybrid]"` |
| 扫描/图片 PDF | 混合 + OCR | `--force-ocr` |
| 非英文扫描件 | 混合 + OCR | `--force-ocr --ocr-lang "ko,en"` |
| 数学公式 | 混合 + 公式 | `--enrich-formula` |
| 图表描述 | 混合 + 图片 | `--enrich-picture-description` |
| 无障碍标签化 | 自动标签 → Tagged PDF | `--format tagged-pdf` |

### 30 秒快速开始

```bash
pip install -U opendataloader-pdf
```

```python
import opendataloader_pdf

opendataloader_pdf.convert(
    input_path=["file1.pdf", "file2.pdf", "folder/"],
    output_dir="output/",
    format="markdown,json"
)
```

> ⚠️ 每次 `convert()` 会启动 JVM 进程，批量处理所有文件一次调用，不要循环调用。

### 混合模式（复杂 PDF #1 精度）

简单页本地处理（0.02s），复杂页路由到 AI 后端：

```bash
# 终端1：启动后端
opendataloader-pdf-hybrid --port 5002

# 终端2：处理
opendataloader-pdf --hybrid docling-fast file1.pdf file2.pdf folder/
```

**OCR**：`--force-ocr`，支持 80+ 语言（en/ko/ja/ch_sim/ch_tra/de/fr/ar...）

**公式提取（LaTeX）**：

```bash
opendataloader-pdf-hybrid --enrich-formula
opendataloader-pdf --hybrid docling-fast --hybrid-mode full file1.pdf
```

输出 JSON 中公式类型：`{"type": "formula", "content": "\\frac{f(x+h) - f(x)}{h}"}`

**图表描述**：用 SmolVLM (256M) 轻量视觉模型生成描述。

### 输出格式

| 格式 | 用途 |
|------|------|
| **JSON** | 结构化数据 + 边界框 + 语义类型 |
| **Markdown** | LLM 上下文 / RAG 分块 |
| **HTML** | 网页展示 |
| **Annotated PDF** | 可视化调试 |
| **Tagged PDF** | 无障碍合规 |
| **Text** | 纯文本 |

JSON 输出示例（每个元素都有边界框）：

```json
{
  "type": "heading",
  "id": 42,
  "level": "Title",
  "page number": 1,
  "bounding box": [72.0, 700.0, 540.0, 730.0],
  "heading level": 1,
  "font": "Helvetica-Bold",
  "font size": 24.0,
  "content": "Introduction"
}
```

### AI 安全：提示注入防护

自动过滤 PDF 中的隐藏攻击：
- 隐藏文本（透明/零号字体）
- 页面外内容
- 可疑不可见层

敏感数据脱敏：`--sanitize`（邮箱/URL/电话 → 占位符）

### PDF 无障碍自动化

**首个端到端开源 Tagged PDF 生成工具**。

| 合规法规 | 截止日期 | 要求 |
|---------|---------|------|
| 欧洲无障碍法 (EAA) | 2025-06-28 | EU 数字产品无障碍 |
| ADA & Section 508 | 生效中 | 美国联邦机构和公共场所 |
| 韩国数字包容法 | 生效中 | 韩国数字服务无障碍 |

**合规管线**：

```
未标签 PDF → 1. 审计 → 2. 自动标签化(Tagged PDF) → 3. 导出 PDF/UA → 4. 可视化编辑器
              (免费)      (Apache-2.0 免费)           (企业版)         (企业版)
```

与 PDF Association + Dual Lab (veraPDF 开发者) 合作，遵循 Well-Tagged PDF 规范，用 veraPDF 验证。

### 能力矩阵

| 能力 | 支持 | 层级 |
|------|------|------|
| 文本提取（正确阅读顺序） | ✅ | 免费 |
| 每个元素的边界框 | ✅ | 免费 |
| 表格提取（简单边框） | ✅ | 免费 |
| 表格提取（复杂/无边框） | ✅ | 免费（混合） |
| 标题层级检测 | ✅ | 免费 |
| 列表检测 | ✅ | 免费 |
| 图片提取（带坐标） | ✅ | 免费 |
| AI 图表/图片描述 | ✅ | 免费（混合） |
| OCR（扫描件） | ✅ | 免费（混合） |
| 公式提取（LaTeX） | ✅ | 免费（混合） |
| Tagged PDF 结构提取 | ✅ | 免费 |
| AI 安全（提示注入过滤） | ✅ | 免费 |
| 页眉/页脚/水印过滤 | ✅ | 免费 |
| 自动标签化 → Tagged PDF | ✅ | 免费（Apache-2.0） |
| PDF/UA-1/2 导出 | 💼 | 企业版 |
| 无障碍工作室（可视化编辑） | 💼 | 企业版 |

### LangChain 集成

```bash
pip install -U langchain-opendataloader-pdf
```

```python
from langchain_opendataloader_pdf import OpenDataLoaderPDFLoader

loader = OpenDataLoaderPDFLoader(
    file_path=["file1.pdf", "file2.pdf"],
    format="text"
)
documents = loader.load()
```

### 多语言 SDK

| 语言 | 包名 |
|------|------|
| Python | `pip install opendataloader-pdf` |
| Node.js | `npm install @opendataloader/pdf` |
| Java | Maven `org.opendataloader:opendataloader-pdf-core` |

### 不支持的

- Word/Excel/PPT 处理（仅 PDF）
- 不需要 GPU（本地模式 CPU 即可）

---

## 查询拓展

- XY-Cut++ 阅读顺序算法与原版 XY-Cut 的改进点是什么？
- 混合模式的 AI 后端用的是 docling-fast，具体架构是什么？
- SmolVLM (256M) 做图表描述的效果如何？与 GPT-4o 视觉对比？
- Tagged PDF 自动标签化的准确率？veraPDF 验证通过率？
- 与 PyMuPDF (AGPL-3.0) 的许可差异对商业项目的影响？
- Hancom Data Loader 企业集成的具体能力（30+ 元素类型）？

---

## 归纳总结

OpenDataLoader PDF 是当前**最强的开源 PDF 解析器**——28K Stars，基准测试 #1（0.907），在阅读顺序、表格提取和标题检测上全面领先。核心架构是**确定性本地 Java 引擎 + AI 混合后端**——简单页 0.02s 秒级处理，复杂页路由到 AI 获得最高精度。

两大独特价值：
1. **每个元素都带边界框**——支持 RAG 源引用（点击答案→高亮原文位置），其他开源解析器不提供
2. **首个端到端开源 Tagged PDF 生成**——无障碍合规市场刚需（EAA 2025-06-28 截止），手动修复 $50-200/文档，这个工具免费

技术亮点：XY-Cut++ 阅读顺序、内置提示注入防护、LangChain 集成、80+ 语言 OCR、LaTeX 公式提取。

---

## 趋势判断

- **PDF 解析进入"AI 混合"时代**：纯规则（PyMuPDF）精度不够，纯 AI（marker）太慢（53s/页）。混合模式（本地 0.02s + AI 按需）是最优解
- **边界框成为 RAG 标配**：没有边界框的解析器无法支持"点击引用→高亮原文"的 UX，这在企业 RAG 中是刚需
- **PDF 无障碍合规催生新市场**：EAA 2025-06-28 截止日期创造了紧迫的企业需求，$50-200/文档的手动修复不可持续
- **Apache-2.0 替代 AGPL/MPL**：从 MPL 2.0 改为 Apache 2.0 说明企业采纳阻力主要来自 License——完全宽松许可大幅降低法务审查门槛
- **PDF→Tagged PDF→PDF/UA 分层商业化**：核心解析免费（引流），PDF/UA 合规企业版收费——经典的开源核心+企业增值模式

---

## 关联分析

- **与用户 ocr-and-documents Skill 的直接关联**：用户有 `ocr-and-documents`（PyMuPDF/marker-pdf 提取）Skill。OpenDataLoader 可以直接替代 marker-pdf——快 100 倍（0.463s vs 53.9s/页）且精度更高（0.907 vs 0.861）
- **与 RAG 技术演进笔记的关联**：OpenDataLoader 解决的是 RAG 第①代（基础检索）的输入质量问题——高质量结构化 Markdown + 边界框 = 更好的 chunking 和源引用
- **与 Hermes Agent 笔记处理的关联**：用户经常从微信公众号、X Article、PDF 论文提取内容做笔记。OpenDataLoader 可以提升 PDF 论文提取的质量（表格/公式/图表），特别是 LaTeX 公式提取对航空结构 AI 方向的论文很有用
- **与用户航空结构 AI 方向的关联**：航空结构设计规范大量是 PDF（适航条例、设计手册），OpenDataLoader 可以精确提取表格和公式，作为知识图谱构建的数据源
- **与 AWS Context Ontology Accelerator 的关联**：AWS 的 Scan 层需要摄入非结构化文档——OpenDataLoader 是理想的 PDF 摄入引擎，输出结构化 JSON 带边界框可直接映射到本体

---

## 📎 关键链接

- 📖 官方文档：[opendataloader.org](https://opendataloader.org)
- 💻 GitHub：[github.com/opendataloader-project/opendataloader-pdf](https://github.com/opendataloader-project/opendataloader-pdf)
- 📊 基准测试：[github.com/opendataloader-project/opendataloader-bench](https://github.com/opendataloader-project/opendataloader-bench)
- 📦 PyPI：`pip install opendataloader-pdf`
- 🔗 LangChain：`pip install langchain-opendataloader-pdf`

---

*笔记创建：2026-08-07 · 来源：github.com/opendataloader-project/opendataloader-pdf*

## 相关笔记

- [RAG技术演进路径-五代全景](2026-08-06-RAG技术演进路径-五代全景.md)
- [AWS-Context-Ontology-Accelerator-语义上下文层](2026-08-06-AWS-Context-Ontology-Accelerator-语义上下文层.md)
- [mise-开发环境管理工具](2026-08-07-mise-开发环境管理工具.md)

---
