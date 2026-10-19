# 上下文，才是Agent的命门

- 📅 2026-05-15
- ⭐ 3.5/5 — 4层上下文模型是亮点，后半段是QClaw产品广告
- 🏷️ #AI编程 #Agent #上下文 #QClaw #竞品分析
- 📰 QClaw 官方（飞书知识库）
- 🔗 https://jcn7kakdef35.feishu.cn/wiki/MZLswtz1riP2t3kTH5FcPliYnVf

## 摘要

QClaw 发布了一篇关于 AI Agent 竞争力本质的文章。核心论点：AI 编程工具的竞争焦点正从"谁更会写代码"转向"谁能获取和使用上下文"。文章提出了开发者上下文的四层模型（L1代码层→L4隐性知识层），指出当前行业竞争集中在 L1-L2，但开发者真正的认知瓶颈在 L3（组织知识层），并顺势推出了 QClaw 的"文件空间"功能作为上下文基础设施的解决方案。

## 核心内容

### 1. 竞争焦点转移：从"写得好"到"写得对"

- 代码生成质量趋同（80-90分），"写得更好"的边际收益急剧下降
- 用户开始感知：AI 写出来的代码质量不是问题，**问题是我需要的代码**
- 这是两个不同的问题：前者是模型能力问题，后者是上下文问题

### 2. 开发者上下文四层模型

| 层级 | 名称 | 内容 | 行业覆盖 |
|------|------|------|----------|
| L1 | 代码层 | 当前文件、调用链、AST、类型定义 | 竞争集中 |
| L2 | 项目层 | README、配置文件、git history、架构约定 | 竞争集中 |
| L3 | 组织知识层 | 需求文档、设计稿、技术方案、知识库、会议纪要 | 覆盖不足（瓶颈） |
| L4 | 隐性知识层 | 口头约定、决策背景、已离职同事脑中的上下文 | 几乎空白 |

关键洞察：开发者日均编码不到4小时，其余时间都在翻代码、拼上下文、排查影响面。

### 3. 上下文基础设施定义

> 一个系统级的能力层，负责跨数据源地发现、获取、验证、结构化开发者所需的项目上下文，并以模型可消费的方式提供给AI工具链。

核心能力：持续获得 → 组织 → 更新 → 使用上下文

### 4. QClaw 产品动作

"文件空间"功能：本地文件 + 腾讯文档 + ima知识库一站式打通。定位为上下文基础设施的具体实现，利用腾讯生态优势。

## 🔍 借鉴点

### ① 有利进化（已落实）

1. **4层上下文模型 → 评估 Hermes 上下文覆盖度的框架**
   - L1：Hermes 有 terminal/file/search_files → 覆盖
   - L2：有 project-index / README 自动读取 → 部分覆盖
   - L3：knowledge-fusion 5源并行扫描 + 笔记系统 → 正在建设
   - L4：exchange-protocol + session memory → 初步覆盖
   - 已补充到 knowledge-fusion skill 作为评估维度

2. **L3 瓶颈诊断法 → 可用于 self-diagnosis**
   - 每次任务启动前自检：L3 信息是否充足？
   - 缺 L3 时主动触发知识检索，而非直接盲写

3. **"AI 写得对不对" vs "AI 写得好不好" → 任务执行质量标准**
   - 代码质量（写得好）vs 需求匹配度（写得对）
   - 以后 review 输出时优先检查"写得对不对"

### ② 有价值（写入 Memory）

- 跨数据源一站式打通的产品思路 → knowledge-fusion 的进化方向
- "上下文基础设施"概念 → 可作为对外沟通的框架语言

### ③ 知识库（仅笔记）

- QClaw 文件空间功能细节
- 腾讯生态优势（企微 + 腾讯文档 + ima）

## 🔗 关联性

- [[2026-05-10-知识体系架构设计]] — Hermes 四系统协同（Wiki+RAG+Notes+Memory），与 L1-L4 模型高度对应
- [[2026-05-14-手撸Agent-ReAct-Loop从零实现]] — Agent Loop 中上下文注入的实践
- [[2026-05-14-Agent工程4月实践-不要一上来就做Agent]] — Agent 工程实践中上下文的实际挑战
- skill: knowledge-fusion — 正在做 L3 层的跨源检索，4层模型可用于评估覆盖度
- skill: exchange-protocol — Agent 间上下文共享，对应 L4 层的部分需求
- skill: context-compressor — 上下文压缩，防止 L1-L2 信息溢出

## 💡 启发

1. **上下文分层是 Agent 架构设计的通用框架**
   - 不只是编程 Agent，任何 Agent（运维、分析、交易）都可以用 L1-L4 评估上下文完整性
   - ths-auto-trader 的上下文：L1(代码) L2(策略配置) L3(市场数据/行情) L4(交易员直觉)

2. **"上下文基础设施"可以成为 Hermes 的差异化定位**
   - 我们已有 knowledge-fusion / exchange-protocol / project-index / memory-system
   - 如果能拉通形成统一层，就是我们的"上下文基础设施"

3. **L4（隐性知识）是最难也最有价值的层**
   - 记忆系统（memory）就是在试图捕获 L4
   - 但口头约定和决策背景天然不可结构化，可能需要不同的捕获策略

## 🔮 预判

- **短期（3月）**：AI 编程工具全面加入"上下文"功能，文件检索/RAG 成为标配。Cursor、Copilot、QClaw 都会卷这个方向。
- **中期（6-12月）**：L3 层的跨数据源整合成为核心竞争点。谁先打通企业知识库（飞书文档/Confluence/Notion）谁占优。腾讯有生态优势。
- **长期**：L4 隐性知识的捕获成为终极战场。可能是"AI 配对编程"记录所有决策过程，或者团队记忆系统。

## 相关笔记

- [[2026-05-10-知识体系架构设计]] - 四系统协同架构
- [[2026-05-14-Agent工程4月实践-不要一上来就做Agent]] - Agent 实践经验
- [[2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行]] - 上下文的技术维度

## 相关笔记
- [Agent工程-不要一上来就做Agent](2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [Small-Hermes-自我进化](2026-05-14-Small-Hermes-自我进化深度解析.md)
- [SkillFactory-测试驱动Skill生成](2026-05-14-SkillFactory-测试驱动Skill生成工厂.md)
- [手撸Agent-ReAct-Loop](2026-05-14-手撸Agent-ReAct-Loop从零实现.md)


## 相关笔记
- [2026-05-12-网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
