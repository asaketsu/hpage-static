# LLM 推理引擎双雄：SGLang vs vLLM 深度对比

> **类型**: 原创技术对比分析
> **日期**: 2026-07-31
> **标签**: `LLM` `推理引擎` `SGLang` `vLLM` `RadixAttention` `PagedAttention` `部署` `基础设施`

---

## 核心结论

SGLang 和 vLLM 是 2025-2026 年 LLM 推理领域最主流的两个开源引擎，**底层技术正在趋同**（PagedAttention、连续批处理、推测解码都已互相借鉴），但**设计哲学和差异化优势不同**：

| 维度 | SGLang | vLLM |
|------|--------|------|
| **起源** | LMSYS (UC Berkeley 系) | UC Berkeley Sky Computing Lab |
| **核心创新** | **RadixAttention**（基数树前缀缓存） | **PagedAttention**（虚拟内存式 KV 管理） |
| **差异化** | 结构化生成 + RL 训练后端 + 大规模 EP | 广泛模型支持 + 易用性 + 社区生态 |
| **哲学** | "为复杂推理工作流极致优化" | "Easy, fast, and cheap for everyone" |
| **2026 规模** | 40 万+ GPU 全球部署 | 2000+ 贡献者，最活跃开源 AI 项目之一 |

> **一句话选型**：通用服务/快速上手/广泛模型兼容 → **vLLM**；Agent 多轮推理/结构化输出/RL 训练/大规模 MoE → **SGLang**。

---

## 一、技术架构对比

### 1.1 核心创新点

#### vLLM: PagedAttention（2023）

灵感来自操作系统的**虚拟内存分页机制**：

```
传统 KV Cache 问题:
┌────────────────────────────────┐
│ 请求A KV: [██████████░░░░░░░░] │ ← 预留连续空间，存在碎片
│ 请求B KV: [██████░░░░░░░░░░░░] │ ← 无法共享前缀
│ 请求C KV: [████████████░░░░░░] │ ← 内存浪费严重
└────────────────────────────────┘

PagedAttention:
┌────────────────────────────────┐
│ KV Cache 被分成固定大小的 Block │
│                                │
│ Block Table (类似页表):         │
│  请求A → [Block0][Block1][Block3]│
│  请求B → [Block0][Block2]       │ ← 共享 Block0（相同前缀）
│  请求C → [Block0][Block1][Block4]│ ← 共享 Block0+Block1
│                                │
│ 物理 Block 池:                  │
│  [B0][B1][B2][B3][B4][B5]...   │ ← 按需分配，零碎片
└────────────────────────────────┘
```

| 特性 | 说明 |
|------|------|
| **灵感** | OS 虚拟内存 + 页表 |
| **机制** | KV Cache 分成固定大小 Block，通过 Block Table 映射 |
| **优势** | 消除内存碎片；支持前缀共享（Copy-on-Write）；显存利用率接近 100% |
| **论文** | Kwon et al., SOSP 2023 |

#### SGLang: RadixAttention（2024）

灵感来自**基数树（Radix Tree）**数据结构，自动缓存和复用前缀：

```
RadixAttention 前缀树缓存:

         [System Prompt]              ← 多个请求共享的 system prompt
              │
         ┌────┴────┐
         │         │
    [few-shot   [User Query
     examples]   context]
         │         │
     ┌───┴───┐     │
     │       │   [Response A]  ← 生成结果也被缓存
  [Task1] [Task2]
     │       │
  [Resp1] [Resp2]

新请求到达时:
1. 在 Radix Tree 中查找最长公共前缀
2. 命中 → 直接复用缓存的 KV (O(1))
3. 未命中 → 计算新 KV 并插入树中
4. 自动 LRU 淘汰
```

| 特性 | 说明 |
|------|------|
| **灵感** | 基数树 (Radix Tree) |
| **机制** | 前缀 KV Cache 以 Radix Tree 组织，自动复用 |
| **优势** | Agent 多轮对话、few-shot、结构化生成的重复前缀自动复用；可达 **3-5x 加速** |
| **与 vLLM 的关系** | vLLM 后来也实现了 Automatic Prefix Caching (APC)，但 SGLang 的 RadixAttention 更深度集成 |

### 1.2 核心创新对比

| 创新点 | vLLM | SGLang |
|--------|------|--------|
| KV Cache 管理 | **PagedAttention**（分页管理） | **RadixAttention**（基数树+分页） |
| 前缀缓存 | Automatic Prefix Caching (APC) | RadixAttention 原生集成 |
| 结构化输出 | xgrammar / guidance | **压缩有限状态机**（Compressed FSM），3x JSON 解码 |
| 批处理 | Continuous Batching | Continuous Batching + **零开销 CPU 调度器** |
| 推测解码 | n-gram / EAGLE / DFlash | DFlash + **Spec V2**（下一代推测解码） |

---

## 二、功能特性全景对比

### 2.1 推理优化技术

| 技术 | vLLM | SGLang |
|------|------|--------|
| 连续批处理 (Continuous Batching) | ✅ | ✅ |
| 分块预填充 (Chunked Prefill) | ✅ | ✅ |
| 前缀缓存 (Prefix Caching) | ✅ APC | ✅ RadixAttention |
| 分页注意力 (PagedAttention) | ✅ 原创 | ✅ 采用 |
| CUDA Graphs | ✅ Piecewise + Full | ✅ |
| 推测解码 (Speculative Decoding) | ✅ n-gram/EAGLE/DFlash | ✅ **DFlash + Spec V2** |
| Prefill-Decode 分离 | ✅ | ✅ PD Disaggregation |
| torch.compile | ✅ 自动内核生成 | ✅ 1.5x 加速 |
| 零开销调度器 | — | ✅ **零开销 CPU 调度器** |
| 缓存感知负载均衡 | — | ✅ |

### 2.2 量化支持

| 量化方案 | vLLM | SGLang |
|---------|------|--------|
| FP8 | ✅ | ✅ |
| FP4 (MXFP4/NVFP4) | ✅ | ✅ FP4 |
| INT8 | ✅ | ✅ INT4/INT8 |
| GPTQ | ✅ | ✅ |
| AWQ | ✅ | ✅ |
| GGUF | ✅ | — |
| Compressed-tensors | ✅ | — |

### 2.3 分布式并行

| 并行策略 | vLLM | SGLang |
|---------|------|--------|
| 张量并行 (TP) | ✅ | ✅ |
| 流水线并行 (PP) | ✅ | ✅ |
| 数据并行 (DP) | ✅ | ✅ |
| 专家并行 (EP) | ✅ | ✅ **大规模 EP（96×H100 验证）** |
| 上下文并行 (CP) | ✅ | — |
| Prefill-Decode 分离 | ✅ | ✅ **PD 分离 + 大规模 EP（GB200 验证）** |

### 2.4 模型支持

| 模型类型 | vLLM | SGLang |
|---------|------|--------|
| Decoder-only LLM (Llama/Qwen/Gemma) | ✅ | ✅ |
| MoE (Mixtral/DeepSeek-V3/Qwen-MoE) | ✅ | ✅ **DeepSeek 专属优化** |
| SSM/Mamba | ✅ | ✅ |
| 多模态 (LLaVA/Qwen-VL/Pixtral) | ✅ | ✅ |
| Embedding 模型 | ✅ | ✅ |
| Reward 模型 | ✅ | ✅ |
| 扩散模型 | — | ✅ **SGLang Diffusion（视频/图像）** |
| 总架构数 | **200+** | 广泛（兼容大部分 HF 模型） |

### 2.5 API 兼容性

| API | vLLM | SGLang |
|-----|------|--------|
| OpenAI Compatible | ✅ | ✅ |
| Anthropic Messages API | ✅ | — |
| gRPC | ✅ | ✅ |
| 工具调用 (Tool Calling) | ✅ | ✅ |
| 推理解析器 (Reasoning Parser) | ✅ | ✅ |
| 结构化输出 | ✅ xgrammar/guidance | ✅ **压缩 FSM** |

---

## 三、差异化优势深度分析

### 3.1 SGLang 的独家优势

#### ① RadixAttention → Agent/多轮推理场景

```
场景: Agent 多轮对话（共享大量重复上下文）

Turn 1: [System][Tools][History] → "帮我查天气"
Turn 2: [System][Tools][History][Turn1] → "帮我订机票"
Turn 3: [System][Tools][History][Turn1][Turn2] → "提醒我..."

RadixAttention:
  Turn 1: 全部计算 → 缓存到 Radix Tree
  Turn 2: [System][Tools][History] 全部命中缓存 → 只算 [Turn1][新输入]
  Turn 3: 前缀全部命中 → 只算 [Turn2][新输入]

vLLM APC:
  类似机制，但 SGLang 的集成更深度、命中率更高
```

> **关键数据**：SGLang 官方报告 RadixAttention 在 few-shot/Agent 场景可达 **3-5x 加速**。

#### ② 结构化生成（压缩有限状态机）

```
场景: 强制 LLM 输出合法 JSON

传统方法: 逐 token 生成 → 检查是否符合 JSON Schema → 不符合则重试
SGLang:  压缩有限状态机 → 在解码时直接屏蔽非法 token

效果: JSON 解码速度提升 3x（论文报告）
```

#### ③ RL & Post-Training 骨干

SGLang 被以下主流 RL 框架采用为推理后端：

| RL 框架 | 团队 |
|---------|------|
| **verl** | 字节火山引擎 |
| **AReaL** | 蚂蚁/inclusionAI |
| **Miles** | RadixArk |
| **slime** | 清华 THUDM |
| **Tunix** | Google |

> SGLang 在 RL 场景的优势：Rollout 高吞吐 + 参数更新快速切换 + 多 LoRA 批处理。

#### ④ 大规模 MoE 部署

```
DeepSeek-V3/R1 部署（SGLang 强项）:
- 96×H100 大规模专家并行: 3.8x Prefill, 4.8x Decode
- GB200 NVL72: 2.7x 解码吞吐
- GB300 NVL72: 25x 推理性能
- Day-0 支持 DeepSeek 全系列
```

### 3.2 vLLM 的独家优势

#### ① 最广泛的模型兼容性

> 200+ 模型架构支持，几乎覆盖所有 Hugging Face 模型。新模型发布通常 vLLM 最先支持。

#### ② 最低上手门槛

```bash
# vLLM: 一行启动
vllm serve Qwen/Qwen3-4B-Instruct

# 自动处理一切：模型加载、批处理、API 服务
```

#### ③ 最活跃的社区

| 指标 | vLLM |
|------|------|
| 贡献者 | **2000+** |
| 来源机构 | 数十个学术机构 + 200+ 公司 |
| 维护 | 社区驱动 |
| 文档 | docs.vllm.ai 完整 |

#### ④ 多样化量化方案

vLLM 支持的量化方案最多（GGUF、compressed-tensors、ModelOpt、TorchAO 等），对消费级硬件更友好。

#### ⑤ Anthropic Messages API

vLLM 除了 OpenAI 兼容 API，还支持 Anthropic Messages API 和 gRPC，客户端兼容面更广。

---

## 四、性能对比（2026 年公开数据）

### 4.1 SGLang 自报性能

| 场景 | 提升 |
|------|------|
| RadixAttention（few-shot/Agent） | **3-5x** 加速 |
| 压缩 FSM（JSON 结构化输出） | **3x** JSON 解码加速 |
| DeepSeek MLA 优化 | **7x** |
| GB300 NVL72 | **25x** 推理性能 |
| GB200 大规模 EP | 3.8x Prefill / 4.8x Decode |
| Llama3 服务（v0.2 vs TensorRT-LLM/vLLM） | 最优 |

### 4.2 横向对比趋势

> ⚠️ 基准测试结果因模型、硬件、配置而异，以下为公开趋势而非绝对结论。

| 场景 | 通常更优 | 原因 |
|------|---------|------|
| Agent/多轮对话 | **SGLang** | RadixAttention 前缀复用 |
| 结构化 JSON 输出 | **SGLang** | 压缩 FSM |
| RL 训练 Rollout | **SGLang** | 专为 RL 优化 |
| DeepSeek MoE | **SGLang** | Day-0 专属优化 |
| 新模型快速部署 | **vLLM** | 模型支持最广 |
| 消费级 GPU | **vLLM** | 量化方案最多 |
| 社区/文档 | **vLLM** | 2000+ 贡献者 |
| 生产稳定性 | **两者** | 均大规模验证 |

---

## 五、硬件支持对比

| 硬件 | vLLM | SGLang |
|------|------|--------|
| NVIDIA GPU (H100/A100/5090) | ✅ | ✅ |
| NVIDIA GB200/GB300 | ✅ | ✅ **深度优化** |
| AMD GPU (MI300/MI355) | ✅ | ✅ **AMD 深度合作** |
| Intel GPU | ✅ | — |
| Intel Xeon CPU | ✅ | ✅ |
| x86/ARM/PowerPC CPU | ✅ | — |
| Google TPU | ✅ 插件 | ✅ **SGLang-Jax 原生** |
| 华为 Ascend NPU | ✅ | ✅ |
| Intel Gaudi | ✅ 插件 | — |
| Apple Silicon | ✅ | — |

---

## 六、生产环境采用情况

### 6.1 SGLang 采用方

> SGLang 每天生成数万亿 token，部署在 40 万+ GPU 上。

| 采用方 | 角色 |
|--------|------|
| **xAI** | Grok 推理后端 |
| **AMD** | 深度合作，MI300X 优化 |
| **NVIDIA** | GB200/GB300 优化 |
| **Cursor** | 代码助手推理 |
| **LinkedIn** | 推理基础设施 |
| Oracle Cloud / Google Cloud / AWS / Azure | 云服务 |
| MIT / UCLA / UW / Stanford / UC Berkeley / 清华 | 学术 |

### 6.2 vLLM 采用方

> vLLM 由 2000+ 贡献者维护，来源涵盖数十个学术机构和 200+ 公司，是使用最广泛的 LLM 推理引擎。

| 采用方 | 角色 |
|--------|------|
| UC Berkeley Sky Computing Lab | 起源 |
| 大量云服务商 | 推理服务后端 |
| Anyscale / Nebius / Baseten | 托管推理 |
| 学术机构 | 研究推理 |

---

## 七、选型决策矩阵

### 7.1 按场景选型

| 你的场景 | 推荐 | 理由 |
|---------|------|------|
| **Agent 多轮推理** | **SGLang** | RadixAttention 前缀复用 |
| **强制 JSON/结构化输出** | **SGLang** | 压缩 FSM |
| **RL 训练 Rollout** | **SGLang** | verl/AReaL 等 RL 框架原生支持 |
| **DeepSeek MoE 大规模部署** | **SGLang** | Day-0 专属优化 |
| **TPU 推理** | **SGLang** | SGLang-Jax 原生 TPU |
| **视频/图像扩散** | **SGLang** | SGLang Diffusion |
| **快速上手/通用服务** | **vLLM** | 一行启动，最易用 |
| **新模型 Day-0 部署** | **vLLM** | 200+ 架构，最快支持 |
| **消费级 GPU（量化）** | **vLLM** | GGUF 等多量化方案 |
| **Apple Silicon** | **vLLM** | 支持 |
| **广泛社区/文档需求** | **vLLM** | 2000+ 贡献者 |

### 7.2 决策树

```
你的首要需求是什么?
│
├── 复杂推理工作流（Agent/多轮/结构化输出/RL）
│   └── → SGLang ✅
│
├── DeepSeek MoE 大规模生产部署
│   └── → SGLang ✅ (GB200/GB300 深度优化)
│
├── TPU 原生推理
│   └── → SGLang ✅ (SGLang-Jax)
│
├── 快速上手 + 通用模型服务
│   └── → vLLM ✅ (一行启动)
│
├── 冷门模型/新模型快速部署
│   └── → vLLM ✅ (200+ 架构)
│
├── 消费级 GPU + 多种量化
│   └── → vLLM ✅ (GGUF/GPTQ/AWQ/...)
│
└── 不确定
    └── → vLLM ✅ (默认安全选择, 社区最大)
```

---

## 八、快速启动对比

### 8.1 vLLM

```bash
# 安装
uv pip install vllm

# 启动服务（一行命令）
vllm serve Qwen/Qwen3-4B-Instruct --port 8000

# 或 Python API
from vllm import LLM
llm = LLM(model="Qwen/Qwen3-4B-Instruct")
output = llm.generate(["Hello, what is LLM inference?"])
```

### 8.2 SGLang

```bash
# 安装
pip install sglang[all]

# 启动服务
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-4B-Instruct \
    --port 30000

# 或使用 SGLang 前端编程（结构化生成）
import sglang as sgl

@sgl.function
def multi_step_qa(s, question):
    s += "Please reason step by step."
    s += sgl.gen("reasoning", max_tokens=256)
    s += "Based on the above, the answer is:"
    s += sgl.gen("answer", max_tokens=64)

# 结构化输出
@sgl.function
def json_output(s):
    s += 'Return a JSON with "name" and "age".'
    s += sgl.gen("json", regex=r'\{"name": "[^"]+", "age": \d+\}')
```

---

## 九、技术演进趋势

### 9.1 功能趋同

两个项目在核心技术上越来越相似：

| 技术 | 谁先有 | 现状 |
|------|--------|------|
| PagedAttention | vLLM 原创 | 两者都有 |
| RadixAttention/前缀缓存 | SGLang 原创 | 两者都有 |
| 连续批处理 | 几乎同时 | 两者都有 |
| 推测解码 (EAGLE/DFlash) | 几乎同时 | 两者都有 |
| Prefill-Decode 分离 | SGLang 先大规模 | 两者都有 |
| Chunked Prefill | vLLM 先 | 两者都有 |

### 9.2 差异化方向

| 方向 | SGLang | vLLM |
|------|--------|------|
| **深度** | 推理工作流深度优化（结构化生成/RL/Agent） | 模型兼容广度（200+ 架构） |
| **硬件** | GB200/GB300 + TPU 深度合作 | 多硬件插件（Gaudi/Spyre/MetaX 等） |
| **新模型** | DeepSeek/Nemotron Day-0 专属优化 | 新架构最快通用支持 |
| **新范式** | SGLang Diffusion（视频/图像） | — |

### 9.3 2026 年新进展

| SGLang | vLLM |
|--------|------|
| **DFlash + Spec V2**（下一代推测解码） | DFlash 推测解码 |
| GB300 NVL72: 25x 推理性能 | — |
| SGLang Diffusion（视频/图像） | — |
| SGLang-Jax（TPU 原生） | TPU 插件 |
| DeepSeek-V4 Day-0 | — |
| Nemotron 3 Ultra/Super Day-0 | — |

---

## 十、与 Hermes / 用户项目的关联

| 关联场景 | 推荐引擎 | 理由 |
|---------|---------|------|
| **Hermes Gateway**（多 Agent 多轮对话） | **SGLang** | RadixAttention 天然适配多轮前缀复用 |
| **DeepSeek/GLM 本地推理** | **SGLang** | Day-0 优化 + MoE 大规模 EP |
| **结构化输出（JSON Schema）** | **SGLang** | 压缩 FSM |
| **快速测试新模型** | **vLLM** | 200+ 架构，一行启动 |
| **Jetson 边缘推理** | **vLLM** | 量化方案多（GGUF），CPU 支持 |
| **HF Speech-to-Speech 集成** | **vLLM**（S2S 文档推荐） | S2S README 中 vLLM 为推荐本地服务器 |
| **RL 训练** | **SGLang** | verl/slime 等 RL 框架原生后端 |

### Hermes 本地部署优化建议

```
当前: Hermes → zai gateway → GLM-5.2 API
                           → sensenova API
                           → lo API

优化后: Hermes → 本地 SGLang/vLLM → GLM/Qwen/DeepSeek 本地模型
                                      ↓
                                 混合策略:
                                 ├── 对话 (Agent多轮) → SGLang (RadixAttention)
                                 ├── 工具调用 (结构化) → SGLang (压缩FSM)
                                 └── 新模型测试 → vLLM (快速启动)
```

---

## 十一、关键术语速查

| 术语 | 说明 |
|------|------|
| **PagedAttention** | vLLM 核心创新，OS 式虚拟内存分页管理 KV Cache |
| **RadixAttention** | SGLang 核心创新，基数树自动缓存复用前缀 KV |
| **Continuous Batching** | 连续批处理，新请求动态加入正在处理的批次 |
| **Chunked Prefill** | 分块预填充，将长 prompt 的 prefill 分块与 decode 交错 |
| **Prefix Caching** | 前缀缓存，复用相同前缀的 KV Cache |
| **Speculative Decoding** | 推测解码，用小模型预测 + 大模型验证 |
| **PD Disaggregation** | Prefill 和 Decode 分离到不同 GPU 节点 |
| **Expert Parallelism (EP)** | 专家并行，MoE 模型的专家分布到不同 GPU |
| **Compressed FSM** | 压缩有限状态机，SGLang 结构化输出加速技术 |
| **EAGLE / DFlash** | 推测解码的 draft model 方案 |
| **MLA** | Multi-head Latent Attention，DeepSeek 的注意力机制 |
| **CUDA Graphs** | CUDA 图，减少 CPU-GPU 通信开销 |
| **APC** | Automatic Prefix Caching，vLLM 的前缀缓存实现 |

## 相关笔记

- [LLM 推理优化 2026 三路线交叉综合](explore/2026-07-28-LLM推理优化2026-三路线交叉综合-增量蒸馏.md) — 推测解码/量化/连续批处理三路线全景，与本文引擎选型互补
- [vLLM Semantic Router Fusion 混合模型路由与推测解码](explore/2026-06-23-vLLM-Semantic-Router-Fusion-混合模型路由与推测解码.md) — vLLM Fusion 模块深度拆解，本文 PagedAttention 的工程延伸
- [本地模型部署 vLLM V1 APC](explore/2026-07-14-本地模型部署-vLLMV1-APC.md) — vLLM V1 前缀缓存实战，本文 APC 概念的部署验证
- [本地模型部署 vLLM V1 APC (早期版)](explore/2026-06-22-本地模型部署-vLLM-V1_APC.md) — APC 机制演进追踪
