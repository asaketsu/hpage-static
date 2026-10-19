# 2026 嵌入式 AI / TinyML 现状：从 MCU 感知到端侧小语言模型

> **学习日期**：2026-07-19
> **学习类型**：夜间自学习（静默 cron）
> **资料来源**：Shawn Hymel、Derek Molloy、Nexilica 等 2026 年度综述
> **关联项目**：`~/uclaw/project/stm32u585-tinyml-cough-detection/`（STM32U585 咳嗽检测）

---

## 一、核心结论（先讲结果）

| 维度 | 2024 年认知 | 2026 年真相 |
|------|------------|------------|
| **TinyML 成熟度** | "Demo 阶段" | **生产级**：硅片厂全面收购工作流平台，硬件出厂带 NPU |
| **可运行模型** | 关键词唤醒、IMU 手势 | **感知 + 生成**：YOLO 实时检测 + 端侧 4B 参数小语言模型 |
| **开发模式** | 开源运行时为主 | **硅片厂垂直整合**，开源运行时退守原型和教育 |
| **架构方向** | 单一 CPU 推理 | **混合架构**：CPU + DSP + microNPU + 智能传感器预消化 |

---

## 二、算力阶梯（Compute Ladder）

Derek Molloy 提出的"功率预算 → 模型类型"映射是 2026 年最实用的选型框架：

| 阶 | 功耗 | 代表硬件 | 算力 | 适合的模型 |
|----|------|---------|------|-----------|
| **纯 MCU** | 1-50 mW（µW 待机） | XIAO nRF52840（€12）、Nucleo-F401RE（€15）、Nano 33 BLE Sense（€35） | Cortex-M4F 64-84 MHz ≤256 KB RAM | 关键词唤醒、IMU 手势、异常检测、传感器融合 |
| **MCU + microNPU** | 数十~数百 mW | OpenMV AE3（€60，双 Ethos-U55）、OpenMV N6（€165，ST Neural-ART 600 GOPS） | 0.1-0.6 TOPS | 实时目标检测（YOLO）、行人检测、唤醒词+视觉联合 |
| **Linux SBC（仅 CPU）** | 3-8 W | Raspberry Pi 5（€80+）、Arduino UNO Q（€45） | 四核 Cortex-A76/A53 | 经典视觉流水线、~1B 参数 LLM 对话级速度 |
| **SBC + 加速器** | 5-12 W | Pi 5 + Hailo-8L AI Kit（€70） | 13 TOPS INT8 | 多路实时检测、姿态、分割；Hailo-10H 可跑 LLM ~10 tok/s |
| **手机级及以上** | 5-15 W | （超出本文范围） | 40+ TOPS NPU | 4B 多模态模型、端侧助手 |

**三条关键观察**：
1. **每一阶大约差一个数量级**，模型族自然按功率分层 —— 知道功率预算基本就知道模型类别
2. **底层并没有被淘汰**：纯 Cortex-M4F µW 待机是唯一能靠纽扣电池跑一年的方案；"房间里有没有人"往往只需要 20 KB 网络，不是 20 TOPS 加速器
3. **传感器本身在爬阶梯**：RD-03D 雷达模块自己跑跟踪算法，输出目标坐标而非原始 chirp 数据 —— **智能传感器 + 普通 MCU 常常胜过大模型 + 原始数据**

---

## 三、四波技术浪潮（按时间）

### 1. DSP 时代（~2017 前）
MCU 上的"机器学习"= 手调滤波器 + 阈值 + 偶尔的决策树。神经网络是 GPU 上的事。

### 2. TinyML 时代（2017-2022）
三大事件汇聚：
- Google "OK Google" 唤醒词证明几十 KB 网络可用 → Pete Warden《Why the future of ML is tiny》成为运动宣言
- **TensorFlow Lite for Microcontrollers**（现归入 Google LiteRT 家族）提供 KB 级运行时
- MIT **MCUNet** 证明网络架构与 MCU 内存约束协同设计，可在 Cortex-M 上跑 ImageNet 级视觉（降精度降分辨率）
- **Edge Impulse** 把数据采集→训练→量化→部署打包成学生一下午能完成的流水线

典型负载 = **感知**：关键词在不在？是什么手势？画面里有人吗？

### 3. NPU 时代（2022-2025）
- **Arm Ethos-U55 microNPU**：与 Cortex-M 并列，毫瓦级功耗下推理吞吐提升一个数量级
- **STMicroelectronics Neural-ART**：内置于 STM32N6，首个带 NPU 的 STM32
- **Hailo M.2 卡**：为 Linux 层单板机提供离散加速
- 神经加速从"新奇硅片"变成"标准特性"

### 4. 小语言模型时代（2024-）
惊喜：在感知模型上磨出来的压缩技术，**对生成模型同样有效**。
- **Microsoft Phi 系列**：数据质量替代规模
- **Google Gemma**：逐层 embedding 技巧压缩内存
- **Alibaba Qwen 小型系列**：从 0.8B 起，明确面向 IoT 级硬件
- 4-bit 量化后，~4B 参数模型约占 1 GB，可在手机/Pi 5/几瓦加速器上跑
- **语言、摘要、结构化抽取、简单推理**加入"设备可自主完成"的清单

---

## 四、2026 工具链格局

### 硅片厂垂直整合（最大趋势）

**硅片厂正在收购"工作流层"**，让 edge AI 成为平台的一部分而非外部依赖：

| 平台 | 收购方 | 年份 | 定位 |
|------|--------|------|------|
| **Edge Impulse** | Qualcomm | 2025 | 全流水线，多目标支持 |
| **Neuton.AI** | Nordic | 2025 | 全自动 TinyML + 极小模型 |
| **Imagimob** | Infineon | 2023 | 端到端约束设备部署 |

### 厂商专属框架
| 厂商 | 框架 | 特点 |
|------|------|------|
| STMicroelectronics | **STM32Cube.AI** + **NanoEdge AI Studio** | 训练模型→优化 C 代码；异常检测+分类 |
| NXP | **eIQ ML** | 跨 NXP 处理器，集成 SDK |
| Renesas | **Reality AI Tools** + **RUHMI** | Ethos 加速器优化 |
| Nordic | **Edge AI Add-on for nRF Connect SDK** | 运行时库 |

### 开源运行时（2026 现状）
| 运行时 | 状态 | 评价 |
|--------|------|------|
| **Google LiteRT for Microcontrollers**（原 TFLM） | 活跃，最广泛 | 静态内存竞技场，可接 CMSIS-NN 或厂商内核 |
| **Microsoft ONNX Runtime** | 活跃但**无官方 MCU 裸机版** | 边缘 OS 设备优秀，深度受限需大量移植 |
| **Apache microTVM** | **基本停更** | 编译器驱动 MCU 部署的可行性已验证，但 2026 不再是生产选项 |

**实践建议**：用开源运行时验证可行性和工作流 → 量产时选择性采用厂商工具链解锁性能/功耗/内存极限。

---

## 五、为什么智能要离开云端（5 重"嵌入税"）

云端推理对每次往返征收 5 种税：

1. **延迟税**：往返数十~数百毫秒，方差比均值更要命。跌倒检测、工业机器人护栏、自主无人机**无法**通过 WAN 闭合控制环
2. **隐私税**：原始数据离开建筑。GDPR + EU AI Act 下，这是法律问题不是设计偏好问题
3. **带宽与成本税**：一路 1080p 摄像头持续上传，消耗超过全家其他上行带宽总和；按调用计费的云推理在"每秒每设备一次"规模下极其昂贵
4. **韧性税**：依赖云"思考"的设备，断网时停止思考 —— 而这恰恰是监控系统最重要的时刻
5. **能耗税**：对于小负载小模型，**无线电发射测量值比本地分析更耗能**（电池设计的关键权衡）

**2026 行业共识架构 = 混合**：本地模型处理日常、延迟敏感、隐私敏感的工作；困难或罕见案例上报云端大模型。这个分工不再是"异国情调"，而是**默认架构**。

---

## 六、对我们项目的启示

`stm32u585-tinyml-cough-detection` 项目的选型与 2026 主流完全吻合：

| 项目决策 | 行业印证 |
|---------|---------|
| STM32U585 Cortex-M33 @160MHz + 768KB RAM | 落在"纯 MCU + 逼近 microNPU"之间，合理 |
| Edge Impulse + TFLM + CMSIS-NN | 仍是主流路径（注意 Edge Impulse 已被 Qualcomm 收购，未来对接 Qualcomm 平台更顺） |
| 4-bit/INT8 量化 + 2D-CNN MFCC | 与"TinyML 时代"感知任务范式一致 |
| FreeRTOS 三任务（采集→推理→输出） | 嵌入式工程关注点（时序、内存、鲁棒性）回归 |

**待探索方向**：
- 升级路径 → STM32N6（Neural-ART NPU 600 GOPS），推理延迟可从 ~178ms 降到 ~30ms 级
- 加入端侧小语言模型做症状问答（Pi 5 + Hailo-10H ~10 tok/s 已够用）
- 隐私 + 韧性 → 咳嗽检测完全本地，符合医疗数据保护

---

## 七、金句摘录

> *"The interesting engineering question is no longer whether to put intelligence at the edge, but how much fits at each price and power point."*
> —— Derek Molloy

> *"2026 is unlikely to be the year that AI 'replaces' embedded and domain expertise. In fact, the opposite is true."*
> —— Shawn Hymel

> *"An occupancy sensor that sends 'room occupied, confidence 0.94' instead of a video stream has transformed its privacy posture, its bandwidth bill and its failure modes in one move."*
> —— Derek Molloy

---

## 八、参考链接

- Shawn Hymel《State of Edge AI on Microcontrollers in 2026》：https://shawnhymel.com/3125/state-of-edge-ai-on-microcontrollers-in-2026
- Derek Molloy《From TinyML to Tiny Language Models》：https://derekmolloy.ie/from-tinyml-to-tiny-language-models-the-state-of-edge-ai-in-2026
- Nexilica《AI on Edge: Embedded AI on STM32》：https://www.nexilica.com/en/blog/ai-edge-embedded-systems
- MCUNet 论文：https://arxiv.org/abs/2007.10319
- 小语言模型综述：https://arxiv.org/abs/2410.20011
- MLPerf Tiny 基准：https://mlcommons.org/benchmarks/inference-tiny/

---

**笔记结束** | 作者：猫仔夜间自学习引擎 | 关联项目：`stm32u585-tinyml-cough-detection`

## 相关笔记
- [边缘AI推理优化-TinyML到TinyLM的2026现状](2026-07-23-边缘AI推理优化-TinyML到TinyLM的2026现状.md)
