# 本地 LLM 部署工具：Ollama vs vLLM vs llama.cpp

- 📅 2026-05-08
- ⭐ 4.5/5 — 实测对比数据扎实，选型决策树实用，唯一不足是 llama.cpp 高并发数据缺失
- 🏷️ #LLM部署 #vLLM #Ollama #llama.cpp #本地推理 #性能测试 #PagedAttention
- 📰 微信公众号「楠楠自瑜」，原作 Chew Loong Nian，译者 Carl Cui
- 🔗 https://mp.weixin.qq.com/s/kZiWDy3Wh2Ngu_W514AgJg

## 摘要

作者在相同硬件（RTX 4090 24GB + 64GB RAM）上实测 Ollama、vLLM、llama.cpp 三大本地 LLM 部署工具。核心发现：Ollama 适合开发原型但生产并发上限约 5 用户（FIFO 队列瓶颈）；vLLM 凭借 PagedAttention + continuous batching 在 50 并发下吞吐量是 Ollama 的 5.9 倍；llama.cpp 是生态基础（Ollama 底层即 llama.cpp），Apple Silicon 和边缘设备首选。三者都暴露 OpenAI 兼容端点，切换只需改 base_url。

## 核心内容

### 关键性能数据

| 指标 | Ollama | vLLM | llama.cpp |
|------|--------|------|-----------|
| 设置时间 | 5 min | 20 min | 10 min |
| 单用户 TPS | 40-50 | 485 | 50-100* |
| 50用户总 TPS | ~155 | 920 | N/A** |
| p95延迟(50用户) | 18.4s | 2.1s | N/A |
| 128并发成功率 | ❌崩溃 | 100% | N/A |
| 系统内存占用 | 1.8GB | 4.6GB | - |

*Apple Silicon Metal；**单用户/低并发设计，高负载有类似Ollama队列限制

### Ollama 架构瓶颈

Ollama 用 FIFO 队列处理请求——第40个用户需等前39个完成。GitHub issue #9054 明确说"不利用多实例并行处理"，自2024年开放至今。作者给40个内部用户部署后响应从3秒暴涨到1分钟+。

适用场景：个人开发、原型、教学演示、<5并发。不适用于任何多用户生产环境。

### vLLM 核心技术：PagedAttention

传统 KV 缓存预分配连续 GPU 显存→浪费率 60-80%。PagedAttention 借鉴 OS 虚拟内存，将 KV 缓存分页管理→浪费率<4%。配合 continuous batching（新请求直接进入当前批次），实现高并发低延迟。

生产级用户：Amazon Rufus（2.5亿客户）、LinkedIn、Roblox（周40亿token）、Stripe。Hugging Face 2025年12月弃用 TGI，官方推荐 vLLM 继任。

限制：必须 NVIDIA GPU（CUDA 7.0+，V100/T4/A10/A100/H100），不支持 Mac/纯CPU。

### llama.cpp：生态基础设施

纯 C/C++ 无依赖，100K+ GitHub star（超越 PyTorch 到达速度）。Ollama 底层跑的就是 llama.cpp。60%+ 量化模型采用 GGUF 格式（llama.cpp 创建的标准）。支持 CPU/CUDA/Metal/ROCm/Vulkan 全平台。2026新增：MCP客户端、多GPU分布式RPC推理、结构化输出解析器。

GGUF 量化精度：Q4_K_M(4bit)对话OK但精确推理下降；Q5_K_M是质量/大小最佳平衡；Q8_0接近全精度。

### 选型决策树

```
你的场景？
├── 个人开发/原型/教学 → Ollama（最快上手）
├── 生产API/10+并发用户 → vLLM（唯一选择）
├── Apple Silicon 设备 → llama.cpp（Metal直调比Ollama快）
├── 边缘设备/纯CPU → llama.cpp
└── 需要精确控制量化级别 → llama.cpp
```

三者都暴露 OpenAI 兼容端点，切换只需改 base_url：Ollama → localhost:11434，vLLM → localhost:8000，llama.cpp → localhost:8080。

### SGLang 补充

SGLang 是 vLLM 的新竞争者：H100 上吞吐量比 vLLM 高 29%（16,200 vs 12,500 tps），通过 RadixAttention 跨请求缓存共享计算。对多轮对话和 RAG 管线特别有效。

## 🔍 借鉴点

- **PagedAttention 分页思想** → 可借鉴到 Agent 上下文管理，当前上下文窗口占用也有类似的"预分配浪费"问题
- **OpenAI 兼容端点统一接口** → jbot 的 model provider 切换已实现类似机制，验证了这一设计方向正确
- **GGUF Q5_K_M 甜区** → Jetson Orin Nano 上部署本地模型时直接用这个量化级别，避免踩坑
- **continuous batching 模式** → 多 agent 并发推理时（jbot+ubot 同时请求本地模型），需要类似机制而非 FIFO 排队
- **开发工具≠部署工具** → Ollama 用于日常调试迭代，生产切 vLLM，这一思路适用于 Agent 自身的架构分层

## 🔗 关联性

- 关联笔记：[2026-05-08-ai-agent-protocol-wars-a2a-mcp](explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md) — Agent 协议层与推理部署层互补，A2A Agent 需要后端推理支撑
- 关联笔记：[2026-05-06-ai-agent-protocol-stack-2026](explore/2026-05-06-ai-agent-protocol-stack-2026.md) — 技术栈全景中推理层的选择直接影响 Agent 架构决策
- 关联 skill：nexa-local-inference — Jetson Orin Nano 本地推理配置，Ollama 部署细节
- 关联 skill：llama-cpp — llama.cpp 本地 GGUF 推理 + HF Hub 模型发现
- 关联技术栈：Jetson Orin Nano (8GB VRAM) → Ollama 当前够用，vLLM 不支持 ARM GPU

## 💡 启发

- **"底层引擎"才是护城河** — llama.cpp 不做上层产品但成为生态标准（GGUF格式、Ollama底层），类比到 Agent 领域：MCP 协议层可能比上层 Agent 框架更有长期价值
- **并发模型决定天花板** — FIFO vs batching 不是优化问题而是架构选择，一旦选定很难改。Agent 任务调度也面临类似抉择
- **量化不是"降级"而是"适配"** — Q5_K_M 在有限硬件上可能是最优解而非妥协，启示：资源受限环境下的工程决策应以目标场景适配为标准而非绝对精度

## 🔮 预判

1. **vLLM 短期统治 NVIDIA 生产部署**，但 SGLang 在 H100 级别会抢占高性能场景，两者可能走向融合（类似 PyTorch/XLA）
2. **Ollama 并发改进缓慢** — FIFO 架构的根本改变需要重构，路线图承诺兑现时间存疑
3. **llama.cpp 从"推理引擎"进化为"Agent运行时"** — MCP 客户端支持是信号，未来可能直接在推理层内置 Agent 编排
4. **GGUF 格式成为量化模型事实标准** — 类似 MP3 之于音频，60%+ 采用率已过临界点

## 相关笔记

- [2026-05-08-ai-agent-protocol-wars-a2a-mcp](explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md) — AI Agent 协议架构深度分析
- [2026-05-06-ai-agent-protocol-stack-2026](explore/2026-05-06-ai-agent-protocol-stack-2026.md) — 2026 AI Agent 技术栈全景
