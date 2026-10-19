# 大模型是怎么来的：从数据到 Foundation Model

> 原文链接：https://mp.weixin.qq.com/s/lrpYmQuAFmk4wot_NK-W9A
> 作者：吴佳浩Alben | 撰稿 2026.5.1，更新 2026.8.17
> 收录时间：2026-08-17 | 类型：技术科普长文（LLM 训练全链路）

#大模型 #Transformer #预训练 #ScalingLaw #分布式训练 #LLM

## 出处

- 原文：[大模型是怎么来的：从数据到 Foundation Model](https://mp.weixin.qq.com/s/lrpYmQuAFmk4wot_NK-W9A)（微信公众号文章，作者：吴佳浩Alben，2026.8.17 更新版）
- 主题：一个百亿/千亿参数大模型的完整诞生链路——数据→Token→Embedding→Transformer→Loss/反向传播→AdamW→分布式训练→后训练
- 官方推荐实践项目：Train LLM From Scratch（作者参与开发的开源项目，完整实现 Tokenizer/Transformer/训练/生成全过程）

## 一、内容详细整理

### 0. 全文一句话主线

原始数据 → 清洗编码成 Token → Embedding 成向量 → Transformer 层层计算给出预测 → Loss + 反向传播转化为"该怎么改参数"的信号 → AdamW 更新参数 → 在数万亿 Token 上循环执行 → 收敛出的那组参数就是 Foundation Model。

### 1. 70B 模型到底意味着什么（体量感）

**推理 vs 训练的显存量级完全不同**：

| 阶段 | 计算口径 | 70B 显存需求 |
|------|----------|-------------|
| 仅存参数（BF16） | 2 Byte/参数 | ≈ 140 GB |
| 训练态（AdamW 混合精度） | 16 Byte/参数（BF16 参数 2 + FP32 主权重 4 + FP32 一阶动量 4 + FP32 二阶动量 4 + 梯度 2） | ≈ 1.1 TB |
| 单张 H100 | — | 80 GB（连训练态都放不下） |

- 结论：70B 训练从第一天起就是**分布式系统工程问题**，不是"训一个模型"。
- 推理阶段通过量化（INT8/FP8/4bit）、KV Cache 优化、模型并行，70B 可部署在 4×H100、8×A100 甚至消费级 48GB 卡小集群。
- **训练和推理对硬件规模的要求不能混为一谈**。

### 2. 数据：大模型真正的燃料

**业界共识：数据质量决定模型能力上限，架构和训练技巧决定能否逼近这个上限。**

#### 2.1 数据来源占比（典型）

| 来源 | 占比 | 特点 |
|------|------|------|
| Common Crawl 网页快照 | 40%~60% | 规模最大，质量参差 |
| 书籍（Books3/图书馆扫描） | 5%~10% | 长文本、语言规范 |
| 代码（GitHub） | 5%~15% | 提升推理与结构化能力 |
| 学术论文（arXiv/PubMed） | 2%~5% | 专业知识密度高 |
| 百科（Wikipedia） | 1%~3% | 事实性强噪声低 |
| 对话/论坛（Reddit/StackExchange） | 5%~10% | 提升问答与推理 |

#### 2.2 清洗去重过滤三道工序

- 去重主流：**MinHash + LSH**——亿级文档下近似线性复杂度找出高相似文档对剔除，防止重复内容过拟合。
- 过滤三类手段：启发式规则（符号占比/重复行数）、质量分类器（高质量语料训练打分）、困惑度过滤（小模型算 perplexity，过高过低都剔除）。
- 文章给出的清洗代码核心逻辑（去 HTML 标签→归一化空白→长度<200 剔除→langdetect 语言过滤 zh-cn/en）。

#### 2.3 数据增强

回译（中→英→中）、结构化转写（表格/知识图谱转自然语言问答）、难例挖掘（针对数学推理等薄弱任务定向扩充）。

#### 2.4 范式转变：Internet Data → AI Generated Data（2025-2026 关键增量）

四类数据协同格局：
```
真实数据（Internet Data）
+ 模型生成数据（Synthetic Data）
+ 人工验证数据（Human Preference Data）
+ Agent 交互数据（Agent Generated Data）← 最值得关注的新增量
```

- **Agent 交互数据** = AI 智能体在真实完成任务过程中产生的行为轨迹（多步工具调用、代码执行反馈、任务成功/失败完整过程），天然带"结果验证"信号。
- 风险：**模型坍缩（Model Collapse）**——纯合成数据训练导致分布收窄、多样性下降，须与真实数据混合并严格过滤。
- **高质量数据已成比参数规模更稀缺的资源**——"容易获取的高质量文本"正被各大模型消耗殆尽。

#### 2.5 数据配比（Data Mixing）

分阶段配比（LLaMA-3 annealing 阶段提高书籍/代码/数学比例）、配比搜索（DoReMi 小模型搜索最优配比再放大）、课程学习（由易到难）。

### 3. Tokenizer：模型如何理解世界

#### 3.1 BPE 核心思想

- 字符级起步，不断合并**出现频率最高的相邻符号对**构建词表。
- GPT 系用 **Byte-level BPE**（字节层操作，天然覆盖所有 Unicode，无未登录词）。
- **SentencePiece**（LLaMA/Qwen 采用）语言无关，空格当普通字符，对中日文更友好。
- 真实分词效果：`"ChatGPT" → ["Chat", "G", "PT"]`；`"今天我们学习Transformer" → ["今天", "我们", "学习", "Transform", "er"]`——高频整词一个 Token，低频复合词拆子词。

#### 3.2 词表设计与 Token 效率

| 模型 | 词表大小 | 说明 |
|------|----------|------|
| GPT-2 | ~50K | — |
| LLaMA-1/2 | 32K | — |
| LLaMA-3 | 128K | 大幅扩容，提升多语言/代码效率 |
| Qwen2.5 | ~150K | 专门优化中文压缩率 |

- 权衡：词表越大 Token 序列越短（省算力），但 Embedding 参数和显存增大。
- **中文模型扩词表的本质是降低 tokenization loss（分词损失）**——同样窗口装更多内容，而不是单纯加参数。

#### 3.3 Embedding：Token 变向量（最常被忽略的一步）

- Tokenizer 只输出整数编号（Token ID），Transformer 处理的是**向量**——中间差一步 Embedding。
- Embedding = 巨大查找表矩阵，词表每个 Token ID 对应一行向量（初始随机，训练中更新）。
- 查到向量后叠加**位置编码（RoPE）**。
- **Transformer 从来没有处理过"文字"，自始至终处理的都是向量。**

### 4. 模型架构：Transformer 如何产生智能

#### 4.1 Decoder-only + causal mask

每个位置只能看到自己及之前的 token——自回归生成的基础。

#### 4.2 Attention 公式逐项拆解

| 参数 | 含义 | 可以理解为 |
|------|------|------------|
| Q（Query） | 查询向量 | 我现在想找什么信息？ |
| K（Key） | 键向量 | 我能够提供什么信息？ |
| V（Value） | 值向量 | 真正要传递的内容 |
| QKᵀ | 相似度 | 当前 Token 与其它 Token 的相关程度 |
| √dₖ | 缩放因子 | 防止点积过大导致 Softmax 饱和 |
| Softmax | 归一化 | 相关性转权重，和为 1 |
| V 加权求和 | — | 根据注意力权重融合所有 Token 信息 |

#### 4.3 RoPE / RMSNorm / SwiGLU 三件套

| 模块 | 解决的问题 | 核心思路 |
|要素|---|---|
| **RoPE** | 位置编码需相对位置感知+长序列外推 | 对 Q/K 按位置施加旋转变换，点积后旋转角自然抵消为相对位置差 |
| **RMSNorm** | LayerNorm 均值中心化计算量大 | 去掉均值步骤，只做均方根缩放 |
| **SwiGLU** | ReLU/GELU 表达力有限 | 门控机制，SiLU(xW1) 逐元素乘 xW2 动态控制信息流 |

RMSNorm 最小实现（LLaMA/Qwen/Mistral 全面采用此三件套）：

```python
class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))
    def forward(self, x):
        rms = x.pow(2).mean(-1, keepdim=True).add(self.eps).sqrt()
        return x / rms * self.weight   # 只缩放不做均值中心化
```

#### 4.4 GQA/MQA：压缩推理 KV Cache

- 标准 MHA 推理时 KV Cache 显存大；MQA 最省但效果略损；GQA 折中——LLaMA-2/3、Qwen2.5 均用 GQA。

#### 4.5 MoE：稀疏激活

- 总参数可以很大（Mixtral/Qwen2.5-MoE/DeepSeek-MoE），每 token 只激活一小部分专家（Top-2）。
- 核心挑战：负载均衡 + 专家并行的通信开销。

#### 4.6 长上下文优化主线（GPT-4 后另一条主线）

```
Attention 效率优化（FlashAttention）
+ KV Cache 压缩（GQA/MQA/MLA）
+ RoPE Scaling（短训练外推长序列）
+ Sliding Window Attention（限制感受野）
+ Context Parallel（超长序列切多卡）
```

与 GQA/MoE 互补：一个解决"参数规模与推理成本"平衡，一个解决"能处理多长的输入"。

### 5. 训练：学会预测下一个 Token

#### 5.1 Next Token Prediction

- 每句话被拆成很多"用前文预测下一个词"的小样本，模型永远只做一件事：**给定已看到的内容猜下一个 Token**。
- NTP Loss 错位对齐核心代码：

```python
def compute_ntp_loss(logits, labels):
    # 错位对齐：用第i个位置预测第i+1个位置
    shift_logits = logits[:, :-1, :].contiguous()
    shift_labels = labels[:, 1:].contiguous()
    return F.cross_entropy(
        shift_logits.view(-1, shift_logits.size(-1)),
        shift_labels.view(-1), ignore_index=-100,
    )
```

#### 5.2 反向传播与 AdamW

- Loss 衡量预测与真实差距；反向传播按链式法则逐层回传，算出每个参数该往哪调、调多少（梯度）；AdamW 自适应步长更新。
- **参数本身不"保存知识"，它只是连接权重。理解/推理等"智能"是训练过程的涌现结果，不是被直接编码进某个参数。**

#### 5.3 Scaling Law 与 Chinchilla 修正

- GPT-3/OpenAI：Loss 随算力幂律下降，观测范围内无平台期——行业敢堆 GPU 的信心来源。
- **Chinchilla（DeepMind 2022）修正：不是参数越大越好，而是参数与数据要匹配**。同算力预算下，"小参数多吃数据"常胜过"大参数训练不足"。
- LLaMA 刻意用远超 Chinchilla 最优点数据量训练较小模型——把**推理成本**纳入综合考量。现代目标=规模×数据×步数动态平衡。

#### 5.4 混合精度与梯度累积

- **BF16**：与 FP32 指数位相同、尾数位更少，数值范围一致，不需 FP16 的 Loss Scaling——当前主流。
- 梯度累积模拟大 batch：

```python
loss = compute_ntp_loss(logits, labels) / accumulation_steps
loss.backward()             # 梯度自动累加到.grad
if (step + 1) % accumulation_steps == 0:
    optimizer.step()
    optimizer.zero_grad()
```

#### 5.5 完整训练循环（不到 20 行）

```python
model = model.cuda()
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
for batch in dataloader:
    optimizer.zero_grad()
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        logits = model(batch["input_ids"])               # 前向：预测下一个token
        loss = compute_ntp_loss(logits, batch["labels"]) # 与真实token对比算Loss
    loss.backward()      # 反向传播：算出每个参数的梯度
    optimizer.step()     # AdamW根据梯度更新参数
```

### 6. 分布式训练：万卡集群拆模型

| 策略 | 拆分对象 | 特点 |
|------|----------|------|
| Data Parallel | 数据分片，每卡完整模型副本 | 简单，但模型须放进单卡 |
| Tensor Parallel | 单层内部矩阵运算 | 通信频繁，一般限单机 NVLink 内多卡 |
| Pipeline Parallel | 模型按层切分 | 需 micro-batch + 1F1B 调度减少气泡 |
| ZeRO / FSDP | 优化器状态/梯度/参数按卡切分 | 消除数据并行冗余存储，Stage 越高越省显存、通信越多 |

**LLaMA-3 405B 真实集群参照**：405B 参数 ≈ 16000×H100，四维并行（TP+PP+DP+CP），机内 NVLink + 跨机 InfiniBand，PyTorch + 类 Megatron-LM + ZeRO/FSDP 显存优化。

> 大模型 = 算法问题 + 超算问题 + 分布式系统问题的叠加。架构解决"算法效率"，并行策略解决"能否物理跑起来"。

### 7. 后训练：Foundation Model → 产品

- 预训练模型只会"续写"（输入"今天北京天气"→输出"很好/晴朗"，无"回答"意识）；Chat 模型输出结构化、切题、带安全边界的回答。
- 中间差的是 **SFT + Alignment（对齐）**：预训练学"语言长什么样"，后训练教"该怎么说话、该怎么帮人"。
- 后训练大量依赖合成数据（拒绝采样候选答案、教师模型推理链）。

### 8. 案例四家（文内只展开 DeepSeek）

- GPT（OpenAI）/ LLaMA（Meta）/ Qwen（阿里）/ DeepSeek。
- **DeepSeek 路线信号：竞争已从"堆参数规模"转向"用更少算力和显存获得同等甚至更强能力"——效率本身正在成为核心竞争力。**

### 9. 回到起点：70B 参数住在哪

- 70B 不是一整块巨大矩阵，而是 Embedding 层 + 每层 Attention（Q/K/V/O 投影）+ 每层 FFN（SwiGLU 三组矩阵）+ Norm + LM Head 这些**成千上万个小矩阵的总和**。
- **FFN 通常参数占比最大**（每层含维度放大再收缩的两三组大矩阵）；Attention 次之；Embedding/LM Head 占比较小（深模型尤甚）。
- 架构每个选择（层数/隐藏维度/头数/FFN 扩展比）直接决定参数分布和作用。

### 全文总结金句

**数据决定模型能力的上限，架构决定能力利用的效率，而系统工程决定模型能否突破规模的边界。** 技术报告背后真正的工作量分布：数据与工程占大头，模型结构创新占相对较小部分。

## 二、查询拓展

写作笔记时围绕原文未展开但值得追问的点做了延伸检索（方向性记录）：

1. **Chinchilla 最优点的具体计算**：Chinchilla 论文给出"每个参数约 20 个 Token"的经验比例（70B 对应约 1.4T Token），LLaMA 系列实际训练量远超此数（inference-optimal 而非 training-optimal）。原文只提"远超最优点"未给数字。
2. **MLA（Multi-head Latent Attention）**：原文长上下文一节提到 MLA 但未展开——DeepSeek-V2/V3 的 KV Cache 压缩方案，把 K/V 联合压缩到低秩 latent 空间，压缩率显著高于 GQA，是 GQA 之后的下一代方案。
3. **Model Collapse 的实证研究**："AI 生成内容递归训练导致模型退化"由 Shumailov et al. 2023（Nature 2024）系统论证，原文提及风险但未引出处。
4. **Agent 交互数据的落地形态**：对应 Tülu 3、OpenRe

asoner 等后训练 recipe 中以工具调用轨迹、可验证奖励（RLVR）为信号的思路；2025-2026 主流模型后训练数据中合成+Agent 轨迹占比快速上升，验证了原文"四类数据协同"判断。

## 三、归纳总结

### 因果链还原（一句话版）

清洗后的海量 Token（燃料）× Transformer 架构（引擎）× NTP+反向传播+AdamW（学习机制）× Scaling Law 提供的确定性收益预期（资本信心）× 分布式并行（物理可行性）= Foundation Model；再经 SFT+对齐（后训练）= Chat 产品。

### 核心认知增量（相对常识版理解）

| 常见误解 | 原文纠正 |
|----------|----------|
| "70B 是一整块大矩阵" | 是成千上万个小矩阵之和，FFN 占比最大 |
| "参数里存着知识" | 参数只是连接权重，智能是训练的涌现结果 |
| "参数越大越好"（原教旨 Scaling Law） | Chinchilla：参数与数据匹配才好；LLaMA 为推理成本选小模型多吃数据 |
| "预训练模型会聊天" | 预训练只会续写，对话能力来自 SFT+对齐 |
| "大模型是纯算法问题" | 是算法+超算+分布式系统工程的叠加 |
| "训练=推理的硬件需求" | 训练 1.1TB 级 vs 推理可量化到 4×H100 |

### 结构化沉淀（五要素中「指导性意见」的前半部分）

- **何时用本文**：需要向非科班（或自己）系统讲清 LLM 从数据到产品的全链路时，这是结构完整度很高的单篇教材；适合作为团队内训/新人 onboarding 材料。
- **何时不用**：需要某个环节的生产级细节（如 Megatron 的 1F1B 调度实现、ZeRO Stage 3 的通信量推导）时，本文是地图不是工兵铲，直接查 Megatron-LM/DeepSpeed 官方文档。
- **与同类文章差异**：文中大量"体量感锚点"（70B=140GB/1.1TB/16000 张 H100）是区别于教科书的关键特色——用可感知的数字建立直觉，而非罗列公式。

## 四、趋势判断

1. **高质量数据稀缺化是未来 2-3 年主叙事**：原文判断"高质量数据已成比参数规模更稀缺的资源"。互联网易得高质量文本被消耗殆尽 → 合成数据+Agent 交互数据占比持续上升。Tülu 3/DeepSeek-R1 等公开 recipe 已验证"可验证奖励的合成数据"路线可行，2026 年新模型发布会越来越像"数据工程成果展"。
2. **效率路线压过堆参数路线**：DeepSeek 系列证明"更少算力/显存获得同等能力"成立后，MLA、稀疏注意力、轻量 MoE 会加速标准化，成为 2026-2027 模型标配。
3. **训练/推理解耦的硬件策略**：训练态 1.1TB vs 推理态可量化部署的悬殊，意味着训练集中化（头部实验室+国家级算力中心）+ 推理分散化（边缘/端侧部署）格局固化——与 Jetson 等边缘侧部署实践方向一致。
4. **Agent 交互数据是下一代能力来源**：原文明确"下一代模型的重要训练素材可能是 Agent 行为轨迹"。这与 Hermes 这类长程 Agent 系统的日志价值上升同构——工具调用轨迹+成功/失败信号天然带验证标签。
5.判断需谨慎之处：原文是科普定位，案例节数据（如 16000×H100）为公开信息经验值，未标注一手出处；MoE 负载均衡、长上下文等节仅给框架未给量化对比，不宜直接作为选型依据。

## 五、关联分析

**与已有笔记/项目的关系**：

- [[2026-04-19-处理大模型幻觉的工程心得]] — 本文"参数不保存知识，智能是涌现结果"与幻觉工程应对互为表里：幻觉不是 bug 而是续写机制的副产物，后训练对齐只能压制不能根除。
- [[2026-04-12-Kronos-financial-kline-foundation-model]] — Kronos 是"Foundation Model 思想迁移到 K 线时序"的实例，本文的预训练范式（NTP→时序预测）可直接映射。
- [[2026-04-22-CATIA-接入-AI-大模型原理]] — CATIA 接入大模型属于推理侧应用，对应本文"训练/推理解耦"一节：应用层只需关心推理部署（量化/KV Cache/并行），不必关心训练工程。
- quant-trading 系列（LLM 因子挖掘、agentic-alpha-research）— "Agent 交互数据是下一代训练素材"判断若成立，量化 Agent 的决策轨迹数据本身就有沉淀价值。
- ~# 相关：[[2026-04-22-CATIA-接入-AI-大模型原理]]（推理侧应用视角）

## 六、笔记五要素自检（工具/项目类笔记适用）

| 要素 | 本笔记覆盖情况 |
|------|----------------|
| ①功能清单 | ✅ 按原文九章逐节整理（见「内容详细整理」） |
| ②使用性评估 | ✅ 见「归纳总结-结构化沉淀」：单篇教材级全链路综述，体量感锚点特色 |
| ③指导性意见 | ✅ 何时用/何时不用/替代方案均已给出 |
| ④案例可寻 | ✅ LLaMA-3 405B 集群案例 + GPT/LLaMA/Qwen/DeepSeek 四家对照 |
| ⑤使用方法借鉴 | ✅ 三个可直接抄的代码段：RMSNorm 实现、NTP Loss 错位对齐、完整训练循环 |

→ 相关：[[2026-04-19-处理大模型幻觉的工程心得]]、[[2026-04-12-Kronos-financial-kline-foundation-model]]

→ 相关：[[2026-08-17-曹原访谈评论-数学逻辑世界与物理世界-AI距离科学发现还有多远]]（能力边界视角，与本篇工程链路互补）
