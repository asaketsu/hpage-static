# SingGuard-Bench: 策略自适应多模态安全基准

> 来源: arXiv:2606.22873 | inclusionAI | 2026-06-22
> GitHub: https://github.com/inclusionAI/Sing-Guard
> HuggingFace: https://huggingface.co/collections/inclusionAI/singguard

## 摘要

SingGuard-Bench 是 inclusionAI 随 SingGuard 模型家族一起发布的多模态安全评估基准。核心创新在于 **策略自适应 (Policy-Adaptive)** —— 同一内容在不同活跃策略下可能获得不同安全标签，而非固定分类。基准覆盖图文安全审核、跨模态隐藏意图检测、对抗攻击鲁棒性、动态规则切换四个维度，共 56,340 个测试样本。

## 关键发现

### 1. 基准规模与结构
- 总样本: 56,340
  - 图像子集: 40,663（10,697 unsafe + 29,966 benign-sensitive）
  - 多模态子集: 13,677（6,487 unsafe + 7,190 benign-sensitive）
  - 动态规则子集: 2,000（4种策略切换配置 × 500）
- 安全分类体系: 三层 taxonomy
  - 8 个一级维度
  - 27 个二级类别
  - 80+ 细粒度风险类型（78个叶节点）
  - 每语言 2,124 个关键词

### 2. 核心创新：动态策略评估
传统基准内容固定 → 标签固定。SingGuard-Bench 引入策略作为运行时输入：
- 同一样本 + 不同策略 → 不同标签
- 4 种切换配置: unsafe→unsafe, safe→safe, unsafe→safe, safe→unsafe
- 关键指标: safe2unsafe 准确率从基线 0.38 提升到 0.57

### 3. 跨模态隐藏意图
单独看图像安全 + 单独看文本安全 → 组合后不安全。这类样本需要多跳推理或领域知识才能识别。

### 4. 任务形式化
输入: x = (query, image, assistant_response)
策略条件预测: f(x, Policy) → (safe/unsafe, reasoning, triggered_category)

### 5. 最优性能
- 图像子集 F1: 0.8759（SingGuard-4B）
- 多模态子集 F1: 0.9943（SingGuard-8B）
- 对抗攻击 F1: 0.9164（SingGuard-2B）
- 动态策略准确率: 0.7415（SingGuard-slow）vs 0.6465（Qwen3-VL-8B）

### 6. 模型家族
- SingGuard-2B / 4B / 8B，基于 Qwen3-VL 架构
- 支持 Fast/Slow 双速推理（快速判定 + 深度推理）
- 输出格式: `<answer>...</answer>` 标签包含规则匹配结果

## 对工作的价值

1. **Agent 安全护栏参考**: 如果要为 Hermes Agent 构建输入/输出安全过滤层，SingGuard 的策略自适应设计值得借鉴 —— 不同场景（飞书群聊 vs 代码执行）可加载不同策略，而非一刀切
2. **多模态安全意识**: benign-sensitive（看似敏感但无害）样本的引入提醒我们，过度拦截会破坏用户体验，Precision 和 Recall 需平衡
3. **动态策略思路**: 与 red-teaming 技能中的 deterministic-guardrails 可结合 —— 把策略写成可执行规则而非硬编码

## 行动建议

- 暂无立即行动项。SingGuard-Bench 数据集标注 "Coming soon"，尚未公开发布
- 持续关注 inclusionAI 后续开源动态，数据集可用后可考虑集成到 Agent 安全测试流程
- 当前模型已开源（2B/4B/8B），如有多模态审核需求可快速部署测试

## 相关笔记

- [SingGuard-Bench策略自适应护栏(07-09)](./2026-07-09-SingGuard-Bench-.md) — 同一基准不同视角整理
- [MCP协议安全攻防前沿](../2026-06-29-MCP协议安全攻防前沿.md) — MCP协议安全研究
