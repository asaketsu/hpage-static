# 开源3D/设计AI: OpenSCAD + LLM（2026增量更新）

> 嗅探学习 | 2026-07-26 | 来源: TinyFish + HN Algolia + arXiv + curl直取
> 前序笔记: [2026-06-09-开源3D设计AI-OpenSCAD+LLM](2026-06-09-开源3D设计AI-OpenSCAD+LLM.md)

## 摘要

本次为 47 天后的增量追踪。领域未出现颠覆性范式转移，但有三条显著进展：(1) **ModelRift 发布"建造万神殿"OpenSCAD LLM Benchmark**，用复杂建筑（穹顶+柱廊+三角楣）替代简单的 cube+hole，成为新的能力标尺；(2) **Google Antigravity 2.0 登顶该 Benchmark**（HN 421pts），但社区对其工程成熟度评价两极分化；(3) 学术界从"LLM 直接写 OpenSCAD"转向**约束求解器辅助的分层 DSL**（AIDL, arXiv:2502.09819），few-shot 下超越 OpenSCAD 本身。同时一篇 dev.to 深度复盘总结了 LLM 在 OpenSCAD 上的三大系统性失败模式。

## 关键发现（增量）

**1. ModelRift Pantheon Benchmark — 新的能力标尺**
- 标的：用 OpenSCAD 重建罗马万神殿（rotunda 穹顶 + portico 柱廊 + pediment 三角楣 + oculus 天窗）
- 设计哲学：OpenSCAD 不适合有机曲面/角色建模，但擅长布尔运算、径向对称、拉伸、构造实体——万神殿恰好是这些特性的"中间难度"测试
- 意义：替代了"cube with a hole"这种只能测 difference()/cube() 语义的玩具测试
- 评测方式：OpenSCAD CLI 渲染预览 + 迭代，弱模型产出"隐约像穹顶建筑"，强模型要正确处理圆鼓身/矩形门廊/穹顶环/正立面的关系
- URL: modelrift.com/blog/openscad-llm-benchmark/

**2. Antigravity 2.0 登顶（Google）**
- HN 421pts 热议，标题"Antigravity 2.0 Tops the OpenSCAD Architectural 3D LLM Benchmark"
- 社区反馈两极：有人认为"三年前惊叹能产出任何东西，现在能挑刺是奢侈"；也有人吐槽 Antigravity IDE 连基本 Electron 部署配置 bug 都没修好、每次用都要浏览器登录、计费碎片化
- 旁证：Autonomous 2025-12 发布的 Fusion agentic assistant，半年后仍"quite bad"——专业 CAD 的 agentic 路径比通用编程难得多
- 启示：通用 LLM（Antigravity/GPT-5.5）在 OpenSCAD 上已超过专用 CAD agent，"一个模型干所有事"暂时占优

**3. AIDL — 约束求解器辅助的分层 DSL（arXiv:2502.09819, 2025-02）**
- 核心洞察：LLM 在 CAD 上的瓶颈是 (a) 无法做空间推理 (b) 长程规划复杂几何困难
- 方案：设计 solver-aided hierarchical DSL "AIDL"，把空间推理卸载给几何约束求解器
- 关键结论：**few-shot 下 AIDL 超越 OpenSCAD**（即使在 OpenSCAD 已在训练数据中的情况下），视觉结果更贴近 prompt 且更易后处理
- 范式意义：纯"LLM 写代码"路线遇到天花板，"LLM 写高层意图 + 求解器落地几何"是更有前途的架构

**4. Why LLMs Fail at OpenSCAD — 三大系统性失败模式（dev.to 深度复盘）**
- **坐标系混乱**：OpenSCAD 是右手系 Z-up，但训练数据混杂 Blender/Unity 的 Y-up 习惯，模型平均后产生 nonsense
- **旋转累积错误**：rotate([x,y,z]) 的 Euler 角顺序极易搞反，"pitched roof"知道词却不知道 3D 含义，屋顶切穿墙体
- **CSG 状态丢失**：union/difference/intersection 需要持续追踪"实体 vs 空洞"，LLM 在 2-3 层嵌套后就丢失 minuend（被减数），"difference means subtract"的模式匹配崩塌
- 实例：要"带窗的房间"，产出 80 行看起来正确的代码，渲染出来是"regret 形状的抽象艺术"

**5. A11yShape — 无障碍建模（arXiv:2508.03852, 2025-08）**
- 面向盲人/低视力（BLV）程序员，用 LLM + OpenSCAD 让他们理解和迭代 3D 模型
- 核心机制：跨表示高亮（cross-representation highlighting）——代码/语义层级/AI描述/3D渲染四处同步选中
- 4 名 BLV 程序员多 session 研究，独立完成 12 个模型，满意度高
- 价值：证明 OpenSCAD 的纯文本本质不仅是 LLM 友好，也是可访问性友好

## 对工作的价值（增量）

- **Benchmark 方法论迁移**：ModelRift 的"选一个领域中间难度的标志性对象"（万神殿之于 OpenSCAD）可作为任何代码生成 benchmark 的设计模板——比 LeetCode 风格的玩具题更能区分模型能力
- **AIDL 架构启发**：solver-aided DSL 模式可迁移到其他"LLM 擅长意图但不擅长精确执行"的领域（如 SQL 查询优化、正则表达式、Shader 编写）——把确定性部分交给专门引擎
- **失败模式诊断框架**：dev.to 的三模式（坐标系/旋转/CSG状态）是诊断任何"代码能跑但结果错"问题的模板：先查约定不一致、再查累积运算、最后查状态追踪
- **Antigravity 风险信号**：登顶 benchmark ≠ 工程成熟，IDE 基础设施 bug 提醒——评估 AI 工具不能只看模型能力分数，要看 dev experience 完整度

## 行动建议（增量）

1. 在自己的代码生成 benchmark 设计中借鉴"标志性对象"原则（如用 React 重建一个真实产品页而非 todo app）
2. 关注 AIDL 论文的 solver-offload 架构，评估是否可用于 Hermes Agent 的工具调用层（把确定性约束交给专门求解器）
3. 将 dev.to 的三大失败模式纳入代码审查 checklist：约定一致性 / 累积运算顺序 / 状态追踪深度
4. Antigravity 2.0 暂作观察，不急于集成——等工程稳定性信号明确

## 参考来源（增量）

- ModelRift Pantheon Benchmark: https://modelrift.com/blog/openscad-llm-benchmark/
- Antigravity 2.0 HN 讨论（421pts）: https://news.ycombinator.com/item?id=48234090
- AIDL 论文: arXiv:2502.09819 (2025-02)
- A11yShape 论文: arXiv:2508.03852 (2025-08)
- Why LLMs Fail at OpenSCAD: https://dev.to/alanwest/why-llms-fail-at-openscad-code-generation-and-how-to-fix-it-2bel

## 相关笔记
- [开源3D设计AI-OpenSCAD+LLM（首版）](2026-06-09-开源3D设计AI-OpenSCAD+LLM.md)
- [开源3D_设计AI-AI编程3D建模](2026-07-16-开源3D_设计AI-AI编程3D建模.md)
- [开源3D_设计AI-Antigravity](2026-06-08-开源3D_设计AI-Antigravity.md)
