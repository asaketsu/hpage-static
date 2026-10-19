# NVIDIA Cosmos：物理 AI 世界基础模型平台 — 功能与使用指南

> **出处**: [NVIDIA Cosmos 官方文档](https://docs.nvidia.com/cosmos/latest/index.html) · [arXiv:2501.03575](https://arxiv.org/abs/2501.03575) · [arXiv:2503.15558](https://arxiv.org/abs/2503.15558) · [GitHub: nvidia-cosmos](https://github.com/nvidia-cosmos) · [HuggingFace](https://huggingface.co/nvidia)
> **日期**: 2026-07-22
> **标签**: #NVIDIA #Cosmos #WorldFoundationModel #PhysicalAI #世界模型 #机器人 #自动驾驶 #合成数据 #视频生成 #VLM
> **核心内容** (conf=0.95): Cosmos 是 NVIDIA 面向 Physical AI（机器人/自动驾驶/工业视觉）的世界基础模型（WFM）平台，包含 Predict（世界预测）、Transfer（可控世界生成）、Reason（物理推理）三大模型家族，每个家族迭代到 v2.5/v2 版本。核心理念：**Physical AI needs to be trained digitally first** — 先在数字世界中训练，再部署到物理世界。

---

## 一、平台定位与核心理念

### 一句话

> Physical AI needs to be trained digitally first. It needs a digital twin of itself (the policy model), and a digital twin of the world (the world model). — [arXiv:2501.03575](https://arxiv.org/abs/2501.03575)

Cosmos = **世界基础模型（World Foundation Model, WFM）平台**，目标是让开发者为自己的 Physical AI 场景构建定制化的世界模型。

### 平台四层架构

```
┌─────────────────────────────────────────────┐
│            应用层：Physical AI               │
│  机器人规划 / 自动驾驶仿真 / 工业视觉分析    │
├─────────────────────────────────────────────┤
│         模型层：Cosmos 模型家族              │
│  Predict (世界预测) / Transfer (可控生成)    │
│  Reason (物理推理) / Tokenizer               │
├─────────────────────────────────────────────┤
│         数据层：视频管护管线                  │
│  视频采集 → 清洗 → 标注 → 训练数据           │
├─────────────────────────────────────────────┤
│         基础设施：NVIDIA NIM + GPU            │
│  NIM 微服务部署 / build.nvidia.com API       │
└─────────────────────────────────────────────┘
```

### 与传统 AI 的差异

| 维度 | 传统生成式 AI | Cosmos Physical AI |
|---|---|---|
| **目标** | 文本/图像生成 | 物理世界的未来状态预测与推理 |
| **训练数据** | 互联网文本/图片 | 大规模视频（含物理动态信息） |
| **输出** | 文章/图片/代码 | 未来世界状态视频、物理推理结论 |
| **核心能力** | 语言理解与生成 | 空间+时间+物理规律理解 |
| **典型场景** | 聊天/写作/编程 | 机器人训练/自动驾驶/工业质检 |

---

## 二、三大模型家族详解

### 模型矩阵总览

| 家族 | 最新版本 | 核心能力 | 参数规模 | 架构 |
|---|---|---|---|---|
| **Predict** | 2.5 | 未来世界状态预测（Text2World/Image2World/Video2World） | 0.6B / 2B / 14B | Flow-based Diffusion |
| **Transfer** | 2.5 | 多模态可控世界生成（RGB+Depth+Segmentation） | 2B | Multi-ControlNet |
| **Reason** | 2 | 物理常识推理与具身决策 | 7B / 8B / 56B | VLM (Qwen2.5-VL base) |

---

### 2.1 Cosmos-Predict：世界预测

**核心功能**：给定文本/图片/视频输入，预测/生成未来的世界状态视频。

#### 版本演进

| 版本 | 发布时间 | 关键特性 |
|---|---|---|
| **Predict1** | 2025-01 | 初版 WFM，支持 Text2World / Video2World，含 Diffusion 和 Autoregressive 两种架构，支持多视角 |
| **Predict2** | 2025-06 | 统一 Text2Image + Video2World，引入 NATTEN 稀疏注意力（2.6× 推理加速），PyPI 发布 |
| **Predict2.5** | 2025-08+ | 统一 Text2World + Image2World + Video2World 三合一，使用 Cosmos-Reason1 作为文本编码器 |

#### Predict2.5 可用模型

| 模型 | 功能 | 链接 |
|---|---|---|
| Cosmos-Predict2-0.6B-Text2Image | 文生图（轻量） | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-0.6B-Text2Image) |
| Cosmos-Predict2-2B-Text2Image | 文生图 | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-2B-Text2Image) |
| Cosmos-Predict2-14B-Text2Image | 文生图（高质量） | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-14B-Text2Image) |
| Cosmos-Predict2-2B-Video2World | 视频→未来世界 | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-2B-Video2World) |
| Cosmos-Predict2-14B-Video2World | 视频→未来世界（高质量） | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-14B-Video2World) |
| Cosmos-Predict2-14B-Sample-GR00T-Dreams-GR1 | 后训练版（机器人场景） | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-14B-Sample-GR00T-Dreams-GR1) |
| Cosmos-Predict2-14B-Sample-GR00T-Dreams-DROID | 后训练版（机器人场景） | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-14B-Sample-GR00T-Dreams-DROID) |
| Cosmos-Predict2-2B-Sample-Action-Conditioned | 动作条件视频生成 | [HF](https://huggingface.co/nvidia/Cosmos-Predict2-2B-Sample-Action-Conditioned) |

#### 快速使用（Python API）

```python
import torch
from imaginaire.constants import get_cosmos_predict2_video2world_checkpoint
from imaginaire.utils.io import save_image_or_video
from cosmos_predict2.configs.base.config_video2world import get_cosmos_predict2_video2world_pipeline
from cosmos_predict2.pipelines.video2world import Video2WorldPipeline

# 1. 创建视频生成 Pipeline
pipe = Video2WorldPipeline.from_config(
    config=get_cosmos_predict2_video2world_pipeline(model_size="2B"),
    dit_path=get_cosmos_predict2_video2world_checkpoint(model_size="2B"),
)

# 2. 指定输入图片和文本提示
image_path = "assets/video2world/example_input.jpg"
prompt = "A robotic arm welding metal structure with sparks flying..."

# 3. 运行生成
video = pipe(input_path=image_path, prompt=prompt)

# 4. 保存结果
save_image_or_video(video, "output/test.mp4", fps=16)
```

#### 安装方式

```shell
# 推荐 uv（比 pip 快 10×）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.10 --allow-existing
uv pip install -U "cosmos-predict2[cu126]" \
  --extra-index-url https://nvidia-cosmos.github.io/cosmos-dependencies/cu126_torch260/simple

# 或通过 diffusers (>=0.34.0)
pip install diffusers
```

#### 后训练（Post-Training）场景

Cosmos-Predict 支持针对特定场景微调，官方提供了完整的后训练指南：

| 后训练场景 | 适用数据集 | 说明 |
|---|---|---|
| 通用视频预测 | 自定义数据集 | 适配任意视频域 |
| 动作条件视频预测 | Bridge / GR00T-Dreams | 机器人动作→视频预测 |
| 多视角预测 | Waymo / AgiBotWorld | 自动驾驶/机器人多摄像头 |
| 游戏场景生成 | DreamGen Bench | 游戏画面世界模拟 |
| 机器人操作 | GR00T-Dreams-GR1/DROID | NVIDIA GR00T 机器人数据 |

---

### 2.2 Cosmos-Transfer：可控世界生成

**核心功能**：基于多模态控制输入（RGB、深度图、分割图、LiDAR、HDMap 等），生成可控的世界模拟视频。

#### 版本演进

| 版本 | 关键特性 |
|---|---|
| **Transfer1** | Diffusion 条件世界模型，支持分割/深度/边缘等多种空间控制，可对不同条件加权 |
| **Transfer2.5** | Multi-ControlNet 架构，JSON 配置控制规格，支持自动控制图生成 + 多 GPU 推理 |

#### 核心应用：Sim2Real（仿真→真实）

```
仿真环境视频  →  Cosmos-Transfer  →  逼真视频
  (简单渲染)     (风格迁移+物理增强)   (可用于训练)
```

**自动驾驶场景**：
- 输入：LiDAR 点云 + HDMap（高精地图）
- 输出：逼真的驾驶场景视频
- 用途：扩充自动驾驶训练数据

#### Transfer2.5 特性

- **JSON 配置驱动**：通过 `controlnet_specs` JSON 灵活配置各模态权重
- **自动控制图生成**：自动从 RGB 计算深度/分割等控制图
- **多 GPU 推理**：支持多卡并行加速
- **World Scenario Video Generation**：场景级视频生成（不只是单帧变换）

---

### 2.3 Cosmos-Reason：物理推理

**核心功能**：物理 AI 推理视觉语言模型（VLM），理解空间、时间、基础物理规律，为机器人提供常识推理和决策规划。

#### 版本演进

| 版本 | 参数量 | 基座模型 | 关键特性 |
|---|---|---|---|
| **Reason1** | 7B / 56B | Qwen2.5-VL | 物理常识 SFT + RL，Chain-of-Thought 推理 |
| **Reason2** | 8B | — | 2D/3D 物体定位、256K 长上下文、时间戳精确推理 |

#### Reason1 架构详解

```
视频/图片 → Vision Encoder → Projector → 视频Token
                                            ↓
文本提示 → Text Tokenizer → 文本Token → 核心 LLM → Chain-of-Thought → 输出
```

- **基座**：Qwen2.5-VL-7B-Instruct（已验证）
- **训练两阶段**：
  1. **Physical AI SFT**：物理常识监督微调
  2. **Physical AI RL**：强化学习优化具身推理
- **推理方式**：长链思维（Long Chain-of-Thought），无需人工标注即可理解世界动态

#### Reason1 能力定义

**物理常识（Physical Common Sense）— 层级本体论**：
- 空间理解（Space）：距离、方向、遮挡
- 时间理解（Time）：事件先后、因果时序
- 基础物理（Physics）：重力、碰撞、摩擦

**具身推理（Embodied Reasoning）— 二维本体论**：
- 不同物理体形态的泛化（人形/轮式/机械臂）
- 环境交互推理

#### 三大应用场景

| 场景 | 说明 |
|---|---|
| **数据标注与管护** | 自动化大规模视频数据集的高质量标注与过滤 |
| **机器人规划与推理** | 作为 VLA 模型的"大脑"，将复杂指令分解为子任务 |
| **视频分析 Agent** | 城市监控/工业运营视频的根因分析与洞察提取 |

#### Reason2 新增能力

- 增强的时空理解与时间戳精度
- 物体检测：2D/3D 点定位 + 边界框坐标
- 推理解释与标签输出
- 长上下文理解（256K Token）

---

### 2.4 Cosmos Tokenizer

视频/图像 Tokenizer，将连续视频帧离散化为 Token，是 Predict 模型的核心组件。

- 支持推理和后训练
- 快速 Tokenizer（Predict2-0.6B 引入）

---

## 三、使用方式总览

### 方式对比

| 方式 | 适合场景 | 门槛 | 灵活性 |
|---|---|---|---|
| **build.nvidia.com API** | 快速试用/原型验证 | 仅需 API Key | ⭐⭐ |
| **NIM 微服务** | 企业级部署 | Docker + GPU | ⭐⭐⭐ |
| **PyPI 安装** | 本地开发/后训练 | Python 3.10 + GPU (Ampere+) | ⭐⭐⭐⭐⭐ |
| **HuggingFace diffusers** | 集成到现有 Pipeline | diffusers>=0.34.0 | ⭐⭐⭐⭐ |

### API 调用（build.nvidia.com）

Cosmos 模型在 NVIDIA build 平台提供托管 API：

| 模型 | API Endpoint |
|---|---|
| Cosmos-Reason2-8B | `https://build.nvidia.com/nvidia/cosmos-reason2-8b` |
| Cosmos-Transfer2.5-2B | `https://build.nvidia.com/nvidia/cosmos-transfer2_5-2b` |
| Cosmos3-Nano | `https://build.nvidia.com/nvidia/cosmos3-nano` |
| Cosmos3-Nano-Reasoner | `https://build.nvidia.com/nvidia/cosmos3-nano-reasoner` |
| Cosmos-Dataset-Search | `https://build.nvidia.com/nvidia/cosmos-dataset-search` |

> **注**：Cosmos3-Nano / Cosmos3-Nano-Reasoner 是 2026 年新增的轻量推理模型，面向边缘部署（如 Jetson）。

### 本地安装系统需求

| 项目 | 要求 |
|---|---|
| GPU | NVIDIA Ampere 架构+（RTX 30 / A100 / H100） |
| CUDA | 12.6 |
| OS | Linux x86-64 |
| Python | 3.10 |
| glibc | ≥2.31 (Ubuntu ≥22.04) |

---

## 四、Cosmos Guardrail 安全护栏

Cosmos 内置双层安全机制：

| 层级 | 功能 |
|---|---|
| **Pre-Guard** | 输入安全检查（拦截有害/不当输入） |
| **Post-Guard** | 输出安全检查（拦截有害/不当生成内容） |

---

## 五、Post-Training 完整工作流

Cosmos 的核心竞争力之一是完善的后训练生态——不是给你一个预训练模型就完了，而是提供针对各种数据集的后训练脚本：

```
预训练 WFM → 选择后训练方案 → 准备数据集 → 运行后训练脚本 → 得到定制化世界模型
```

### 官方提供的后训练路径

```
Cosmos-Predict2.5
├── 通用 Post-Training Guide
├── Auto Multiview (Waymo)          → 自动驾驶多视角
├── Action-Conditioned              → 机器人动作→视频
├── Cosmos-NeMo-Assets              → 游戏场景
├── LoRA Post-Training              → 轻量微调
└── DreamGen Bench                  → 游戏世界生成

Cosmos-Predict2
├── Custom Dataset
├── Action-Conditioned
├── Cosmos-NeMo-Assets
├── AgiBotWorld-Alpha              → 智元机器人数据
├── GR00T-Dreams-GR1/DROID         → NVIDIA 机器人数据
└── Text2Image Post-Training

Cosmos-Transfer2.5
├── 通用 Post-Training Guide
├── Auto Multiview (HDMap)          → 自动驾驶地图条件
└── World Scenario Video Generation

Cosmos-Reason1
├── Post-Training Guide
├── Rejection Sampling              → 推理质量筛选
└── Benchmark Example
```

---

## 六、Physical AI 生态关联

Cosmos 不是孤立产品，它是 NVIDIA Physical AI 全栈的核心组件：

```
              NVIDIA Physical AI 全栈
                     |
     ┌───────────────┼───────────────┐
     |               |               |
  数据层          模型层          部署层
     |               |               |
 Cosmos Video    Cosmos WFM     Jetson Thor
 Curation Pipeline  (Predict/    (边缘推理芯片)
 (视频采集管护)    Transfer/     Isaac Sim
                   Reason)       (仿真验证)
                     |               |
                     └───────┬───────┘
                             |
                         GR00T
                     (机器人基础模型)
```

### 生态合作伙伴（GTC 2026 披露）

| 领域 | 合作方 |
|---|---|
| **自动驾驶** | 现代、LG、VinFast |
| **工业制造** | FANUC、ABB、KUKA、YASKAWA |
| **人形机器人** | Figure、Boston Dynamics、宇树、1X、AGIBOT |
| **物流** | KION + Accenture + GXO |
| **医疗** | CMR Surgical、Johnson & Johnson |

---

## 七、与竞品对比

| 平台 | 核心定位 | 优势 | 劣势 |
|---|---|---|---|
| **NVIDIA Cosmos** | Physical AI WFM 平台 | 全栈（数据→模型→部署）、开源开放、NVIDIA 生态深度集成 | 需要 NVIDIA GPU、学习曲线陡 |
| **Genesis World** | 物理引擎 + 世界模型 | 43M FPS 极速物理仿真（RTX 4090） | 生态较小、无商业支持 |
| **Google Genie 2** | 通用世界模型 | Google 研究实力 | 未开源、仅 Demo |
| **WorldVLA/WAM** | 学术世界模型 | 论文创新（WAM > VLA 鲁棒性） | 无工程化平台 |

---

## 八、实践启发

### 对机器人/具身智能项目

1. **GR00T-Dreams 数据集**：Cosmos 可生成合成机器人操作视频，用于训练 VLA 策略模型。双轮腿机器人项目可利用 Cosmos 生成平衡控制场景的合成训练数据。

2. **Reason 作为机器人大脑**：Cosmos-Reason 可作为高层规划器——给定环境视频+任务指令，Reason 输出下一步动作的文本描述，底层控制器（如 LQR）执行。

3. **Sim2Real 数据增强**：Transfer 模型可将简单仿真渲染（如 Isaac Sim）转换为逼真视频，缩小 sim-to-real gap。

### 对 AI Agent 开发

1. **视频理解 Agent**：Reason 模型可作为视频分析 Agent 的核心组件，提供物理常识推理能力。
2. **合成数据生成**：Predict 可为计算机视觉项目生成无限训练数据。
3. **世界模型作为环境模拟器**：类似 RL 中的环境，Cosmos 可预测"如果执行动作 A，世界会变成什么样"。

### Jetson 边缘部署

- Cosmos3-Nano 系列是专为边缘设计的轻量版本
- Reason2-8B 参数量适中，Jetson Orin 可推理
- Predict2-0.6B 是最小的生成模型，适合边缘 PoC

---

## 九、交叉关联

| 笔记/项目 | 关联点 |
|---|---|
| **World Models 2026 范式转移** | Cosmos 是工业三巨头之一（vs Genesis 1.0 / Newton） |
| **NVIDIA Isaac GR00T 平台** | Cosmos 是 GR00T 机器人平台的 World Model 底座 |
| **AgentLoop 经验自进化** | Cosmos 世界模型 = "环境的经验"；经验自进化 = "Agent 行动的经验" |
| **双轮腿机器人 V2** | Cosmos 可生成合成训练数据 + Reason 作为高层规划器 |
| **ESP-VISION 边缘 AI** | Cosmos3-Nano 可作为边缘视觉推理候选 |
| **无感 FOC 虚拟传感器** | Cosmos Predict 可生成电机运行视频用于训练虚拟传感器 |

---

## 十、信息来源清单

| 来源 | 类型 | 可信度 | URL |
|---|---|---|---|
| NVIDIA Cosmos 官方文档 | 官方 | 确证 | https://docs.nvidia.com/cosmos/latest/index.html |
| arXiv:2501.03575 — Cosmos WFM Platform | 学术 | 确证 | https://arxiv.org/abs/2501.03575 |
| arXiv:2503.15558 — Cosmos-Reason1 | 学术 | 确证 | https://arxiv.org/abs/2503.15558 |
| GitHub Cosmos-Predict2 | 官方代码 | 确证 | https://github.com/nvidia-cosmos/Cosmos-Predict2 |
| HuggingFace nvidia/Cosmos-* | 官方模型 | 确证 | https://huggingface.co/nvidia |
| build.nvidia.com Cosmos Models | 官方 API | 确证 | https://build.nvidia.com/nvidia/cosmos-reason2-8b 等 |
| NVIDIA Isaac GR00T 发布稿 | 官方 | 确证 | https://investor.nvidia.com/news/... |

---

## 十一、数据缺口与局限

| 缺口 | 说明 |
|---|---|
| Cosmos3 详细架构 | Cosmos3-Nano/Reasoner 的技术报告尚未公开发布 |
| Transfer2.5 完整 API | 官方文档为 SPA，子页面 404（JS 渲染），Quickstart 代码需从 GitHub 获取 |
| Jetson 性能基准 | 官方仅标注 Ampere+ GPU，未提供 Jetson 具体推理延迟数据 |
| 后训练显存需求 | 各后训练方案的具体 VRAM 需求未在 README 中统一列出 |
| Cosmos-Reason2 论文 | Reason2 技术报告/论文尚未在 arXiv 发布 |
| 许可证细节 | NVIDIA Open Model License 的商用条款需逐条审查 |

## 相关笔记
- [NVIDIA-Cosmos物理AI世界基础模型深度研究](2026-07-21-NVIDIA-Cosmos物理AI世界基础模型深度研究.md)
- [NVIDIA-GR00T端到端人形机器人实操教程](2026-07-22-NVIDIA-GR00T端到端人形机器人实操教程.md)
- [NVIDIA-Isaac-GR00T-人形机器人平台](2026-06-11-NVIDIA-Isaac-GR00T-人形机器人平台.md)
