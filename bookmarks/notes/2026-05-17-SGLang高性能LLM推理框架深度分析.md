# SGLang：高性能 LLM 推理框架深度分析

- 📅 2026-05-17
- ⭐ 4.5/5 — LLM 推理领域事实标准，全栈优化+结构化生成，生产级验证
- 🏷️ #LLM推理 #SGLang #vLLM #DeepSeek #RadixAttention #结构化输出 #RL训练
- 📰 LMSYS 官方 GitHub + PyTorch 2025 演讲 + 技术博客
- 🔗 https://github.com/sgl-project/sglang
- 关联：[[2026-05-17-PageIndex项目分析]] — PageIndex 使用索引技术，SGLang 可作为后端推理引擎

## 摘要

SGLang 是 LMSYS（UC Berkeley 主导）开发的高性能 LLM 推理框架，采用前后端双引擎架构：前端提供结构化生成 DSL 编程语言，后端运行时集成 RadixAttention 前缀缓存、零开销 CPU 调度器、Prefill-Decode 分离等核心优化。全球 400K+ GPU 部署，日处理万亿级 token，已成为 DeepSeek 官方推荐推理引擎。2026 年在 GB300 NVL72 上实现 25x 推理加速，并扩展至视频/图像生成（SGLang Diffusion）。

## 核心内容

### 一、双引擎架构设计

**Frontend（前端编程层）**：
- SGLang DSL：Python 域特定语言，定义 LLM 交互流程
- 结构化输出约束：压缩有限状态机（Compressed FSM），原生 JSON/Schema 支持
- OpenAI API 兼容：零改动迁移
- 多模态支持：多图像/视频输入（LLaVA-OneVision）

**Runtime（后端运行时）**：
- RadixAttention：前缀树缓存 KV cache，复用公共前缀，最高 5x 加速
- 零开销 CPU 调度器：无额外开销的 batch 调度
- Continuous Batching：动态批处理，请求完成即释放 slot
- Prefill-Decode 分离（PD Disaggregation）：独立扩缩容，DeepSeek 场景 3.8x Prefill + 4.8x Decode
- Speculative Decoding：投机采样，小模型引导大模型加速
- Paged Attention：分页注意力，高效管理 GPU 显存
- 多维并行：Tensor/Pipeline/Expert/Data Parallelism
- 量化全栈：FP4/FP8/INT4/AWQ/GPTQ

### 二、性能里程碑

| 版本 | 时间 | 核心优化 | 性能数据 |
|------|------|---------|---------|
| v0.1 | 2024/01 | RadixAttention + 压缩 FSM | 3x JSON 解码加速 |
| v0.2 | 2024/07 | Llama3 服务优化 | 优于 TensorRT-LLM, vLLM |
| v0.3 | 2024/09 | DeepSeek MLA + torch.compile | 7x 吞吐 + 1.5x 编译加速 |
| v0.4 | 2024/12 | 零开销调度器 + Cache-Aware LB | 结构化输出进一步提升 |
| — | 2025/05 | 96xH100 大规模 EP | 2.7x 解码吞吐 |
| — | 2025/09 | GB200 NVL72 PD 分离 | 3.8x Prefill, 4.8x Decode |
| — | 2025/10 | TPU 原生支持 (SGLang-Jax) | 跨硬件统一体验 |
| — | 2025/11 | SGLang Diffusion | 视频/图像生成加速 |
| — | 2026/02 | GB300 NVL72 | **25x 推理性能** |

### 三、硬件生态全覆盖

| 硬件平台 | 状态 | 代表型号 |
|---------|------|---------|
| NVIDIA GPU | ✅ 全栈 | GB200/B300/H100/A100/Spark/5090 |
| AMD GPU | ✅ ROCM | MI355/MI300 |
| Google TPU | ✅ Jax backend | 全系列 |
| Intel Xeon | ✅ | CPU 推理 |
| Ascend NPU | ✅ | 华为昇腾 |

### 四、模型支持矩阵

**LLM**：Llama, Qwen, DeepSeek, Kimi, GLM, GPT, Gemma, Mistral, Nemotron, MiMo, LLaDA 2.0

**Embedding**：e5-mistral, gte, mcdse

**Reward**：Skywork

**Diffusion**：WAN, Qwen-Image（SGLang Diffusion）

**多模态**：LLaVA-OneVision（多图像/视频）

### 五、SGLang vs vLLM 核心对比

| 维度 | SGLang | vLLM |
|------|--------|------|
| 核心定位 | 结构化生成 + 推理引擎 | 纯推理引擎 |
| 编程接口 | SGLang DSL（Python） | Python API |
| 前缀缓存 | RadixAttention（前缀树） | PagedAttention |
| 结构化输出 | 压缩 FSM 原生支持 | 需 Outlines 等插件 |
| DeepSeek | 官方推荐，MLA+DP Attention | 社区支持 |
| TPU 支持 | ✅ SGLang-Jax | ❌ |
| RL 训练 | ✅ 原生集成（verl, slime 等） | ❌ |
| Diffusion | ✅ SGLang Diffusion | ❌ |
| 生产规模 | 400K+ GPU | 广泛使用 |
| 开源组织 | LMSYS（非营利） | vLLM Project |

### 六、RL & Post-Training 生态

SGLang 是 RLHF/RLAIF 训练的首选 rollout backend，原生集成主流 RL 框架：

| 框架 | 来源 | 说明 |
|------|------|------|
| AReaL | inclusionAI | RL 框架 |
| Miles | radixark | RL 框架 |
| slime | THUDM | RL 框架 |
| Tunix | Google | RL 框架 |
| verl | 火山引擎 | RL 框架 |

### 七、快速上手

```bash
# 安装
pip install sglang

# 单 GPU 启动
python3 -m sglang.launch_server --model meta-llama/Llama-3-8B --port 30000

# DeepSeek 多 GPU
python3 -m sglang.launch_server --model deepseek-ai/DeepSeek-V3 --tp 8 --port 30000

# OpenAI 兼容调用
import openai
client = openai.Client(base_url="http://127.0.0.1:30000/v1", api_key="EMPTY")
```

## 🔍 借鉴点

- **RadixAttention 前缀树缓存** → Hermes Agent 长对话场景可借鉴：相同 system prompt 的请求复用 KV cache，减少重复计算
- **PD 分离架构** → 推理服务部署时可独立扩缩容 prefill 和 decode 节点，降低延迟
- **压缩 FSM 结构化输出** → Agent 工具调用场景，JSON Schema 约束可直接编译为 FSM，避免重采样
- **零开销 CPU 调度器** → 多 Agent 并发推理时的 batch 调度设计参考
- **OpenAI API 兼容** → 零改动迁移，可直接替代 vLLM 作为推理后端

## 🔗 关联性

- 关联 Skill：serving-llms-vllm — vLLM 部署指南，SGLang 是其强力竞争者
- 关联 Skill：llm-inference-optimization — 推理优化技术栈，SGLang 集成了其中大部分技术
- 关联项目：PageIndex — 文档结构化索引，SGLang 可作为后端推理引擎加速 RAG
- 关联技术：DeepSeek V3/R1 → SGLang 是官方推荐推理引擎

## 💡 启发

- **结构化生成是未来**：SGLang 把结构化输出当成一等公民，而不是事后插件。Agent 时代的 LLM 调用几乎都需要 JSON/Schema 约束，这块 SGLang 有天然优势
- **推理框架的生态壁垒**：SGLang 通过 RL 训练生态（verl 等）建立护城河，不仅仅是推理引擎，而是训练-推理一体化平台
- **前缀缓存的价值被低估**：多轮对话中 system prompt 通常不变，RadixAttention 可以大幅降低延迟和成本

## 🔮 预判

- **SGLang 将取代 vLLM 成为主流**：DeepSeek 官方背书 + 结构化输出 + RL 生态，三重优势叠加。预计 2026 年底市占率超 60%
- **Diffusion 推理统一**：SGLang Diffusion 把视频/图像生成纳入统一框架，LLM + Diffusion 融合推理是下一个增长点
- **Jetson/边缘部署待突破**：当前 SGLang 偏向数据中心级部署，边缘端（如 Jetson Orin）仍是 llama.cpp 的天下

## 相关笔记

- [[2026-05-17-PageIndex项目分析]] — 文档索引与 RAG，SGLang 可作为后端
