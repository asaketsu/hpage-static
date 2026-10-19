# AKQuant对比分析 — Rust回测引擎与我们的脚本量化体系互补进化

#AKQuant #量化框架 #Rust #WalkForward #回测引擎 #A股T+1 #对比分析 #开源吸收

## 出处

- 原项目：https://github.com/akfamily/akquant（akfamily，**2,239 stars**，2026-01-30 创建，v0.3.54，MIT）
- 出品方：AKShare 作者（数据侧权威的量化生态延伸）
- 分析日期：2026-09-03 | 深度模式：zip 镜像下载 + 源码精读（Rust 108 文件 31,788 行 + Python 全模块 + CHANGELOG 全读）
- 定位："专为量化投研设计的下一代高性能混合框架——Rust 核心 + Python 接口"

## 一、内容详细整理

### 项目画像

| 维度 | 内容 |
|------|------|
| 架构 | Rust 核心引擎（pyo3 abi3-py310）+ Python 策略层 |
| 数据 | Zero-Copy `add_arrays` 借用 NumPy 缓冲；策略侧 `get_history` 返回安全快照 |
| ML | 内置 Walk-forward Validation（`SklearnAdapter`/`PyTorchAdapter` + `ValidationConfig`） |
| 指标 | `akquant.talib` 双后端（python/rust）103 个 TA-Lib 指标 |
| 因子 | Polars 驱动表达式引擎：`Rank(Ts_Mean(Close, 5))` Alpha101 风格 |
| 优化 | 多进程网格搜索 |
| 风控 | RiskRule 体系：RestrictedList / MaxOrderSize / MaxOrderValue / MaxPositionSize / CashMargin，按 stock/futures/option/portfolio 分册 |
| 实盘 | CTP/miniqmt/ptrade 三内置 broker；`session_tag` 多任务委托隔离 |
| 测试 | **198 个测试文件 + golden 基线测试**（BASELINE_REPORT + baselines + 数据 + runner） |
| 示例 | 74 个 examples（快速入门→参数优化→ML walk-forward→实盘 CTP→期权→因子表达式） |

### 源码精读三大发现

**① Walk-forward 的框架化实现（与我们 skill 同域）**

`python/akquant/ml/model.py`（312 行）：
```python
self.model.set_validation(
    method="walk_forward",
    train_window=50,    # 用最近 50 根 bar 训练
    test_window=20,     # 样本外预测窗口
    rolling_step=10,    # 每 10 根 bar 重训
    frequency="1m",
)
```
- `QuantModel` ABC（fit/predict/save/load/clone）+ 双适配器（Sklearn/PyTorch）
- 特征工程 `prepare_features(df, mode)` 训练/预测共享，`mode` 区分 label 有效性
- `on_train_signal` 回调可跳过 warmup 期训练
- **启示**：walk-forward 被做成"模型包装器的验证配置"而非独立流程——策略代码不感知切片细节

**② A 股规则建模精度（CHANGELOG 揭示的硬功夫）**

T+1 卖单修复（issue #391，`__engine_rule_version__` 1.5.4）堪称教材级：
- **问题**：`NextOpen` 成交策略下，`on_cross_section` 提交的卖单在下一根 bar 开盘成交，但可用持仓风控读的是**下单时刻**快照——T 日买入的持仓在快照里仍被 T+1 锁定，卖单被误拒，连锁导致买入腿 `Insufficient margin`，**整条日频调仓链路瘫痪**
- **修法**：`RiskRule` 新增 `defer_for_delayed_execution()`——延迟撮合的股票卖单跳过提交时校验，撮合时按成交时点复查；撮合侧维护 slice 内逐笔推进的 `projected_available_positions`，**同 slice 多笔卖单累计扣减**（裸卖/超卖仍被拒）
- **三处边界刻意不放宽**：同周期成交仍按提交时校验；买单不查可用持仓；**实盘不延后**（柜台报单时就要校验）
- **黄金基线联动**：`stock_t1` 基线更新——"挂单/成交"两笔转为成交、**策略注释明确期望失败的日内 T+0 转卖仍为拒单**（关键不变量未破坏）

**③ daily_returns 非交易日伪零（我们同样会踩的坑）**

`resample("D").last().ffill()` 把周末节假日补成权益点 → `pct_change()` 产生 28.7% 人造零 → **年化波动率 0.194 稀释到 0.164、Sharpe 0.662 掉到 0.560（偏差 15.5%）**。更隐蔽的是"同一份回测两个矛盾的 Sharpe"：Rust 侧 metrics 用 BTreeMap 按实际交易日聚合（对的），Python 报告图走 daily_returns（错的）——摘要卡和图表对不上。修法：非交易日不进索引、序列长度=交易日数-1、跨周回归测试锁定口径。

### CHANGELOG 的质量文化（本项目最深护城河）

每条 fix 的结构：现象 → 根因 → 影响面（"不是边缘场景而是整条链路"）→ 修法原理 → 刻意不放宽的边界 → 行为变更提示 → golden 基线联动 → 回归测试（"已用改坏实现验证过可复现失败，非恒真断言"）。**`__engine_rule_version__` 语义化版本追踪规则行为变更**——回测结果的可比性靠它保证。

## 二、关联分析（与我们量化体系的对比）

| 维度 | AKQuant | 我们的体系（stock-iron-rules/screener/cron 盯盘） | 判定 |
|------|---------|--------------------------------------------------|------|
| 架构 | 事件驱动回测引擎，Rust 性能 | 轻量 Python 脚本 + cron 自动化 | **互补不替代**：我们重"盯盘+铁律执行"，它重"研究+回测" |
| A 股规则 | T+1 校验时点精细到撮合时刻；golden 基线锁定 | 铁律逻辑在策略层，回测精度有限 | **它的规则引擎值得抄思想** |
| Walk-forward | ValidationConfig 框架化（模型包装器） | walk-forward-validation skill（方法论文档） | **同域不同层**：它给代码实现参考 |
| 因子 | Polars 表达式引擎（Alpha101 风格） | quant-ic-validation + llm-factor-mining（LLM 侧挖掘） | 方向不同：它算得快，我们挖得新 |
| ML 集成 | SklearnAdapter/PyTorchAdapter 内置 | quant-ml-pipeline skill | 可参考其 Adapter 设计 |
| 风控 | RiskRule 编译进引擎 | agent-trading-safety skill + 半仓铁律 | **我们的安全层在 Agent 侧**，它的在引擎侧——层次不同 |
| 数据 | AKShare 同门（数据兼容零成本） | 腾讯/akshare/iwencai 多源 | 数据侧已对齐（都用 akshare） |
| 质量文化 | golden 基线 + engine rule versioning + 198 测试 | error-case-library + quant-evidence-governance | **理念同源，它更机械化** |
| 成本 | 需学习框架 + Rust 黑盒风险 | 零学习成本，脚本即改即用 | 我们的实用主义在盯盘场景成立 |

**核心判断**：不引入 akquant 作依赖（我们的主力场景是实时盯盘+铁律执行，不是研究回测；框架锁定成本 > 收益），但**吸收它的四个工程模式**进化现有 skill。

## 三、进化落实（三档处理）

### ① 有利进化（已落实/立即可用）

| # | 借鉴点 | 落点 | 状态 |
|---|--------|------|------|
| 1 | 非交易日伪零陷阱（Sharpe 偏差 15.5% 案例） | walk-forward-validation skill 补"日收益序列口径"节 | ✅ 已 patch |
| 2 | T+1 卖单校验时点语义（下单时点 vs 成交时点） | a-stock-quant-system skill 补 A 股回测规则精度提醒 | ✅ 已 patch |
| 3 | golden 基线测试模式（改规则→基线对比→不变量锁定） | quant-evidence-governance skill 补"规则变更防回归"节 | ✅ 已 patch |
| 4 | Walk-forward ValidationConfig 参数化设计（train_window/test_window/rolling_step） | walk-forward-validation skill 补框架参考 | ✅ 已 patch（与 #1 合并） |

### ② 有价值备用（记入本笔记备查）

- `session_tag` 委托隔离（`{broker}-{session_tag}-{run_salt}{seq}` 的 client_order_id 设计）——未来多任务实盘时参考
- `defer_for_delayed_execution()` 的"校验时点对齐成交时点"思想——任何延迟执行系统的风控设计通则
- 零数据标的告警（"没成交"与"没数据"必须可区分）——screener 静默失败防御
- Polars 因子表达式引擎——若因子计算成为瓶颈再考虑

### ③ 知识性存档

- Rust+Python 混合架构的 pyo3 实践（abi3-py310 稳定 ABI）
- CHANGELOG 写法范式（Keep a Changelog + 行为变更显式提示）
- CTP broker 的 client_order_id 幂等键设计（409 Conflict 案例）

## 查询拓展

- AKShare↔AKQuant 数据管道的完整链路（ParquetDataCatalog 设计）
- 期权/期货保证金模块（src/margin、src/settlement）的规则库
- golden 测试 runner.py 的基线管理机制
- 与 vnpy/backtrader/qlib 的详细对比（akquant 的差异化是 Rust 性能 + A 股规则深度）
- `on_cross_section` 横截面回调与 `rebalance_weights` 调仓 API

## 归纳总结

1. **AKQuant 与我们不是竞品是邻座**：它做"研究回测的重工业"（Rust 引擎+规则建模），我们做"盯盘执行轻步兵"（脚本+铁律+cron）——数据侧同源（akshare），层次互补。
2. **本项目最该学的不是代码是"规则版本化"纪律**：`__engine_rule_version__` 让每次规则变更可追踪、回测结果可比——我们的铁律/screener 改版时同样需要（目前只靠 git log）。
3. **两个数值陷阱是全行业通病**：非交易日伪零（Sharpe 偏差 15.5%）和 T+1 校验时点错位（整条调仓链路瘫痪）——都是"框架级隐蔽错误"，任何自研回测都要自查。
4. **golden 基线 = 量化系统的回归测试**：改一个规则后"哪些用例该变、哪些不该变"必须预先声明（日内 T+0 转卖必须仍被拒）——这与 error-case-library 的"复现失败验证"同源但更前置。
5. **CHANGELOG 即文档的极致形态**：每条修复自带根因-影响面-边界-基线联动，2239 stars 但工程纪律是万星级——akfamily 从 AKShare 带来的口碑方法论。

## 四、趋势判断

1. **Rust 内核 + Python 接口会成为量化框架标配架构**：性能敏感层下沉 Rust、策略层保持 Python 灵活——2026 年新框架（akquant/rust-vnpy 系）全面采用此模式。
2. **A 股规则建模深度成为本土框架的分水岭**：T+1 细节、涨跌停、申报价格笼子这些"脏规则"的精确处理比回测速度更稀缺——akquant 在这条线上建立护城河。
3. **Walk-forward 从方法论下沉为框架内置件**：ValidationConfig 式的"验证即配置"会普及——防过拟合不再是研究纪律而是工程默认。
4. **golden 基线测试会在量化工程中普及**：规则引擎复杂化后，"改 A 不破坏 B"只能靠基线锁定——这是量化系统从脚本走向工程化的必经之路。

## 五、指南分析

**什么时候用 akquant**：

| 场景 | 建议 |
|------|------|
| 日频/分钟级策略的系统回测 | ✅ 直接用（A 股规则最全） |
| ML 因子策略 walk-forward 验证 | ✅ ValidationConfig 开箱即用 |
| 因子表达式批量计算 | ✅ Polars 引擎 |
| CTP 期货实盘 | ✅ 内置 broker |
| 轻量盯盘/铁律执行 | ❌ 我们的 cron+脚本更轻 |
| LLM 因子挖掘 | ❌ 与它正交，我们继续 llm-factor-mining |

**依赖决策**：暂不引入本机（Jetson 跑回测违反资源铁律；且我们无重型回测需求）——AutoDL 侧如需系统回测可直接 pip install akquant。

## 拓展应用推荐

- **给 walk-forward-validation / a-stock-quant-system / quant-evidence-governance**：已 patch 四个借鉴点（见 §三①）
- **给 tdx-quant-trader / stock-analysis-system**：T+1 校验时点语义作为回测精度自查项
- **延伸阅读**：AKShare（同门数据源）、quant-evidence-governance skill（我们的证据治理）

---

→ 相关：[[2026-09-02-MiniMind从零训练LLM全链路-3块钱64M模型与AgenticRL.md]]（同周开源吸收：教学极简 vs 工程极重两极样本）
→ 相关：[[2026-09-01-贝叶斯与神经网络世纪和解-BBT两阶段配方与人脑偏爱简单.md]]（"结构化先验"哲学呼应：规则引擎=先验）
→ 相关：[[2026-08-22-同花顺FinancialAPI-官方A股数据与AgentSkill全家桶.md]]（A股数据侧对照）
