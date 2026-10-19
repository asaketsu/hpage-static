# 量化交易进阶 — Dirichlet 分层配置 · Regime-Aware 风控 · MRINN 规则感知

> 探索日期 2026-09-01 | 兴趣等级 L4 | 来源 3 篇论文 + 综述 | 前序笔记: 2026-08-28-LLM驱动Alpha挖掘三代进化, 2026-08-25-AQuA递归自改进, 2026-08-06-泊舟AI交易员

---

## 摘要

三个独立学术方向在同一主题下汇聚: **交易规则如何被结构化编码进模型决策链路**。Dirichlet 分层策略把「仓位大类 → 个股」拆成两级，避免单次全市场分配的不稳定; Regime-Aware (Wasserstein HMM) 把市场状态推断嵌入均值-方差优化，Sharpe 2.18 vs SPX 1.18; MRINN 把电力市场的显式定价规则嵌入神经网络潜在空间，参数从 10× 降到 1× 仍保持精度。三个方向的核心共性是 **显式结构先验 > 黑箱数据驱动**。

---

## 核心发现（5 个）

### 1. Dirichlet 分层配置: 两级策略胜过单层

**来源: arXiv:2605.17307 (SAC 深度强化学习多市场组合管理, 2023-2026 三市场 WFO 验证)**

- **Flat policy**: 单一 Dirichlet 分布直接对所有资产+现金输出权重向量，参数空间 |assets| 维，一次分配决定全部仓位
- **Hierarchical policy**: 第一级 Dirichlet 决定「权益 vs 现金」大类配比 (1 维)，第二级 Dirichlet 在权益池内分配个股权重 (|equities| 维)
- **实证结果**: LSTM+Hierarchical 在 Nikkei 225 / Euro Stoxx 50 / Nasdaq-100 三个市场的所有 WFO 折叠中，**波动率和最大回撤系统性低于 Flat 版本**
- **关键洞见**: 把「要不要进场」(大类决策) 和「进哪个」(选股) 解耦，等价于在策略内部插入了一个**隐含的 Regime Gate**——大类层天然充当市场状态判据

```
决策树结构对比:

Flat:        [Dirichlet] → 全资产权重
              ↑ 一次分配 |assets|+1 维

Hierarchical: [Dirichlet₁] → 权益/现金大类
                    ↓ 权益部分
              [Dirichlet₂] → 个股权重
```

### 2. Regime-Aware: Wasserstein HMM 把标签稳定性变成一等公民

**来源: arXiv:2603.04441 (Explainable Regime-Aware Investing)**

| 对比维度 | Wasserstein HMM (本文) | KNN 非参数基线 | SPX Buy & Hold |
|---------|----------------------|----------------|---------------|
| Sharpe | 2.18 | — | 1.18 |
| Max Drawdown | -5.43% | 高 | -14.62% |
| 换手率 | 低 (平滑权重) | 极高 (最近邻突变) | 0 |
| 自适应复杂度 | ✅ 预测式模型阶选择 | ❌ 固定 K | ❌ |
| 标签身份保留 | ✅ Wasserstein 模板锚定 | ❌ 标签切换 | N/A |

**三大技术创新**:
- **严格因果滚动 HMM**: 每天重新估计，不含未来信息
- **预测式模型阶选择**: 用 one-step-ahead log-likelihood 决定当前应保留几个 regime，而非一次性 BIC 或手动设死
- **2-Wasserstein 模板锚定**: 用闭式 Gaussian-Wasserstein 距离将新估计的 HMM 成分映射到历史模板，避免标签切换 (label switching)，这是滚动 HMM 最大痛点

**"Liberation Day" 2025 验证**: 模型检测到向 stress regime 的转移，系统性降低权益暴露，转向 USD/国债，peak-to-trough 损失显著小于 SPX。

> 「Regime-aware investing 的核心挑战不是 regime 是否存在，而是如何稳定地推断它。」

### 3. MRINN: 规则感知神经网络 — 从电力市场移植到金融的范式

**来源: arXiv:2605.09061 (Market-Rule-Informed Neural Network, 德国/奥地利平衡市场)**

- **问题**: 不平衡电力价格由显式结算规则 P_t = g(F_t) 确定，但传统深度学习（LSTM/Transformer）把 P_t 当纯黑箱时间序列目标，让模型从数据中重新学习已知规则——**浪费参数且不可解释**
- **MRINN 架构**: 把定价规则 g(·) 编译成**可微算子**，嵌入神经网络潜在空间。输入原始信号 F_t → 神经编码 → **规则层 (可微)** → 输出
- **关键设计**: 保留原始信号信息 (不预先压缩成 P_t)，避免不同 F_t → 相同 P_t 导致的信息不可逆损失
- **效果**: 训练参数量大幅减少、训练时间缩短，推理 <1s，精度与 iTransformer/PatchTST 持平

**可移植性映射（从电力市场 → 金融市场）**:

```
电力市场                    金融市场类比
─────────────────────────────────────────────────
不平衡定价规则 g(·)         交易规则/风控铁律
aFRR/mFRR 信号             量价/盘口/订单流
稀缺函数                   涨跌停/熔断/流动性冲击
市场参考价 P_mkt            行业指数/ETF 锚定
```

### 4. 三个方向的共同哲学: **显式结构先验 = 更好的鲁棒性**

| 技术 | 显式先验 | 注入位置 | 效果 |
|------|---------|---------|------|
| Hierarchical Dirichlet | 大类/个股解耦 | 策略架构层 | 降波动+降回撤 |
| Wasserstein HMM | 高斯成分几何恒等性 | 推断层 | 降换手+稳定标签 |
| MRINN | 定价规则可微化 | 模型层 | 降参数+提推理速度 |

**核心结论**: 这三个方向的共同模式是「**把人类/制度已知的结构知识编译进模型**」，而非让模型从零学起。对 A 股交易而言，交易规则（涨跌停、换手率限制、集合竞价规则）天然就是这种「已知规则」，值得用类似 MRINN 的方式嵌入。

### 5. AQuA 密封沙箱 × Hierarchical Dirichlet × Regime Gate 的三重叠加

已有笔记 2026-08-25 AQuA 提出的「密封沙箱防过拟合」框架，可与上述三项组合：

- **AQuA** 提供进化/过拟合检测外壳
- **Hierarchical Dirichlet** 替代 AQuA 现有的单层策略输出，天然提供「市场状态门控」
- **Wasserstein HMM Regime 标签** 可作为 AQuA 沙箱的**外部判据**——当 HMM 判定进入 stress regime 时，沙箱自动收紧策略准入阈值

---

## 关键概念详解

### Wasserstein 距离与 Gaussian 成分恒等性

2-Wasserstein 距离在两个多元高斯分布 N(μ₁,Σ₁) 和 N(μ₂,Σ₂) 之间有闭式解:

```
W₂²(N₁,N₂) = ‖μ₁-μ₂‖² + tr(Σ₂ + Σ₁ - 2(Σ₁^{1/2} Σ₂ Σ₁^{1/2})^{1/2})
```

- 不需要数值最优传输求解
- 天然度量两个 regime 成分之间的"形状差异"
- 模板追踪用指数平滑逐步更新，避免每次重新做组合匹配

### Hierarchical Dirichlet 实现要点

```python
# 伪代码: Hierarchical Dirichlet policy
class HierarchicalDirichletPolicy(nn.Module):
    def forward(self, state):
        # 第一层: 权益/现金大类
        alpha1 = self.net1(state)  # shape: (2,)
        equity_frac = sample_dirichlet(alpha1)  # 权益占比
        
        # 第二层: 个股
        alpha2 = self.net2(state)  # shape: (N_assets,)
        stock_weights = sample_dirichlet(alpha2)
        
        # 组合
        final_weights = torch.cat([equity_frac * stock_weights, 
                                   1 - equity_frac])
        return final_weights
```

### MRINN 可微规则层

核心思路是把规则函数 g(·) 写成可微 Python/Torch 代码:

```python
# 示例: 模拟涨跌停规则作为可微约束
def clip_price(price, prev_close, limit=0.1):
    lower = prev_close * (1 - limit)
    upper = prev_close * (1 + limit)
    return torch.clamp(price, lower, upper)
```

该算子可嵌入 Transformer/MLP 的隐藏层之间，梯度正常回传。

---

## 与现有工作的关联

### P0: A股铁律策略 × Regime-Aware 风控

当前 `stock-iron-rules` skill 的 14 条铁律本质上是**离散规则集合**，但缺一个连续的 Regime 判据。Wasserstein HMM 可以：
1. 用 A 股多指标（量比、换手率、涨跌家数、融资余额）构建多变量时间序列
2. 训练滚动 HMM 识别 market regimes（如「普涨」「普跌」「结构性分化」「震荡」）
3. 铁律按 Regime 加权——stress regime 下收紧铁律阈值，bull regime 下适当放宽

### P1: Hierarchical Dirichlet 替代单层仓位

`quant-trading` skill 现有策略直接输出每只股票的目标仓位，可以改为两级:
- 第一级: 今日权益总敞口（基于宏观/情绪信号）
- 第二级: 备选池内个股分配（基于技术因子/基本面因子）

### P2: MRINN 规则层 → 量化因子挖掘

`llm-factor-mining` skill 用 LLM 生成因子代码，可新增一个约束: 生成的因子代码必须兼容一个可微规则层（如涨跌停裁剪、流动性阈值），确保因子天然尊重 A 股交易规则。

---

## 关键风险与盲点

- **Wasserstein HMM 的 Regime 稳定性依赖特征选择**: 论文用多资产价格收益率做输入；如果特征选择差（如仅用单指数），标签仍可能漂移 → 官方验证
- **Hierarchical Dirichlet 的「权益/现金」二分类在 A 股不适用**: A 股不能做空、现金机会成本不同，需改为「满仓/半仓/空仓」三态或引入 ETF 对冲 → 社区复现
- **MRINN 的电力市场规则与金融规则复杂度不同**: 电力定价规则是确定性的分段函数；金融「规则」多为启发式约束（如涨跌停），可微化路径不同 → 未验证
- **SAC 在金融上的统计显著性有限**: arXiv:2605.17307 承认「跨三市场全部达到 HAC-稳健显著超额回报的假设仅部分确认」→ **RL 在金融上的优势可能不如论文声称的那么强**

---

## 一页速查

> **Dirichlet 分层**: 大类/个股解耦，隐含 Regime Gate，波动+回撤双降
>
> **Wasserstein HMM**: 滚动 HMM + 预测阶选择 + 2-Wasserstein 标签锚定，Sharpe 2.18，dd -5.43%
>
> **MRINN**: 规则→可微算子→嵌入神经网络，参数 10× 降到 1×，推理 <1s
>
> **共性**: 显式结构先验 > 黑箱数据驱动
>
> **A 股落地路径**: Wasserstein HMM 做 Regime 判据 → Hierarchical Dirichlet 替代单层仓位 → MRINN 规则层嵌入因子生成

---

## 待深入

1. **MRINN 可微规则层在金融上的具体实现案例**: 论文仅覆盖电力市场，金融领域的 rule-informed NN 需要查更多文献
2. **A 股多变量时间序列适合哪种距离度量做 regime 模板**: 论文用 Gaussian-Wasserstein，A 股收益率非高斯（厚尾、偏态），可能需要 kernel-Wasserstein
3. **Hierarchical Dirichlet × Regime Gate × A 股铁律 的联合回测**: 需要实盘数据验证，属于 L4 实践任务
4. **AQuA 沙箱的「外部 Regime 判据」接口设计**: 需要修改 `stock-iron-rules` skill

---

## 来源列表

| # | 论文 | arXiv ID | 关键指标 |
|---|------|---------|---------|
| 1 | Explainable Regime-Aware Investing | 2603.04441 | Sharpe 2.18, dd -5.43% |
| 2 | Deep RL for Diversified Portfolio (Hierarchical Dirichlet) | 2605.17307 | 三市场 WFO, 2003-2026 |
| 3 | MRINN for Imbalance Price Forecasting | 2605.09061 | 参数 10×↓, 推理<1s |
| 4 | Agentic Trading Survey | 2605.19337 | 综述, 规则/RL/LLM 三线 |
| 5 | TradingAgents (多 Agent 金融框架) | 2412.20138 | 7 Agent, 辩论式决策 |
