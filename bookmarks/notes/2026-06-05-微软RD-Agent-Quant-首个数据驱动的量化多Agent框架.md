# 微软 RD-Agent-Quant：首个数据驱动的量化多 Agent 框架

> 📅 2026-06-05 | 夜间自学习
> 🔗 来源：GitHub microsoft/RD-Agent + arXiv:2505.15155 (NeurIPS 2025) + arXiv:2603.01712 (ICML 2026) + arXiv:2603.01692 (ACL 2026 Findings)
> 🏷️ 关键词：RD-Agent、量化交易、因子挖掘、多 Agent 框架、因子-模型联合优化、MLE-bench、LLM 自动化研发

---

## 一、核心突破

### 1.1 R&D-Agent 是什么

微软 R&D-Agent 是一个 **自动化 AI 研发引擎**，核心目标是让 AI 驱动数据驱动的 AI——自动完成从想法提出（R）到代码实现（D）的全闭环。

其量化金融子产品 **RD-Agent(Q)** 是 **首个数据驱动的量化多 Agent 框架**，实现因子-模型联合优化。

### 1.2 核心成果

| 指标 | 结果 |
|------|------|
| 论文发表 | NeurIPS 2025（主会） |
| 因子效率 | 比基准因子库高 **2× ARR**，使用 **70% 更少因子** |
| 资源对比 | 超越 SOTA 深度时序模型，且资源预算更小 |
| MLE-bench 排名 | **第一名**（超越 OpenAI AIDE） |
| 单次成本 | 低于 **$10** |
| 后续论文 | ICML 2026（FT-Dojo）+ ACL 2026 Findings（Reasoning as Gradient） |

---

## 二、架构设计

### 2.1 R + D 双 Agent 模式

```
R Agent（Research）     →  提出新想法、阅读论文、生成因子假设
                         ↓
D Agent（Development）  →  实现想法、编写代码、运行回测
                         ↓
Co-STEER 循环           →  从数据中学习，迭代优化
```

**关键创新**：不是单 Agent 一次完成，而是 R 和 D 双 Agent 交替迭代，每次循环从数据和结果中学习（Co-STEER）。

### 2.2 因子-模型联合优化（Factor-Model Co-optimization）

传统量化流水线：因子挖掘 → 模型训练（两步独立）

RD-Agent(Q) 的创新：**交替优化因子和模型**

```
Round 1: 生成初始因子 → 训练模型 → 评估
Round 2: 基于模型反馈优化因子 → 重新训练 → 评估
Round N: ...直到收敛
```

这种交替优化在预测准确性和策略鲁棒性之间取得了优秀平衡。

### 2.3 Co-STEER 机制

**Co**operative **S**elf-**T**uning **E**volution with **E**xperienced **R**easoning：

1. **经验积累**：每轮迭代的成功/失败经验被记录
2. **知识提取**：从经验中提取可复用的模式
3. **推理引导**：用已有知识指导下一轮的因子生成
4. **自我调优**：根据反馈自动调整策略参数

---

## 三、量化场景实战

### 3.1 因子挖掘流水线

RD-Agent(Q) 的因子挖掘流程：

1. **论文理解**：自动阅读金融研究论文，提取可量化化的因子假设
2. **因子生成**：基于假设生成 Python 因子代码
3. **回测验证**：在真实股票数据上运行回测
4. **性能评估**：计算 IC（信息系数）、IR（信息比率）、换手率等指标
5. **迭代优化**：基于评估结果修改因子公式

### 3.2 研究助手功能

- **论文阅读**：自动解析金融论文，提取模型结构和因子公式
- **财报解读**：从金融报告中提取可量化的信号
- **代码实现**：将论文中的数学公式转化为可执行代码

### 3.3 性能数据

| 方法 | ARR | 因子数量 | 资源预算 |
|------|-----|---------|---------|
| 基准因子库 | 1.0× | N/A | N/A |
| SOTA 深度时序 | <2.0× | - | 高 |
| **RD-Agent(Q)** | **~2.0×** | **70%更少** | <$10 |

---

## 四、MLE-bench 王者

### 4.1 排名对比

| Agent | Lite (%) | Medium (%) | High (%) | All (%) |
|-------|----------|------------|----------|---------|
| **RD-Agent o3(R)+GPT-4.1(D)** | **51.52 ± 6.9** | **19.3 ± 5.5** | **26.67 ± 0** | **30.22 ± 1.5** |
| RD-Agent o1-preview | 48.18 ± 2.49 | 8.95 ± 2.36 | 18.67 ± 2.98 | 22.4 ± 1.1 |
| AIDE o1-preview | 34.3 ± 2.4 | 8.8 ± 1.1 | 10.0 ± 1.9 | 16.9 ± 1.1 |

**关键洞察**：o3 做研究（R）+ GPT-4.1 做开发（D）的组合效果最佳。将推理强模型用于高层规划，将编码强模型用于实现——这验证了 R+D 分离的架构优势。

### 4.2 成本优化策略

RD-Agent 支持混合模型配置：
- **Research Agent**：使用强推理模型（o3）——需要深度思考和创意生成
- **Development Agent**：使用编码专精模型（GPT-4.1）——需要代码生成和调试
- 通过 LiteLLM 后端灵活切换模型提供商

---

## 五、技术栈与部署

### 5.1 技术要求

- **平台**：仅 Linux
- **Python**：3.10 / 3.11（CI 测试通过）
- **Docker**：必需（用于隔离执行环境）
- **LLM 后端**：通过 LiteLLM 支持 OpenAI / Azure / DeepSeek 等

### 5.2 安装

```bash
conda create -n rdagent python=3.10
conda activate rdagent
pip install rdagent
```

### 5.3 配置

支持多模型后端配置：

```bash
# OpenAI
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# DeepSeek（成本优化）
CHAT_MODEL=deepseek/deepseek-chat
DEEPSEEK_API_KEY=xxx

# Embedding 可用 SiliconFlow
EMBEDDING_MODEL=litellm_proxy/BAAI/bge-m3
LITELLM_PROXY_API_BASE=https://api.siliconflow.cn/v1
```

### 5.4 Web UI

提供实时交互界面：
- `rdagent server_ui` 启动前端
- 实时查看因子生成过程和回测结果
- 追踪完整的执行轨迹

---

## 六、论文发表与学术影响

RD-Agent 的研究成果密集发表在顶级会议：

| 论文 | 会议 | 核心贡献 |
|------|------|---------|
| R&D-Agent-Quant (2505.15155) | **NeurIPS 2025** | 量化多 Agent 框架，因子-模型联合优化 |
| FT-Dojo (2603.01712) | **ICML 2026** | 自主 LLM 微调，benchmark 驱动的领域适应 |
| Reasoning as Gradient (2603.01692) | **ACL 2026 Findings** | 将推理轨迹视为梯度，优化 Agent 学习 |

**学术趋势**：从"LLM 辅助量化"走向"LLM 自主完成量化研发全流程"。

---

## 七、对 Hermes 量化系统的启示

### 7.1 与现有 Skill 的对比

| 维度 | Hermes 量化 Skill | RD-Agent(Q) |
|------|------------------|-------------|
| 因子生成 | 手动编写 / i问财自然语言 | LLM 自动生成 + 迭代优化 |
| 因子评估 | 单次回测 | 多轮交替优化 |
| 模型训练 | 固定流程 | 因子-模型联合优化 |
| 研究辅助 | 无 | 自动论文阅读 + 公式提取 |
| 成本 | 高（人工） | <$10/轮 |

### 7.2 可借鉴的设计模式

1. **R+D 双 Agent 模式**：将因子研究（R）和因子实现（D）分开，用不同模型处理
   - Hermes 可将现有的 `agentic-alpha-research`（R）与 `quant-ml-pipeline`（D）串联
   - R 用强推理模型，D 用编码模型

2. **Co-STEER 闭环**：每轮迭代记录成功/失败经验
   - 在 `exchange-protocol` 的经验池中追加因子研究经验
   - 用统计聚合（深层洞察发现）替代简单取最新

3. **因子-模型联合优化**：当前 Hermes 的因子挖掘和模型训练是独立的
   - 引入交替优化：模型反馈 → 因子调整 → 重新训练

4. **LiteLLM 后端**：RD-Agent 的多模型配置模式
   - Hermes 的 `model-adapter` Skill 可借鉴此模式

### 7.3 落地路径

**Phase 1**（1 周）：
```bash
pip install rdagent
# 在 jc-server 上部署 RD-Agent
# 测试量化因子自动生成流水线
```

**Phase 2**（2 周）：
- 将 RD-Agent(Q) 的因子生成能力集成到 Hermes 量化 Skill
- 用 Hermes 的 cron 任务驱动每日因子迭代

**Phase 3**（1 月）：
- 引入因子-模型联合优化
- 建立因子经验库（复用 exchange-protocol 的 JSONL 经验池）

---

## 八、知识缺口与后续探索

1. **RD-Agent 在 A 股市场的适配**：当前论文主要在美股验证，A股的 T+1/涨跌停板/因子失效模式需要额外适配
2. **与 i问财的集成**：RD-Agent 的因子生成能否与 i问财的自然语言选股互补？
3. **因子过拟合防控**：2× ARR 在实盘中的可持续性如何？Walk-Forward 验证的适用性
4. **Jetson Orin 本地部署**：RD-Agent 的 LLM 推理开销在边缘设备上的可行性
5. **多策略组合**：RD-Agent 生成的因子如何与现有均线/动量策略组合？

---

## 九、参考资料

- [GitHub: microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) — 完整源码和文档
- arXiv:2505.15155 — R&D-Agent-Quant (NeurIPS 2025)
- arXiv:2603.01712 — FT-Dojo: Autonomous LLM Fine-Tuning (ICML 2026)
- arXiv:2603.01692 — Reasoning as Gradient (ACL 2026 Findings)
- [RD-Agent Live Demo](https://rdagent.azurewebsites.net/) — 因子挖掘在线演示
- [RD-Agent Documentation](https://rdagent.readthedocs.io/) — 完整技术文档
- [MLE-bench 排名详情](https://aka.ms/RD-Agent_MLE-Bench_O3_GPT41) — 基准测试


## 相关笔记
- [[2026-05-31-LLM量化交易前沿-Agent评估与Alpha因子|LLM量化交易前沿-Agent评估与Alpha因子]]
- [[2026-04-29-LLM-Agent驱动量化交易系统前沿学习|LLM-Agent驱动量化交易系统前沿学习]]
- [[2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统|stoc蒸馏-AI-Agent自学习量化交易系统]]
- [[2026-04-24-通达信tdxquant量化模拟交易封装|通达信tdxquant量化模拟交易封装]]
- [[2026-04-30-Meta-Hyperagents自适应Agent框架|Meta-Hyperagents自适应Agent框架]]
