　　
# tool-gateway-observability

## 项目信息
构型类型：未知
功能标签：工具

## 项目简介
　　# Tool Gateway 可观测性系统 > 完成日期：2026-04-19 > 状态：已上线（前端构建通过，后端测试通过） --- ## 概述 Tool Gateway 是 Hermes Agent 的**工具调用指标采集与可视化系统**。在每次工具调用时自动采集延迟、成功/失败数据，通过 Dashboard 实时展示。 **核心理念**：零配置、零侵入、自动生效。 --- ## 架构 ``` ┌─────────────────────────────────────────────────┐ │  model_tools.py :: handle_function_call()       │ │  ┌─────────────────────────────────────────┐    │ │  │  L499-505: 记录开始时间 _tg_start       │    │ │  │  L507-521: 执行工具 registry.dispatch() │    │ │  │  L523-530: 计算延迟，调用 collector      │


## 相关笔记
- [Hermes-Agent-v0.10.0-release-analysis](2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Hermes-Agent-v0.10.0-insight](2026-04-18-Hermes-Agent-v0.10.0-insight.md)
