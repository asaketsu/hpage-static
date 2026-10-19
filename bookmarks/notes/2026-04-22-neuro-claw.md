　　
# neuro-claw

## 项目信息
构型类型：未知
功能标签：AI

## 项目简介
　　# 🐾 NeuroClaw — 下一代边缘 AI Agent 框架 > 基于 ESP-Claw 架构，融合端侧推理、语义记忆、联邦协作、零信任安全的边缘 AI Agent 框架 ## 一句话 让每个 IoT 设备都成为有记忆、能推理、可协作的自主智能体。 ## 为什么 ESP-Claw（乐鑫官方）证明了 MCU 上跑 Agent Loop 可行，但存在关键局限： | 痛点 | 影响 | |------|------| | LLM 完全依赖云端 | 断网 = Agent 瘫痪 | | 记忆检索原始（Summary Tag） | 无法语义匹配，记忆增长后效率崩溃 | | 单设备孤岛 | 无法协作完成超出单设备能力的任务 | | MCP 明文通信 | 安全风险，无法商用 | | 无自进化 | 行为无法自动改进 | NeuroClaw 解决这些问题。 ## 核心模块 ``` NeuroClaw ├── NeuroMemory    — 语义记忆检索（Embedding + LSH） ├── NeuroRouter    — TinyML 智能事件路由（云端/本地分流） ├──



## 相关笔记
- [[2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent]] (关键词: claw)
