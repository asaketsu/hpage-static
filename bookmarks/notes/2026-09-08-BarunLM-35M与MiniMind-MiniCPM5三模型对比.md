# BarunLM-35M vs MiniMind vs MiniCPM5-2B：三个小模型的定位与用途对比

> **来源**：微信公众号（评论文，介绍 BarunLM-35M）
> **原文链接**：https://mp.weixin.qq.com/s/JPmVKpTs0ZG1PqEqcTmLhA
> **模型卡**：https://huggingface.co/harrrshall/BarunLM-35M
> **GitHub**：https://github.com/harrrshall/barunlm-35m
> **对比对象**：MiniMind-v1-small（本项目 AirCraft 已用）/ MiniCPM5-2B（OpenBMB）
> **记录日期**：2026-09-08

**标签**：#小模型 #BarunLM #MiniMind #MiniCPM5 #参数效率 #注意力架构 #边缘部署 #教育

---

## 一、内容整理

### 1.1 BarunLM-35M 是什么

- **参数量**：35,072,768（约 3500 万 = 0.035B，不是 3.5B）
- **架构**：decoder-only，给定前 token 预测下一个 token（与 GPT 同路线）
- **定位**：**不是聊天模型**——无指令微调，默认任务是 completion（文本续写）。能生成文字 ≠ 具备通用问答能力。
- **最大特点**：足够小 + 足够开放——训练配置、源码、权重、评测协议全公开，适合当"缩小版实验室"玩。

### 1.2 核心架构创新：3:1 局部/全局注意力交替 + 残差选择器

- **注意力节奏**：3 层局部注意力（窗口 256 token，只处理相邻范围）+ 1 层全局注意力（扫描整段序列）。"局部负责眼前信息，全局定期开会"。
- **设计动机**：标准全局注意力每层都扫全序列，序列变长时计算/显存压力大；但语言中很多关系发生在附近（短语/相邻句），不需要每层都承担全局扫描的昂贵代价。
- **可学习残差选择器**：每 4 层一组出现一次。小型"保留还是更新"开关——前面表示已含好信息时不必覆盖，新计算确实更好时才向前传。
- **其他工程组合**：GQA（分组查询注意力）、Partial RoPE（50% 旋转位置编码）、QK Normalization、门控注意力输出、bounded SwiGLU。不是 BarunLM 发明的新概念，但压进了 35M 参数的完整系统。

### 1.3 架构精确配置（模型卡）

```
参数量:          35,072,768
层数/宽度:       12 / 448
注意力头:        7 query heads, 1 key/value head (GQA)
注意力节奏:      3 local + 1 full (每4层循环)
局部窗口:        256 tokens
位置编码:        50% partial RoPE
FFN 宽度:        1,228
残差选择:        每 4 层
词表:            16,384 (byte-level BPE)
上下文长度:      2,048 tokens
嵌入:            input/output weights tied
```

### 1.4 训练配置

- **训练 token 数**：57 亿（5.70B），约 162.5 tokens/parameter
- **训练数据**：教育文本 + 合成内容 + 数学 + 通用网页 + 代码
- **硬件**：最终阶段单张 NVIDIA H200
- **上下文**：2048 token
- **优化器**：Muon（原文提及）
- **重要澄清**："单张 H200 训练完成" ≠ "普通显卡可轻松复现全部训练"——H200 对应的是 57 亿 token 预训练预算，推理只需普通消费级 GPU。

### 1.5 评测结果与复现争议

**原始报告**（9 项零样本任务：ARC-Challenge/Easy、BoolQ、HellaSwag、LAMBADA、OpenBookQA、PIQA、SciQ、WinoGrande）：

```
模型                参数量     宏平均准确率    BarunLM 领先
BarunLM-35M         35.1M      41.01%         —
LFM2.5-230M-Base    229.7M     39.20%         +1.81 pp
Pythia-160M          162.3M     37.35%         +3.66 pp
Stentor-30M          30.4M      36.46%         +4.55 pp
TinyStories-33M      68.5M      33.16%         +7.85 pp
Pythia-70M           70.4M      31.71%         +9.30 pp
```

- 用 6.55× 更少参数超过 LFM2.5-230M。配对 bootstrap 置信区间 [+0.92, +2.71] pp。
- **去污染处理**：排除 1,854 个样本（correctness-blind 13-token 精确扫描训练历史）。

**独立复现争议**：
- BarunLM 复现得 41.37%（与官方相近）✅
- LFM2.5-230M 复现得 49.57%（而非原报告的 39.20%）❌
- 结论：原始表格不能当作脱离条件的总排行榜。"是否胜过更大模型"必须连同完整评测协议一起讨论。

### 1.6 原文的教育定位（"好玩实验课"设计）

原文把 BarunLM-35M 定位为大模型课程案例：①跑英文续写看生成质量 → ②拆参数量到可见组件 → ③画 3:1 注意力节奏图 → ④读训练配置理解配方 → ⑤跑评测质疑数据污染 → ⑥改局部窗口/全局间隔做小实验。

---

## 二、查询拓展

### 2.1 局部/全局交替注意力（Sliding Window + Periodic Global）

BarunLM 的 3:1 节奏本质是 **Sliding Window Attention（SWA）+ Periodic Global** 的变体。Longformer（Beltagy et al. 2020）最早系统化提出"局部窗口 + 少量全局 token"的混合方案；BigBird（Zaheer et al. 2020）用理论证明稀疏注意力可逼近全注意力表达力。BarunLM 的工程创新不在发明这个模式，而是把它压缩到 35M 参数的极小规模——"3 局部 1 全局"的节奏在小模型中很少见（小模型通常每层都用全注意力，因为层数少不敢浪费），这恰恰是其参数效率的来源。

### 2.2 GQA（Grouped-Query Attention）

BarunLM 用 7 query heads + 1 KV head（比值 7:1），这是 GQA 的极端配置（接近 Multi-Query Attention）。GQA 由 Ainslie 等（2023）提出，在推理时把 KV cache 压缩为 1/N（相比标准 MHA），对带宽受限场景（小模型典型瓶颈）收益最大。MiniMind 也用了 GQA（16:8 = 2:1），但没这么极端。

### 2.3 Partial RoPE 与 QK Normalization

Partial RoPE（50%）指只对 query/key 的一半维度施加旋转位置编码——降低位置信息对表示空间的占比，腾出更多容量给语义。QK Normalization（对 Q·K 做 LayerNorm）是 recent 小模型稳定训练的标配（如 ViT-22B），防止注意力 logits 爆炸。这两个在小模型中比大模型更关键——参数少、容量紧，任何数值不稳定都会吞噬学习信号。

### 2.4 bounded SwiGLU 与门控注意力输出

SwiGLU（Shazeer 2020）是 GLU 变体的 FFN 激活，已成为 Llama 系标准。bounded 版指对输出加范数约束（bound），防止小模型中 FFN 输出尺度漂移。门控注意力输出（gated output）指注意力输出经过一个门控再与残差融合——类似 ResNet 的"学习跳跃连接"，与原文说的"可学习残差选择器"一脉相承。

### 2.5 参数效率与 tokens/parameter 比例

BarunLM 的 162.5 tokens/parameter 是一个有意为之的设计选择。Chinchilla 法则（Hoffmann et al. 2022）建议 ~20 tokens/parameter 为最优，但后续研究（Llama 系列实践）证明过训练（over-training）用更多 token 换更小推理成本是值得的。BarunLM 取 162.5 是强过训练路线——在参数固定（35M）时用更多算力换更好质量，代价是训练成本上去了但推理永久便宜。

---

## 三、归纳总结

### 3.1 三模型规格总表（代码块，无 Markdown 表格语法）

```
维度               BarunLM-35M              MiniMind-v1-small        MiniCPM5-2B
──────────────────────────────────────────────────────────────────────────────────
参数量              35.1M                    ~26M                     2,516M (2.5B)
非嵌入参数          35.1M                    ~26M                     1,982M
架构                decoder-only             decoder-only             decoder-only (LlamaForCausalLM)
层数                12                       8                        42
隐藏维度            448                      512                      (Llama标准)
注意力头(Q/KV)      7/1 (GQA极端)            16/8 (GQA 2:1)           16/2 (GQA 8:1)
注意力节奏          3 local + 1 global       全局每层                  全局每层
局部窗口            256 tokens               N/A                      N/A
词表                16,384 (byte BPE)        6,400 (中文BPE)           (标准Llama)
上下文长度          2,048                    512                      131,072
位置编码            50% partial RoPE         标准(推测RoPE)            RoPE
FFN                 bounded SwiGLU           标准                      SwiGLU
残差选择器          每4层                    无                       无
嵌入绑定            input/output tied        未知                     标准
训练token           5.7B (162.5 tok/param)   未知                     大规模(UltraData)
训练硬件            单张H200                 CPU可训                  大规模集群
MoE                 否                       配置保留(use_moe=false)   否
是否指令微调        否(base模型)             否(base)                 是(RL+OPD后训练)
是否聊天模型        否(completion)           否(completion)            是(工具调用+agent)
```

### 3.2 定位分野（三个模型各属不同生态位）

- **BarunLM-35M**：参数效率研究样本。用 6.55× 更少参数在零样本基准上超过 230M 模型（虽然复现有争议）。价值在**架构创新的公开可拆解性**，不在产品级可用。
- **MiniMind-v1-small**：教学级中文 LLM。vocab 6400、max_seq 512 极小，专为"看懂 Transformer 每一行代码"设计。AirCraft 项目用它做航空材料 LoRA 微调的验证管线，验证的是管线而非模型能力。
- **MiniCPM5-2B**：产品级端侧 LLM。2.5B 参数但支持 131K 上下文 + 工具调用 + agent 任务，2B 级开源 SOTA（平均 53.9 分超 4B 级）。定位是**可部署的本地助手**，不是教学样本。

### 3.3 架构设计哲学对比

```
BarunLM：      极致参数效率 → 3:1注意力交替 + 残差选择器 + GQA 7:1
              "每层都全局太贵，3层局部+1层全局够用"
              
MiniMind：    最简教育实现 → 全局每层 + GQA 2:1 + MoE保留未启用
              "最小可读的完整Transformer，学生能看懂每一行"

MiniCPM5-2B： 产品级密集 → 42层Llama标准 + GQA 8:1 + 131K上下文
              "标准架构极致调参+RL+OPD，推理在端侧可跑"
```

---

## 四、趋势判断

### 趋势1：35M 级模型正在成为"参数效率研究"的标准化实验台

依据：BarunLM、Stentor-30M、TinyStories-33M、Pythia-70M 都在此量级公开权重+评测。原因：35M 是"能在单张 GPU 上跑完整预训练 + 全量评测"的最小量级，同时参数够多能展示注意力/FFN/残差等架构差异的效果。小模型是架构实验的"果蝇"。

### 趋势2：局部/全局交替注意力从大模型向小模型下沉

依据：Longformer/BigBird 最初解决大模型长序列问题；BarunLM 把它用到 35M 小模型上。趋势是：稀疏注意力不再只是"长序列省钱手段"，而是"小模型省参数手段"——局部层省下来的参数预算给 FFN 或更多层。这对边缘部署有直接价值。

### 趋势3：评测可复现性正成为小模型社区的信任门槛

依据：BarunLM 原报告 LFM2.5-230M 得 39.20%，独立复现得 49.57%——10 pp 差距意味着至少一方评测流程有严重问题。BarunLM 自己做了去污染（排除 1854 样本）和 bootstrap 置信区间，这是正面做法；但"比较对象用不同评测代码/提示格式"的争议无法靠单方努力解决。社区需要共享评测 harness（LM Evaluation Harness 0.4.12 是候选）。

### 趋势4：端侧 LLM 从"能跑"向"能当 agent"进化

依据：MiniCPM5-2B 支持 131K 上下文 + 工具调用 + agent 任务，在 LiveCodeBench 得 69.1 超 4B 级模型。BarunLM 和 MiniMind 还在 completion 基础模型阶段。端侧模型的差异化竞争已从"MMLU 多少分"转向"能不能跑 agent workflow"。

---

## 五、关联分析

### 5.1 与 AirCraft 项目的直接关联

AirCraft 项目用 MiniMind-v1-small 做航空材料 LoRA 微调。BarunLM-35M 提供了一个有趣的替代/对照选项：

- **参数量接近**（35M vs 26M），但 BarunLM 架构更先进（12 层 vs 8 层、GQA 7:1 vs 2:1、3:1 注意力节奏 vs 全局每层）。
- **词表差异**是关键障碍：BarunLM vocab=16384 byte-level BPE（英文友好），MiniMind vocab=6400 中文 BPE（中文友好）。航空材料问答是中文场景，BarunLM 需要换中文词表才能用——直接 LoRA 不够，得续训。
- **上下文**：BarunLM 2048 vs MiniMind 512——若航空材料回答需要更上下文，BarunLM 有 4 倍空间。
- **如果目标升级**：把 AirCraft 从"验证管线"提升到"可用问答"，MiniCPM5-2B 是跳一级的候选——2.5B 中文能力强、支持指令微调、131K 上下文。但训练成本和推理资源需求也跳一级。

### 5.2 与 DUCK-Pi_5 / Jetson 边缘 AI 部署的关联

三模型在 Jetson Orin 上的部署可行性梯度：
- MiniMind-v1-small（26M, float32, 103MB）：Jetson CPU 可跑，已验证。
- BarunLM-35M（35M, 推测 float32, ~140MB）：Jetson CPU 可跑，但需写 Python generate 脚本（不依赖 trust_remote_code，原生 PyTorch）。
- MiniCPM5-2B（2.5B, BF16, ~5GB）：需 GGUF Q4 量化后 Jetson 可跑（约 1.5GB），但推理速度取决于量化框架（llama.cpp 优于 transformers）。

### 5.3 三模型对"小模型有什么用"的不同回答

- BarunLM 的回答：**研究**——拆架构、改模块、跑评测，建立大模型直觉。
- MiniMind 的回答：**教学+验证管线**——看懂 Transformer 每行代码、跑通 LoRA 全流程。
- MiniCPM5-2B 的回答：**产品**——本地助手、coding agent、工具调用。

---

## 六、金句摘录

> 「模型能生成文字，不等于模型具备通用问答能力。」— 区分 completion model 与 chat model 的第一性原理。

> 「局部注意力负责便宜地处理眼前信息，全局注意力负责定期开会。这不是说远距离关系不重要，而是没有必要让每一层都承担同样昂贵的工作。」— 3:1 注意力节奏的设计哲学，一句话说清稀疏注意力的工程价值。

> 「会读评测表，比会背一个漂亮分数更重要。」— 原文对评测素养的核心主张，与 AlienMind 笔记"验证闭环是存亡判据"同构。

> 「它不适合拿来做通用聊天助手，也不适合承担知识问答、工具调用或高风险决策。它的上下文窗口只有 2048 token。」— 诚实的适用边界声明。

---

## 七、行动启示

```
启示                                行动
────────────────────────────────────────────────────────────────
BarunLM 架构可移植到 MiniMind       3:1 注意力节奏 + 残差选择器可作为
                                    MiniMind 的架构升级实验（同参数量
                                    对比参数效率提升）
中文词表是 BarunLM 迁移的最大障碍    若尝试 BarunLM 做中文任务：先续训
                                    中文 BPE 词表（6400→16384扩容）
                                    + 中文语料续训，再 LoRA
AirCraft 若升级基座                 MiniCPM5-2B-Q4 是从"验证管线"到
                                    "可用问答"的跳级方案，GGUF 在 Jetson
                                    可跑
评测素养                            对任何"X 比 Y 强 N 倍"的宣称：
                                    先查评测 harness 版本/提示格式/去污染
                                    处理，再信结论
小模型是架构实验的果蝇              局部/全局交替注意力 + 残差选择器
                                    可移植到 DUCK-Pi_5 的 RL 策略网络
                                    （如果策略网络需要更长序列记忆）
```

---

## 八、拓展应用推荐

- **上手 BarunLM**：`hf download harrrshall/BarunLM-35M --local-dir BarunLM-35M` → 不需要 trust_remote_code，原生 PyTorch generate.py 直接跑；GitHub 仓库 `harrrshall/barunlm-35m` 有完整测试。
- **架构移植实验**：把 BarunLM 的 3:1 注意力节奏单独抽出来，移植到 MiniMind-v1-small 上做对照（同 26M 参数，全局每层 vs 3:1 交替），跑航空材料问答 eval loss 对比——这是本项目 AirCraft 可直接发起的增量实验。
- **MiniCPM5-2B 部署**：GGUF Q4 版本已发布（`MiniCPM5-2B-GGUF`），Jetson 上用 llama.cpp/Ollama 可跑；支持工具调用+131K 上下文，适合做本地 agent 原型。
- **延伸阅读**：Longformer 论文（稀疏注意力理论基础）、Chinchilla 法则（tokens/parameter 比例）、LM Evaluation Harness 文档（评测标准化）、MiniCPM5 技术报告（arXiv:2506.07900，端侧 LLM 训练配方）。

---

## 九、指南分析

**阅读与使用指南：**

1. **文体定性**：原文是一篇克制的小模型评测/教育文——不替 BarunLM 背书为"最强"，主动指出评测复现争议，诚实声明适用边界。这在"小模型营销文"中很少见，可信度高。
2. **原文增量 vs 本笔记增量**：原文给了 BarunLM 架构+训练+评测的完整介绍；本笔记补了三模型规格对比表、AirCraft 项目迁移可行性、Jetson 部署梯度——这些是原文没有的。
3. **BarunLM 的真实价值不在"35M 最强"**：41% 的零样本准确率在产品级场景不可用。真实价值在：①公开了 3:1 注意力节奏 + 残差选择器在小模型中的工程实践；②提供了一个 35M 参数级、原生 PyTorch、不需 trust_remote_code 的可拆解实验台。
4. **迁移到中文场景的坑**：BarunLM 是英文 byte-level BPE（vocab 16384），直接用于中文 LoRA 效果会很差——必须先续训中文词表。MiniMind 的 6400 中文 BPE 反而更适合中文场景微调。MiniCPM5-2B 是三模型中唯一原生支持中文且经过 RL 后训练的产品级模型。
5. **选择建议一句话**：学架构 → BarunLM；学管线 → MiniMind（已在 AirCraft 验证）；做产品 → MiniCPM5-2B。

## 相关笔记

- [2026-09-08-MiniMind从零训练极小语言模型-全管线与7阶段案例](./2026-09-08-MiniMind从零训练极小语言模型-全管线与7阶段案例.md) — 对比组之一的完整管线展开
- [2026-09-08-1G垂域微调基座选型与海光DCU适配全解析](./2026-09-08-1G垂域微调基座选型与海光DCU适配全解析.md) — 选型结论的工程化延伸（DCU 适配）
- [2026-09-09-小模型LoRA微调数据质量](./2026-09-09-小模型LoRA微调数据质量.md) — 三模型之上的数据质量变量
