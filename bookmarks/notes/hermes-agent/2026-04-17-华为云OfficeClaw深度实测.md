# 华为云 OfficeClaw 深度实测：Harness Engineering 跑通了

- 📅 2026-04-17
- ⭐⭐⭐⭐ 4/5 — 技术架构有参考价值，但文章偏软文
- 🏷️ #OfficeClaw #华为云 #HarnessEngineering #多Agent协同 #PPT生成 #竞品动态
- 📰 公众号：AI信息Gap（木易）

## 核心内容

### Harness Engineering 范式
- 由 Terraform 创始人 Mitchell Hashimoto 提出，OpenAI/Anthropic 官方背书
- 核心思路：不再死磕模型，给模型设计精密的「外部运行环境」— 约束、上下文、验证、生命周期
- 类比：以前让AI自由发挥写作文，现在给选题+提纲+参考+批改标准

### 实测场景

| 场景 | 输入 | 产出 | 耗时 |
|------|------|------|------|
| ChatGPT 5.4 技术分析 PPT | 一句话 | 18页 Claude 风格 | ~30分钟 |
| 423页斯坦福 AI Index 报告转 PPT | 一段提示词 | 25页带图表 | 全自动 |

### 多 Agent 协同架构
- **Alice** → 调研（联网搜索、网页抓取、产出调研报告）
- **Bob** → 大纲规划（结构化大纲设计）
- **Charlie** → 设计（逐页 HTML 渲染，字体/配色/排版）
- **Eve** → 文档解析（423页 PDF → 90KB Markdown）
- 主 Agent 只管编排，每个子 Agent 有独立上下文边界和验证逻辑

### 6 阶段工作流
1. 环境检测
2. 需求收集（页数三档 + 风格五选一）
3. 内容规划研究（深度调研）
4. 幻灯片生成（逐页 HTML）
5. PPTX 导出（HTML → PPTX 转换）
6. 交付验收（文件校验）

### 产品生态
- 内置 7 个华为云 MaaS 模型，含 GLM-5.1
- 技能广场 33614 个 Skills
- 支持飞书/微信/钉钉/小艺接入
- Windows 本地部署，数据不出本机
- 敏感字段自动脱敏加密

## 关键洞察

**Harness = 我们一直在做的事**: 约束、上下文、验证、生命周期 — 本质就是 Hermes 的 Skill 体系 + 工具调用 + QA 校验。概念包装得好，但不是新东西。

**命名子 Agent 人设有亮点**: Alice/Bob/Charlie/Eve 比匿名 delegate_task 更有组织感，用户能直观理解"谁在干什么"。

**风格品牌化命名**: "Claude风格""NVIDIA风格"比 "Bold Signal""Neon Cyber" 更直观，降低用户选择成本。

**33614 Skills 要打折扣**: 数量≠质量，大部分是低质量 prompt 模板。我们的 138 个精品路线更适合深度用户。

## 启发与借鉴

1. **子 Agent 角色命名**: delegate_task 时可以加人设描述，输出更清晰
2. **风格预设品牌化**: html-slides 的 12 种预设可以加品牌别名
3. **多阶段 To-Do 可视化**: 任务拆解后展示进度，用户感知更好
4. **PPT 生成深度**: 逐页 HTML 精细渲染的思路值得 ppt-generator 借鉴

## 批判性思考

- **30分钟出 PPT** — 慢但深，质量 > 速度，这个定位合理
- **文章是软文** — "没有模板味""独一份"来自作者自己，缺乏横向对比
- **"专家团围绕你"** — 营销话术，实际就是 multi-agent delegation
- **Windows Only** — 本地部署但目前只支持 Windows，限制了用户群

## 相关笔记
- [2026-04-17-AutoClaw-自进化与Skill商店](2026-04-17-AutoClaw-自进化与Skill商店.md) - 智谱 AutoClaw 动态
- [2026-04-13-hermes-agent-vs-openclaw](2026-04-13-hermes-agent-vs-openclaw.md) - Hermes vs OpenClaw 对比
- [2026-04-07-OpenClaw-autonomy-harness-loop](2026-04-07-OpenClaw-autonomy-harness-loop.md) - OpenClaw 自主性约束循环
- [2026-04-04-OpenClaw 为什么越用越好用？本质就是一堆 md 文件](2026-04-04-OpenClaw 为什么越用越好用？本质就是一堆 md 文件.md) - OpenClaw 本质分析
