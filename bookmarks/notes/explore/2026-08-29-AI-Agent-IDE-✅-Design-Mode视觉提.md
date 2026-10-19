# AI Agent IDE: Design Mode 视觉提示（2026-08-29 增量）

> 嗅探学习 | 2026-08-29 | 来源: TinyFish Search + curl 直取 Cursor 官方博客 + HN Algolia + GitHub API
> 前序笔记: [AI Agent IDE SDD三层谱系与ACP标准化](2026-08-29-AI-Agent-IDE-SDD三层谱系与ACP标准化-增量.md)、[Intent spec-driven多Agent协调](2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md)
> 知识基: ai-agent-ide-knowledge-bank.md（本次同步更新）

## 摘要

本次为 AI Agent IDE 领域第 4 次嗅探，聚焦知识基未覆盖的子方向「Design Mode 视觉提示」——用空间交互（点击/圈选/绘制/语音）替代纯文本 prompt 指挥 agent 改 UI。Cursor 于 2026-06-05 发布 Design Mode 更新，是当前该方向的标杆实现；外围有 prompt-canvas（开源 React overlay）、Figma Make annotations（设计侧对齐）、Google Generative UI（模型侧）三条相关线。核心命题：**UI 工作是空间性的，chat 是线性的——视觉提示在收紧「看到→改到」的回路**。

## 关键发现（增量）

**1. Cursor Design Mode：视觉提示的完整产品形态**（官方博客，2026-06-05）
- 四种意图传达方式：**点击选中元素**（对单个组件下指令）、**多选**（描述元素间关系，如"让 B 和 A 一致"、批量调整）、**绘制标注**（圈选区域，标注冻结在当前视口帧上，agent 看到的就是你看到的页面状态）、**语音叙述**
- **技术实现是关键增量**：选中元素会注入两路互补信号——①元素身份（xpath、组件名、attributes、computed styles、**React fiber tree 的 props**）②截图（空间上下文：布局、周边元素、精确页面状态）。即"结构化 DOM 信号 + 视觉信号"双通道，不是纯截图扔给多模态模型
- **异步多编辑流水线**：一条编辑未完成就可发下一条，支持管理多个并行 subagent；agent 完成后 app 热重载，"noticing→editing"循环变紧
- 模型匹配：这类高频小编辑推荐 Composer 2.5（快 + 界面工作强），印证「编辑节奏决定模型选型」而非一味用最大模型
- 入口在 Cursor 浏览器（Agents Window），annotation 直接叠加在运行中的产品上

**2. prompt-canvas：开源平替，23★ 早期项目**（github.com/adiasg/prompt-canvas，2025-09 创建）
- npm 包 + React 组件，dev 模式挂载 overlay，在真实前端上绘制批注 → 截图复制 → 粘贴给任意 coding agent
- 与 Cursor 路线的本质差异：**无 DOM/fiber 信号通道**，只有视觉信号；也不做 agent 集成，只解决"画给 agent 看"这一步
- Quickstart 本身是一个 installation prompt（让 agent 自己装 overlay）——工具分发也在 agent 化

**3. Figma Make：设计侧的同一收敛**（官方 solutions 页）
- properties panel + annotations：选中元素直接改属性，或在上下文中写 in-context prompt，"bridging design and code"
- 与 Cursor Design Mode 互为镜像：Cursor 从 IDE 侧往设计走，Figma 从设计侧往代码走，两者在中点（可视化元素级编辑 + 上下文内 prompt）收敛

**4. Google Generative UI：模型侧的前置条件成熟**（research.google 博客）
- Gemini 3 多模态理解 + agentic coding 能力 → AI Mode 可按任意 prompt 即时生成交互式工具/模拟器/游戏
- 意义：视觉提示闭环（理解视觉→生成视觉）的两端都被模型能力覆盖，Design Mode 类交互是模型能力的产品化出口

**5. 治理视角：A2UI 的安全分层**（griddynamics.com）
- agent 生成交互 UI 引出三风险：安全（注入）、可移植性、一致性
- A2UI 方案：agent 输出声明式 JSON 组件描述，客户端用**预审核组件目录**映射到原生控件——生成与执行解耦。对「agent 生成 UI」场景是比直接生成代码更安全的参考架构

## 对工作的价值（增量）

- **spec 之外的第三种意图通道**：知识基已沉淀 text spec（SDD）与 chat prompt，Design Mode 补上 spatial prompt——对 UI 密集型任务，「点选+圈画+语音」比写 spec 快一个量级。意图通道选型：结构性变更→spec；空间性微调→视觉提示
- **双通道信号注入可直接迁移**：Cursor 的「结构化身份（xpath/fiber/样式）+ 视觉截图」双信号模式，适用于任何 Hermes 需要把页面状态传给模型的前端调试/自动化场景——纯截图丢信息，纯 DOM 丢布局，两者互补
- **冻结帧标注解决状态歧义**：annotation 冻结在指令发出时的视口帧，agent 看到的页面状态与用户所见一致——多模态自动标注/前端 E2E 失败报告设计可借鉴，消除"截图时页面已变化"的竞态
- **标注即证据**：视觉提示天然带「指向哪个元素」的定位信息，比自然语言描述（"顶部那个蓝色的按钮"）消歧能力强，可作为 Hermes vision 流水线中 prompt 构造的格式参考

## 行动建议（增量）

1. Hermes 前端调试场景（若有）可实验 prompt-canvas：零成本拿到"视觉批注→agent"链路，验证双通道信号是否必要（对比纯截图效果）
2. 知识基已新增「视觉提示」子领域章节；下次该主题再触发时，追踪点：Cursor Design Mode 的 agent 编辑精度评估、prompt-canvas 是否长出 DOM 信号通道、Figma Make annotations 与代码 agent 的双向同步
3. 若做「agent 生成操作界面」类需求，参考 A2UI 的预审核组件目录模式，禁止 agent 直出可执行代码

## 参考来源（增量）

- Cursor 官方博客（全文直取）: https://cursor.com/blog/design-mode（2026-06-05，Erik Nilsson 等）
- prompt-canvas: https://github.com/adiasg/prompt-canvas（23★，2025-09-16 创建）
- Figma Make: https://www.figma.com/solutions/ai-ui-generator
- Google Generative UI: https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt
- A2UI 安全架构: https://www.griddynamics.com/blog/ai-agent-for-ui-a2ui
- Visual Vibe Coding（早期概念文，2025-08）: https://testchimp.io/blog/visual-vibe-coding/

## 相关笔记

- [AI Agent IDE SDD三层谱系与ACP标准化](2026-08-29-AI-Agent-IDE-SDD三层谱系与ACP标准化-增量.md)
- [Intent spec-driven多Agent协调](2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md)
