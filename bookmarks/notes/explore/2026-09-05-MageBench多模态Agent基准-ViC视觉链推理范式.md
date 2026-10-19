# MageBench 多模态 Agent 基准：ViC 视觉链推理范式与三环境实证

> 探索日期：2026-09-05 | 兴趣等级：L3 | 来源数量：3（arXiv 2412.04531 全文 / GitHub README / WACV 2026 PDF）| 类型：auto-explore
> 关联：[2026-09-05 Agent记忆三阶段进化与2026基准盘点](../2026-09-05-Agent记忆三阶段进化-Storage到Experience与2026基准盘点.md)（语言侧 Agent 基准盘点，本篇补多模态侧）

## 摘要

MageBench 是微软开源的**推理导向**多模态 Agent 基准（arXiv 2412.04531，WACV 2026 接收，代码+HF Leaderboard 全开源）。核心贡献是提出 **ViC（Vision-in-the-Chain）** 推理范式：现有 LMM 基准与 Visual CoT 的推理链全在文本侧（视觉只负责输入端信息提取），而真实 Agent/机器人需要**视觉信号在决策全程持续更新并参与推理链**。三环境 483 场景（WebUI 网页重建 / Sokoban 推箱子 / Football 足球），两种基线 Agent（Global 单次观察 = Visual CoT；Online 持续交互 = ViC）。核心结论：Online 设置下**仅 GPT-4o 与 Gemini-1.5-Pro 超过随机基线**，全部远逊人类（PhD 标注者）；模型普遍缺乏基于视觉反馈修正规划的能力、视觉想象力与图文交错长上下文处理。

## 关键发现

### 1. ViC vs Visual CoT 的本质区别

```
Text CoT:    纯文本推理链
Visual CoT:  图像 → 信息提取 → 之后全程文本推理
             （视觉只是输入端，推理仍是"文本链"）
ViC:         每步动作后获得新视觉观察 → 进入下一步推理
             （视觉反馈是推理链的持续组成部分）
             对应场景：导航 / 驾驶 / 机器人 / 网页渲染反馈迭代
```

论文的筛选铁律：**凡用文本反馈就能完成的任务一律不收**（很多网页操作环境因此被排除）——保证"视觉反馈不可或缺"。

### 2. 环境选择哲学：推理导向而非环境导向

三原则：推理代表性 / 视觉反馈不可或缺 / 简单轻量（低延迟低成本，为未来 RL 训练与 scaling 留空间）。机器人仿真（OmniGibson）、VR 游戏（Minecraft）、App 操作被主动排除——它们高层规划太简单，错误集中在感知与指令跟随层，"规划层面没有可操作性"。

- **WebUI**：按截图+图文交错描述重建网页，评 AES（原子元素 CSS 相似度）。考工程知识与能力
- **Sokoban**：182 关推箱子，历史最优 reward。考空间智能与前瞻规划（大量输局陷阱态）
- **Football**：108 场景（个人突破/团队配合/世界杯实战），只控持球者，18 个文本动作。考多体协作交互，密集奖励函数（6 项 λ 加权：推进/过人/进球/抢断/传球/射门质量）替代高方差胜率

### 3. Table 1 核心数据（mini set）

```text
                 WebUI AES%        Sokoban Reward      Football
                 Global  Online     Global  Online      Online
Claude-3.5      64.11   62.08     48.26   45.35       16.94
Gemini-1.5-Pro  44.79   39.30     46.13   51.84       18.33
GPT-4o          34.28   35.50     46.09   53.03       21.20
InternVL2-76B   16.22   16.76     44.56   43.58       10.50   ← 开源最强
Random 基线      0.00    0.00      46.61   46.61       17.33
Human(PhD)      68.71   94.32     83.63   96.85       54.68
```

三个刺点：

- **Sokoban 随机基线高达 46.61**——绝大多数开源模型在线设置不如乱按
- **Claude WebUI-Global 64.11 ≈ 人类 68.71**，但 Online 掉到 62 vs 人类 94：人类能看着渲染结果持续改代码到近乎完美，模型做不到（图文交错长上下文短板）
- Football 只有 Online（21 AI 玩家随机性太大，Global 无意义）

### 4. Best-of-N 曲线揭示的 RL 可训性分化（最有工程价值的发现）

- **Football**：best-of-N 陡峭上升，多模型可超人类 → **RL 提升空间大**
- **Sokoban**：best-of-N 增长缓慢，模型 best-of-N 远不如人类 best-of-1 → 试错难以产生有价值轨迹，**视觉想象力/前瞻规划是机制级缺失**，直接 RL 强化收益有限（需要世界模型类机制）
- **WebUI**：曲线形态类似代码生成的 pass@N

### 5. 错误统计：RA（重复动作）是 ViC 数据缺失的信号

IA（格式非法）/ RA（token 重复导致重复动作）。RA 高发于训练-测试域不匹配——Claude 在 Football-O RA 43%、InternVL2 在 Sokoban-O RA 80%。结论：现有模型普遍没训过 ViC 型数据。

### 6. 可复用工程设计

- Online Agent 记忆解耦：AM=5（动作记忆）/ OM=1（观察记忆），因多数 LMM 多图输入受限；实测两类记忆对当前模型影响不大
- Football 自动渲染算法：平均 API 调用 80 → <20 次/场景，结果无影响
- 统一 OpenAI 输入格式接 vllm/lmdeploy/各家 API；环境三行 API（`get_env()` → `take_action()` → `Evaluator()`），POMDP 形式化
- 方差控制：mini 集 Sokoban/WebUI 重复 3 次、Football 10 次取均值；解析错误才给 2 次重试

## 对现有 Skill/笔记改进建议

- **P2**：`edge-llm-quantization`（Jetson 端侧 VLM 部署）可补一条"端侧 VLM Agent 能力评测参考 MageBench Sokoban（零重型依赖）"——暂缓，待实际做端侧 Agent 评测时再 patch
- **P2**：与 2026-09-05 Agent 记忆基准盘点笔记互链（语言侧 vs 多模态侧互补）——本篇已建立链接 ✅
- `vision-image-recognition` 排查链不受影响（静态识图 ≠ ViC 动态推理，两回事）

## 对工作的价值

- **选型警示**：给 Hermes/GLM-4.5V 类视觉任务选模型时，静态 VQA 分数不能外推 Agent 能力——ViC 是正确评测视角；图文交错长上下文是独立短板
- **机器人规划预判**：Sokoban 结论直接警示 DUCK-Pi_5 类项目——视觉前瞻规划不能靠 best-of-N/简单 RL 补，需引入显式世界模型或搜索机制
- **可跑性**：环境轻量（Docker cuda11.8，A100 验证），Jetson Orin 原则上可跑 mini set 作端侧 VLM 实测

## 行动建议

1. 做端侧 VLM Agent 选型时，用 MageBench mini set（Sokoban 零重型依赖）做 30 分钟快测（P2）
2. 跟踪 HF Leaderboard（microsoft/MageBench-Leaderboard）看 2026 新模型在 ViC 上的进展（P2）
3. 记忆/笔记系统无需变更，仅建立互链 ✅

## 关键风险与盲点

- 来源级别：**官方验证**（论文 + 开源代码 + HF Leaderboard 三件套）
- 模型阵容停在 2024-12（GPT-4o/Gemini-1.5/Claude-3.5 时代）；o3/GPT-5/Gemini-3 一代在 ViC 上表现未知，"仅 2 模型超随机"的结论可能已过时
- 人类基线取自 PhD 标注者，门槛偏高；开源模型后续版本（Qwen2.5-VL/Qwen3-VL）未覆盖
- 轻量环境是双刃剑：可扩展性好但牺牲真实性；Football 只控持球者是多智能体的弱化版

## 一页速查

> **MageBench = 微软 | WACV 2026 | arXiv 2412.04531 | 三环境 483 场景**
> 核心概念：ViC（Vision-in-the-Chain）= 视觉反馈持续参与推理链，区别于 Visual CoT（视觉只在输入端）
> 三环境：WebUI 重建（工程）/ Sokoban 182关（空间规划）/ Football 108场景（协作，仅 Online）
> 两基线：Global（一次观察全输出=Visual CoT）/ Online（AM=5,OM=1 持续交互=ViC）
> 铁数据：Sokoban 随机基线 46.61，多数开源模型不如随机；Claude WebUI-Global 64≈人类 69 但 Online 62 vs 人类 94
> RL 分化：Football best-of-N 陡（RL 有戏）；Sokoban 平（视觉想象力机制级缺失，RL 难救）
> RA 重复动作 = ViC 训练数据缺失信号（InternVL2 Sokoban-O RA 80%）
> 用途：VLM Agent 选型评测（勿用静态 VQA 分数外推）；端侧可跑

## 待深入

- HF Leaderboard 上 2025-2026 新模型（Qwen3-VL / GLM-4.6V / Gemini-3）成绩
- ViC 型训练数据如何构造（论文只诊断未给方案）——与视觉想象力/世界模型路线的交叉

## 来源列表

1. arXiv 2412.04531v1 全文（2024-12，WACV 2026 接收）— https://arxiv.org/abs/2412.04531
2. GitHub microsoft/MageBench README（工程细节与 API）— https://github.com/microsoft/MageBench
3. WACV 2026 CVF Open Access PDF — https://openaccess.thecvf.com/content/WACV2026/papers/Zhang_MageBench_Bridging_Large_Multimodal_Models_to_Agents_WACV_2026_paper.pdf


## 相关笔记

- [2026-09-04-SimSkill自进化仿真Agent三层记忆](./2026-09-04-SimSkill自进化仿真Agent三层记忆.md) — 仿真Agent记忆结构
- [2026-09-05-Agent记忆三阶段进化-Storage到Experience与2026基准盘点](../2026-09-05-Agent记忆三阶段进化-Storage到Experience与2026基准盘点.md) — 语言侧基准盘点姊妹篇
