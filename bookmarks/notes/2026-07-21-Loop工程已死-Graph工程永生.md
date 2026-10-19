# Loop工程已死，Graph工程永生

> **出处**: [微信公众号 - PaperAgent](https://mp.weixin.qq.com/s/i3zHIqkJU9cX1G1Nc5RUzA)
> **日期**: 2026-07-21
> **标签**: #AI-Agent #Graph-Engineering #Workflow #Agent-编排 #Claude
> **核心内容** (conf=0.95): Loop Engineering（循环工程）让 Agent 自动长时间运行，Graph Engineering（图工程）用有向图组织多个 Agent 的协作与数据流转。文章提出 14 条 Graph Engineering 实操原则，核心是用"节点=任务、边=数据流"的思维重构线性脚本，通过 parallel() 扇出、barrier 扇入、钻石拓扑等模式实现可扩展的多 Agent 编排。

---

## 核心概念

| 概念 | 定义 |
|---|---|
| **Loop Engineering** | 在 Agent while 循环外再套循环（父循环包裹子循环），减少人工干预，让 Agent 自主感知环境持续执行 |
| **Graph Engineering** | 用有向图（Directed Graph）组织多个 Agent 协作，节点=任务，边=数据依赖 |

## 14 条实操原则

### 1. 节点是任务，边是流动的东西
- 节点 = 工作单元（一个 agent、一个有界任务，一进一出）
- 边 = 依赖关系（A 的输出喂给 B 的输入）
- **常见错误**：把"然后"当成边。只有数据真正流过时边才存在

### 2. 线性脚本是一张退化图
- A→B→C→D 是单条不分叉的链，能跑但慢且脆
- 剪掉不携数据的箭头，链塌成更宽的形状：多个独立节点并行 → 汇聚节点

### 3. 给每个节点一个契约
- 有界输入、有界输出、恰好一个任务
- 用 JSON schema 强制，mismatch 时自动重试

### 4. 把边当作数据契约
- A 产出这个形状，B 被设计来消费这个形状
- 边就是普通代码（reduce/filter/dedupe），不需要 agent，"边免费"

### 5. 用 parallel() 扇出
- N 个独立节点不要串行，全部并发
- parallel() 是 barrier，等全部完成；抛错解析为 null，不拖垮整批

### 6. 在 barrier 处扇入
- 扇入节点一次看到全部上游结果：去重、排序、提前退出
- 仅当某阶段真的需要全部前序结果时才用 barrier

### 7. 钻石拓扑：拆分 → 工作 → 合并
- fan out → reduce → synthesize
- 一个节点拆活、多个并行干活、一个合并

### 8. 用条件在运行时路由边
- router 节点检查结果，决定下游路径
- 确定性是特性：节点处用判断，边处用脚本的可靠

### 9. 在边上放验证器
- 对抗式验证：spawn N 个怀疑者反驳，多数存活才保留
- 多视角验证：正确性、安全、复现性
- 裁判组：并行 judge 打分，综合赢家 + 亚军

### 10. 隔离节点，一次失败毒不到整张图
- 抛错节点解析为 null，.filter(Boolean)
- 并行写文件用 git worktree 隔离

### 11. 加环但要收敛
- loop-until-dry：持续 spawn 直到连续 K 轮无新发现
- 去重对照所有见过的（不只是已确认的）

### 12. 跨节点分层模型
- 无聊节点跑便宜模型，判断节点用贵模型
- 大 run 前查 model，扇出降档、合并保高档

### 13. 拓扑就是成本与延迟
- parallel() barrier 让一切等最慢节点
- pipeline() 让每个 item 独立流过，无 barrier
- **默认用 pipeline()，只在需要全集时才用 barrier**

### 14. 让 Claude 自己画图——自路由
- dynamic workflows：描述目标，Claude 自己写编排脚本
- 为每次 run 量身定制图，而非固定模板

## 我的注解

这与 Hermes 的多 Agent 编排模式高度相关：
- Hermes 的 `delegate_task` 批量模式 ≈ parallel() 扇出
- Hermes 的 Kanban workflow ≈ 钻石拓扑（拆分→并行→合并）
- Hermes 的 Skills 层 ≈ 节点契约（标准化输入输出）
- 核心启示：减少 Agent 间的假依赖（不携数据的串行），更多用并行 + barrier 汇聚

## 相关笔记
- [Harness-vs-Loop-vs-Graph三层实践指南](2026-07-28-Harness-vs-Loop-vs-Graph三层实践指南.md)
