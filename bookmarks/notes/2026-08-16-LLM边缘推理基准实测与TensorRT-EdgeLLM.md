# LLM 边缘推理基准实测与 TensorRT Edge-LLM 部署新路径

#边缘推理 #Jetson #TensorRT #量化部署 #基准测试

> 日期：2026-08-16 ｜ 类型：技术调研笔记 ｜ 来源：arXiv 2604.24785v2 + NVIDIA Jetson AI Lab 官方教程
> 关联：衔接 2026-08-15 PTX Tensor-Core GEMM 多精度研究、nexa-local-inference skill（Ollama on Jetson Orin Nano Super）

---

## 一、核心结论（先看这个）

1. **加速器 vs CPU 能效差距高达 40×**——RPi5 纯 CPU 推理 27–77 MJ/Mtok，加 NPU/GPU 后降到 0.6–5.5 MJ/Mtok。边缘部署 LLM 没有加速器等于浪费一个数量级的能量。
2. **Jetson Orin Nano Super（我们的设备）GPU offload 只带来 1.24×–1.82× 能效增益**——因为它 CPU 基线本来就强（6 核 A78AE），不像 RPi5 那样夸张。但**绝对吞吐全场第一**：1.5B 模型 9.37–9.59 tok/s，约为 M5Stack NPU 的 4 倍。
3. **NVIDIA 官方新推出 TensorRT Edge-LLM**：纯 C++ 推理路径（无 Python 解释器），Orin（sm_87）支持 FP16 + INT4 AWQ；FP8/NVFP4 仅 Thor（sm_110）可用。这是 Orin 上替代 Ollama 的性能路线。
4. **M5Stack AX630C（$99.90, 3.2 TOPS）吞吐密度 Tps/m³ 全场第一**——空间受限场景（无人机/卫星地面站）的最优解，54×54×13mm 体积跑出 2.42–3.44 tok/s。
5. 与 PTX GEMM 研究结论互相印证：**推理规模下约束是内存带宽不是算力**——Jetson 102GB/s LPDDR5 共享内存是 1.5B–3B 模型能跑顺的物理基础。

---

## 二、内容整理（功能清单：这篇论文/工具提供了什么）

### 2.1 论文《Cloud to Edge: Benchmarking LLM Inference on Hardware-Accelerated Single-Board Computers》(arXiv 2604.24785v2)

- **多维度基准方法论**：联合评估推理性能（吞吐/TTFT）+ 硬件效率（能耗 MJ/Mtok）+ 物理约束（吞吐密度 Tps/m³）
- **两个新复合指标**：
  - 吞吐密度 Tps/m³ = 吞吐 ÷ 设备外部体积（空间受限场景选型用）
  - MJ/Mtok = 每百万 token 能耗（能量受限场景选型用）
- **四平台实测**：M5Stack LLM（AX630C NPU 3.2 TOPS）/ RPi5 纯 CPU / RPi5+Hailo-10H（40 TOPS NPU）/ Jetson Orin Nano Super（67 TOPS GPU）
- **模型矩阵**：DeepSeek-R1-Distill-Qwen-1.5B、Qwen2.5（0.5B/1.5B/Instruct/Coder）、Llama 3.2（1B/3B），全部 Q4_K_M
- **开放数据**：OSF (osf.io/5r9t4) + GitHub 基准套件 (kaze-technologies/LLM-Edge-Benchmarking-Suite)

### 2.2 TensorRT Edge-LLM（NVIDIA 官方，github.com/NVIDIA/TensorRT-Edge-LLM）

- 高性能 **C++ 推理运行时**，面向嵌入式 LLM/VLM，运行时无 Python 解释器参与
- 工作流三步：Python 导出量化 ONNX（x86/Thor）→ 目标设备上编译 TensorRT engine（**必须在本机构建**）→ 原生二进制加载服务
- 量化支持：INT4 AWQ（4× 压缩）、NVFP4（4×）、FP8（2×）——**Orin 只支持 FP16/INT4，Thor 才有 FP8/NVFP4**
- 模型支持面：Llama 3.x、Qwen3/3.5/3.6（0.6B–27B）、Qwen3-VL、InternVL3/3.5、Phi-4-Multimodal、Nemotron-Nano（Mamba2 混合架构）、Alpamayo R1（机器人 VLA）
- C++ API 三调用集成：create runtime → capture CUDA graphs → `handleRequest()` 每查询

---

## 三、关键实测数据（Jetson 相关，Q4_K_M，100 token 生成，n=5）

| 模型 | 指标 | M5Stack NPU | RPi5 CPU | RPi5+Hailo | Jetson CPU | **Jetson GPU** |
|------|------|------------|----------|------------|-----------|---------------|
| R1-Distill-1.5B | tok/s | 2.42 | 0.32 | 1.53 | 6.01 | **9.59** |
| | MJ/Mtok | **0.57** | 33.24 | 3.47 | 2.09 | 1.15 |
| Qwen2.5-1.5B | tok/s | – | 0.27 | 4.37 | 4.21 | **9.37** |
| | MJ/Mtok | – | 35.30 | **1.30** | 1.38 | 1.11 |
| Qwen2.5-1.5B-Instruct | tok/s | 2.55 | 0.30 | 6.34 | 6.90 | **9.09** |
| | MJ/Mtok | **0.57** | 35.31 | 0.88 | 1.83 | 1.17 |
| Llama3.2-1B | tok/s | 3.44 | 0.39 | – | 9.51 | **10.96** |
| | MJ/Mtok | **0.41** | 27.87 | – | 1.64 | 1.23 |
| Llama3.2-3B | tok/s | – | 0.14 | 1.01 | 4.30 | **6.31** |
| | MJ/Mtok | – | 76.64 | 5.51 | 3.04 | **1.72** |

**要点提炼**：
- Jetson GPU 在 3B 模型上能效反超所有对手（1.72 MJ/Mtok），模型越大 GPU 优势越明显——NPU 固定算子图对小模型优化好，大模型吃带宽
- M5Stack 的 MJ/Mtok 数字最好（0.41–0.57）但吞吐只有 2–3.4 tok/s：**极低功耗 ≠ 高性能**，选型看约束
- RPi5+Hailo NPU 相对 CPU 能效提升 9.57×–39.97×，是 RPi 生态的质变
- TTFT 方面 Jetson GPU 1.38–3.16ms 级（流式首 token），交互体验最佳

### 硬件规格对照

| 设备 | 体积 | 价格 | 算力 | 内存 |
|------|------|------|------|------|
| M5Stack LLM | 54×54×13mm | $99.90 | 3.2 TOPS INT8 | 4GB（1GB 可用）+3GB NPU RAM |
| RPi5 | 85×56×17mm | $222.75 | – | 8GB LPDDR4X |
| RPi5+AI HAT+ | 85×56×20mm | $451.83 | 40 TOPS INT4 | 8GB+8GB NPU |
| **Jetson Orin Nano Super** | 100×79×21mm | $304.78 | 67 TOPS INT8 | 8GB LPDDR5 **102GB/s** |

---

## 四、使用性评估（好不好用/适用场景）

| 维度 | 评价 |
|------|------|
| 论文方法论 | ⭐⭐⭐⭐⭐ 首次把物理体积纳入 LLM 选型指标，IoT/无人机场景直接可用 Tps/m³ 排序 |
| 论文局限 | 只测 Ollama 系 runtime（原生/Hailo 定制/StackFlow），TensorRT-LLM/ONNX RT 留作未来工作；无冷启动/热节流数据；模型仅到 3B |
| TensorRT Edge-LLM | ⭐⭐⭐⭐ 生产级路径（无 Python 开销），但工程门槛高：需 x86/Thor 导出 + 本机编译 engine + 20-50GB 存储 |
| 与 Ollama 对比 | Ollama 适合快速原型（GGUF 生态全）；Edge-LLM 适合部署（C++ 常驻、CUDA graph 捕获），两者是原型→生产的两阶段 |

**适用场景判定**：
- 空间极限（无人机载荷、可穿戴）→ M5Stack AX630C
- 已有 RPi5 生态 → 加 AI HAT+（$229 升级换 40 TOPS）
- 综合性能+二次开发（我们的情况）→ **Jetson Orin Nano Super**：吞吐第一、生态最全、GPIO/DLA/PVA 可扩展
- Thor 级新项目 → FP8/NVFP4 全开，8B VLM 本地跑

---

## 五、归纳总结：指导性意见（何时用/何时不用/替代方案）

1. **何时用 TensorRT Edge-LLM**：模型固定（Qwen3-4B 级）、追求最低延迟和能效、要嵌入 C++ 应用（机器人/kiosk/工业检测）。官方教程明确 Orin Nano 8GB 可跑 Qwen3-4B INT4 AWQ。
2. **何时继续用 Ollama**：需要频繁换模型试验、GGUF 生态依赖、或运行 3B 以下小模型（论文数据显示此规模 Ollama 已够用，Jetson GPU 9-11 tok/s）。
3. **何时不值得**：云端 API 可用且无隐私/离线硬约束时，别折腾边缘；3B 以下纯 CPU 推理（RPi5 0.14-0.86 tok/s）不可用于交互场景，只能做批处理。
4. **替代路线**：llama.cpp（跨平台 GGUF）/ MLC-LLM（通用编译）/ vLLM（服务器级，Orin 支持有限）。EdgeReasoning 论文（arXiv 2511.01866）提醒：Orin Ampere 架构不支持 INT4 计算回退 INT8，AWQ W4A16 实际跑 INT8 kernel——**量化宣传与硬件实际执行有落差**。
5. **与 PTX GEMM 研究的衔接**：GEMM 研究证明 INT4 原生 mma.sync 比 WMMA 快 2.9-4.3×；Edge-LLM 的 INT4 AWQ 正是利用这类原生低精度路径。若要极致性能，手写 kernel（PTX 路线）> Edge-LLM > Ollama。

---

## 六、案例可寻

- **官方教程案例**：Qwen3-4B-Instruct-2507 INT4 AWQ 在 Jetson Orin Nano 8GB 完整跑通（导出→编译→推理）；Cosmos-Reason2-8B VLM NVFP4 在 Thor
- **论文场景**：无人机、卫星地面站、坚固化便携作业、OT/国防内网（数据不出边界是硬约束）
- **我们自己的案例**：nexa-local-inference skill 已在 Orin Nano Super 上跑 Ollama——本文给出的下一步演进就是 Edge-LLM 路线
- 踩坑案例（教程 Troubleshooting 官方记录）：
  - Jetson 上裸 `pip install torch` 会挂（`_dlpack_exchange_api` AttributeError）——必须用 NVIDIA PyTorch 容器 + `--system-site-packages` venv + `pip install --no-deps .`
  - FP8 导出 8B 模型需 6× 模型大小的 GPU VRAM + 20× CPU RAM——显存不够改用 INT4 AWQ
  - Orin Nano 上 `make -j$(nproc)` 会 OOM——降为 `make -j4` 或串行

---

## 七、使用方法借鉴（可直接抄的命令）

### 7.1 论文基准套件（想复现或测自己的板子）

```bash
git clone https://github.com/kaze-technologies/LLM-Edge-Benchmarking-Suite
# Python harness 对接各 runtime HTTP API，自动 warmup + n=5 计时 + 功率计读数
# 完整数据: https://osf.io/5r9t4
```

### 7.2 TensorRT Edge-LLM 三步工作流（Orin Nano 跑 Qwen3-4B）

```bash
# Step 1: x86 主机导出（量化为 INT4 AWQ ONNX）
tensorrt-edgellm-quantize llm \
  --model_dir Qwen/Qwen3-4B-Instruct-2507 \
  --output_dir $MODEL_NAME/quantized \
  --quantization int4_awq

# Step 2: Orin Nano 本机编译 runtime + engine（engine 必须本机构建！）
git clone https://github.com/NVIDIA/TensorRT-Edge-LLM.git
cd TensorRT-Edge-LLM && git submodule update --init --recursive
export EDGELLM_PLUGIN_PATH=$(pwd)/build/libNvInfer_edgellm_plugin.so
make -j4   # Orin Nano 限内存，禁止 -j$(nproc)

# Step 3: C++ 推理（生产集成三调用）
# createRuntime() → captureCudaGraphs() → handleRequest()
```

### 7.3 精度-平台兼容速查（抄进部署 checklist）

| 精度 | 内存节省 | Orin (sm_87) | Thor (sm_110) |
|------|---------|--------------|---------------|
| FP16 | 基线 | ✅ | ✅ |
| FP8 | 2× | ❌ | ✅ |
| INT4 AWQ | 4× | ✅ | ✅ |
| NVFP4 | 4× | ❌ | ✅ |

---

## 八、对我们体系的改进建议

| 优先级 | 建议 | 落点 |
|--------|------|------|
| P1 | nexa-local-inference skill 补充 Edge-LLM 备选路线（当前只有 Ollama） | skill patch |
| P2 | 用论文的 MJ/Mtok 口径给 Jetson 上的 TTS/LLM 服务做能效基线，纳入 system-info 巡检 | 待用户指令 |
| P2 | edge-llm-quantization skill 增加"Orin 无 FP8/INT4 计算回退 INT8"的坑点说明 | skill patch |
| P3 | M5Stack AX630C 作为机器人/移动场景候选记录备查 | 决策备选 |

**参考来源**：
- arXiv 2604.24785v2（Cloud to Edge 基准论文）
- jetson-ai-lab.com/tutorials/tensorrt-edge-llm（官方教程）
- github.com/NVIDIA/TensorRT-Edge-LLM
- EdgeReasoning arXiv 2511.01866（W4A16 在 Orin 回退 INT8 的证据）

---

## 九、查询拓展（延伸问题与检索线索）

- **Q: Jetson Orin Nano Super 上 Ollama 换 TensorRT Edge-LLM 能快多少？** 线索：NVIDIA 官方 benchmark 表（nvidia.github.io/TensorRT-Edge-LLM 性能页）有 AGX Thor 默认设置数据；Orin 需自测，预期来自去除 Python 开销 + CUDA graph 捕获
- **Q: 8GB 统一内存跑 Qwen3-4B INT4 后还剩多少余量跑 TTS/视觉任务？** 线索：INT4 后权重 ~2.4GB + KV cache + 系统（LuxTTS/F5-TTS 常驻约 3-4GB），需实测并发余量
- **Q: M5Stack AX630C 国内可购性和 StackFlow 中文资料？** 线索：淘宝 M5Stack 官方店；StackFlow 文档主要在 axcl 生态
- **Q: 论文的 Tps/m³ 指标怎么算的？** 线索：tok/s ÷ 设备外部体积（mm³→m³），排除电源/外壳/散热间隙
- **Q: Thor 之外，AMD Ryzen AI / 高通 Hexagon NPU 有无同类官方 runtime？** 线索：AMD Lemonade / QNN SDK，留在下期调研

## 十、趋势判断

1. **边缘 LLM runtime 正在从"Python 胶水"收敛到"C++ 原生"**：Ollama（易用）→ llama.cpp（性能）→ TensorRT Edge-LLM（生产 C++）。三阶段与服务器端 vLLM 路径完全同构，趋势明确。
2. **量化格式进入平台分裂期**：INT4 AWQ 全平台通吃，FP8/NVFP4 成 Thor/Ada+ 专属，Orin 世代被锁死在 INT4——**买边缘硬件前先查 sm_ 架构支持的精度表**，这将成为选型新常识。
3. **基准方法论从单轴走向多维**：只看 tok/s 的时代结束，MJ/Mtok（能耗）+ Tps/m³（体积）组合才是 IoT 场景的决策口径，预计 2026 下半年更多论文跟进这套复合指标。
4. **带宽是边缘推理的终极约束**（与 PTX GEMM 研究互证）：102GB/s LPDDR5 是 Jetson 跑 3B 模型的物理天花板，下一代 unified memory 带宽提升比 TOPS 数字更值得关注。
5. **7B 以下模型边缘化已成定局**：论文 $350 以下设备全部跑通 0.5B–3B Q4 模型，剩余战场在 4B–8B（Edge-LLM 教程主线）和 VLM 多模态。

## 相关笔记

- [手写 PTX Tensor-Core GEMM 多精度研究](./2026-08-15-手写PTX-TensorCore-GEMM多精度研究-L4.md) — 带宽约束结论互证的底层算子研究
- [模型兼容Jetson和RK3588-跨平台边缘AI部署](../2026-08-13-模型兼容Jetson和RK3588-跨平台边缘AI部署工程实践.md) — 跨平台边缘部署工程实践
- [2026本地大模型部署指南-从8GB到万亿参数](./2026-08-10-2026本地大模型部署指南-从8GB到万亿参数.md) — 本地部署全景
- [DeepSeek-V4-Flash A100部署-推理框架对比](./2026-08-12-DeepSeek-V4-Flash-A100部署-推理框架与基础设施形态对比.md) — 数据中心侧推理架构对照
