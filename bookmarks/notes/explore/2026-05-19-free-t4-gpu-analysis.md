# 免费 T4 算力全景分析（2026版）

> 日期：2026-05-19 | 来源：Google Developers Blog + 多源搜索
> 关键词：T4 GPU、免费算力、Google Colab、VS Code、Kaggle、Lightning AI

---

## 一、核心发现

### 发现1：Google Colab 正式进入 VS Code — 零成本 T4 直连

Google 于 2025 年 11 月发布官方 Colab VS Code 扩展，将 Colab 的云端 GPU/TPU 运行时直接嵌入本地 VS Code 编辑器。这意味着：

- **免费用户**：T4 GPU（16GB VRAM），无需浏览器标签页
- **Colab Pro/Pro+**：可使用 A100、L4 等高端 GPU
- 本地 `.ipynb` 文件直接连接云端运行时，无需上传

**设置步骤（3步）：**
1. VS Code 扩展商店搜索 "Google Colab" → 安装官方扩展（会自动装 Jupyter 依赖）
2. 打开任意 `.ipynb` 文件 → 点击右上角 "Select Kernel"
3. 选择 "Colab" → 选 T4 GPU 运行时 → Google 账号登录 → 完成

> 扩展地址：https://marketplace.visualstudio.com/items?itemName=Google.colab
> 同时发布在 Open VSX（支持 VSCodium 等 VS Code 衍生编辑器）

### 发现2：T4 GPU 性能边界

| 指标 | 规格 |
|------|------|
| GPU | NVIDIA Tesla T4 |
| VRAM | 16 GB |
| 精度 | FP32 / FP16 / INT8 |
| 算力 | FP32 8.1 TFLOPS, FP16 65 TFLOPS (Tensor Core) |
| 适合模型 | ≤1B 参数训练 / ≤7B 推理（量化后） |
| 不适合 | 大模型全参微调、大规模并行训练 |

### 发现3：免费 T4 平台横向对比

| 平台 | GPU | 免费额度 | 单次上限 | 持久存储 | 需信用卡 | 核心优势 |
|------|-----|----------|----------|----------|----------|----------|
| **Google Colab** | T4 (16GB) | ~15-30h/周 | 12h | ❌ 需挂载 Drive | ❌ | VS Code 扩展、生态最广 |
| **Kaggle Notebooks** | T4 (29GB)/P100 | 30h/周 | 12h | ✅ 持久化输出 | ❌ | 数据集集成、社区竞赛 |
| **Lightning AI** | T4/A10G | 80 GPU小时 | 6h | ✅ Studio 持久 | ❌ | VS Code 风格界面、F5-TTS 模板 |
| **SageMaker Studio Lab** | T4 | ~4h GPU/次 | 4h | ✅ 持久项目 | ❌ | GitHub 集成、无 AWS 账号需求 |
| **Paperspace Gradient** | T4/M4000 | ~免费额度有限 | 6h | ✅ 持久存储 | ❌ | Jupyter Lab 界面 |
| **Google Cloud $300** | 多种 | $300 新用户额度 | 按额度 | ✅ | 需信用卡 | 全功能 GCP |
| **Oracle Cloud** | A10 | 永久免费层 | 无硬限 | ✅ | 需信用卡 | Always Free GPU |

---

## 二、Colab + VS Code 深度分析

### 2.1 架构原理

```
本地 VS Code (.ipynb)
    ↕ Colab Extension
Google Colab Runtime (云端 T4)
    ↕
Google Cloud Infrastructure
```

- VS Code 作为前端编辑器，代码执行在 Colab 云端
- 本地文件 ↔ 云端运行时实时同步
- 网络断开后运行时会被回收（12 小时限制）

### 2.2 免费层限制

- **时间**：每周约 15-30 小时 GPU，具体取决于 Google 当前的资源分配
- **单次会话**：最长 12 小时，空闲超时会断开
- **不保证**：高峰期可能分配不到 GPU，或被降级为 CPU
- **存储**：运行时环境临时性，重启后丢失（需配合 Google Drive）

### 2.3 实际适用场景

| 场景 | 适合度 | 说明 |
|------|--------|------|
| 小模型训练（<1B） | ⭐⭐⭐⭐⭐ | T4 16GB 足够 |
| 7B 模型推理（GPTQ/AWQ） | ⭐⭐⭐⭐ | 4-bit 量化后约 4-5GB |
| 模型微调（LoRA/QLoRA） | ⭐⭐⭐⭐ | 7B QLoRA 约需 10-12GB |
| 数据预处理 | ⭐⭐⭐⭐⭐ | CPU 即可，GPU 加速更快 |
| 大模型全参微调 | ⭐⭐ | 13B+ 需 A100 |
| 长时间训练 | ⭐⭐ | 12h 限制 + 随机断开 |
| Ollama 本地推理 | ⭐⭐⭐ | 可行但需要保持会话 |

---

## 三、多平台组合策略 — 算力最大化

### 3.1 策略：三平台轮转

**目标：每周获得 ~80+ 小时免费 GPU 时间**

| 时段 | 平台 | 任务 |
|------|------|------|
| 上午 | Colab (VS Code) | 模型训练、实验迭代 |
| 下午 | Kaggle | 数据处理、大规模推理 |
| 晚间 | Lightning AI | 部署测试、API 开发 |
| 备用 | SageMaker Studio Lab | 短任务调试 |

### 3.2 持久化方案

所有平台运行时都是临时的，需要数据持久化策略：

```
Google Drive ←→ Colab（15GB 免费）
Kaggle Datasets ←→ Kaggle（100GB+ 数据集空间）
GitHub ←→ 所有平台（代码版本控制）
Lightning Studios ←→ Lightning AI（持久化工作区）
```

### 3.3 自动化技巧

- **防断连**：在 notebook 中加 JS heartbeat（仅限 Colab 浏览器版）
- **数据备份**：训练 checkpoint 定期保存到 Google Drive
- **任务排队**：用 GitHub Actions 触发 Kaggle notebook 执行

---

## 四、Jetson Orin Nano vs 免费 T4 对比

| 指标 | Jetson Orin Nano Super | 免费 T4 |
|------|----------------------|---------|
| AI 算力 | 67 TOPS (INT8) | 65 TOPS (INT8 Tensor Core) |
| VRAM | 8GB 统一内存 | 16GB 独立显存 |
| 可用性 | 24/7 本地 | 15-30h/周，随机断开 |
| 延迟 | 极低（本地） | 高（网络） |
| 适合 | 持续推理、边缘部署 | 一次性训练、大显存任务 |
| 成本 | 已有硬件 = 0 | 真正 0 成本 |

**结论**：两者互补。Jetson 做持续推理和部署，T4 做训练和大显存任务。

---

## 五、行动建议

1. **立即**：安装 Colab VS Code 扩展，配置 T4 运行时
2. **短期**：注册 Kaggle + Lightning AI，配置三平台轮转
3. **中期**：建立 checkpoint → Drive → 本地 Jetson 的自动化流水线
4. **长期**：关注 Google Colab 对 VS Code 扩展的更新（官方说"才刚开始"）

---

## 六、知识缺口

- Colab VS Code 扩展是否支持 SSH 远程连接（vscode:// 协议）
- 免费层 T4 是否支持多 GPU（Colab Pro 支持）
- Lightning AI 80 GPU 小时的具体 GPU 型号
- Oracle Cloud Always Free GPU 的实际可用性（A10 供应紧张）

---

*来源：Google Developers Blog (2025-11-13), Reddit r/LocalLLaMA, Thunder Compute, electronics.alibaba.com, Kaggle 官方论坛, Lightning AI 官网*

## 相关笔记
- [不加GPU多榨15%算力-大模型网络优化](2026-05-22-不加GPU多榨15%算力-大模型网络优化.md)
