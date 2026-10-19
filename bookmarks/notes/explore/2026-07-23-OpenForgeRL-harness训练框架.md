# OpenForgeRL：在真实 Harness 中端到端训练 Agent 的开源框架

> **arXiv**: [2607.21557](https://arxiv.org/abs/2607.21557) | **发表**: ICLR 2027 投稿
> **作者**: Xiao Yu, Baolin Peng, Ruize Xu, Hao Zou, Qianhui Wu, Hao Cheng, Wenlin Yao, Nikhil Singh, Zhou Yu, Jianfeng Gao
> **机构**: 微软研究院
> **日期**: 2026-07-23
> **领域**: cs.AI / cs.CL — Agent 训练基础设施
> **精读日期**: 2026-07-27

---

## 一、内容详细整理

### 1.1 核心问题与研究动机

现代 AI Agent 已不再是一个裸 LLM，而是被包裹在日益复杂的**推理 harness** 中——Claude Code、Codex、OpenClaw 等编排脚手架，负责多轮交互、工具调用、上下文管理，并通过 MCP Server、浏览器、GUI 连接外部系统。

然而，**开源社区无法端到端训练这些 harness-based agent**，原因有二：

1. **推理-训练不匹配**：Harness 将推理变成了 stateful、multi-process 的流程（嵌套工具调用、subagent、长程上下文），而开源 RL 框架（veRL、Slime 等）假设 rollout 是简单的单轮或多轮 + 轻量工具调用。为了训练不得不重新实现一个简化版 harness，导致 **train-deploy mismatch**。
2. **环境无法共址**：Harness rollout 需要专用容器化环境（独立 CPU/内存），无法与训练节点共址运行，而大多数开源 RL 框架假设 rollout 在 trainer 本地执行。

这两个差距导致**闭源 harness-based 系统越来越领先于研究社区能训练和研究的水平**。

---

### 1.2 方法论：OpenForgeRL 双组件架构

#### 2.1 核心设计理念

**解耦训练与推理**——不需要重新实现 harness，而是通过两个轻量组件让任意 harness 接入任意 RL 训练框架。

### 2.2 组件一：轻量 Proxy（推理拦截器）

- **作用**：包装推理服务器（如 vLLM），拦截所有来自 harness 容器的生成请求
- **关键能力**：将 harness 的 LLM 调用路由到 RL 框架的推理引擎，同时记录每个 prompt-response pair
- **轨迹重建**：rollout 结束后，proxy 收集终局奖励 r_T 和所有 prompt-response pairs，重建为标准训练样本：

  ```
  τ = (s_0^H, a_0, r_0), (s_1^H, a_1, r_1), ..., (s_T^H, a_T, r_T)
  其中 r_t = γ^(T-t) · r_T，通常 γ=1.0
  ```

- **GRPO 优化**：组内比较不同轨迹的平均奖励计算 advantage

### 2.3 组件二：Kubernetes Orchestrator（远程沙箱编排）

- 基于 Orchard (Peng et al., 2026) 实现，在 Microsoft Azure 上创建/管理/删除 rollout 容器 pod
- 弹性扩展并发环境数量，不增加训练节点负载
- **三个工程挑战的解决方案**：
  - **异步 rollout + 超时**：不用 turn 限制（不同 harness 的 "turn" 定义不一致，且 Codex 不暴露 turn 限制），改用墙钟超时。超时后终止 rollout 并返回 error signal，训练继续从其余 rollout 收集
  - **错误处理**：网络问题、harness 崩溃、超时等非策略原因导致的失败，丢弃整条轨迹的所有样本（参考 DAPO 策略），避免误导性训练信号
  - **部分 rollout 的信用分配**：论文承认当前策略过于简单（直接丢弃），更好的 credit assignment 是未来方向

### 2.4 数据合成 Pipeline（五步法）

为数据稀缺领域（GUI/计算机使用）生成 SFT 和 RL 任务：

1. **Propose**：基于 web/X API 或参考资产池，生成贴合真实场景的候选指令
2. **Prune**：去除低质量和重复任务
3. **Build**：为每个任务构建可执行环境（自定义 Dockerfile）和验证脚本
4. **Test**：用独立开源 LLM/VLM rollout 测试任务
5. **Refine**：修补缺陷直到通过所有检查

Test 和 Refine 阶段确保每个任务在进入数据集前完整可执行。Pipeline 自然从 Linux/CLI 任务扩展到 GUI 任务（用 Xvfb 渲染虚拟显示）。

**数据规模**：
- Claw（SFT 892 条 / RL 343 条）
- GUI Computer-Use（SFT 795 条 / RL 252 条）
- GUI Browser-Use（SFT 1496 条 / RL 900 条）

---

### 1.3 关键实验结果

#### 3.1 Claw Agent 实验（Qwen3-30B-A3B）

训练配置：
- 骨干模型：Qwen3-30B-A3B-Thinking（MoE，~3B 活跃参数）
- SFT：MiniMax-M2.5 蒸馏，每任务 N=3 rollouts，仅保留成功的
- RL：从 SFT checkpoint 继续，GRPO，batch=8，group=8，8×B200 GPU
- Harness：ReACT、ZeroClaw、OpenClaw、Codex（四种）

**ClawEval / QwenClawBench / MCPAtlas 结果**：

- Claude Opus 4.6（SOTA）：70.8 / 59.5 / 76.4
- **OpenForge-Claw(SFT+RL)：31.7 / 33.7 / 28.1**
- OpenForge-Claw(SFT)：21.7 / 32.1 / 23.6
- Qwen3-30B-A3B-Thinking（基座）：14.3 / 21.8 / 12.4
- Qwen3-Coder-30B-A3B-Instruct：30.4 / 24.3 / 19.1

RL 在 SFT 基础上全面提升：pass^3 21.7→31.7（+10），QwenClawBench 32.1→33.7，MCPAtlas 23.6→28.1。

### 3.2 GUI Agent 实验（Qwen3-VL-8B）

训练配置：
- 骨干模型：Qwen3-VL-8B-Thinking（~8B）
- SFT：Kimi-K2.5 蒸馏
- RL：GRPO，batch=8，group=8，8×B200 GPU
- Harness：Kimi-Agent（Computer-Use）、Molmo-Web（Browser）

**OSWorld-Verified / Online-Mind2Web / WebVoyager 结果**：

- GPT 5.4（SOTA）：75.0 / 92.8 / —
- Claude Opus 4.6：72.7 / 84.0 / —
- **OpenForge-GUI(SFT+RL)：37.7 / 63.0 / 72.3**
- OpenForge-GUI(SFT)：34.4 / 57.4 / 61.5
- Qwen3-VL-8B（基座）：29.4 / 38.7 / 49.2

8B 模型超越了同规模的 UI-TARS-1.5-7B（27.4/31.3/66.4）和 OpenCUA-7B（28.2），接近甚至超过数倍大的模型。

### 3.3 Harness 对比分析（核心洞察）

在 ClawEval 上用四种 harness 评估同一个训练后模型（pass@1）：

- ReACT* → ZeroClaw → OpenClaw → Codex（复杂度递增）
- 基座模型：26.1 / 32.5 / 11.4 / 12.2
- SFT+RL 后：45.1 / 48.5 / 20.9 / 32.5

**两个趋势**：
1. 支持直接添加自定义工具的 harness（ReACT/ZeroClaw）性能最高
2. SFT+RL 在除 OpenClaw 外的所有 harness 上都大幅提升；OpenClaw 增益有限但消耗更长的 prompt 和上下文

### 3.4 跨 Harness 泛化

- 仅在 ZeroClaw 训练 → 评估未见过的 OpenClaw/Codex：仍提升 +3.3/+4.6
- 在三种 harness 上联合训练 → 全面最优，ZeroClaw 48.5、OpenClaw 20.9（+9.5）、Codex 32.5（+20.3）
- **结论**：多 harness 训练显著优于单 harness，因为模型见到更丰富的工具调用和控制流

### 3.5 RL 学到了什么（行为分析）

对比 100 条 SFT vs SFT+RL 轨迹：

- **工具使用转变**：generic shell calls 从 22.6% 降至 13.9%，转向专用服务工具。RL 教会模型"用对的专用工具，而非 fallback 到通用 shell"
- **轨迹变短**：RL 后平均轨迹长度略减
- **自验证增强**：模型更多地在写操作后读回确认
- **工具覆盖扩大**：使用了任务要求的更广的工具集
- **Error recovery 最弱**：即便 RL 后仍是最弱能力。论文假设：这类能力难以仅从 RL 获得，可能需要专用数据或训练方法

---

### 1.4 创新点分析

1. **首次实现 harness-agnostic 训练**：不需要重新实现简化版 harness，通过 proxy + orchestrator 让真实部署的 harness 直接参与训练。这与 Polar (Xu et al., 2026) 的并发工作形成对比——后者仅覆盖 SWE-Bench-Verified，OpenForgeRL 覆盖 6 个 benchmark、文本+视觉两类模态

2. **轨迹重建的优雅抽象**：将 harness 推理抽象为无序的 prompt-response pair 集合 τ，用 γ^(T-t) 的折扣奖励回溯分配。这让任何 RL 算法（不限于 GRPO）都能消费

3. **墙钟超时替代 turn 限制**：认识到 "turn" 在不同 harness 中定义不一致，改用墙钟时间，更适合异构 harness 生态

4. **Harness 难度的实证发现**：首次系统性证明"简单、工程化良好的 harness 更容易被学习"，为 harness 设计提供了量化依据

5. **Error recovery 瓶颈的诚实声明**：承认 RL 无法显著改善 error recovery，需要 dedicated data。这与 Beyond the Leaderboard (2607.05775) 的发现呼应——error recovery 是 Agent 六大失败模式中最顽固的

---

### 1.5 局限性与未来方向

#### 论文自述
- 部分 rollout 的信用分配直接丢弃，可能损失有价值的训练信号
- Error recovery 需要 dedicated data 或训练方法
- 数据合成 pipeline 的质量上限取决于 seed 资产

### 分析补充
- **仅验证了 MoE 小模型**：Claw 用 30B-A3B（~3B active），GUI 用 8B。更大规模模型的 scaling 行为未验证
- **GRPO 特定优化**：轨迹重建后的 advantage 计算绑定了 group-based 算法，PPO 等非组算法需适配
- **Azure 依赖**：orchestrator 基于 Azure K8s，迁移到其他云厂商需额外工程
- **harness 版本漂移**：训练用某版本 harness，部署时 harness 迭代可能引入新的 train-deploy mismatch

---

## 二、查询拓展

### 2.1 Harness-agnostic 训练范式

OpenForgeRL 首次系统性地将"训练-部署解耦"理念引入 Agent 训练。传统 RL 训练假设模型与训练框架直接交互，而 harness-based agent 的推理是 multi-process、stateful 的。Proxy 拦截 + 轨迹重建的组合，本质上是一种 **"推理即训练数据"** 的范式——任何能发出 LLM 调用的系统，都可以成为训练数据源。

### 2.2 GRPO 与 Group-based 优化

本文使用 GRPO（Group Relative Policy Optimization），不使用 critic 网络，而是在同一 group 内比较不同轨迹的奖励来计算 advantage。组大小为 8，意味着每个 prompt 采样 8 条轨迹做相对比较。这是 DeepSeek-R1 验证过的高效 RL 算法，适合 agent 场景因为 terminal reward（成功/失败）信号天然适合组内对比。

### 2.3 veRL 训练框架

veRL（Sheng et al., 2024）是字节跳动开源的分布式 RL 训练框架，支持 PPO/GRPO 等算法，使用 3D 并行（数据/张量/流水线）。OpenForgeRL 将 veRL 作为训练后端，通过 proxy 将远程 rollout 容器与本地训练循环连接。

### 2.4 MCP Server 与 Skill.md 生态

论文提到 ClawEval 专用工具通过 **SKILL.md 文件**暴露给 OpenClaw 和 Codex。这与 Hermes Agent 的 Skill 体系完全一致——SKILL.md 是工具/能力的声明式描述文件，Agent 读取后决定何时调用。论文验证了"SKILL.md 驱动的工具注册"在训练侧同样有效。

### 2.5 Xvfb 虚拟显示与 GUI Agent 训练

GUI Agent 训练用 Xvfb（X virtual framebuffer）在无头容器中渲染虚拟 X 显示，让 VLM 可以通过截图+鼠标键盘操作控制"虚拟计算机"。这是 computer-use agent 训练的关键基础设施。

---

## 三、归纳总结

### 3.1 核心贡献

### 🔨 P0：Proxy 拦截模式 → Agent Trajectory 记录中间件

OpenForgeRL 的 proxy 在推理层拦截所有 LLM 调用并记录 prompt-response pair。Hermes Gateway 可实现类似的 **trajectory recording 中间件**：
- 记录每次工具调用的完整输入输出，形成可复用的 trajectory 数据
- 用途：失败分析（error-case-library 的数据源）、行为审计、未来 SFT 微调的数据积累
- 工作量：在 Hermes Gateway 的请求管道中插入一个 recording hook，约 2-3 天
- 现状：Hermes 有 observability-dashboard 但未系统化记录 prompt-response pair

### 🔨 P0：Harness 难度排序 → Skill 分层架构验证

论文实证证明"简单 harness 更易学习"，且 RL 让模型从 generic shell 转向专用工具。这直接验证了 Hermes 的 Skill 分层设计（SPyCE 论文 2607.13854 也有类似结论）：
- 执行技能（原子操作）应优于通用 shell 脚本
- Skill 的 discoverability 和 specificity 比"万能工具"更有效
- 可执行的改进：审查现有 Skill 中哪些过于通用（fallback 到 shell），拆分为专用 Skill

### ⚠️ P1：数据合成 Pipeline → Cron 自动测试场景生成

论文的五步法（propose→prune→build→test→refine）可适配为 Hermes 的自动化测试：
- 用 cron 定期生成 Skill 的测试场景（从真实用户日志或合成）
- 自动验证 Skill 在新模型版本下的回归
- 关键障碍：需要可执行的 Dockerfile 环境和 verifier 脚本，Hermes 的环境多样（飞书/Jetson/本地）
- 增量路径：先从单个高价值 Skill（如 lark-cli）开始试点

### 🔨 P1：Error Recovery 专用数据 → error-case-library 强化

论文明确指出 error recovery 是 RL 也难以提升的能力，需要 dedicated data。Hermes 已有 `error-case-library` skill 方向，但需要系统化：
- 每次失败不仅记录根因，还应记录"成功恢复"的完整路径
- 构建 recovery trajectory 数据集，用于 Agent 行为模式学习
- 可与 watchdog skill 联动，自动捕获恢复成功/失败的案例

### ⚠️ P2：多 Harness 训练泛化 → 多模型适配验证

论文证明多 harness 联合训练 > 单 harness。Hermes 使用多个模型（GLM/Qwen/等），可类比验证：
- 同一 Skill 在多个模型上的表现差异
- Skill 的描述是否需要 per-model 适配
- 关键障碍：需要标准化的 benchmark，目前 Hermes 无统一的 Skill eval suite

### ❌ P3：K8s 远程容器 → Jetson 边缘场景不适用

OpenForgeRL 的 K8s orchestrator 基于云厂商（Azure），需要弹性 GPU 资源。Jetson Orin 是单机边缘设备，无法复现这种远程 rollout 架构。但概念可借鉴：
- 将"重计算任务 offload 到远程"的思路用于 Jetson 的模型推理卸载
- 实际更适合用 Hermes 的 delegate_task 机制做本地异步编排

---

## 7. 关联论文

- **Polar (Xu et al., 2026)** — 并发工作，类似 proxy 方案但仅覆盖 SWE-Bench-Verified。OpenForgeRL 覆盖范围更广（6 benchmark + 文本/视觉）
- **Beyond the Leaderboard (2607.05775)** — Agent 六大失败模式分类法，error recovery 是最顽固的。本文实证呼应
- **SPyCE (2607.13854)** — 技能-策略协同进化，Skill 分层设计。本文的"简单 harness 更易学习"提供了训练侧的证据
- **veRL (Sheng et al., 2024)** — 本文使用的 RL 训练后端，支持 PPO/GRPO
- **DAPO (Yu et al., 2025a)** — 错误轨迹处理策略（丢弃全部样本）的来源
- **Orchard (Peng et al., 2026)** — K8s orchestrator 的基础框架

---

## 8. 一句话总结

OpenForgeRL 通过轻量 Proxy + K8s Orchestrator 解耦 harness 推理与 RL 训练，首次让开源社区能在真实部署的 harness（Claude Code/Codex/OpenClaw）中端到端训练 Agent，并用数百到数千任务在 6 个 benchmark 上超越同规模开源模型，同时揭示了"简单 harness 更易学习"和"RL 提升 self-verification 但 error recovery 仍需 dedicated data"两个关键发现。


## 相关笔记

- [AREX 递归自改进深度研究 Agent (07-25)](./2026-07-25-AREX递归自改进深度研究Agent.md) — 递归自改进范式，与 OpenForgeRL 的 RL 训练形成方法论对比
- [ACM 上下文管理五原语 (07-24)](./2026-07-24-ACM上下文管理五原语.md) — Agent 上下文管理，harness 训练的基础设施层
- [Agent 记忆两极：选择性持久化 vs 率失真压缩 (07-25)](./2026-07-25-Agent记忆两极-选择性持久化vs率失真压缩.md) — Agent 记忆机制，训练时的状态管理参考
