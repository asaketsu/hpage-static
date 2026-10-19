# AlphaEvolve：DeepMind Gemini驱动的算法发现AI Agent

**来源**：Google DeepMind 官方博客 + Wikipedia + Medium | **日期**：2026-05-19 | **类型**：proactive-sniff

---

## 摘要

AlphaEvolve 是 Google DeepMind 在 2025 年 5 月发布的一个进化式编码 Agent，基于 Gemini 大语言模型，能够**自主发现和优化算法**。它结合了 LLM 的创造性问题求解能力和进化计算框架，在 50 个开放数学问题上，75% 重新发现了最优解，20% 发现了改进解。更重要的是，它已用于优化 Google 自身的 TPU 电路设计和 Gemini 训练矩阵乘法内核。

## 关键发现

### 1. 工作原理：LLM + 进化搜索
- **LLM 生成**：Gemini Flash（广度）+ Gemini Pro（深度）联合生成算法变体
- **自动评估器**：验证每个变体的正确性和性能
- **进化框架**：选择最优变体，迭代改进，形成"变异→评估→选择"闭环

### 2. 数学突破
- 在 50 个开放数学问题中：
  - **75%** 重新发现 SOTA（state-of-the-art）解法
  - **20%** 发现了**优于人类已知**的改进解法
  - 典型案例：推进了 kissing number problem（接触数问题）的求解

### 3. Google 内部应用
- **Borg 集群调度优化**：发现简单却高效的启发式算法，提升 Google 数据中心调度效率
- **TPU 电路设计优化**：自动化优化芯片电路布局
- **Gemini 训练内核优化**：改进矩阵乘法 kernel 性能

### 4. 开源社区响应
- AlphaEvolve 发布后，多个开源实现迅速涌现
- 表明算法发现 AI 已成为研究热点

## 对工作的价值

| 维度 | 影响 |
|------|------|
| **算法设计** | 未来可能用 AlphaEvolve 类工具辅助寻找更优算法，尤其适合组合优化、数学证明类问题 |
| **工程优化** | 芯片设计、调度算法、性能调优等场景可借鉴其"LLM+评估器"模式 |
| **AI 研究范式** | FunSearch → AlphaEvolve → 下一代：从"生成知识"到"发现知识"的演进路径清晰 |

## 行动建议

1. **关注后续进展**：DeepMind 已开放注册，后续可尝试在特定领域问题（如调度、路由、压缩）上验证效果
2. **借鉴架构**：LLM 生成 + 自动评估 + 进化选择 的模式可迁移到代码生成、测试用例生成等场景
3. **跟踪开源实现**：社区已有多个实现，适合本地化实验

## 相关笔记
- [Gemini图片风格复刻Prompt工作流](hermes-agent/2026-05-05-Gemini图片风格复刻Prompt工作流.md)
- [Google-AI被SEO操纵的调查报告](2026-05-21-Google-AI被SEO操纵的调查报告.md)
- [ai-coding-agent-competition-landscape](explore/2026-05-08-ai-coding-agent-competition-landscape.md)
- [Google-AI-Mode搜索广告-AI商业化的分水岭](2026-05-22-Google-AI-Mode搜索广告-AI商业化的分水岭.md)
- [competitor-ai-models-2026](explore/2026-05-05-competitor-ai-models-2026.md)
