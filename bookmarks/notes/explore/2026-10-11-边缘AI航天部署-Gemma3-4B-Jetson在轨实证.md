# 边缘AI航天部署-Gemma3-4B-Jetson在轨实证

> 探索日期 2026-10-11 | 类型 auto-explore | 来源 6+（arXiv 2606.18271 / IEEE Spectrum / 新华网 / 科学网 / NavyaAI 实测 / Jetson AI Lab）
> 前序笔记：[2026-10-10-边缘AI航天部署-语义压缩下行](./2026-10-10-边缘AI航天部署-语义压缩下行.md)

**标签**：#边缘AI #航天 #Gemma3 #Jetson #在轨推理 #VLM #量化部署 #多Agent

---

## 一、摘要

昨日笔记讲清了「为什么要星上语义压缩」（下行带宽硬瓶颈），今日的补全拼图是「用什么模型在轨跑」：2026-04-16，NASA JPL 在 Loft Orbital 的 YAM-9 卫星上完成 **NAVI-Orbital**——业界首次视觉语言模型（VLM）在轨自主多模态推理。核心配置惊人地朴素：**Hugging Face 可直接下载的 Gemma 3 4B 开源权重 + Q4_0 GGUF 量化 + NVIDIA Jetson Orin AGX**，零微调，8GB 显存即跑。同一周，中国三体计算星座宣布已完成 10 个 AI 模型在轨部署验证。开源 4B 级模型 + 消费级边缘板 = 航天可用，这是 2026 年边缘 AI 的分水岭事实。

```
NAVI-Orbital 数据链（与昨日语义压缩管线逐层对应）:
上行: 操作员 plain-English prompt + 目标标签列表（替代传统指令序列）
在轨: Gemma3-4B(Q4_0 GGUF+mmproj) 逐景分类→生成文本描述→结构化记录
下行: 每图仅数十 KB 文本摘要；高价值景才回传原图
对话: 有 ISL 星间链路时可近实时追问（scripted QA / interactive chat）
```

## 二、关键发现

### 2.1 NAVI-Orbital：首次在轨 VLM 推理的工程账本

- **模型**：Gemma 3 4B instruction-tuned，**Q4_0 GGUF 量化 + 专用 mmproj 多模态投影器**做视觉-语言融合；4bit 下 4B 参数仅需 8GB 显存
- **硬件**：YAM-9 计算集群含抗辐照 FPGA/CPU/GPU 异构三节点；Gemma 跑在 **Jetson Orin AGX**（Comp2，248 TOPS GPU，OpenEmbedded 系统）；整星太阳能供电 150-500W
- **性能**：AID 基准 7960 张图 **zero-shot 88.16% 准确率**（同一权重，非专用训练）；工程模型实测 **每图 VLM 周期 26.6s**（GPU 版 13min/5图 vs 纯 CPU 37min+）
- **上下文策略**：context 20,000 tokens（为 Pan-and-Scan 高分辨率图块 embedding 留空间），输出上限 1,000 tokens 约束单图延迟与显存
- **架构**：LangGraph conductor + 三自包含 agent（orchestrator/detector/dialogue）+ FastAPI 生命周期端点（/start /stop /kill /health）；agent graph 独立 multiprocessing.Process，**杀 worker 即回收 GPU 显存，控制面不重启**——功率/显存受限平台的教科书级进程隔离
- **执行分工**：transformer 层全量 offload GPU，4 条 CPU 线程管 tokenization/采样/图像 IO/LangGraph 状态

### 2.2 部署教训：Docker 翻车，裸机救场

飞行配置最初想用容器化部署，但**当时所有容器镜像都无法在目标 CPU/GPU 上稳定提供硬件加速**（Python 3.12 + CUDA 库冲突）→ 飞行版改为**裸机 Python venv**。发射后 2026-Q1 NVIDIA 更新容器才在 Flatsat 补验成功容器化。与 DUCK ONNX 部署链的经验同构：边缘平台上「官方容器 ≠ 能跑」，最终都要落到对板子 CUDA/l4t 版本的实测。

### 2.3 Jetson 上 Gemma 3 4B 的实测性能阶梯（社区数据）

- **Orin Nano 8GB**（Q4_K_M, Ollama）：单用户 ~9.5 tok/s（54s 端到端延迟）；**16 并发直接失败**——4B 级在 8GB 板只够单人批处理，不够多用户服务
- **Orin NX**（Gemma 3n E4B, Q4_K_XL）：12 tok/s，语音助手全链可用（wake<100ms + Whisper CPU + LLM 12tok/s + TTS<100ms 首字节）
- **AGX Orin**（TensorRT-LLM，3B 级参考）：80-120 tok/s，但引擎编译 30-90min，只适合高量产固化
- 对照：NAVI 选 Orin AGX 而非 Nano，正是「在轨 26.6s/图」与「跑不动」的分界——**板型选择由延迟预算反推**

### 2.4 中美在轨 LLM 格局对照

- 美国：Booz Allen 2024 首个 LLM 上 ISS（HPE Spaceborne Computer-2）→ 2025 Space Llama（Llama 3.2 量化版，ISS 数字助手）→ 2026 NAVI-Orbital（首个自主航天器上 VLM，非 ISS 有人站）
- 中国：三体计算星座 2025-05 首发一箭十二星，整轨互联 5POPS/30TB；单星最高 744TOPS；搭载 80 亿参数天基模型（业内首个多任务在轨模型）；2026-02 已完成 **10 个 AI 模型与应用在轨部署验证** + 6 星建链，水环境三星协同试验全链跑通
- 共同点：走的都是「开源权重 + 量化 + 边缘板」路线，无人再等专用抗辐照 AI 芯片成熟

## 三、对工作的价值

- **jbot 本地推理直接可复现**：我自己的 Jetson Orin Nano Super（67 TOPS）正是 NAVI 的地面同款试验台——Gemma 3 4B Q4 GGUF（Ollama 一条命令）即可复现「8GB 显存跑 4B VLM」配置，与 nexa-local-inference skill 的现有链路零冲突，属于低成本验证
- **多 Agent 编排的边缘工程模式**：NAVI 的「FastAPI 控制面 + subprocess 隔离 agent graph + 杀进程回收显存」三件套，可直接抄进 Hermes 任何 GPU 受限部署（包括 LuxTTS daemon 的显存管理）；LangGraph 在功率受限平台跑通三 agent 协作 = 多 agent 编排的边缘可行性实证
- **ASC 云台项目的架构参照**：NAVI 证明 4B VLM 在 8GB 边缘设备可用，ASC 的「笔记本推理」档位未来若下沉到 Jetson 端侧，模型选型锚点就是 4B Q4 级
- **与昨日笔记闭环**：昨日「压缩即 embedding」（传信息不传图）+ 今日「VLM 生成文本摘要」（NAVI 下行每图仅数十 KB）= 语义压缩的两条技术路线在轨都已验证

## 四、行动建议

1. 复现项：jbot 上 `ollama run gemma3:4b` 实测 tok/s 与显存占用，与 NAVI 的 26.6s/图对照，落到 nexa-local-inference skill 的模型选型表
2. 观察项：NAVI 下一代（RAG 接地 + 分割/跨帧跟踪）与三体星座 10 模型在轨清单的公开细节，季度回查
3. 复用项：NAVI 的 subprocess GPU 回收模式可充实 edge-llm-quantization skill 的部署章节

## 五、一页速查

> - 2026-04-16 NAVI-Orbital：Gemma3-4B(Q4_0 GGUF) 在 Jetson Orin AGX 上在轨 zero-shot 推理，AID 88.16%，每图 26.6s
> - 零微调：换观测目标 = 改 prompt，不改模型不改软件——开源权重的开放词表能力是关键
> - 8GB 显存门槛：4B@4bit 是 8GB 统一内存板的甜点位；Orin Nano 只够单人用，多人服务需 AGX 级
> - 飞行教训：容器在边缘 GPU 上不可靠时，裸机 venv 是正路；进程隔离回收显存是标配
> - 中美并行：Space Llama(ISS) / NAVI(自主卫星) / 三体 8B 天基模型+10 模型在轨验证
> - 下行范式转变：数十 KB 文本摘要替代数百 MB 原图，"tactical satellite" 成为可能

## 六、待深入

- NAVI 的 mmproj 视觉投影器在 Q4_0 下的精度损失量化（论文附录 vs FP16 基线）
- 三体星座 8B 天基模型的具体部署形态（GGUF? 昇腾? 星载操作系统 API）公开信息仍少
- 在轨单粒子翻转（SEU）对推理结果的静默污染——NAVI 未讨论，是下一批论文的必争点

## 七、来源

- arXiv:2606.18271 — NAVI-Orbital: First In-Orbit Demonstration of a Zero-Shot VLM for Autonomous EO（NASA JPL + Loft Orbital）
- IEEE Spectrum — NASA Uses AI to Analyze Satellite Images in Orbit（2026 报道）
- 新华网/科学网/科创板日报 — 三体计算星座首发与 2026-02 在轨验证进展
- NavyaAI — Jetson Orin Nano LLM Benchmark: 158 TPS at 8 Watts
- iotdigitaltwinplm — LLMs on Jetson Orin Benchmarked 2026（TensorRT-LLM vs vLLM）
- julien.cloud / my-gemma.com — Gemma 3/3n Jetson 部署实战
