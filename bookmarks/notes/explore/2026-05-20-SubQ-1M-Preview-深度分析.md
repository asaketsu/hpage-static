# SubQ 1M-Preview：首个商用亚二次复杂度 LLM 深度分析

> 📅 2026-05-20 | 🏷️ LLM架构, 长上下文, 亚二次复杂度, SSA, 效率革命
> 来源：VentureBeat, DataCamp, 新浪科技, 网易, Reddit, subq.ai

---

## 摘要

2026年5月5日，迈阿密初创公司 Subquadratic 走出隐身模式，发布全球首个商用亚二次复杂度 LLM——**SubQ 1M-Preview**。该模型声称拥有**1200万 token 原生上下文窗口**，采用全新的**SSA（Subquadratic Sparse Attention，亚二次稀疏注意力）架构**，在1M token场景下比 FlashAttention 快 52 倍，成本不到 Claude Opus 的 5%。同日公司完成 2900 万美元种子轮，估值 5 亿美元。

这一发布标志着 LLM 行业从"规模竞赛"向"效率竞赛"的关键转折点。但社区对其技术宣称存在显著质疑，需要独立验证。

---

## 核心发现

### 1. SSA 架构：重新定义注意力计算

**传统 Transformer 的痛点**：
- 稠密注意力（Dense Attention）假设"任意一对 token 都可能重要"
- 每个 token 都要与其他所有 token 进行比较
- 注意力计算量随序列长度呈**二次方增长** O(n²)
- 128K token 已是工程极限，1M token 成本高昂

**SSA 的创新**：
- 去除"任意对都重要"的假设
- 通过**内容相关的选择机制**，将注意力路由到真正重要的位置
- 只在有信息量的位置上计算注意力，其余直接跳过
- 计算复杂度从 O(n²) 降至**线性 O(n)**
- 12M token 时注意力 FLOPs 降低近 **1000 倍**

### 2. 性能基准：亮眼但需验证

| 基准测试 | SubQ 1M-Preview | Claude Opus 4.7 | GPT-5.5 | Gemini 3.1 Pro |
|---------|-----------------|-----------------|---------|----------------|
| RULER 128K | 95.0% | 94.8% | - | - |
| SWE-Bench Verified | 81.8% | 80.8% | - | 80.6% |
| MRCR v2 (研究版) | 83 | 32.2 | 74.0 | 26.3 |
| MRCR v2 (生产版) | 65.9 | - | - | - |

**关键解读**：
- RULER 128K 与 Opus 4.6 几乎打平，证明长上下文基础能力达标
- SWE-Bench 超过 Opus 4.6，显示代码理解能力
- MRCR v2 是**最关键测试**：考察长上下文多源证据检索整合能力
  - 研究版 83 远超 Opus 4.7 的 32.2
  - 生产版 65.9 仍显著领先
  - 但生产版与研究版差距较大（65.9 vs 83），需关注

### 3. 实际速度优势

| 上下文长度 | 相对 FlashAttention-2 加速 |
|-----------|---------------------------|
| 128K | 7.2× |
| 256K | 13.2× |
| 512K | 23× |
| 1M | 52.2× |

**吞吐反转现象**：随着上下文长度增加，稠密注意力相对 SSA 会变得更慢。SSA 的优势在长上下文工作负载最有价值的区间内不断扩大。

### 4. 商业模式与生态

- **基于开源模型微调**：CTO 确认不从头训练，而是基于 DeepSeek 或 Kimi 等开源模型
- **种子轮 2900 万美元，估值 5 亿美元**：资本看好长上下文赛道
- **API 可用**：声称成本仅为前沿模型的 1/5

---

## 技术细节

### SSA 工作原理

```
传统 Dense Attention:
  每个 token → 与所有其他 token 比较 → 计算注意力权重 → 聚合
  复杂度: O(n²)

SSA Subquadratic Sparse Attention:
  每个 token → 内容相关路由 → 选择关键位置 → 仅计算重要交互
  复杂度: O(n)
```

**关键设计**：
1. **基于内容的路由能力**：模型根据语义决定"去哪里看"，不依赖位置模式
2. **检索能力**：无论关键信息出现在何处，都能被检索到
3. **线性扩展**：上下文翻倍 → 计算成本仅翻倍，而非四倍

### 与现有技术的对比

| 技术 | 内存复杂度 | 计算复杂度 | 备注 |
|-----|-----------|-----------|------|
| 标准 Dense Attention | O(n²) | O(n²) | 原始 Transformer |
| FlashAttention | O(n) | O(n²) | 线性内存但计算仍二次 |
| FlashAttention-2 | O(n) | O(n²) | 优化实现 |
| FlashAttention-3 | O(n) | O(n²) | B200 优化，无额外加速 |
| SSA (SubQ) | O(n) | O(n) | 真正线性 |

**重要澄清**：清华大学交叉信息研究院博士指出，"计算和内存上都是线性扩展"这一特性并非 SSA 独有——FlashAttention 早已实现线性内存，是业界标配。SubQ 的真正创新在于**计算复杂度**的线性化。

---

## 疑点与争议

### 1. 技术来源质疑

前 OpenAI Sora 团队成员 Will Depue 质疑：
> "SubQ 几乎可以肯定是对 Kimi 或 DeepSeek 稀疏注意力（sparse attention）的微调。"

CTO 随后部分证实：
> "我们确实将开源模型的权重作为起点，这是基于我们目前的资金规模和公司发展阶段做出的选择。"

**这意味着**：SSA 可能是对现有稀疏注意力机制的改进，而非完全原创架构。

### 2. 历史教训：Magic.dev 的 LTM-2-mini

2024年8月，旧金山公司 Magic.dev 发布 LTM-2-mini：
- 宣称 1 亿 token 上下文窗口
- 声称相对标准注意力 1000 倍效率优势
- 累计融资超过 5 亿美元

**但到 2026 年初**：
- 没有任何 Magic 之外的开发者或企业公开使用记录
- 技术报告没出
- 模型没开源
- Benchmark 没有第三方复现

**警示**：长上下文赛道存在"PPT 发布→融资→无人使用"的风险模式。

### 3. 需要独立验证的关键宣称

| 宣称 | 验证状态 | 风险等级 |
|-----|---------|---------|
| 12M token 原生上下文 | 未独立验证 | 🔴 高 |
| 1M token 52× 加速 | 未独立验证 | 🔴 高 |
| 成本为 Opus 的 5% | 未独立验证 | 🟡 中 |
| MRCR v2 65.9 | 第三方验证（生产版） | 🟢 低 |
| RULER 128K 95.0% | 第三方验证 | 🟢 低 |

---

## 对工作的价值

### 1. 长期文档处理的可能性

如果 SSA 技术得到验证，将彻底改变：
- **代码库分析**：整个项目代码库作为上下文
- **法律文档**：完整合同、法规文本一次性处理
- **科研文献**：整本书籍、论文合集作为输入
- **日志分析**：TB 级系统日志统一分析

### 2. 成本优化方向

当前长上下文成本结构：
```
1M token 稠密注意力 ≈ Claude Opus 价格
1M token SSA (SubQ) ≈ Opus 价格的 5%
```

对于 Hermes Agent 的长文档处理场景，如果 API 可用，可大幅降低：
- 知识库检索成本
- 长文档摘要成本
- 多文档对比分析成本

### 3. 技术借鉴

SSA 的核心思想——**内容相关的路由机制**——可迁移到：
- **Agent 工具选择**：根据任务语义路由到最合适的工具
- **上下文压缩**：识别并保留关键信息，跳过冗余
- **技能调度**：动态选择最相关的 Skill 而非全量加载

---

## 行动建议

### 短期（1-2 周）

1. **关注 API 可用性**：等待 SubQ API 开放，申请测试额度
2. **验证宣称**：用已知长文档测试集验证 RULER/MRCR 分数
3. **对比测试**：与现有长上下文方案（Kimi、DeepSeek）对比

### 中期（1-3 月）

4. **技术调研**：深入研究 SSA 论文（如有发布）
5. **开源追踪**：关注是否有开源版本或权重泄露
6. **竞品监控**：跟踪其他公司对亚二次架构的跟进

### 长期（3-6 月）

7. **架构借鉴**：将 SSA 的"内容路由"思想应用到 Agent 系统
8. **成本评估**：如果验证成功，规划长上下文工作流重构
9. **生态参与**：关注 Subquadratic 社区，参与早期采用

---

## 知识缺口

| 缺口 | 获取方式 | 优先级 |
|-----|---------|-------|
| SSA 技术论文 | 等待官方发布 | 🔴 高 |
| 独立第三方基准 | 关注 HuggingFace/OpenCompass | 🔴 高 |
| API 定价与限流 | 等待官方文档 | 🟡 中 |
| 开源权重 | 关注 HuggingFace | 🟡 中 |
| 实际生产案例 | 等待用户反馈 | 🟢 低 |

---

## 参考来源

- [VentureBeat: SubQ claims 1,000x efficiency gain](https://venturebeat.com/technology/miami-startup-subquadratic-claims-1-000x-ai-efficiency-gain-with-subq-model-researchers-demand-independent-proof)
- [SubQ 官方博客: Introducing SubQ](https://subq.ai/introducing-subq)
- [DataCamp: SubQ AI Explained](https://www.datacamp.com/blog/subq-ai-explained)
- [新浪科技: 领先于Transformer！新架构首个1200万上下文模型](https://finance.sina.com.cn/tech/roll/2026-05-06/doc-inhwxtah8384329.shtml)
- [网易: 号称1200万token上下文的模型来了，数据亮眼但疑点重重](https://www.163.com/dy/article/KS9AJL5P05119734.html)
- [Reddit 讨论](https://www.reddit.com/r/ArtificialInteligence/comments/1t4nxcd/subq_just_blew_my_mind_12m_token_context_with/)

---

## 进化标记

- **新工具/API**：SubQ API（待验证）→ 标记为 L4 探索
- **新技术**：SSA 亚二次稀疏注意力 → 需深入理解
- **风险模式**：长上下文"PPT 发布"陷阱 → 需警惕
- **可借鉴思路**：内容相关路由机制 → 可迁移到 Agent 系统

## 相关笔记
- [2026年5月AI模型密集发布](explore/2026-05-17-2026年5月AI模型密集发布.md)
