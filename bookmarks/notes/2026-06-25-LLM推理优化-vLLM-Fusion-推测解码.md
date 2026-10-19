# LLM 推理优化 2026 全栈 — vLLM Fusion 路由、推测解码与生产部署

> 学习日期：2026-06-25 | 来源：vLLM Blog 2026-06-16 / Red Hat Developer 2026-06-12 / vLLM Docs
> 学习模式：夜间自学习 | 主题：LLM 推理优化与部署

---

## 核心发现（5 条）

### 1. vLLM Semantic Router Fusion：混合模型面板路由（Mixture-of-Models）

**发布**：vLLM Blog, 2026-06-16 | **核心论点**：模型质量不仅取决于 checkpoint，也取决于围绕它的服务系统

**Fusion 四阶段模式（Panel-Judge-Synthesis-Trace）**：
1. **Panel** — 多个模型独立生成候选答案（快/便宜/私有/推理模型可混搭）
2. **Judge** — 评判模型分析一致点、矛盾点、部分覆盖、独特洞见、盲区
3. **Synthesis** — 合成调用返回最终答案
4. **Trace** — 完整记录参与模型和决策路径，支持事后调试

**关键设计**：Fusion 是**路由策略**而非全局端点，运营者可决定哪些请求走 Fusion。

### 2. 推测解码（Speculative Decoding）：7 种方法生产化部署

**来源**：Red Hat Developer + vLLM Docs | **性能**：代码生成/结构化输出最高 **3x+ 加速**

| 方法 | 原理 | 适用场景 | 优势 |
|------|------|---------|------|
| **EAGLE** | 从隐藏状态训练 draft head | 通用加速 | 最优加速比 |
| **MTP** | 模型自带 Multi-Token Prediction | DeepSeek/Gemma 等 | 零额外训练 |
| **Draft Model** | 独立小模型预测 | 有配套小模型时 | 灵活 |
| **PARD** | 并行 Draft Model | 降低 draft 延迟 | 高吞吐 |
| **MLP** | 多层感知机预测 | 轻量级部署 | 低内存 |
| **N-Gram** | 统计 N-gram 预测 | 代码/结构化输出 | **零训练，无需 GPU** |
| **Suffix Decoding** | 后缀树匹配 | Agent 代码/重复模式 | **对 Agent 场景 4x 加速** |

**数学保证**：无损（输出分布与纯自回归完全等价）。

### 3. N-Gram 和 Suffix Decoding：零训练加速的颠覆性价值

这两种方法**不需要 GPU、不需要训练、不需要额外模型**——纯粹基于统计模式匹配：
- **N-Gram**：维护 token 序列统计表，基于上下文预测下一个 token
- **Suffix Decoding**：构建后缀树，匹配已见过的完整输出片段
- **Agent 工作流**（工具调用 JSON schema、函数签名高度重复）是 Suffix Decoding 的理想场景

### 4. vLLM 2026 其他重要进展

| 日期 | 发布 | 意义 |
|------|------|------|
| 2026-06-05 | vLLM SR v0.3 Themis | 从信号到有状态生产路由，支持会话连续性、隐私安全策略 |
| 2026-06-09 | vime | 简洁稳定的 LLM 强化学习框架 |
| 2026-06-10 | DiffusionGemma | 首个原生支持的 Diffusion LLM (dLLM) |
| 2026-06-12 | MiniMax M3 | Day-0 支持 1M-token 多模态推理 |

### 5. 推测解码方法选择决策树

```
有 GPU 训练能力？
├─ 是 → EAGLE（最优加速比）
│       模型自带 MTP 头？
│       └─ 是 → MTP（零额外训练）
└─ 否
    ├─ 输出高度重复（代码/Agent）？ → Suffix Decoding 或 N-Gram（零训练）
    ├─ 有配套小模型？ → Draft Model
    └─ 需要最低延迟？ → PARD（并行 draft）
```

---

## 技术细节

### Fusion 配置示例

```yaml
entrypoint:
  model: "vllm-sr/fusion"   # 限定匹配 Fusion 决策
  panel:
    - "qwen2.5-72b"          # 强推理
    - "llama-3.3-70b"        # 冗余确认
    - "deepseek-v3"          # 代码专长
  judge: "gpt-4o-mini"       # 低成本评判
  synthesis: "qwen2.5-72b"   # 最终合成
  trace: true                # 全路径记录
```

### 生产性能基准

| 场景 | 加速比 | 条件 |
|------|--------|------|
| 代码生成 | 3x+ | 可预测负载 |
| 结构化输出 | 3x+ | 重复模式 |
| Agent 工具调用 | 4x | Suffix Decoding |
| decode-heavy 负载 | 3x | AWS Trainium + vLLM + Qwen3 |

**关键约束**：draft 和 target 必须共享 tokenizer 和词表。

---

## 对 Hermes Agent 的应用价值

| 优先级 | 改进项 | 说明 |
|--------|--------|------|
| **P1** | 推测解码本地部署 | Jetson Orin 本地模型启用 N-Gram/Suffix Decoding，零训练成本加速 Agent 代码生成 |
| **P1** | 模型 failover 升级 | antigravity-model-failover 结合 SR Fusion，高价值任务多模型面板交叉验证 |
| **P2** | 成本优化路由 | 简单请求 → 快模型，复杂请求 → Fusion 面板，model-switch Skill 自动决策 |
| **P2** | Suffix Decoding + Agent | Agent 工具调用格式高度重复（JSON schema），是 Suffix Decoding 的理想场景 |

---

## 相关笔记

- [2026-06-23-vLLM-Semantic-Router-Fusion-混合模型路由与推测解码](./explore/2026-06-23-vLLM-Semantic-Router-Fusion-混合模型路由与推测解码.md)
- [2026-06-14-LLM推理优化2026全栈指南-量化推测解码KV缓存](./explore/2026-06-14-LLM推理优化2026全栈指南-量化推测解码KV缓存.md)
- [2026-06-11-ReasonAlloc推理模型KV-Cache预算分配](./explore/2026-06-11-ReasonAlloc推理模型KV-Cache预算分配.md)
