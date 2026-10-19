# 这套Gemini科研流程，还有博士生不知道吗？

> **来源**：全息学术 · 微信公众号 · 2026-05-29
> **原文**：https://mp.weixin.qq.com/s/nJF9POQuM39j9hQStPhIyg
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

文章介绍了一套基于 Gemini + NotebookLM + Google AI Studio 的科研全流程四阶段方法论：文献吞噬与选题（NotebookLM）→ 研究设计与审稿挑刺（Gemini Advanced）→ 学术写作与去AI痕迹化（模块化生成+润色）→ 格式自动化与工作流闭环（APA/LaTeX）。核心主张：AI 负责重复劳动，人负责判断方向。适合社科/经管类实证论文场景。

## 核心内容

### 阶段一：文献吞噬与选题破局

工具：NotebookLM

四步法：
1. **建文献库**：上传多篇 PDF 到 NotebookLM
2. **生成文献矩阵**：用结构化 prompt 提取"作者/年份、研究对象、核心问题、理论视角、关键变量、方法、数据来源、结论、局限"九列
3. **归纳研究路径**：将多篇文献整理为 3-5 条主线（代表文献+共同问题+常用理论+变量+方法+结论）
4. **找 Research Gap**：从理论解释不足、变量矛盾、对象集中、方法单一、数据局限五角度分析，输出3个选题方向

选题自检四问：有没有数据？变量能不能测量？理论能不能支撑？方法能不能落地？

### 阶段二：研究设计与审稿挑刺

工具：Gemini Advanced / Google AI Studio

两步法：
1. **搭建 Conceptual Framework**：列出 IV/DV/中介/调节/控制变量+数据来源+假设，让 AI 从学术严谨性角度评估（内生性、遗漏控制变量、反向因果）
2. **SSCI/CSSCI 审稿标准挑刺**：从理论贡献、变量选择、因果识别、样本选择、模型设定、稳健性检验、替代解释七方面批判性评估

### 阶段三：学术写作与去AI痕迹化

工具：Gemini Advanced / Google Docs

关键原则：写作顺序 Results → Discussion → Introduction（倒金字塔法）

1. **模块化写初稿**：一次只让 AI 做一件事，避免幻觉。Results 分四部分：基准回归→控制变量→稳健性检验→异质性分析
2. **去 AI 痕迹**：用高级学术润色 prompt，强调变量关系、数据可落地性、逻辑闭环、可量化解释机制，避免空洞文学描述

### 阶段四：格式自动化

1. **清洗参考文献**：统一 APA 第七版格式
2. **检查引用匹配**：正文与参考文献交叉验证
3. **转 LaTeX**：booktabs 三线表格式

### 避坑指南

1. 涉及页码/样本量/统计结果，必须回源文件核对（防幻觉）
2. 未发表数据不上传，公司名替换为 Firm A/B
3. AI 生成的方向/代码/润色不代表结论成立
4. 一次只处理一个任务，输出更稳

## 关键概念

- **NotebookLM**：Google 的 AI 笔记工具，可上传文档后进行 AI 问答和摘要，适合文献管理
- **Conceptual Framework**：概念框架，论文中变量关系的理论模型图（IV→MV→DV + 调节变量）
- **Research Gap**：研究空白，现有文献未覆盖的问题领域
- **倒金字塔法**：先写 Results（最确定的部分），再写 Discussion，最后写 Introduction
- **模块化生成法**：将论文拆成小模块逐个生成，避免长文本幻觉

## 能力边界

**适用**：社科/经管类实证论文（问卷/面板数据/实验）
**局限**：
- 理工科需要大量公式推导，AI 辅助有限
- NotebookLM 中文文献支持不如英文
- 审稿标准 prompt 偏 SSCI/CSSCI 体系
- "去AI痕迹"prompt 本质是换表达，不能替代真正的研究贡献

## 最佳实践

1. 文献矩阵的九列结构是精华，可直接复用为文献综述模板
2. "审稿人挑刺"比"帮我检查"效果好得多 — 角色设定决定输出质量
3. 倒金字塔写作顺序是学术写作的通用建议，不依赖 AI 也成立
4. 一次一个任务的原则适用于所有 LLM 交互场景

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 角色扮演 Prompt 模式 | "以SSCI审稿人标准批判性评估"比"帮我检查"效果好 | Hermes 的分析类 Skill 可借鉴角色设定模式，提高输出质量 | 在 deep-analysis/scholar-assist skill 中加入角色扮演 prompt 模板 |
| 2 | 结构化文献矩阵 | 九列文献矩阵（作者/问题/理论/变量/方法/数据/结论/局限）是可复用框架 | 可提炼为通用"文献综述模板 Skill"，适用于读书笔记和竞品分析 | 评估是否值得创建 research-literature-review skill |
| 3 | 倒金字塔+模块化写作 | Results→Discussion→Intro 顺序 + 一次一个任务 | 与 Hermes 的"小批推进法"理念一致，可互相印证 | 已有 small-batch-execution skill 覆盖此模式 |
| 4 | AI去痕迹化 | 润色prompt强调"变量关系+数据落地+逻辑闭环" | 已有 humanizer skill，可参考学术场景增加专业领域润色模式 | 评估 humanizer skill 是否需要增加学术写作模板 |
| 5 | 四阶段分工模型 | NotebookLM输入→Gemini处理→人判断→格式自动化 | 类似 Hermes 团队分工（Data→Dev→ubot→Content），可提炼为通用"AI协作分工模板" | 暂无直接行动，但概念可迁移到团队任务路由设计 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- scholar-assist skill 已有论文检索/摘要能力
- deep-analysis skill 已有结构化分析框架
- humanizer skill 已有去AI痕迹功能

### 改进方案
1. scholar-assist 增加文献矩阵模板和 Research Gap 分析 prompt
2. humanizer 增加学术写作场景的专业润色模式

### 已执行操作
- ✅ 笔记已写入
- ⏳ 待评估是否创建 research-literature-review skill

## Skill 可行性评估

**结论：不建议创建独立 Skill。**

理由：
1. 文章内容本质是一组 Prompt 模板 + 工作流程建议，不涉及可程序化自动化的步骤
2. 所有关键 Prompt 可直接嵌入现有 scholar-assist skill 的模板库中
3. NotebookLM 是外部工具，无法通过 Hermes 工具链直接调用
4. 流程中的判断环节（选题自检四问、审稿评估）需要人参与，不适合自动化

**建议行动**：将精华 Prompt 模板补充到 scholar-assist skill 的 references/ 中，作为学术写作参考。


## 相关笔记
<!-- 待关联：新笔记暂无关联 -->
