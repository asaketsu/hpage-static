　　
# kronos-predictor

## 项目信息
构型类型：未知
功能标签：量化

## 项目简介
　　# Kronos Predictor - A股K线预测引擎 基于 [Kronos](https://github.com/shiyu-coder/Kronos) 开源金融K线基础模型，在 Jetson Orin Nano 上本地部署，为神探系统提供零样本预测信号。 ## 项目目标 1. **信号验证层**：神探出买卖点 → Kronos 预测方向校验，过滤假信号 2. **概率区间**：多路径采样输出涨跌概率，替代确定性判断 3. **自适应集成**：Kronos 预测 + 神探规则评分 → 融合信号 ## 技术方案 **模型**: Kronos base (102.3M参数) - HuggingFace 加载 **硬件**: Jetson Orin Nano (8GB VRAM, arm64) **推理**: PyTorch + CUDA，batch 多资产并行 **集成**: 输出 DataFrame → 神探评分模块消费 ## 目录结构 ``` kronos-predictor/ ├── scripts/        # 推理脚本、数据获取 ├──



## 相关笔记
- [[2026-04-12-Kronos-financial-kline-foundation-model]] (关键词: kronos)
