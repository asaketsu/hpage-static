# Harness VLA无需训练 — 冻结VLA封装成可调用原语+记忆引导Agent

#HarnessVLA #冻结VLA #AgenticPlanner #Primitive #记忆复用 #长程操作 #清华大学 #免训练部署

> **出处**：微信公众号「CCF学术组委会」，2026-08-17 11:40 发布（论文精读）
> 原文链接：https://mp.weixin.qq.com/s/hSPyX_zRAQD3t9XLvciG3g
> 论文：Harness VLA: Steering Frozen VLAs into Reliable Manipulation Primitives via Memory-Guided Agents（arXiv:2607.08448v3, 2026，于超团队清华大学）
> 抓取方式：移动 UA 直接 curl（3.4MB 全文）
> 主题：参数完全冻结的 VLA 不重训练，封装成 primitive + Agentic Planner 编排 + 双层记忆复用——LIBERO-Pro 上把冻结 VLA 从 50% 拉到 82.4%

## 一、内容整理

### 0. 核心思路

> 不要求一个 VLA 独自完成整条长程任务。**冻结的 VLA 封装成可调用原语（vla_act）处理 contact-rich 局部交互；确定性 analytic primitives 负责移动/旋转/导航/释放；最上层 Agentic Planner 决定下一步调用谁**

解决的问题：已训练好、参数冻结的 VLA，在任务和场景变化后（Semantic Retargeting / Goal Re-binding / Spatial-layout Shift / Unstable Local Contact）如何继续完成任务——很多 VLA 本来就有抓取/按按钮/开抽屉的局部能力，缺的是**把已有能力按新目标重新组织**。

### 1. 系统架构（三层闭环）

```
Task(自然语言) + RGB-D + Robot State + Memory
        ↓
   Agentic Planner（不输出 joint/torque/action chunk）
        ↓ 从固定 Primitive Library 选一个 + 结构化 JSON 参数
   ┌─ Analytic Primitives（运动学/模型控制器，免学习）
   │   move_to / move_pose / rotate_wrist / rotate_pitch
   │   set_gripper / release / navigate_to / move_base
   └─ vla_act（冻结 VLA 统一封装）
        prompt + max_chunks + stop predicate
        ↓
   环境/机器人执行 → 新 RGB-D + Robot State → Planner 验证
   → 继续 / Re-stage / Retry（直到任务达成或预算耗尽）
```

调用示例：`{"action": "vla_act", "prompt": "grasp the red mug", "max_chunks": 4, "stop": "object securely grasped"}`

### 2. 两类 Primitive 分工

| 类别 | 承担 | 依据 |
|---|---|---|
| **Analytic** | Free-space Transport / Staging / 姿态调整 / Navigation / Release | 几何目标清楚、接触少——运动学直接解 |
| **vla_act** | 抓取 / 紧约束放置 / 按钮按压 / 门-抽屉 / 插入 / 铰接物体 | contact-rich——训练好的 VLA 才会 |

**关键设计——staging/re-staging**：VLA 调用前后的机器人状态由 Planner 主动改变——先把机器人送进更适合调用 VLA 的局部状态（后退→重新定位→调 wrist→改 pre-contact pose→再调 vla_act）。一次 VLA invocation 只是 agent rollout 中的一次局部尝试。

### 3. 双层 Memory（存执行经验不存参数）

| 层 | 内容 | 形态 |
|---|---|---|
| **Task Specific Memory** | "这件事通常怎么做"——primitive 执行结构 | reference seed 上 exploratory bootstrapping（允许 reset+反复尝试），成功后存 JSONL trace；**空间坐标替换成 symbolic perception query**（"Move above current mug position"），新场景重新 grounding |
| **Global Memory** | "用这些 primitives 时要记住什么"——跨任务复用 | Success Rules + Failure Models：怎么写完整 task prompt、识别 empty grasp、避免 false success、何时 re-stage |

新 seed/目标位置/perturbation 部署时：读两类 memory + 当前 RGB-D 重新 grounding——**复用"执行结构和经验"，不重放固定坐标**（Mug 左边换右边，结构不变坐标重算）。

### 4. 测试阶段约束

- Reset Primitive 禁用 + 执行预算收紧
- 闭环执行：Stage → vla_act → 观察 Contact Outcome → 满足成功条件继续；empty grasp/unstable contact/wrong pose → Re-ground / Re-stage / Retry

### 5. 实验结果（四 benchmark）

| Benchmark | Frozen VLA 裸跑 | Harness VLA | 提升 |
|---|---|---|---|
| LIBERO（标准桌面） | RLinf 95.3% | Claude Code **96.0%** | +0.7 |
| **LIBERO-Pro**（指令重定向+位置交换） | RLinf 50.0% | Claude Code **82.4%** | +32.4（较对照最高 +38.6pp） |
| **RoboCasa365**（家庭厨房长程） | RLDX-1 30.0% | Codex **55.4%** | +25.4 |
| RoboTwin C2R（双臂 Clean→Randomized 迁移） | — | **58.4%**（clean 的 memory 直接迁移） | — |

**Backend 无关性**：VLA 换 RLinf/RPent/RLDX-1/LingBot-VLA 任一，Planner（Codex/Claude Code）看到的接口统一是 vla_act——上层只需知道何时调用+如何组织状态。

### 6. 核心结论（作者定位）

> Harness VLA 解决的不是"怎样训练一个更大的 VLA"，而是**"怎样把已存在的 VLA 能力组织成有任务分解、记忆、闭环反馈和失败恢复能力的执行系统"**。四不变量：参数不改变｜Primitive 词表不扩张｜Agent 重新 ground 场景｜Memory 复用已验证经验

## 二、查询拓展

1. **staging 状态空间的最优搜索**：Re-stage 的候选动作（后退/旋转/换 pre-contact pose）有无系统性排序策略，还是全靠 LLM 先验？
2. **Memory 的泛化边界**：Task Specific Memory 的 primitive 结构在多大概的场景分布偏移下失效（如桌面→货架）？
3. **与 DIMOS/ROS 技能栈的融合**：vla_act 作为 DimOS Skill 暴露、Analytic primitive 走 Stream 控制是否等价于本文架构的工程化？
4. **执行预算与安全约束**：预算耗尽前的失败判定；真机上 retry 循环的物理安全边界（连续失败时急停条件）
5. **LLM Planner 的延迟代价**：每步 primitive 切换都要过一次 LLM 推理（秒级）——长程任务的端到端时间与实时性的权衡

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | 冻结 VLA 封装成 vla_act 原语 + 解析式原语库 + Agentic Planner 编排 + 双层记忆——免训练把长程任务成功率最高拉 +38.6pp |
| 架构 | Planner（Claude Code/Codex）只选 primitive 给 JSON 参数；Analytic 管几何明确的；vla_act 管 contact-rich 的 |
| 天才处 | ①staging/re-staging 主动构造 VLA 的有利初始状态 ②记忆存结构不存坐标（symbolic query 化）③接口统一使 VLA backend 可插拔 |
| 数据 | LIBERO-Pro 50→82.4%；RoboCasa365 30→55.4%；RoboTwin C2R 迁移 58.4% |
| 边界 | 不解决"训练更大 VLA"；记忆泛化有限；LLM 每步规划有延迟；测试时禁 reset |
| 定位 | 与 AI4AI 同一哲学的机器人版：能力转移不靠改参数，靠组织方式（harness） |

## 四、趋势判断

1. **"冻结模型+Agent 编排"成为 2026 具身智能主流路线**：重训练成本高企（97 万数据+8×A100），Harness 类方案零训练成本拿 +30pp——ROI 压倒性优势下，"模型即插即用+上层编排"将成部署默认
2. **VLA 的商品化接口正在形成**：vla_act（prompt+max_chunks+stop predicate）事实上定义了 VLA 的"调用协议"——如同 LLM 的 function calling 之于 ChatGPT，VLA 生态会出现统一的 primitive calling 标准
3. **记忆=结构不存坐标 是跨场景迁移的通用范式**：symbolic perception query 化的记忆与 AI4AI 的"脚手架捕获可复用任务结构"完全同构——两大顶会路线在 2026 汇流到同一结论
4. **Coding Agent（Claude Code/Codex）作为机器人大脑的合法性确立**：论文直接用 Claude Code 当 Planner 并给出硬数据——通用 Coding Agent 下场机器人编排，ROS 工程师的角色向"Primitive 提供者"迁移
5. **与端到端 VLA 的分层共存格局**：OpenVLA/π0 卷模型能力，Harness/DimOS 卷组织能力——最终形态是 DimOS 提供运行时骨架 + Harness 提供编排策略 + VLA 提供局部技能的三层栈

## 五、关联分析

### 与已有笔记/体系的关联

| 关联对象 | 关系 | 说明 |
|---|---|---|
| 笔记《2026-08-18-AI4AI测试时能力迁移》 | 同一哲学双实例 | AI4AI：强模型为弱模型搭推理脚手架（0.49→0.91）；Harness VLA：Agent 为冻结 VLA 搭操作脚手架（50→82.4%）——**"不改参数改组织"范式在 NLP 与机器人双领域同年验证** |
| 笔记《2026-08-18-SEAL自适配语言模型》 | 对照路线 | SEAL 走权重层自进化（改参数）；Harness 走环境层编排（不改参数）——两条路线的成本差（重训练 vs 零训练）决定后者先落地 |
| 笔记《2026-08-18-DimOS双神经系统架构》 | 运行时+策略互补 | DimOS 提供 Module/Stream/RPC/Skill 运行时骨架，Harness VLA 提供 Planner 编排策略——vla_act 就是 DimOS @skill 的机器人实例，两层可组合成完整栈 |
| 笔记《2026-08-18-OpenVLA架构解剖》 | 技能层直接关联 | OpenVLA 类冻结 VLA 正是 vla_act 的候选 backend——解剖它的三笔代价（慢/量化误差/无本体）由 Analytic primitive+staging 补偿 |
| Hermes skill 体系 | 同构映射 | Task Specific Memory=experience-bank（任务经验卡）；Global Memory=error-case-library（跨任务失败模式）；staging=skill 的前置条件设计；Planner 决策树=iron_rules_engine 的模式路由 |
| skill `subtask-lifecycle` / `agent-workflow-orchestration` | 编排工程对照 | Harness 的 primitive 选择循环与我们的子任务生命周期管理同构——"预算收紧+禁 reset"对应生产环境的资源约束设计 |

### 对我们的直接价值（吸收+优化自我）

1. **"记忆存结构不存坐标"直接平移到 experience-bank**：经验卡应记录"这类问题通常的解决路径"（symbolic 步骤），参数值（具体路径/版本号）现场重新 ground——修复记忆的时效性问题时照此改造
2. **staging 思维用于任务编排**：调用重操作（如 hermes 升级/模型切换）前主动构造有利初始状态（备份/健康检查/预热），失败后不盲目重试而是 re-stage（改前置条件再试）——可写进 subtask-lifecycle 的失败恢复模式
3. **接口统一化使 backend 可插拔**：sensenova/zai/openrouter 的模型调用应统一成 `model_act(prompt, max_tokens, stop)` 式单一接口——fallback 链切换时上层逻辑零改动
4. **"冻结+编排"的经济启示**：与其等更大的 glm-6，不如把现有 glm-5.3 用 harness 组织好——我们的 skill 体系正是在做这件事，本文给了机器人侧的硬数据背书

→ 相关：2026-08-18-AI4AI测试时能力迁移-强模型为弱模型搭推理脚手架.md
→ 相关：2026-08-18-DimOS双神经系统架构-Agent离散思考与物理连续世界的共存设计.md
→ 相关：2026-08-18-OpenVLA架构解剖-7B-VLA透明样本的完整链路与OFT手术.md
→ 相关：2026-08-18-SEAL自适配语言模型-LLM部署后持续自我进化的双循环架构.md

## 相关笔记
- [边缘AI与On-Device-LLM前沿学习](2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [LLM-Agent多智能体信用归因与自进化](2026-05-31-LLM-Agent多智能体信用归因与自进化.md)
- [TinyML-ESP32端到端训练流水线提取](2026-06-03-TinyML-ESP32端到端训练流水线提取.md)
- [GPUStack-开源GPU集群管理平台-推理部署与统一调度](2026-08-11-GPUStack-开源GPU集群管理平台-推理部署与统一调度.md)
- [局域网A100算力池×双OCR-批量文档与微调业务流程](2026-08-15-局域网A100算力池×双OCR-批量文档与微调业务流程.md)
- [8卡A100局域网训练微调全流程指导](2026-08-16-8卡A100局域网训练微调全流程指导.md)
- [A100局域网部署DeepSeek-V4-Flash-框架选型与8卡微调](2026-08-16-A100局域网部署DeepSeek-V4-Flash-框架选型与8卡微调.md)
- [DeepSeek-Harness迁移笔记-Hermes老手艺8组对照](2026-08-16-DeepSeek-Harness迁移笔记-Hermes老手艺8组对照.md)
- [LLM边缘推理基准实测与TensorRT-EdgeLLM](2026-08-16-LLM边缘推理基准实测与TensorRT-EdgeLLM.md)
- [MIT人脑推理不依赖语言-LLM路线的神经科学参照系](2026-08-16-MIT人脑推理不依赖语言-LLM路线的神经科学参照系.md)
- [局域网A100训练农场lan-llm-farm-算力调用与四案例微调全流程](2026-08-16-局域网A100训练农场lan-llm-farm-算力调用与四案例微调全流程.md)
- [投机解码生产化指南-EAGLE-3到P-EAGLE的vLLM实践](2026-08-17-投机解码生产化指南-EAGLE-3到P-EAGLE的vLLM实践.md)
- [AI4AI测试时能力迁移-强模型为弱模型搭推理脚手架](2026-08-18-AI4AI测试时能力迁移-强模型为弱模型搭推理脚手架.md)
- [Dense-MoE-Diffusion三种架构科普-大模型像公司的三种组织方式](2026-08-18-Dense-MoE-Diffusion三种架构科普-大模型像公司的三种组织方式.md)
- [SEAL自适配语言模型-LLM部署后持续自我进化的双循环架构](2026-08-18-SEAL自适配语言模型-LLM部署后持续自我进化的双循环架构.md)
- [小模型LoRA微调实证-Qwen3.5-0.8B生产级抽取与边缘端峰值内存压缩](2026-08-18-小模型LoRA微调实证-Qwen3.5-0.8B生产级抽取与边缘端峰值内存压缩.md)
- [SinkFlex-RL长视野Agent高效RL训练](explore/2026-08-14-SinkFlex-RL长视野Agent高效RL训练.md)
- [SkillMisevo技能误进化](explore/2026-08-15-SkillMisevo技能误进化.md)
- [后训练技术-拒绝采样RS-RAFT到Reinforce-Rej](explore/2026-08-16-后训练技术-拒绝采样RS-RAFT到Reinforce-Rej.md)
- [SecondThought并行推理](explore/2026-08-18-SecondThought并行推理.md)
- [自进化Agent三框架与2026记忆基准](2026-08-16-自进化Agent三框架与2026记忆基准.md)
- [Agent记忆系统2026综述-write-manage-read闭环与记忆即RL策略转向](2026-08-18-Agent记忆系统2026综述-write-manage-read闭环与记忆即RL策略转向.md)
- [DimOS双神经系统架构-Agent离散思考与物理连续世界的共存设计](2026-08-18-DimOS双神经系统架构-Agent离散思考与物理连续世界的共存设计.md)
- [AI-Agent-IDE-Cursor竞品全景](explore/2026-08-16-AI-Agent-IDE-Cursor竞品全景.md)
- [Agent-Optimization替代SEO-GEO商业模式](explore/2026-08-16-Agent-Optimization替代SEO-GEO商业模式.md)
