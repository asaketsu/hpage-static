# 主流LLM微调方法全景 — 全参/LoRA/QLoRA/DoRA/AdaLoRA/VeRA/PiSSA/Prompt/Adapter与SFT-DPO-GRPO栈

#LLM微调 #PEFT #LoRA #QLoRA #DoRA #AdaLoRA #VeRA #PiSSA #SFT #DPO #GRPO #RLHF #全参微调 #Adapter #PromptTuning #Axolotl #Unsloth

> **出处**：本研究型笔记，综合 PEFT skill 文档（LoRA/QLoRA/DoRA/AdaLoRA/VeRA/PiSSA 等，含 HF PEFT 官方口径、NVIDIA DoRA 解读、arXiv DoRA 2402.09353、ICLR 2026 MiSS 论文 e365c5fd…、Post-Training Playbook 2026、腾讯云《LoRA到QLoRA演进》、SegmentFault《LoRA/QLoRA/全量微调怎么选》、RedHat《LoRA vs QLoRA》）整理。
> 来源 URL：
> - https://arxiv.org/html/2402.09353v5 （DoRA 论文）
> - https://developer.nvidia.com/blog/introducing-dora-a-high-performing-alternative-to-lora-for-fine-tuning （NVIDIA DoRA 解读）
> - https://gopikrishtummala.github.io/posts/mlops/modern-post-training-peft-2026 （Post-Training Playbook 2026）
> - https://cloud.tencent.com/developer/article/2611321 （LoRA到QLoRA演进）
> - https://segmentfault.com/a/1190000047641645 （微调完全指南）
> - https://www.redhat.com/zh-cn/topics/ai/lora-vs-qlora （LoRA vs QLoRA）
> 主题：把 2025-2026 仍在主流使用的 LLM 微调方法按“更新什么、省不省显存、是否增加推理开销、生产怎么选”统一整理，并给出流程与落地指南

## 一、内容整理

### 0. 一句话结论

LLM 微调已经进入"**SFT 做能力定制 + PEFT 做低成本部署 + DPO/GRPO 做偏好对齐**"三段式；方法选择本质是在**质量上限、显存成本、迭代速度、推理零开销**之间取舍。**没有一种方法普适，生产默认先 LoRA/QLoRA，需要更高质量或大方向更新时上 DoRA/全参，对齐阶段用 DPO/GRPO**。

### 1. 方法分类

**A. 全参微调（Full Fine-Tuning, Full FT）**

- 更新范围：全部权重 100%
- 原理：冻结无，端到端梯度更新
- 优点：质量上限最高；能学大方向变化；最接近从头训练
- 缺点：显存/存储/训练时长高；7B FP16 通常 ≥80GB 显存，70B 需多卡（4-8×A100/H100）；产物大
- 适用：有充足算力、追求最高质量、领域漂移很大、小模型（<1B）本身便宜
- 注意：小模型（<1B）全参往往性价比高于 PEFT

**B. LoRA（Low-Rank Adaptation）**

- 更新范围：在冻结基座权重 W 旁学习低秩增量 ΔW = B·A，只训练 A/B；约 0.1-3%
- 典型：r=8-16，α≈2r；target_modules 取 q_proj/k_proj/v_proj/o_proj，复杂任务扩展到 gate/up/down_proj 或 all-linear
- 优点：推理时可将 A/B 合并回 W，**无额外推理延迟**；适配器小（6-50MB），可多适配器切换；收敛快
- 缺点：参数效率≠计算加速；仍要跑 B(Ax) 或合并后等价路径；极端任务可能不如 DoRA/全参
- 适用：绝大多数企业级 7B-70B 微调默认起点
- 记忆点：Llama 8B 上 r=16 约 14M 可训练参数 / 总 8B，约 0.17%

**C. QLoRA（Quantized LoRA）**

- 更新范围：4-bit 量化基座 + LoRA 增量（通常 NF4 + bf16 计算）
- 原理：用量化降低基座占用，LoRA 仍用高位梯度；配合 paged optimizer/gradient checkpointing
- 优点：70B 可压到单卡/少量 GPU（如 80GB H100）；消费级 GPU 能玩；存储极低
- 缺点：相比 LoRA 可能有约 5% 质量折损；4-bit 量化会损失小参数；某些算子兼容性需验证
- 适用：算力受限、迭代实验快、70B 级资源受限微调
- 推荐：资源受限时，从 QLoRA 而不是 LoRA 起步

**D. DoRA（Weight-Decomposed LoRA）**

- 更新范围：LoRA 的低秩参数 + 额外向量幅度控制；更新量与 LoRA 接近（约 0.1-3%）
- 公式核心：`W ≈ m · (V + ΔV) / ||V + ΔV||_c`，把**方向更新**和**幅度学习**拆开；m 是学习幅度，V 是冻结方向，ΔV 是 LoRA 更新方向
- 优点：在相近参数量下比 LoRA 更接近全参微调效果；NVIDIA 解读称能关闭 LoRA 与 FT 之间约 90% 的差距；适合领域适配、术语/写作风格/知识迁移
- 缺点：参数略增；幅度项需合并/部署注意；并非所有框架都默认支持
- 适用：需要比 LoRA 更高质量但显存不能上全参时

**E. AdaLoRA（Adaptive LoRA）**

- 更新范围：动态给不同层/参数分配 rank 预算；总训练参数可低于固定 rank LoRA
- 原理：用二阶信息/奇异值度量不同参数的重要性，rank 向高影响层集中，低影响层截断
- 优点：异构任务/层重要性差异大时更省；自动 rank 分配减少手工调参
- 缺点：动态预算增加实现复杂度；稳定性依赖调度器
- 适用：多任务、复杂领域、希望在固定预算下最大化质量

**F. VeRA / DVoRA（Vectorized/Extreme PEFT）**

- 更新范围：极低参数（约 0.02-0.04%）
- 原理：把 LoRA 矩阵近似为向量或极小结构，参数更少
- 优点：参数极小，适合资源极端受限、快速原型
- 缺点：质量上限低于 LoRA/DoRA；DoRA 论文实验中 VeRA 低于 DoRA/DVoRA
- 适用：实验、资源极小、可接受质量折损

**G. PiSSA / MoRA / 新型 SVD 初始化类**

- 更新范围：LoRA 结构或近似，初始化方式不同
- PiSSA：用主奇异向量（SVD）初始化 LoRA，训练更快；DoRA 论文表列其前向 `y=W0x+BAx`，A/B 由 U/S/V 初始化
- MoRA：低秩结构变体；ICLR 2026 MiSS 论文将其与 PiSSA/DoRA/VeRA 等并列为 LoRA 变体
- 优点：初始化更贴合权重空间，收敛可能更快
- 缺点：部署/框架支持不如 LoRA 普及；工程成熟度仍需验证
- 适用：研究、希望比 LoRA 更快收敛且不换框架生态

**H. Adapter Tuning / IA³**

- 更新范围：在层之间插入小型神经网络适配器，或只训练重标量；约 0.01-4%
- 优点：IA³ 参数极少；adapter 可多任务加载；部分场景部署简单
- 缺点：若不合并，**推理会增加少量开销/延迟**；表现中等
- 适用：多任务并行、推理延迟不敏感、参数极小需求

**I. Prompt Tuning / Prefix Tuning / P-Tuning v2**

- 更新范围：prompt token、virtual tokens、或前缀 embedding；通常 <0.1%
- 优点：参数极小、任务切换方便；无需改模型结构
- 缺点：对生成任务/复杂任务效果相对弱；长上下文任务可能不稳定
- 适用：简单任务、NLU、资源极小、需要快速任务切换

### 2. 训练范式：SFT / RLHF / DPO / GRPO

| 范式 | 数据 | 目标 | 典型流程 | 适用 |
|---|---|---|---|---|
| SFT | (prompt, answer) 单标注 | 学格式/能力/领域知识 | 基座→DPO 前能力定制 | 默认第一站，产品输出定制 |
| RLHF | 偏好 + reward model | 按人类偏好对齐 | SFT→奖励模型→PPO | 高质量偏好对齐，工程重 |
| DPO | (prompt, chosen, rejected) | 直接优化偏好，省奖励模型 | SFT→偏好数据→DPO | 有偏好对时默认替代 RLHF |
| GRPO | 同一 prompt 多个候选 + 可验证答案 | 强化优化，避免完整 PPO | SFT→候选→组内归一奖励 | 数学/代码/可验证答案任务 |
| 全参 vs PEFT | 可与上面任意范式组合 | 决定“更新权重范围” | SFT/LoRA/QLoRA/DoRA 只是更新范围选择 | 不要和训练目标混淆 |

2026 常见栈：**SFT（10k-100k）→ LoRA/DoRA 微调 → DPO 或 GRPO 对齐 → 模型合并/部署**。

### 3. 生产实测经验

- **LoRA rank 选择**：Mastercard 生产研究（arXiv 2606.08051，24 变体 × 270M-8B）显示，LLaMA 3.1-8B 上 rank8(96.75 F1) 与 rank32 生产基线(96.95) 仅差 0.20；**默认 rank8 已足够，rank32 未必更值**。
- **训练峰值窗口**：epoch 3.7-5.2 常为质量峰值，之后可能过拟合；必须在全部 checkpoint 上做 heldout 评估再选最佳。
- **推荐配方**：r=8, α=16(α/r=2.0), LR 1e-4 cosine, 有效 batch 16, 6 epoch, 每 200 步存 checkpoint。
- **部署前后双测**：基准到 serving 迁移平均 -0.8 F1；模型合并、量化、KV cache、vLLM 等部署环节可能改变结果。
- **LoRA 内存瓶颈**：边缘端 LoRA 的瓶颈常是**激活值**而非权重；3B/2048 ctx 实测通过量化、选择性 checkpoint、softmax 近似、logits 掩码，可从 26.20GB 降到 1.02GB。

## 二、查询拓展

1. DoRA 与 QLoRA 叠加（QDoRA）在 70B/80B GPU 上的质量与显存曲线
2. Unsloth 与 QLoRA 在 H100/A100 上的显存/速度对比，是否只是工程优化而非方法创新
3. SFT→DPO→GRPO 三段训练中的数据泄漏风险与验证集污染规避
4. LoRA rank 选择与任务复杂度关系：指令跟随 vs 数学推理 vs 代码生成的最佳 rank
5. vLLM 多 LoRA 并发服务：adapter 数量、上下文长度、batch size 对吞吐的影响
6. 模型合并（LoRA merge / SLOR / model merging）后质量退化原因与恢复方法

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | 微调=更新什么（Full/LoRA/QLoRA/DoRA等）×训练什么目标（SFT/DPO/GRPO）；两者组合选择 |
| 默认起点 | 企业级 7B-70B：LoRA；显存紧：QLoRA；要更接近全参：DoRA；可验证任务：SFT+GRPO |
| 核心取舍 | Full FT 质量最高但贵；LoRA 平衡最好；QLoRA 降显存；DoRA 提质量；DPO/GRPO 做偏好/正确性 |
| 误区 | “参数少=更快”不完全成立；LoRA 类方法参数少但仍需基座前向和梯度存储 |
| 生产化 | 不能只看训练损失；必须 benchmark、heldout、部署前后双测，checkpoint 遍历选峰值 |

## 四、趋势判断

1. **PEFT 已取代“全参微调”成为默认工程路径**：7B 以上模型除非有充分算力和质量刚需，否则 LoRA/QLoRA/DoRA 是主流
2. **DoRA 正在从研究走向生产**：它解决 LoRA 与 Full FT 之间的质量差距，是 LoRA 的自然增强层
3. **DPO/GRPO 替代传统 RLHF 成为偏好对齐主流**：省 reward model/PPO 的复杂度；GRPO 对数学/代码更可验证
4. **微调工程化超过方法创新**：Axolotl/LLaMA-Factory/Unsloth/PEFT/vLLM 等工具链决定落地速度，方法只是参数选项
5. **边缘微调成为下一战场**：LoRA 激活内存优化让 3B 级别模型在 Jetson/手机接近可微调，对应 TinyML 趋势

## 五、关联分析

| 关联对象 | 关系 |
|---|---|
| skill `peft-fine-tuning` | 本笔记的方法来源与代码模板主库；LoRA/QLoRA/IA3/Prefix 等均覆盖 |
| skill `fine-tuning-with-trl` | DPO/GRPO/PPO 对齐训练的实操 skill |
| skill `axolotl` | YAML 化微调编排，LoRA/QLoRA/DoRA 多方法工程化 |
| skill `unslhot` 类工程优化（如存在） | 显存/速度工程优化与本笔记的“参数少≠计算快”互补 |
| skill `jetson-orin-platform` / `gpu-farm-engineering` | 本仓 GPU 微调算力评估与边缘部署路线 |
| 笔记《2026-08-18-TinyMCU跑AI全流程》 | TinyML 是 PEFT 在 MCU 层的同构：同样追求“只更新小量参数/低资源部署” |
| 项目 `pocket-tts-cpu` / `tinyml-vibration-mcu` | 本地小模型部署与边缘微调共同构成“低成本 AI 落地栈” |

→ 相关：~/.hermes/skills/mlops/training/peft/SKILL.md
→ 相关：~/.hermes/skills/mlops/training/fine-tuning-with-trl/SKILL.md

## 六、拓展应用推荐

**① 本仓可落地任务**
- **Jetson 本地微调 3B/8B 模型**：用 QLoRA + 梯度压缩 + 选择性 checkpoint，适配私有知识库问答或工具调用风格
- **多任务 adapter 服务**：一个基座模型挂载不同 LoRA（客服/代码/股票分析/笔记润色），部署时 vLLM `LoRARequest` 切换
- **私有数据 SFT→DPO 管线**：先从高质量问答对 SFT，再用人工/规则偏好对 DPO，最后部署前 benchmark

**② 场景-方法推荐表**

| 场景 | 推荐方法 | 理由 |
|---|---|---|
| 企业私有问答/知识库 | QLoRA + SFT | 显存可控、数据量通常不大、质量够用 |
| 代码/数学强化 | SFT + GRPO | 有可验证答案，组内强化效果好 |
| 风格/角色/写作定制 | LoRA/DoRA + SFT | 方向变化明显，DoRA 更接近全参 |
| 多租户/多任务 | LoRA 多 adapter | 模型基座共享，adapter 切换 |
| 资源极端受限 | QLoRA/Prompt/IA³ | 参数与显存最低 |

**③ 推荐工具链**
- 方法层：Hugging Face PEFT
- 对齐层：TRL（SFTTrainer / DPOTrainer / GRPO）
- 编排层：Axolotl / LLaMA-Factory
- 推理层：vLLM（支持 LoRA 服务）
- 实验追踪：WandB / TensorBoard

## 七、指南分析

**选型决策树**

1. 模型是否 <1B？
   - 是：优先考虑 Full FT，便宜且质量上限好
   - 否：进入 2
2. 显存是否 <24GB 或只有消费级 GPU？
   - 是：QLoRA（4-bit + LoRA）
   - 否：进入 3
3. 是否接受 LoRA 质量？
   - 是：LoRA（r=8-16）
   - 否：DoRA / Full FT
4. 是否有偏好对？
   - 是：SFT 后接 DPO
   - 否：只做 SFT
5. 是否有可验证答案（代码/数学）？
   - 是：SFT 后接 GRPO
   - 否：DPO 或停止 SFT

**标准微调流程**

```text
需求定义
→ 数据集构建（SFT pairs / preference pairs / verifiable outputs）
→ 选基座（7B-70B；质量与显存预算）
→ 选方法（Full/LoRA/QLoRA/DoRA/Adapter/Prompt）
→ 训练（SFT → DPO/GRPO，如需要）
→ 评估（heldout benchmark + 业务指标）
→ 部署（合并权重 / 多adapter服务 / vLLM）
→ 监控（质量漂移、失败样例、推理延迟、成本）
```

**参数速查**

| 超参 | 推荐 | 说明 |
|---|---|---|
| rank r | 8-16 | 大多数任务够用，质量不足再升 |
| alpha | 2×rank | LoRA 常见起点 |
| target_modules | attention + MLP | 更复杂任务用 all-linear |
| LR | 1e-4 / 2e-4 | LoRA/QLoRA 常用，需 cosine 或 warmup |
| epochs | 3-6 | 小数据多轮，但防止过拟合 |
| batch | 有效 batch 16 | 单卡小 bs + gradient accumulation |

**避坑**
- 不要把 LoRA 参数少误解成推理快：推理速度取决于合并方式与基座；多 adapter 切换反而有管理成本
- 不要只看训练损失：模型往往在中期 checkpoint 最佳，最后 checkpoint 不一定最好
- 不要 DPO 前跳过 SFT：SFT 负责能力/格式，DPO 负责偏好，职责不同
- 不要训练集/测试集混用：偏好数据和验证集泄漏会制造虚假高指标
- 部署前后要双测：量化、合并、vLLM 推理路径都可能改变输出


## 相关笔记

- [模型训练精度实战](./2026-08-18-模型训练精度实战-FP16-BF16-FP8选择查验与MiniMind-LoRA训练全链路.md) — 方法全景的实操验证层
- [小模型LoRA微调实证](./2026-08-18-小模型LoRA微调实证-Qwen3.5-0.8B生产级抽取与边缘端峰值内存压缩.md) — LoRA 生产落地证据
- [LittleLearner只学到五年级](./2026-08-18-LittleLearner只学到五年级-预训练边界决定能力天花板的对照实验.md) — 后训练无法突破预训练边界的对照证据
