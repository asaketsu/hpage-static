# LLM 推理优化 2026：量化、推测解码、KV缓存与生产引擎全景

> 来源：MorphLLM "LLM Inference Optimization" (2026)、CallSphere "Quantization, Speculative Decoding" (2026)、Google Cloud "Five Techniques"
> 日期：2026-06-13

---

## 一、为什么推理优化是核心战场

> "训练是一次性成本；推理是决定商业可行性的持续支出。"

### 现实数据

- API 价格 2025→2026 下降约 80%，GPT-4 级性能降至 **$0.40/M tokens**
- Agentic 工作流每个任务 50-200 次 LLM 调用，使 per-token 定价具有欺骗性
- 三个复合问题：上下文膨胀（turn 30 的 input tokens 是 turn 1 的 5-10×）、冗余计算、硬件利用率不足

---

## 二、模型层优化

### 2.1 量化（Quantization）

| 方法 | 位宽 | 质量损失 | 速度增益 | 内存减少 |
|------|------|---------|---------|---------|
| FP16（基线） | 16 | 无 | 1× | 1× |
| INT8 (W8A8) | 8 | 极小 | 1.5-2× | 2× |
| GPTQ (W4A16) | 4 | 小 | 2-3× | 4× |
| AWQ | 4 | 小 | 2-3× | 4× |
| GGUF Q4_K_M | 4 | 小 | 2-3× | 4× |
| QuIP# | 2 | 中等 | 4-5× | 8× |

**实际案例**：70B 模型 FP16 需 ~140GB（2×A100 80GB），4-bit 量化后可放入**单张 A100** 甚至消费级 RTX 4090（24GB）。

#### 2026 新突破

- **SmoothQuant**：将量化难度从激活迁移到权重 → 2× 内存减少，精度损失可忽略，速度提升 1.56×
- **TurboQuant**（Google，2026.03）：将 KV cache 压缩至 **3 bits/value**，零精度损失 → **6× KV cache 内存减少**

```bash
# llama.cpp 量化
./quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M

# vLLM AWQ 量化服务
python -m vllm.entrypoints.openai.api_server \
  --model TheBloke/Llama-3.3-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1
```

### 2.2 剪枝（Pruning）

- 结构化剪枝：移除整个注意力头/MLP 列
- 非结构化剪枝：将单个权重置零
- 剪枝后的 6B 模型比密集对应物快 **30%**，MMLU 得 72.5（超过未剪枝 4B 的 70.0）

### 2.3 知识蒸馏（Knowledge Distillation）

训练小"学生"匹配大"教师"输出分布。**最优流水线：P-KD-Q（剪枝→蒸馏→量化）**——每步效果叠加。

---

## 三、系统层优化

### 3.1 连续批处理（Continuous Batching）

- 每个生成步骤插入新请求、返回已完成请求
- **3-10× 吞吐提升**，Anyscale 生产环境测得 **23× 提升**
- 平均延迟降低 **50-80%**

### 3.2 PagedAttention 与 KV Cache 管理

传统 KV cache 为最大序列长度预分配内存，浪费高达 **90% GPU 内存**。

**PagedAttention**（vLLM）：将 KV cache 分割为按需分配的可复用页面 → 内存浪费减少 90%，服务吞吐提升高达 **24×**。

**2026 进阶技术**：
- **ChunkKV**：以语义块为压缩单位
- **RocketKV**：两阶段流水线（粗粒度 KV 驱逐→细粒度压缩）

### 3.3 推测解码（Speculative Decoding）

```
Draft Model（小/快）→ 生成 K 个候选 token
Target Model（大/准）→ 单次前向传播验证所有 K 个 token
接受匹配的 → 第一个不匹配的替换为 Target 的选择
重复
```

- 输出与正常自回归解码**数学等价**
- 典型加速 **2-3×**（EAGLE3 离线 draft 模型）
- 特定领域/硬件优化可达 **5×**
- **关键洞察**：draft 模型的延迟比其准确率更重要
- **QuantSpec**：将量化引入 draft + KV cache，接受率 >90%，加速 ~2.5×

### 3.4 FlashAttention

通过 tiling + fused softmax 最小化内存 I/O。**FlashAttention-3** 是当前最快的自定义注意力内核，已集成到 vLLM 和 SGLang。

---

## 四、推理引擎对比（2026）

| 引擎 | 版本 | H100 吞吐 | 关键特性 | 最佳场景 |
|------|------|----------|---------|---------|
| **SGLang** | v0.4.3 | 16,200 tok/s | RadixAttention 前缀缓存 | 前缀密集（RAG、多轮对话） |
| **LMDeploy** | Latest | 16,200 tok/s | 持久化批调度 | 高吞吐服务 |
| **vLLM** | v0.7.3 | 12,500 tok/s | PagedAttention，Blackwell 支持 | 灵活性，频繁换模型 |
| **TensorRT-LLM** | Latest | 高并发最高 | 编译 CUDA 内核 | 单模型长期生产 |

**选型建议**：
- vLLM → 频繁换模型，最易上手
- SGLang → 共享前缀（聊天机器人、RAG、多轮）
- TensorRT-LLM → 单模型长期部署，追求最大吞吐

---

## 五、应用层优化（最高 ROI）

### 5.1 Prompt Caching

复用已计算的 KV 张量，缓存部分跳过 prefill。上下文 >10K tokens 时 **80-90% 延迟降低**。Anthropic 缓存 token 不计入速率限制 → 80% 缓存命中时 **5× 吞吐**。

### 5.2 语义缓存

存储完整请求-响应对，语义相似查询直接返回缓存。AWS 基准测试：重复查询模式 **3-10× 成本节省**。

### 5.3 上下文压缩

- **LLMLingua**：通过排序/保留关键 token 实现高达 **20× 压缩**
- **风险**：摘要重写会丢失文件路径/错误码/决策等关键细节

---

## 六、组合生产栈

```
请求 → 连续批处理引擎
  ├── PagedAttention（内存效率）
  ├── 量化模型（INT8/INT4）
  ├── GQA/MQA（减少 KV cache）
  ├── 推测解码（速度）
  └── 前缀缓存（共享 prompt）
```

**复合效果**：优化良好的服务栈可比朴素实现服务 **10-50× 更多请求/GPU**。

---

## 七、实践启示

### 对 Jetson Orin 边缘部署的映射

| 技术 | 适用性 | 备注 |
|------|--------|------|
| GGUF Q4_K_M 量化 | ✅ 必须 | 67 TOPS 下 7B-13B 模型唯一可行方案 |
| 推测解码 | ⚠️ 受限 | 双模型同时加载受 8GB VRAM 限制 |
| PagedAttention | ✅ 推荐 | vLLM/llama.cpp 均支持 |
| 连续批处理 | ⚠️ 受限 | 并发请求数通常 <5 |
| KV cache 量化（TurboQuant 3-bit） | ✅ 高价值 | 可显著延长有效上下文长度 |

### 关键行动项

1. 评估 TurboQuant 3-bit KV cache 在 llama.cpp 的可用性
2. 优先在所有部署中使用 GQA 模型（如 Qwen2.5 系列）减少 KV cache
3. 前缀缓存在 Agent 多轮对话中收益最大——确保启用

---

## 参考资源

- MorphLLM "LLM Inference Optimization: Cut Cost & Latency" (2026)
- CallSphere "Quantization, Speculative Decoding" (2026)
- Google Cloud "Five Techniques to Reach the Efficient Frontier"
- arXiv:2604.05012 — "Comparative Characterization of KV Cache Management Strategies"
- vLLM PagedAttention — arXiv:2309.06180

## 相关笔记
- [Multi-Stream LLMs 并行流](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
- [LoRA GRPO最优配置实证](2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md)
- [Anthropic Colossus2 GB200](2026-05-22-Anthropic-Colossus2-GB200-AI基础设施军备竞赛.md)
