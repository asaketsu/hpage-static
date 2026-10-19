# LLM 后训练 RL 框架 2026 全景：slime / Miles / verl / vime 四大引擎与生态

#AI-Agent #LLM #RL后训练 #slime #verl #SGLang

> **出处**：THUDM/slime GitHub (https://github.com/THUDM/slime) | LMSYS Miles ROCm 博客 (https://www.lmsys.org/blog/2026-03-17-rocm-miles-rl-amd) | verl-project/verl GitHub (https://github.com/verl-project/verl) | Zylos Research RL Post-Training 综述 | Anyscale Open Source RL Libraries
> **学习日期**：2026-08-02
> **学习来源**：THUDM/slime GitHub、LMSYS Miles ROCm 博客 (2026-03-17)、verl-project/verl GitHub、Zylos Research RL Post-Training 综述、Anyscale Open Source RL Libraries
> **知识衔接**：接续《radixArk 的 Miles 与 SGLang：大规模 RL 后训练双引擎》(2026-07-31)

---

## 内容详细整理

（见下方正文）

---

## 一、核心结论

2026 年 LLM 后训练 RL 框架已形成**以推理引擎为分界线的两大阵营**：

| 阵营 | 推理引擎 | 代表框架 | 验证模型 |
|------|---------|---------|---------|
| **SGLang-Native** | SGLang | **slime** → Miles / Relax / Dressage / TritonForge | GLM-4.5~5.2 全系列 |
| **vLLM-Native** | vLLM | **verl** (HybridFlow) → vime | Qwen / Llama / DeepSeek |
| **引擎可换** | vLLM 或 SGLang | verl (默认), slime (通过 vime) | 多模型 |

**关键判断**：slime 已成为**经 SOTA 模型生产验证最充分的 RL 后训练框架**（GLM-4.5 到 GLM-5.2 全部使用）。verl 则在生态广度和学术社区活跃度上领先（HybridFlow 论文发表于 EuroSys 2025）。

---

## 二、slime：SGLang-Native 的 RL Scaling 基座

### 2.1 设计哲学

slime 的核心设计理念是**"一个高性能 RL 内核支撑一切"**：

```
Megatron (训练) ←→ Data Buffer ←→ SGLang (Rollout)
                                        ↓
                            自定义数据生成函数
                    (多轮/工具/沙箱/验证器/环境)
```

**三大设计原则**：

1. **Native 透传**：不抽象引擎能力，直接透传 Megatron 参数和 SGLang 参数（`--sglang-` 前缀）。上游引擎优化零摩擦接入
2. **单后端深度优化**：只选 SGLang 一个 rollout 后端，避免多引擎抽象导致的"最小公分母"问题
3. **数据生成自由**：数学、代码、搜索、工具、沙箱、验证器、多 Agent 系统——全部作为数据生成或奖励工作流插入，不需要 fork 训练内核

### 2.2 架构模块

| 模块 | 职责 |
|------|------|
| **Training (Megatron)** | 主训练进程，从 Data Buffer 读数据，训练后同步参数到 rollout |
| **Rollout (SGLang + router)** | 生成新数据（含奖励/验证器输出），存入 Data Buffer |
| **Data Buffer** | 桥接模块，管理 prompt 初始化、自定义数据和 rollout 方法 |

### 2.3 高级特性

- **PD 分离部署**：Multi-turn / Agentic 工作流的 prefill/decode 资源隔离
- **Router 策略**：会话亲和路由（Session Affinity）用于多轮 Agent
- **Delta Weight Sync**：训练/推理分离部署，支持跨 GPU 型号/厂商的权重增量同步
- **External Rollout Engines**：推理服务于训练作业之外独立管理

### 2.4 生产验证

| 模型 | slime 版本 |
|------|-----------|
| GLM-5.2 / GLM-5.1 / GLM-5 / GLM-4.7 / GLM-4.6 / GLM-4.5 | 全部使用 slime 进行 RL 后训练 |
| Qwen3.6 / 3.5 / 3Next / 3MoE / 3 / 2.5 | 社区支持 |
| DeepSeek V3 / V3.1 / R1 | 社区支持 |

---

## 三、Miles：企业级大规模 RL 后训练（基于 slime）

### 3.1 定位

Miles 由 RadixArk 开发，**基于 slime 构建**，保持与 slime 上游紧密对齐，同时增加企业级特性：

| 扩展方向 | 具体能力 |
|---------|---------|
| **更深的 SGLang 集成** | 路由记录回放（R3）、统一 FP8 |
| **运营工具** | RL-Insight 在线可观测性 |
| **部署支持** | ROCm 预构建容器（MI300/MI350） |
| **新模型/硬件** | INT4 QAT、多供应商支持 |
| **低精度训练** | FP8 pipeline、INT4 量化感知训练 |

### 3.2 Miles 的三大核心技术（前篇已记录，此处补充实测数据）

| 技术 | 解决问题 | ROCm 实测数据 |
|------|---------|--------------|
| **Unified FP8** | 训练和推理统一 FP8，消除精度不一致导致 RL 崩溃 | ROCm roadmap 中 |
| **R3 (Rollout Routing Replay)** | SGLang 记录 MoE 专家路由 → Megatron 回放 | ROCm roadmap 中 |
| **INT4 QAT** | 1TB 模型装入单机 H200 | ROCm roadmap 中 |

### 3.3 ROCm 实测性能（MI300X × 8 GPU）

**训练配置**：Qwen3-30B-A3B，GRPO（32×8 采样，8k 响应上限，global batch 256），TP4/EP8

| 步骤组件 | 耗时 | 占比 |
|---------|------|------|
| **Rollout 生成** | 152.79s | 39.4% |
| Actor 训练 | 95.30s | 24.5% |
| 权重更新 | 33.85s | 8.7% |
| Log-prob 计算 | 31.53s | 8.1% |
| **总步时间** | **388.50s** | 100% |

**关键发现**：
- **Rollout 生成占 GPU 时间 70-90%**（证实 RL 工作负载中推理是瓶颈）
- Rollout 吞吐：~1.1k-1.3k tok/GPU/s
- 训练吞吐：~15-16k tok/s
- AIME 准确率：step 19 的 0.665 → step 139 的 **0.729**

### 3.4 AMD GPU 为何适合 RL

| 特性 | 对 RL 的意义 |
|------|-------------|
| 大 HBM 容量 | 长序列 rollout 需要大显存 |
| 高内存带宽 | Rollout 生成的解码阶段是带宽密集型 |
| 高效长上下文推理 | RL 训练生成数千并行环境的长序列 |
| 强多节点扩展 | 分布式 rollout 跨节点扩展 |

---

## 四、verl (HybridFlow)：引擎无关的学术标杆

### 4.1 HybridFlow 核心创新

verl 是 HybridFlow（EuroSys 2025）的开源实现，核心创新是 **"Hybrid Engine" 共享 GPU 内存**：

```
传统 RL 架构：
  训练进程 (GPU) ←→ 权重传输 ←→ 推理进程 (GPU)
  问题：权重传输开销巨大

verl Hybrid Engine：
  Actor 模型 ─┬─ 训练阶段：FSDP/Megatron
              └─ Rollout 阶段：vLLM/SGLang
  共享同一 GPU 内存，无需跨进程权重传输
```

### 4.2 2026 年关键进展

| 时间 | 进展 |
|------|------|
| 2025/12 | GRPO + LoRA 训练 **1 万亿参数模型**跨 64 H800 GPU |
| 2026/05 | **uni-agent**：统一 Agent 框架，大规模构建/运行/训练 LLM Agent |
| 2026/05 | **VeRL-Omni**：扩散模型和全模态模型的后训练统一栈 |
| 2026/05 | **vexact**：零不匹配 HuggingFace rollout（批量不变内核，与 FSDP 共享模型定义） |
| 2026/06 | **verl-SpeCo**：推测解码协同训练框架，训练期间保持 draft 模型对齐 |
| 2026/07 | **RL-Insight**：RL 训练在线可观测性 |

### 4.3 算法支持

| 算法 | 来源 |
|------|------|
| GRPO / PPO / DPO | 核心支持 |
| SPEAR | 自模仿渐进探索（ICLR 2026） |
| RuleReasoner | 规则推理强化（ICLR 2026） |
| MetaphorStar | 图像隐喻理解视觉 RL |

---

## 五、四大引擎对比矩阵

| 维度 | slime | Miles | verl | vime |
|------|-------|-------|------|------|
| **推理后端** | SGLang（唯一） | SGLang | vLLM 或 SGLang | vLLM（唯一） |
| **训练后端** | Megatron | Megatron / FSDP | Megatron / FSDP | Megatron |
| **GPU 内存** | 独立部署 | 独立部署 | **Hybrid Engine 共享** | 独立部署 |
| **权重同步** | Delta Weight Sync | Delta Weight Sync | Hybrid（零开销） | 独立 |
| **企业特性** | 基础 | LoRA/TITO/FP8/INT4 | uni-agent/Omni/vexact | 基础 |
| **AMD ROCm** | ✅ | ✅ | ❌ | ❌ |
| **生产验证** | GLM 全系列 | 企业部署 | 万亿参数 | 社区 |
| **开发团队** | THUDM (清华) | RadixArk | ByteDance / Volcano | vLLM 项目 |
| **论文** | LMSYS Blog | — | EuroSys 2025 | — |

---

## 六、slime 生态全景（11 个独立系统）

这些不是 demo，而是使用 slime 作为可复用 RL 基座的生产级系统：

| 系统 | 定位 | 核心创新 |
|------|------|---------|
| **Dressage** | 可扩展 Agent RL | 黑盒 Agent + 白盒循环统一训练（Alibaba Accio） |
| **Miles** | 企业级大规模 RL | R3/Unified FP8/INT4 QAT（RadixArk） |
| **vime** | vLLM-Native RL | slime + vLLM 替换 SGLang |
| **Relax** | 全模态 Agentic RL | Ray Serve + TransferQueue + DCS 异步权重同步 |
| **OpenClaw-RL** | 个性化 Agent RL | "对话即可训练"，GRPO 二元反馈 + 在线策略蒸馏 |
| **P1** | 物理竞赛 RL | 多阶段 RL + 自适应可学性调整 |
| **RLVE** | 可验证环境 RL | 400 个程序化生成验证环境 |
| **TritonForge** | GPU 内核生成 RL | SFT + RL 两阶段训练 Triton 内核生成 |
| **APRIL** | 加速 RL 训练 | 主动部分 Rollout，解决长尾生成瓶颈 |
| **qqr** | 开放 Agent 进化 | ArenaRL 锦标赛排名 + MCP 集成 |
| **ART** | AWS Bedrock RL | AgentCore Runtime + 装饰器适配 |

---

## 七、核心技术洞察

### 7.1 RL 工作负载的本质矛盾

```
RL 训练 ≠ 预训练

预训练：计算密集，GPU 利用率高
RL 训练：Rollout 生成占 70-90% GPU 时间
         → 推理效率是 RL 系统的决定性瓶颈
         → 内存容量和带宽比 FLOPS 更重要
```

这解释了为什么 AMD MI300X（192GB HBM3, 5.3TB/s 带宽）在 RL 场景有竞争力——尽管 FLOPS 低于 H100，但大显存和高带宽恰好匹配 rollout 需求。

### 7.2 权重同步的三种范式

| 范式 | 代表 | 优势 | 劣势 |
|------|------|------|------|
| **Hybrid Engine（共享内存）** | verl | 零传输开销 | 部署不灵活 |
| **Delta Weight Sync** | slime / Miles | 跨设备/跨厂商灵活 | 有传输开销 |
| **External Rollout** | slime / Miles | 完全解耦 | 最大灵活性，最高开销 |

### 7.3 Agentic RL 的崛起

2026 年最显著趋势：RL 从"单轮数学推理"扩展到"多轮工具使用 Agent 训练"：

- **Multi-turn rollout** 成为默认接口（Miles multi-turn 实测平均轮数随训练递增）
- **Sandbox 集成** 标准化（bwrap / E2B / Kubernetes）
- **Token 级轨迹捕获** + TITO 训练（Dressage 创新）
- **长尾生成问题**：APRIL 通过过度供给请求 + 主动管理部分完成来解决

---

## 八、对实际工程的启示

### 8.1 选择框架的决策树

```
是否需要训练 GLM 系列？
  → slime（原生支持，最充分验证）

是否需要 vLLM 生态？
  → verl（Hybrid Engine 最优内存效率）或 vime

是否需要 AMD GPU？
  → Miles（唯一 ROCm 完整支持）

是否需要 Agentic RL（多轮工具）？
  → slime（Dressage/OpenClaw-RL 生态）或 verl（uni-agent）

是否需要超大规模（1T+）？
  → verl（万亿参数验证记录）
```

### 8.2 与前篇笔记的串联

本篇是《radixArk 的 Miles 与 SGLang》的**生态全景展开**。前篇聚焦 Miles + SGLang 的 RL 闭环，本篇揭示了 Miles 只是 slime 生态的一个节点：

- slime 是**所有这些框架的共同祖先**
- Miles 是 slime 的企业级扩展
- vime 是 slime 的 vLLM 版本
- Relax 是 slime 的全模态版本
- Dressage 是 slime 的 Agent 专用版本

**对飞机结构设计专家模型 GRPO 后训练的启示**（研究策划中提到）：如果后续需要做专家模型的 RL 后训练，**slime 是首选**——因为 GLM 系列（即本系统正在使用的模型）的 RL 后训练全部基于 slime，兼容性最佳。

---

## 九、与既有知识体系关联

| 关联笔记 | 关系 |
|---------|------|
| 《radixArk 的 Miles 与 SGLang：大规模 RL 后训练双引擎》 | 本篇是其生态全景展开 |
| 《LLM 推理加速 2026：MTP 与推测解码实战全景》 | verl-SpeCo 是推测解码在 RL 训练中的应用 |
| 《AI Agent 协议生态 2026：MCP-A2A 四层架构》 | OpenClaw-RL/qqr 将 MCP 集成到 RL 训练中 |
| 《飞机结构设计 AI：知识图谱与专家模型研究策划》 | GRPO 后训练的候选框架评估 |

---

## 十、术语表

| 术语 | 含义 |
|------|------|
| **Rollout** | RL 中策略生成训练数据的过程（推理阶段） |
| **Hybrid Engine** | verl 的训练/推理共享 GPU 内存架构 |
| **R3 (Rollout Routing Replay)** | Miles 的 MoE 路由回放技术 |
| **TITO** | Token-level training with token-level importance sampling |
| **PD 分离** | Prefill/Decode 解耦部署 |
| **Delta Weight Sync** | 增量权重同步（只传变化部分） |
| **DCS** | 分布式检查点服务（Relax 的 NCCL 广播权重同步） |
| **vexact** | verl 的零不匹配 HuggingFace rollout |

---

## 查询拓展

基于本次学习产生的后续可深入方向：

1. **slime 的 R3 (Rollout Routing Replay) 技术细节**：SGLang 如何记录 MoE 专家路由？Megatron 如何回放？这对 Qwen3-30B-A3B 等 MoE 模型训练稳定性有何影响？→ 深读 slime docs/en/advanced/ 和 Miles 论文
2. **Agentic RL 的 token 捕获机制**：Dressage 的 Paddock/Sandbox/Proxy 三层如何实现 token 级 logprob 捕获？TITO 训练如何保证长 horizon 工具交互的稳定性？→ 研究 Dressage GitHub
3. **verl Hybrid Engine 的内存共享实现**：训练和推理共享 GPU 内存的具体 CUDA 内存管理机制？权重切换时是否有显存碎片化问题？→ 深读 HybridFlow (EuroSys 2025) 论文
4. **AMD MI300X vs NVIDIA H100 在 RL 场景的 TCO 对比**：Rollout 占 70-90% 时间，大 HBM 容量优势如何转化为成本优势？→ 扩展实测数据
5. **OpenClaw-RL "对话即可训练"的在线策略蒸馏**：hindsight hint 如何从后续反馈中提取？与 DPO 的区别？→ 阅读 OpenClaw-RL 文档
6. **APRIL 的主动部分 Rollout**：过度供给请求如何管理？部分完成如何与完整 rollout 对齐？→ 研究 RLsys-Foundation/APRIL

---

## 归纳总结

**一句话总结**：slime 已成为 SOTA 模型生产验证最充分的 RL 后训练框架（GLM 全系列），其生态（Miles/verl/vime/Relax/Dressage 等 11 个系统）覆盖了从企业级训练到个性化 Agent 的完整 RL 场景，核心瓶颈是 rollout 推理效率（占 70-90% GPU 时间）。

**五大核心发现**：

| # | 发现 | 实践价值 |
|---|------|---------|
| 1 | slime 是 GLM-4.5~5.2 全系列的 RL 框架 | 本系统使用 GLM-5.2，slime 是后训练首选 |
| 2 | Rollout 生成占 RL 训练 70-90% GPU 时间 | 推理引擎效率决定 RL 系统性能，内存>算力 |
| 3 | 11 个独立系统构建在 slime 之上 | 证明 slime 的可复用性和生态生命力 |
| 4 | Hybrid Engine（verl）vs Delta Weight Sync（slime）| 前者零开销但不灵活，后者灵活但有传输成本 |
| 5 | Agentic RL（多轮工具训练）成为 2026 默认范式 | 从单轮数学推理扩展到多步工具 Agent |

**实践建议**：如需对飞机结构设计专家模型做 GRPO 后训练，首选 slime（GLM 系列原生支持，SGLang rollout 与本系统推理引擎一致）。

---

## 趋势判断

| 趋势 | 判断 | 置信度 | 依据 |
|------|------|--------|------|
| **RL 后训练框架收敛** | slime + verl 双寡头格局形成，新框架将基于二者而非从零构建 | ⭐⭐⭐⭐ | 11 个生态系统全部基于 slime，verl 有万亿参数验证 |
| **SGLang 成为主流推理后端** | 在 RL 场景将超越 vLLM（vime 是 vLLM 的追赶） | ⭐⭐⭐ | slime/Miles/Relax/TritonForge 全选 SGLang |
| **Agentic RL 成为核心场景** | 多轮工具使用训练将超过单轮推理训练 | ⭐⭐⭐⭐ | Miles multi-turn 实测、Dressage/OpenClaw-RL 趋势 |
| **AMD GPU 在 RL 场景崛起** | MI300X 的大 HBM 在 rollout 密集型工作负载中有结构优势 | ⭐⭐⭐ | Miles ROCm 支持 + MI300X 实测数据 |
| **RL 工程正确性成为竞争壁垒** | "脚本能跑"→"数值精确、可复现、可追溯"，slime 的 CI/调试/追踪投入将成为优势 | ⭐⭐⭐⭐ | slime 的 correctness-first 文档化设计 |

---

## 关联分析

| 关联笔记 | 关系 | 更新内容 |
|---------|------|---------|
| 《radixArk 的 Miles 与 SGLang：大规模 RL 后训练双引擎》 | 本篇是其生态全景展开 | 增加了 slime 基座 + 11 个生态系统的完整地图 |
| 《LLM 推理加速 2026：MTP 与推测解码实战全景》 | verl-SpeCo 是推测解码在 RL 训练中的应用 | 可补充推测解码的 RL 训练加速维度 |
| 《AI Agent 协议生态 2026：MCP-A2A 四层架构》 | OpenClaw-RL/qqr 将 MCP 集成到 RL 训练 | RL 训练框架是 MCP 的消费端之一 |
| 《飞机结构设计 AI：知识图谱与专家模型研究策划》 | GRPO 后训练的候选框架评估 | slime 是首选（GLM 系列原生支持） |

**对 Skill/Memory 的改进建议**：
1. 可创建 `llm-rl-post-training` Skill，记录 slime/Miles/verl 的选型决策树和部署流程
2. `quant-ml-pipeline` 或 `agentic-alpha-research` Skill 可参考 Agentic RL 的多轮训练范式
3. 前篇 Miles 笔记的"五大 RL 框架"表可更新为包含完整 slime 生态系统


## 相关笔记

- [radixArk Miles 与 SGLang 大规模 RL 后训练](./2026-07-31-radixArk-Miles与SGLang大规模RL后训练.md) — 本文前篇，Miles 双引擎深入解析
- [推理时计算扩展 Best-of-N 到 Compute-Optimal](./2026-07-28-推理时计算扩展-从Best-of-N到Compute-Optimal自适应分配.md) — 训练后推理扩展的配合
- [LLM 推理模型 RL 训练前沿 GRPO 到 DAPO](./2026-07-18-LLM推理模型RL训练前沿-从GRPO到DAPO与异步系统.md) — 训练侧 RL 算法演进
- [极简参数 PEFT 与 GRPO 推理训练](./2026-06-02-极简参数PEFT与GRPO推理训练-从TinyLoRA到VeFA实证前沿.md) — 低成本 RL 训练路径
