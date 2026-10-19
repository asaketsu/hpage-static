# Edge AI / TinyML 部署 — 深度探索笔记

> 探索日期: 2026-05-19 | 主题: Edge AI / TinyML 部署 | 优先级: MEDIUM

---

## 核心发现

### 1. 市场规模与趋势
- **TinyML 市场 2025**: US$ 15.3 亿 → **2035 年预计 US$ 96.5 亿**，CAGR 20.2%
- 驱动因素：边缘计算需求、超低延迟、能源效率、实时决策
- 趋势：从云端 AI 向**边缘原生智能**迁移

### 2. 2026 Edge AI 技术报告关键主题（Wevolver）
| 主题 | 说明 |
|------|------|
| **Edge Foundation Models** | Llama 3.2、Gemma 3、Phi-mini 等小模型家族在边缘部署 |
| **Multimodal Edge Models** | 多模态边缘模型兴起 |
| **Ultra-Low-Power Architectures** | 超低功耗边缘智能架构 |
| **Agentic AI at the Edge** | 边缘端 Agent 智能体 |
| **Physical AI & Embodied AI** | 物理 AI 与具身智能 |
| **Edge MLOps & Orchestration** | 边缘 MLOps 与编排 |
| **Trust Stack** | 安全、隐私、可解释性 |

### 3. 硬件平台对比
| 平台 | 适用场景 | 特点 |
|------|---------|------|
| **ESP32** | 超低功耗传感器、简单推理 | 40KB SRAM，适合分类/检测 |
| **Raspberry Pi 5** | 中等复杂度边缘推理 | CPU+GPU，适合视觉/NLP |
| **NVIDIA Jetson Orin Nano Super** | 高性能边缘 AI | GPU 加速，适合多模态/大模型 |

### 4. 嵌入式 ML 框架演进
- **TensorFlow Lite for Microcontrollers**: 成熟，ESP32 支持良好
- **Edge Impulse**: 一站式平台，从训练到部署
- **ONNX Runtime Micro**: 跨平台推理引擎
- **Power-optimized AI accelerators**: 2026 年更多低功耗 AI 加速器出现

### 5. 关键工程权衡
- **模型压缩**: 量化（INT8/INT4）、剪枝、蒸馏
- **内存约束**: MCU 通常 <256KB RAM，需模型<500KB
- **功耗预算**: 电池供电设备需 <10mW 推理功耗
- **延迟要求**: 实时控制需 <10ms 推理时间

---

## 与现有项目的关联

| 项目 | 关联点 |
|------|--------|
| **ths-auto-trader** | 边缘端行情数据处理、低延迟信号生成 |
| **AERIS-10 Radar** | FPGA+MCU 架构天然适合 TinyML 部署 |
| **Jetson 传感器集成** | Jetson Orin 边缘推理平台 |

---

## 结论与评分

**评分**: 28/40 (70%)

**核心结论**:
1. TinyML 已从 Demo 阶段进入**生产落地阶段**，但规模远小于云端 AI
2. 2026 年关键趋势是**边缘基础模型 + 多模态 + Agent 化**
3. 硬件生态成熟：ESP32/Jetson/RPi 形成清晰的分层选择
4. 工程核心仍是**资源约束下的权衡**，而非算法创新

**建议**:
- 对 ESP32 项目：关注 Edge Impulse 和 TFLite Micro 的最新工具链
- 对 Jetson 项目：关注 Llama 3.2/Phi-mini 的量化部署方案
- 对雷达项目：TinyML 可用于信号预处理/异常检测

---

## 参考来源
- Wevolver 2026 Edge AI Technology Report
- Shawn Hymel: State of Edge AI on Microcontrollers in 2026
- DataM Intelligence: TinyML Market Forecast 2026-2035
- PROMwad: Embedded ML Trends 2026
- LinkedIn: TinyML on ESP32 Hands-on (2026)

## 相关笔记
- [esp32-edge-impulse-pipeline](explore/2026-05-18-esp32-edge-impulse-pipeline.md)
