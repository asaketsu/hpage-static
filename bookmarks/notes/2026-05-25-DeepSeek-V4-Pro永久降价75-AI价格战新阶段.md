# DeepSeek V4-Pro 永久降价 75%：AI 价格战进入绞肉机阶段

> **来源**：Reuters · Engadget · SCMP · HN #48237663 · 2026-05-23
> **原文**：https://finance.yahoo.com/sectors/technology/articles/chinas-deepseek-permanent-75-price-133313757.html
> **笔记ID**：sniff-20260525-deepseek-v4-price-war
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[Anthropic首度盈利](2026-05-22-Anthropic首度盈利-击碎AI泡沫论.md) [AI编码工具战争](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)

## 摘要

2026年5月23日，DeepSeek 宣布将旗舰模型 V4-Pro 的 75% 促销降价永久化，API 价格降至原来的 1/4。V4-Pro 是 1.6 万亿参数 MoE 模型，支持 100 万 token 上下文，Think Max 模式下性能对标 GPT-5.4 和 Claude Opus 4.6。价格调整后，输入 token 低至 $0.003625/M，比西方同类模型便宜 35-100 倍。这一举措将 AI 价格战推入新阶段，迫使竞争对手重新审视定价策略。

## 核心内容

### 1. 降价详情

降价前后的价格对比：
  输入 token：$0.0145/M → $0.003625/M（75% off）
  输出 token：$3.48/M → $0.87/M（75% off）
  缓存命中：低至 $0.003625/M
  人民币定价：0.025-6 元/百万 token（原 0.1-24 元）

DeepSeek 明确表示促销到期后（2026/05/31 UTC）不会恢复原价，而是将折扣价定为正式价格。

### 2. V4-Pro 模型规格

1.6 万亿参数 MoE（Mixture of Experts）架构
100 万 token 上下文窗口
Think Max 模式下对标 GPT-5.4、Claude Opus 4.6
定位：推理、编码、长程 Agent 工作流
已开源权重（open-weight）

### 3. 背后的算力支撑

DeepSeek 未明确是否因华为 Ascend 950 芯片供应增加而降价，但声明预计下半年华为 Ascend 950 超节点大规模量产后，Pro 定价还将进一步下降。这暗示国产芯片替代正在取得实质进展。

### 4. 行业影响

  Anthropic 此前指责 DeepSeek 进行"蒸馏攻击"（从 Claude 学习），但价格战已无法逆转
  Artificial Analysis 第三方评测确认 V4-Pro 在"每美元智能量"指标上全球领先
  全球算力供给紧张推高高端模型价格的背景下，DeepSeek 的降价策略形成鲜明对比
  中国 AI 公司走"极致性价比"路线 vs 美国"尖端能力+高价"路线

## 关键概念

**Token 经济学**：AI 模型的定价以百万 token 为单位，输入/输出/缓存命中各有不同费率。价格战的核心是降低每单位"智能"的成本。

**MoE（Mixture of Experts）**：通过稀疏激活专家子网络，大幅降低推理成本。DeepSeek V4-Pro 的 1.6T 参数中只有部分在每次推理时被激活。

**每美元智能量（Intelligence per Dollar）**：Artificial Analysis 提出的评测维度，衡量相同预算下能获得多少 AI 能力。

## 能力边界

  低价不等于低质量，但长期可持续性存疑：DeepSeek 的真实成本结构不透明
  开源权重 ≠ 开源：模型权重开放但训练数据和方法未公开
  地缘政治风险：美国出口管制可能影响华为 Ascend 芯片供应链
  蒸馏争议：Anthropic 的指控如果属实，说明低价部分建立在"学习"竞品输出的基础上

## 最佳实践

  企业用户应建立多模型价格监控机制，利用价格波动优化成本
  开发者可用 V4-Pro 处理高吞吐任务（批量分类、数据清洗），将复杂推理留给高端模型
  关注华为 Ascend 生态的成熟度，评估国产芯片替代的可行性

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 多级定价策略 | 缓存命中价 < 输入价 < 输出价，三级定价 | Hermes Gateway 可实现请求级成本优化：对重复查询自动路由到缓存或低价模型 | 在 gateway 配置中增加 price-aware routing 规则 |
| 2 | 开源权重的利用 | open-weight 模型可本地部署，进一步降低成本 | 评估 V4-Pro 本地部署可行性（需 Ascend 950 或等效 GPU） | 调研本地部署所需硬件和推理框架 |
| 3 | 价格战中的差异化 | DeepSeek 走性价比，Anthropic 走质量+安全 | Hermes 的 model-adapter skill 已有 provider 切换机制，可增加价格维度 | 在 model-adapter 中集成实时价格对比，自动选择最优性价比模型 |
| 4 | MoE 架构的效率启示 | 稀疏激活大幅降低推理成本 | Agent 系统可借鉴：不同复杂度任务激活不同"专家"skill 组合 | 设计 skill 激活的稀疏路由机制，避免每次请求加载所有 skill |
| 5 | 华为 Ascend 生态跟踪 | 国产芯片替代正在取得进展 | 关注国产 AI 芯片生态，为未来硬件采购提供参考 | 建立芯片生态追踪笔记标签 #国产芯片 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
  wiki-kb 已有 AI 商业化相关词条
  RAG 索引包含多篇 AI 定价和竞争格局笔记
  Memory 中记录了 Anthropic 盈利和 AI 基础设施军备竞赛

### 改进方案
1. 在 wiki-kb 中新增"Token经济学"专题页面，整合所有定价相关笔记
2. 更新 AI 竞争格局词条，加入 DeepSeek 降价事件时间线
3. 建立 model-adapter 的价格感知路由原型

### 已执行操作
- ✅ 笔记已写入 bookmarks/notes
- ⏳ wiki-kb 专题页面待下次会话创建

## 相关笔记
- [If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约](2026-05-22-If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约.md)
- [Multi-Stream-LLMs-并行流解锁语言模型](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
- [Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力](2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md)
- [OpenAI后训练团队Yann-Dubois深度访谈](2026-05-23-OpenAI后训练团队Yann-Dubois深度访谈.md)
- [QLoRA在RL训练中的精度影响-量化与强化学习深度解析](2026-05-23-QLoRA在RL训练中的精度影响-量化与强化学习深度解析.md)
- [VLM强化学习RL训练-视觉编码器与LoRA配置前沿](2026-05-24-VLM强化学习RL训练-视觉编码器与LoRA配置前沿.md)
- [nashsu-llm_wiki项目分析_deep-blue](2026-05-24-nashsu-llm_wiki项目分析_deep-blue.md)
- [DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现](2026-05-25-DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现.md)
- [VPO向量策略优化多样性训练提升推理搜索](explore/2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [antization-deploy-deep-20260524](explore/edge-llm-quantization-deploy-deep-20260524.md)
- [llm-inference-opt-2026-05-20-supplement](explore/llm-inference-opt-2026-05-20-supplement.md)
- [llm-inference-optimization-2026](explore/llm-inference-optimization-2026.md)
