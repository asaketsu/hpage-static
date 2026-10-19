# 后训练全景：SFT / DPO / RLHF 原理与实操（研究笔记）

> 主题: 什么是后训练（Post-Training）？与微调（Fine-tuning）的差异？SFT、DPO、RLHF 各自怎么做？
> 依据: 本机 TRL skill（含 SFT/DPO/GRPO/reward-modeling 工作流与超参表）+ InstructGPT/DPO/GRPO 论文脉络 + 本周 Scaling Law 系列笔记（GLM-5.3 = 后训练旋钮实证）
> 类别: LLM 训练 · 对齐 · 偏好优化

---

## 一、什么是后训练（内容整理）

### 1.1 定义与位置

**后训练（Post-Training）= 预训练（从海量无标注语料学语言能力）之后、部署之前的一切训练阶段**。目的：把一个"会说话的"基座模型（Base Model）变成"会干活、对人胃口"的可用模型（Instruct/Chat Model）。

```
预训练（Next-Token Prediction，万亿 tokens）
    ↓ 产出: Base Model（会续写，不会听话）
后训练（指令/偏好/能力注入）
    ├─ SFT  → 会遵循指令
    ├─ 偏好对齐（RLHF / DPO / GRPO…）→ 输出符合人类偏好
    └─ 能力后训练（代码/数学/Agent/长时域 RL）→ GLM-5.3 旋钮
    ↓ 产出: Instruct/Chat Model
```

### 1.2 后训练 vs 微调：辨析（易混点）

| 维度 | 微调 Fine-tuning | 后训练 Post-Training |
|------|-----------------|---------------------|
| 词义范围 | **单指技术动作**：在已有模型上继续做监督训练（SFT 就是典型微调） | **指阶段集合**：预训练之后的所有训练阶段（SFT + 对齐 + 能力 RL） |
| 默认含义 | 通常 = 监督学习（有标注对，loss = 交叉熵） | 包含监督（SFT）**和强化学习**（RLHF/GRPO/DPO 对比学习） |
| 数据形态 | prompt→completion **标准答案对** | SFT 用答案对；对齐阶段用**偏好对**（chosen/rejected）或**只给 prompt**（靠 reward 打分） |
| 优化目标 | 拟合示范答案的分布 | 对齐阶段优化的是**相对偏好/奖励**，不是拟合某个标准答案 |
| 语境惯例 | 学术圈说"微调一个 7B"一般指 SFT/LoRA | 工业界说"后训练"（如唐杰的"拨后训练旋钮"）= SFT+RL 全家桶 |

**一句话辨析**：微调是技术动作（SFT ⊂ 微调），后训练是流程阶段（SFT + 偏好对齐 + 能力 RL ⊂ 后训练）。说"GLM-5.3 只动了后训练"意思是基座权重冻结思路下，SFT/RL 阶段的配方变了——不是只做了一次微调。

### 1.3 为什么预训练模型不能直接用

Base Model 的问题：续写而非回答（问"法国首都"可能续写成"是哪个国家的问题"）、不拒绝有害请求、风格不贴合人类预期。InstructGPT 论文核心发现：**1.3B 参数经后训练的对齐效果可超过 175B 纯预训练模型**——后训练的杠杆极大。

## 二、SFT — 监督微调（指南分析）

### 2.1 原理

给模型看大量「指令 → 高质量回答」对，直接用**交叉熵损失**教它模仿示范答案。本质仍是监督学习：模型学到的是"这个 prompt 下，人类期望的输出分布长什么样"。

**Loss**：`L = -Σ log P(y_t | y_<t, x)`（对示范答案 y 做 next-token 负对数似然，prompt x 的 token 通常不计 loss——completion-only loss）

### 2.2 数据格式

```json
{"prompt": "什么是法国首都？", "completion": "法国的首都是巴黎。"}
```

对话式（chat template 渲染后训练，assistant 段计 loss）。

### 2.3 实操（TRL SFTTrainer，照录可用）

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
dataset = load_dataset("trl-lib/Capybara", split="train")

training_args = SFTConfig(
    output_dir="Qwen2.5-0.5B-SFT",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=2e-5,
    logging_steps=10,
    save_strategy="epoch",
)
trainer = SFTTrainer(model=model, args=training_args, train_dataset=dataset, tokenizer=tokenizer)
trainer.train(); trainer.save_model()
```

**超参基准**：lr=2e-5（全参）/ 1e-4~2e-4（LoRA），epoch 1-3，7B+LoRA 约 16GB 显存。

### 2.4 SFT 的边界

- 只能教"示范里有的行为"——上限 = 数据质量（专家锚定：Garbage in Garbage out）
- 无法表达"两个回答都比第三个好，但第一个更好一点"这种**序关系**——这正是偏好优化登场的地方

## 三、RLHF — 基于人类反馈的强化学习（指南分析）

### 3.1 原理（InstructGPT 三步曲）

1. **SFT**：先做监督微调得到起点模型
2. **训练奖励模型 RM**：对同一 prompt 采样多个回答，人工排序 → 训练一个打分模型（Bradley-Terry 损失：`L = -log σ(r_chosen - r_rejected)`），把"人类偏好"压缩成一个标量函数
3. **PPO 强化学习**：把 LLM 当策略（policy），RM 当环境奖励，用 PPO 优化策略让回答得分最高，同时加 **KL 惩罚**约束不要偏离 SFT 模型太远（防 reward hacking / 胡言乱语）

**Reward 公式**：`R = r_RM(y) - β·KL(π_θ || π_SFT)`

### 3.2 为什么必须 KL 惩罚

RM 是从有限偏好数据学出的近似——策略一旦找到 RM 的盲区（比如输出复读机式的高分模式），就会刷分作弊（reward hacking）。KL 项把策略拴在 SFT 模型附近，牺牲一点分数换分布不跑飞。

### 3.3 实操（TRL 完整管线）

```bash
# Step 2: Reward Model（AutoModelForSequenceClassification, num_labels=1）
#   RewardConfig(lr=1e-5, epochs=1) + RewardTrainer + ultrafeedback_binarized

# Step 3: PPO
python -m trl.scripts.ppo \
    --model_name_or_path Qwen2.5-0.5B-SFT \
    --reward_model_path Qwen2.5-0.5B-Reward \
    --output_dir Qwen2.5-0.5B-PPO \
    --learning_rate 3e-6 \
    --per_device_train_batch_size 64 \
    --total_episodes 10000
```

**显存**：PPO 7B ≈ 40GB+（policy + ref + RM + value 同时在线）；**不稳定点**：kl_coef（0.05→0.1 提稳）、cliprange（0.2→0.1 提稳）。

### 3.4 RLHF 的优劣

- ✅ 表达力最强：奖励可来自 RM、可验证任务的真实信号（数学对错/代码测试通过率）、AI 审判（RLAIF）
- ❌ 工程复杂度最高：四模型同框、超参敏感、训练易崩

## 四、DPO — 直接偏好优化（指南分析）

### 4.1 核心洞察

DPO 论文标题即答案：**Your Language Model is Secretly a Reward Model（你的语言模型本身就是个奖励模型）**。数学上可以证明：最优策略与 RM 的关系有闭式解，把 reward 反解出来代入 RL 目标，**RLHF 的目标可以直接改写成只用策略模型自身的对数概率表达的损失**——不需要显式 RM、不需要 PPO 采样循环。

### 4.2 做法（对比学习）

数据 = chosen/rejected 偏好对。损失：

**`L_DPO = -log σ( β·[ log π_θ(y_w|x)/π_ref(y_w|x) − log π_θ(y_l|x)/π_ref(y_l|x) ] )`**

直观读法：拉大"好答案相对参考模型的对数概率提升量"与"坏答案的提升量"之差。β 控制偏离参考模型的强度（KL 约束的化身）。

### 4.3 实操（TRL DPOTrainer）

```python
from trl import DPOTrainer, DPOConfig
config = DPOConfig(output_dir="Qwen2.5-0.5B-DPO", beta=0.1,
                   learning_rate=5e-7, per_device_train_batch_size=4)
trainer = DPOTrainer(model=model, args=config,
                     train_dataset=preference_dataset,  # prompt/chosen/rejected
                     processing_class=tokenizer)
trainer.train()
```

**要点**：β=0.1 默认（大→保守，小→激进）；lr 极小（5e-7~1e-6，DPO 对 lr 敏感易过拟合）；显存比 PPO 省一半（只需 policy + ref，7B 约 24GB）。

**10+ 变体速览**（本机 dpo-variants 参考）：IPO（防过拟合理论更强）/ Robust（标签噪声）/ Hinge（间隔式）/ BCO（二分类视角）/ DiscoPOP（自动损失发现）——默认 sigmoid 够用，噪声大选 robust，过拟合选 ipo。

### 4.4 DPO 的优劣

- ✅ 简单稳定、省显存、无需 RM 和在线采样，开源社区事实标准
- ❌ 离线方法：只见过数据里的回答，不能探索新策略；数据外泛化弱于在线 RL；偏好对质量决定一切

## 五、三者对比与选择（归纳总结）

| 维度 | SFT | DPO | RLHF(PPO) | GRPO（附） |
|------|-----|-----|-----------|-----------|
| 数据 | prompt+标准答案 | chosen/rejected 对 | 排序数据训 RM + prompt | 只需 prompt（组内相对比较） |
| 损失 | 交叉熵 | 对比损失（闭式 KL 约束） | PPO + KL 惩罚 | 组相对优势 + KL |
| 需要显式 RM | 否 | 否 | **是** | 否（规则/可验证信号可直用） |
| 在线采样 | 否 | 否 | 是 | 是 |
| 显存 7B | 16GB(LoRA) | 24GB | 40GB+ | 24GB |
| 稳定性 | 高 | 高 | 低 | 中 |
| 表达力 | 模仿 | 偏好排序 | 最强 | 强（推理/代码主流） |
| 典型 lr | 2e-5 | 5e-7 | 3e-6 | 1e-5 |

**选型口诀**：有标准答案→SFT；有偏好对、要省事→DPO；有可验证任务（数学/代码）→GRPO；要极致对齐且有 infra→PPO-RLHF。真实管线是组合：**SFT 打底 → DPO/GRPO 调偏好/能力**。

## 六、与本周笔记群的互证（趋势判断）

1. **GLM-5.3 = 后训练旋钮的实证**（唐杰笔记）：同基座 753B/40B 冻结，一个月"长时域环境训练+RL"→ Coding 国产最优——正是表中 GRPO/RL 路线在代码域的规模化应用；Yanhua 补全提醒：n=1 证明余量存在，还不是可外推定律
2. **Alloomi"经验焊权重"= 机构版后训练**（穷富孩子笔记）：任务现场数据→回放→post-training，飞轮与 InstructGPT 三步曲同构，只是 RM 换成"专家锚定的交付标准"
3. **后训练 Chinchilla 还没出现**：SFT/RL/环境三类算力的最优配比未知——对应 fine-tuning-with-trl skill 的超参表全是经验值，这轮 alpha 在配方
4. **显存阶梯决定个人/小团队路线**：SFT(LoRA)→DPO→GRPO 单卡可及，PPO-RLHF 是大厂专属——与"穷人版焊权重"（evolver/skill 固化）形成资源对照

## 七、本机验证与工具链（拓展应用推荐）

- 本机 TRL skill（`fine-tuning-with-trl`）已含全部四个工作流可运行代码：SFTTrainer/RewardTrainer+PPO/DPOTrainer/GRPOTrainer + 10 个 DPO 变体超参表 + GRPO 生产级模板（templates/basic_grpo_training.py）
- 显存约束下的可行组合（Jetson 不跑训练，仅列管线供其他机器执行）：QLoRA+SFT（指令注入）→ DPO（偏好）→ GRPO（可验证任务）——对应 USER.md 铁律"代码管线就绪即可，执行留待其他机器"
- 评测闭环：对齐后必跑金标集（对应 content-judge skill：多维评分 <阈值标记不合格），防止"对齐税"（能力下降换听话）

## 查询拓展与出处（引用与关联）

- 论文: InstructGPT (2022, arXiv:2203.02155) · DPO (2023, arXiv:2305.18290) · GRPO (DeepSeekMath, 2024)
- 本机 skill: `fine-tuning-with-trl`（本文代码与超参来源）及其 references：sft-training / dpo-variants / reward-modeling / online-rl / grpo-training
- 本机关联笔记: 2026-08-20《唐杰后训练旋钮时代》+《Yanhua 批判性补全》·《AI也分穷人家孩子和富人家孩子》· 《DeepSeek Harness 四种预设》（极简模式=官方跑分框架）· train-mini-llm/train-lm-pipeline 项目（预训练侧对照）
- 术语速查: Base Model=预训练产物 · Post-Training=SFT+对齐+能力RL统称 · Fine-tuning=监督续训动作 · Alignment=让输出符合人类偏好 · RLHF 家族=RM-based(PPO) / RM-free(DPO/GRPO)


## 相关笔记

- [唐杰：万亿参数是弯路，后训练旋钮时代](./2026-08-20-唐杰万亿参数是全行业弯路后训练旋钮时代.md) — 同主题权威观点，后训练旋钮的行业定调
- [Scaling Law 新解](./2026-08-20-ScalingLaw新解GLM-5.3对照实验与Lab即Infra.md) — 后训练旋钮的实证基础，GLM-5.3 对照实验
- [LLM 后训练 RL 效率与可靠性](./2026-08-20-LLM后训练RL效率与可靠性-RLVR调度Debate抗Hack与ES换道.md) — 后训练 RL 的前沿技术深化
- [AI 也分穷人家孩子和富人家孩子](./2026-08-20-AI也分穷人家孩子和富人家孩子-Alloomi自进化Agent.md) — 后训练的全栈视角：模型后训练+应用层自进化
