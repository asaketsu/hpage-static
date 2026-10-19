# Hermes + NotebookLM：知识管理自动挡

- 📅 2026-05-05
- ⭐⭐⭐ 3.5/5 — Hermes + NotebookLM 组合的实际使用体验，有可借鉴的工具和工作流设计思路
- 🏷️ #Hermes #NotebookLM #知识管理 #自动化 #notebooklm-py
- 📰 林月半子的AI笔记（微信公众号）
- 🔗 https://mp.weixin.qq.com/s/wZ-YzUIZ_QcC_SNAK9HF2w

## 摘要

文章介绍 Hermes Agent + Google NotebookLM 的组合玩法。NotebookLM 是 Google 出的 AI 知识工具，围绕上传资料做问答和生成，回答自带来源引用。痛点在于手动上传/组织/整理太麻烦，长期坚持不下去。作者提出让 Hermes 负责"采集、投喂、执行动作"，NotebookLM 负责"分析、问答、生成结果"，形成知识飞轮自动循环。核心工具是开源 CLI `notebooklm-py`，通过命令行操作 NotebookLM。作者认为这套组合最大价值是省 Token（资料不占 prompt 空间）和知识自动滚动积累。

## 核心内容

### NotebookLM 是什么
Google 出的 AI 知识工具，与 ChatGPT/Claude 的区别是围绕你给它的资料工作。扔 10 篇论文进去，回答就从这 10 篇里找，每条带来源。核心能力：基于资料的问答、摘要生成、思维导图、音频概述。

### 痛点与解法
NotebookLM 手动流程：手动上传文档→手动组织提问→手动复制整理结果。用不久的核心原因不是工具不好，是重复手动操作让人懒得打开。Hermes 接入后变成：Hermes 采集投喂→NotebookLM 分析→结果回流知识库→下次起点更高。

### 基础用法四步
1. 列笔记本：自然语言指令列出所有 Notebook，含名称/ID/创建时间
2. 加资料：直接给 Hermes 链接，它自动加到指定 Notebook
3. 提问：基于已投喂资料在终端里直接问答
4. 生成输出：思维导图（JSON）/PPT 等，自动下载到本地

### 深层价值：省 Token + 知识飞轮
- 大量资料放 NotebookLM 管，Hermes 只在需要时取关键片段，避免每次都把资料塞 prompt
- 知识飞轮：采集→投喂→分析→生成→回写→下一次起点更高，自动循环
- Obsidian/LLM Wiki 积累的内容也可同步进 NotebookLM 做深度研究

### 搭建三步
1. 安装 notebooklm-py（开源 CLI，github.com/win4r/notebooklm-py）
2. `notebooklm login` 登录 Google 账号
3. `notebooklm list` 验证打通

## 🔍 借鉴点

- notebooklm-py CLI（github.com/win4r/notebooklm-py）→ 可作为知识分析的补充通道，与现有 Obsidian + LLM Wiki 方案互补。NotebookLM 擅长多文档交叉分析和带来源的问答，弥补了 Obsidian 纯检索的短板
- 知识飞轮概念（采集→投喂→分析→生成→回写）→ 可融入现有 exchange-protocol / knowledge-sync 体系，形成类似的自动循环
- "省 Token"分工思路（大资料外挂、Agent 只取关键片段）→ 适用于我们的长文档处理场景，避免每次把大量背景塞 prompt

## 🔗 关联性

- 关联已有笔记：[2026-05-04-个人Agent自进化五步闭环](2026-05-04-个人Agent自进化五步闭环.md) — 知识飞轮是自进化闭环在知识管理领域的具体应用
- 关联已有 skill：exchange-protocol — 经验交换协议可以借鉴"飞轮"模式，让经验自动流动和积累
- 关联已有 skill：knowledge-sync — 知识库同步审查可以扩展 NotebookLM 作为分析通道
- 关联技术栈：Obsidian + LLM Wiki（我们已有方案）— NotebookLM 是互补路径，不是替代
- 关联竞品索引：Hermes Workspace — 文章作者使用 Hermes 的方式值得参考

## 💡 启发

- 知识管理的核心瓶颈不是"工具不够强"，而是"手动流程坚持不了"。自动化不是锦上添花，是长期使用的必要条件
- Agent 的价值定位应该是"中间层"——连接各种工具，串联动作流，而不是什么都自己做。Hermes 当手脚，NotebookLM 当大脑，分工比全能更实用
- "知识飞轮"的关键不是单个环节多高效，而是环环相扣形成正反馈。每次使用都让下一次起点更高，这才是可持续的知识管理

## 🔮 预判

- NotebookLM 类工具会越来越多地被 Agent 串联，"外挂知识库"模式会成为 Agent 标配能力
- 短期：notebooklm-py 值得评估安装，作为知识分析的补充工具
- 中期：知识飞轮模式可以系统化到我们的 skill 体系，形成采集-分析-沉淀-回用的完整闭环
- 长期：多 Agent + 多知识库协同会是趋势，不同知识库各有擅长（NotebookLM 擅长交叉分析，Obsidian 擅长本地检索，LLM Wiki 擅长结构化），Agent 负责按需调度

## 相关笔记

- [2026-05-04-个人Agent自进化五步闭环](2026-05-04-个人Agent自进化五步闭环.md) - 自进化闭环与知识飞轮的底层逻辑一致
- [2026-05-03-ai-agent-resources-ecosystem](2026-05-03-ai-agent-resources-ecosystem.md) - Agent 生态中知识管理工具的位置

