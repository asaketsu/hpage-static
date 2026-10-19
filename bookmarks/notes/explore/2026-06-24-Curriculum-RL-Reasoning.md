# Curriculum RL Can Incentivize Reasoning Capacity Beyond the Base Model — 精读笔记

## 元数据

- **标题**: Curriculum Reinforcement Learning Can Incentivize Reasoning Capacity in LLMs Beyond the Base Model
- **arXiv ID**: 2606.22317
- **作者**: Pengxiang Cai 等
- **日期**: 2026年6月
- **领域**: RLVR / 推理能力扩展 / 课程学习

---

## 核心问题与研究动机

### 核心问题
标准RLVR（Reinforcement Learning with Verifiable Rewards）能否真正扩展模型的推理能力边界？还是仅仅在重新分配基础模型已有的轨迹采样概率？

### 研究动机
- Limit-of-RLVR研究[40]发现：标准RLVR通常提升pass@1，但在大k（pass@256）下推理能力边界不扩展，甚至收缩
- 根本原因：当某个问题的所有rollout都失败时，group-normalized advantage全部为0，该样本成为"零优势组"，无法提供任何奖励驱动的学习信号
- 这形成了一个"优化死区"：最需要学习的样本恰恰是最无法提供学习信号的样本

---

## 方法论（Boundary-Aware Curriculum RL）

### 核心思想
将"推理能力边界附近"的样本转化为可训练的RL数据，每轮课程包含三步：

1. **大样本pass@k探索**：用大k值（如pass@256）采样估计当前推理能力边界
2. **针对性教师引导**：对边界附近或略超边界的样本添加少量结构化教师轨迹
3. **课程RL训练**：基于pass@k探索结果选择合适难度的课程，巩固新学到的推理模式

### 关键洞察：零优势组（Zero-Advantage Groups）

对于GRPO风格的更新，假设采样G个rollout {y_i}，二元奖励r_i∈{0,1}：

- 组归一化优势：Â_i = (r_i - r̄) / (σ_r + ε)
- 如果所有rollout都失败：r̄=0, σ_r=0 → Â_i=0 → 梯度贡献为0
- 这些"零优势组"样本定义了当前推理能力边界

### 课程迭代机制
- 每轮重新用pass@k探索更新模型
- 定位新的推理能力边界
- 将更多"Beyond"样本转化为"Reward-reachable"样本

---

## 关键实验结果

### 实验设置

- **模型**：Qwen2.5-7B、Qwen2.5-7B-Instruct、Qwen3-8B、DeepSeek-R1-0528-Qwen3-8B、Llama-3.1-8B-Instruct
- **训练数据**：DAPO-Math-17K子集
- **评估基准**：AIME 2024、AIME 2025、MATH500
- **评估指标**：pass@k（k∈{1,2,4,8,16,32,64,128,256}），pass@256作为推理能力边界代理

### 核心发现

#### 1. pass@k曲线分析
- Vanilla RLVR：增益主要集中在pass@1附近，pass@256增益有限甚至下降
- Curriculum RL：同时提升低k和高k部分，pass@256平均提升+9.8个百分点

#### 2. 对比Vanilla RLVR
- Vanilla RLVR平均pass@256变化：-0.5个百分点（略微下降）
- Curriculum RL平均pass@256变化：+9.8个百分点
- Vanilla RLVR在不同benchmark上表现不稳定，有时提升有时下降

#### 3. 问题级边界迁移（Table 2）
- 538个基础模型256样本未解问题中，226个在课程训练后变得可解
- 各模型迁移数：
  - Qwen2.5-7B-Instruct: 53/86
  - Qwen2.5-7B: 15/50
  - Qwen3-8B: 29/71
  - LLaMA-3.1-8B-Instruct: 90/170
  - DeepSeek-R1-0528-Qwen3-8B: 39/161

#### 4. 训练样本组成变化（Figure 4）
- 课程迭代过程中，"Beyond"样本减少，"Reward-reachable"样本增加

---

## 创新点分析

1. **零优势组理论**：从group-level角度解释了RLVR能力边界受限的机制
2. **边界感知课程**：首次将pass@k探索与课程学习结合，主动定位能力边界
3. **小样本教师引导**：仅需少量结构化轨迹即可将零优势组转化为可训练样本
4. **迭代边界扩展**：通过多轮课程逐步将"不可解"问题转化为"可解"问题

---

## 局限性与未来方向

### 局限性
- 未探索最优课程选择策略
- 依赖pass@k探索的采样效率（需要大量rollout）
- 教师引导的质量依赖教师模型能力
- 目前仅在数学推理领域验证

### 未来方向
- 更高效的边界估计器（减少pass@k采样成本）
- 替代教师引导源（如合成推理轨迹、搜索增强）
- 扩展到其他推理领域（代码、逻辑推理）
- 与推理时间扩展（inference-time scaling）结合

---

## 借鉴点评估

### 对Hermes Agent的借鉴

| 借鉴点 | 当前状态 | 优先级 |
|--------|----------|--------|
| 边界感知工具选择：在Agent工具调用中识别"零优势"场景（所有工具调用都失败的问题），主动切换策略 | 未实现 | P1 |
| 课程式任务分解：将复杂任务按难度分级，从易到难逐步学习 | 部分实现（subtask-lifecycle） | P2 |
| pass@k式探索：对关键决策点进行多路径采样探索 | 未实现 | P2 |

### 对Jetson Orin边缘部署的借鉴

| 借鉴点 | 当前状态 | 优先级 |
|--------|----------|--------|
| 推理能力边界评估：在边缘设备上用pass@k评估模型实际能力边界 | 未实现 | P2 |
| 小样本引导微调：用少量高质量示例引导边缘模型适应新任务 | 部分实现 | P3 |

### 对量化交易的借鉴

| 借鉴点 | 当前状态 | 优先级 |
|--------|----------|--------|
| 零优势组识别：识别所有策略都失效的市场状态，避免在"优化死区"中训练 | 未实现 | P1 |
| 课程式策略学习：按市场难度分级训练策略，从简单市场状态开始 | 未实现 | P2 |

---

## 关联论文

- Limit-of-RLVR [40]：发现RLVR能力边界受限现象
- GRPO、DAPO、GSPO：RLVR基础算法
- DeepSeek-R1 [7]：推理模型RL训练
- Reverse curriculum RL [35]：反向课程RL
- Easy-to-hard curriculum RL [24,45]：由易到难课程RL

## 相关笔记

- [LoRA-GRPO最优配置实证](../2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md) (关键词: RL, GRPO)
- [后训练RL前沿-DrGRPO-异步RL-GenPRM](2026-06-06-后训练RL前沿-DrGRPO-异步RL-GenPRM.md) (关键词: RL, 后训练)
- [Neurosymbolic Reasoning](2026-05-28-symcode-neurosymbolic-reasoning-exploration.md) (关键词: reasoning)
