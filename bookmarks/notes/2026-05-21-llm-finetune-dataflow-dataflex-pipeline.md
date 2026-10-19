# LLM 微调数据管线：DataFlow + LlamaFactory + DataFlex 全链路

来源：微信公众号（DataFlow / DataFlex 技术团队）
链接：https://mp.weixin.qq.com/s/zj7dO7CEpuMSrcX4f5P-JQ
日期：2026-05-21
评分：⭐4/5
标签：#LLM微调 #数据管线 #DataFlow #DataFlex #LlamaFactory #SFT #LoRA
关联：[2026-05-21-react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md)

---

## 摘要

文章提出了 LLM 微调的核心痛点不在训练而在数据准备，并介绍了三个开源项目组成的完整工具链：DataFlow（数据生产）→ LlamaFactory（模型训练）→ DataFlex（数据动态优化）。核心思想是将数据准备从"写一堆临时脚本"变成"组装可复用的流水线"，通过算子化设计和标准 JSON 格式衔接各环节。

## 核心内容

### 痛点拆解

1. **数据准备是最大瓶颈**：解析→清洗→切分→生成样本→格式对齐，每换数据源重来一遍
2. **格式适配地狱**：Alpaca 三字段、ShareGPT 列表结构、CoT 标签包裹——格式错直接导致 loss 异常
3. **多数据源混合盲调**：医疗/法律/通用数据混训，最优配比只能反复实验逼近，无显式解

现有工具的单点局限：

| 工具类型 | 代表 | 缺什么 |
|---------|------|--------|
| 数据清洗 | Nemo-Curator, Data-Juicer | 面向预训练语料，不支持"PDF → QA 对 → Alpaca JSON" |
| 训练框架 | LlamaFactory, Axolotl | 假设数据已准备好，不管"原始文档到训练数据"的 gap |
| 数据策略 | DoReMi, LESS | 论文效果好但工程门槛高，需深改训练器 |

### DataFlow：数据生产流水线

**GitHub**: OpenDCAI/DataFlow (3.8k⭐)

算子（Operator）设计——每步处理封装为独立算子，通过统一存储层传递数据。替换某环节只换对应算子。

**内置流水线**：
- 文本处理：纯文本 → QA 对（SFT 训练）
- 知识库清洗：PDF/Word → 结构化知识
- 推理增强：QA 对 → CoT 推理链
- Agentic RAG：生成需外部工具调用的训练数据
- Text2SQL：自然语言 → SQL 查询

**四步处理流程**（以文本/PDF → SFT 数据为例）：

1. **文本切分**：按 token 数/语义边界切 chunk
2. **知识清洗**：LLM 去噪（广告/导航/格式噪声），用 `<cleaned_start>/<cleaned_end>` 标签提取
3. **QA 生成**：LLM 生成结构化问答对，含 reasoning_steps、supporting_facts、领域标签
4. **格式转换**：QA → Alpaca/ShareGPT 格式 JSON + dataset_info.json

**关键设计决策**：用 LLM 生成训练数据，不是 ETL 数据搬运。文本切分清洗只是前置工序，QA 生成才是价值产出环节。

**DataFlow-Skills**：通过结构化 Skills 把编排能力交给 Agent（Claude Code、Cursor），自然语言描述 → 自动生成流水线。

CLI 一键流程：
```bash
dataflow text2model init    # 初始化
dataflow text2model train   # 全流程（含 LlamaFactory 训练）
dataflow pdf2model train    # PDF 输入变体
dataflow chat               # 训练后测试
```

### LlamaFactory：模型训练

**衔接方式**：纯数据格式约定（标准 JSON + dataset_info.json），无 API/服务依赖。

训练配置自动生成（.cache/train_config.yaml），覆盖模型选择、微调方法、数据集指向、超参。

**Template 层亮点**：不同模型的对话模板差异统一封装。配置 `template: qwen` 即自动处理所有格式细节。

### DataFlex：动态数据策略

**GitHub**: OpenDCAI/DataFlex (696⭐)

**核心理念**：把数据调度从"训练前静态决策"变成"训练中动态优化"。

三种策略：

| 策略 | 算法 | 做什么 |
|------|------|--------|
| Dynamic Select | LESS, NICE, Delta Loss | 评估样本价值，优先学习困难样本 |
| Dynamic Mix | DoReMi, ODM | 多数据源动态调比例（初期通用→后期领域） |
| Dynamic Weight | 样本级 loss 加权 | 反向传播时给不同样本不同权重 |

**运行时注入设计**（不需要 fork LlamaFactory）：
- 替换参数类：扩展训练参数，加 DataFlex 配置项
- 替换训练器：默认 Trainer → SelectTrainer/MixTrainer/WeightTrainer
- 替换数据加载器：支持多数据源动态采样

**实验数据**（SlimPajama-627B 子集）：

| 设置 | 方法 | MMLU | PPL |
|------|------|------|-----|
| Slim-Pajama-6B | 基线 | 25.27 | 4.217 |
| Slim-Pajama-6B | DoReMi | 25.84 | 4.134 |
| Slim-Pajama-6B | ODM | 26.04 | — |
| Slim-Pajama-30B | 基线 | 25.51 | 3.584 |
| Slim-Pajama-30B | DoReMi | 25.97 | — |
| Slim-Pajama-30B | ODM | — | 3.429 |

幅度不算夸张，但方向一致：准确率提升 + 困惑度下降。

**DoReMi 动态混合流程**：
1. 预热：用初始比例跑若干步
2. 评估：根据各域 loss 差异计算新比例
3. 重建：按新比例重采样，创建新 DataLoader
4. 训练：继续若干步
5. 循环 2-4 直到结束

关键技术细节：每个样本打 domain_id 标签，MixTrainer 按域权重对 loss 加权。

## 关键概念

- **算子（Operator）**：DataFlow 的基本处理单元，有明确的输入输出契约，可独立替换
- **DataFlow-Skills**：将数据编排能力暴露给 Agent 的结构化接口
- **运行时注入**：DataFlex 通过 Python 模块系统在启动时替换 LlamaFactory 组件，不修改源码
- **domain_id 标签**：标识样本来源，在 loss 计算时用于按域加权

## 能力边界

1. **QA 质量依赖 LLM**：LLM 生成的 QA 对可能含幻觉，文章未讨论质量验证机制
2. **实验规模偏小**：验证实验在 SlimPajama 子集上，提升幅度 0.5-0.8 MMLU 点，大规模效果待验证
3. **动态策略的计算开销**：预热+周期性评估比例额外消耗训练资源
4. **Agentic RAG 数据管线**：只提了名字，没展开细节

## 最佳实践

1. **中间产物可检视**：raw_chunk → cleaned_chunk → QA_pairs 全链路可检查，不是黑盒
2. **算子化复用**：换 LLM/切分策略只需替换单个算子
3. **标准格式衔接**：各环节通过 JSON 格式解耦，可独立使用或组合
4. **运行时注入而非 fork**：不改上游代码，兼容性好

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 算子化数据管线 | DataFlow 把数据准备封装为可替换算子 | Hermes 的 skill 系统本身就是算子化设计，可借鉴 DataFlow 的数据算子模式构建 agent 训练数据管线 | 设计 data-pipeline skill 模板，每个处理步骤 = 一个 skill |
| 2 | DataFlow-Skills Agent 编排 | 自然语言 → Agent 自动生成流水线 | 与 Hermes 的 skill 系统天然契合，可将数据处理 skill 暴露给 subagent 自动编排 | 在 skill frontmatter 中加 pipeline_hint 字段 |
| 3 | 动态数据混合 | DoReMi 周期性调比例，domain_id 加权 | 多任务微调场景（如 Hermes 的多角色模型）可直接用 DataFlex 做训练数据优化 | 下次做模型微调时引入 DataFlex 做 dynamic mix |
| 4 | 中间产物可检视 | raw_chunk → cleaned_chunk → QA_pairs 全链路 | 类似 context-compressor skill 的理念：每步有可检查的中间输出 | 在数据处理 skill 中强制要求中间产物落盘 |
| 5 | 运行时注入 | 不 fork LlamaFactory，Python 模块替换 | 借鉴到 Hermes 插件系统：不改核心代码，通过模块注入扩展功能 | 已有类似模式（toolset），可进一步标准化 |

## 🔗 RAG / Wiki 联动

### 当前状态
- LLM 微调数据管线知识已有笔记：[2026-05-21-react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md) 覆盖了 GLM-5 的 agentic RL 训练全链路
- 本笔记补充了 **数据准备和 SFT 阶段** 的工程工具链

### 改进方案
1. 与 ReAct Agent 笔记互补：GLM-5 报告侧重 RL 训练阶段，本文侧重 SFT 数据准备阶段
2. DataFlow 的 Agentic RAG 流水线与 Hermes agent 系统有直接借鉴关系

### 已执行操作
- ✅ MD 笔记已写入
- ⏳ HTML 待生成
- ✅ index.md 已更新


## 相关笔记
- [[2026-05-18-Fine-Tuning理论与实践-从理论基础到2026全景.md]]
- [[2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md]]
- [[2026-05-17-LoRA高效微调前沿技术全景.md]]
- [[2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md]]
