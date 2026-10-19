# THS Auto Trader — 2025-2026 生态系统最新动态深度研究

> 2026-05-18 | proactive-learn 深度研究 | Topic: ths-auto-trader
> 方法：web_extract + browser 多源交叉验证（web_search 不可用时的降级方案）
> 覆盖方向：easytrader、xtquant/QMT、vnpy_ifind、AI Agent 量化新范式、同花顺客户端变化
> 字数: ~3200 | 难度: L3（趋势跟踪级）

---

## 一、核心发现（6 个关键发现）

### 发现 1：xtquant 已正式上架 PyPI，Python 3.13 原生支持 — 🔴 重大变化

这是本项目最具实操价值的变化。此前 skill 记录"xtquant 不在 PyPI，需券商渠道获取"，现已过时。

**实证数据**：
- PyPI 地址：https://pypi.org/project/xtquant/
- 最新版本：**250516.1.1**（2025-06-11 发布）
- 支持 Python 3.6 ~ 3.13（<3.14）
- 许可证：GNU GPLv3
- 维护者：gokoushiro, jfaaa33, raise_tech
- 安装：`pip install xtquant`

**250516 版本新特性（重大更新）**：
| 新能力 | 说明 | 对项目的影响 |
|--------|------|------------|
| Python 3.13 | 原生支持最新 CPython | Jetson 上部署更灵活 |
| 银证转账 | `query_bank_info()`, `bank_transfer_in/out()` | 资金管理自动化 |
| 期货/期权资金划转 | 多品种资金统一管理 | 策略扩展到衍生品 |
| 北交所支持 | 含市价报价方式说明 | 覆盖全市场 |
| datetime 时间范围 | `xtdata` 支持 datetime 传入 | 数据查询更直观 |
| 大单统计（VIP） | 主力资金流向数据 | 策略信号增强 |
| 分类板块列表（投研版） | 行业/概念板块数据 | 选股池管理 |
| 期权预估保证金 | 期权策略风控 | 期权策略成本预估 |
| ATM 市场 | 新交易场所支持 | 交易范围扩展 |

**版本发布节奏**：约每 2-3 个月一个版本，持续维护中。

**实践启发**：
1. `pip install xtquant` 一行命令即可获取 QMT 接口，不再需要联系券商获取安装包
2. 但 QMT 客户端本身仍需 Windows（.NET/WPF），xtquant 只是 Python 封装层
3. RemoteQMTBroker 架构（HTTP API 远程调用）仍然是最可行的 Jetson Linux 方案

---

### 发现 2：easytrader 2026 年持续维护，MiniQMT 成为核心方向 — 🟡 值得关注

**最新状态**：
- ⭐ 9.7K stars | 🍴 3K forks | 699 commits
- 版本：v0.23.7（2025-04-19）
- 2026 年已有 5 次提交，仍活跃

**2026 年关键 Commits**：
| 日期 | 变更 | 意义 |
|------|------|------|
| 2026-02-28 | 添加项目指南和设置文档 | 项目规范化 |
| 2026-01-15 | 修复 MiniQMT entrust_prop 参数 | MiniQMT 严格参数检查 |
| 2026-01-07 | 修复多次复制窗口验证码问题 | GUI 自动化稳定性 |

**Issue 趋势分析**（关键信号）：
- **Issue #524**（2026-03）：用户报告"同花顺新版下单程序已没有市场选择" — ⚠️ 同花顺客户端 UI 已变更
- Issue #525：请求支持盘后固定价格交易 — 新需求
- Issue #521：银河证券客户端兼容性 — 券商适配需求持续

**实践启发**：
1. 同花顺新版客户端 UI 变化可能影响 easytrader 的 GUI 自动化路径
2. MiniQMT 的 `buy()` 函数做了严格参数检查（不再接受额外 `entrust_prop`），如果项目使用了此参数需要适配
3. easytrader 的长期趋势：从 GUI 自动化 → MiniQMT API 模式，与 xtquant 方案逐步趋同

---

### 发现 3：vnpy_ifind 2026 年新增前复权支持 — 🟡 数据层增强

**最新状态**：
- 仓库：https://github.com/vnpy/vnpy_ifind
- ⭐ 52 stars | 33 commits | 4 tags
- 2026-04-02：**新增股票前复权支持** — 重要数据功能
- 2026-04-04：社区 PR 合并

**vnpy 主框架更新**（影响 iFinD 集成）：
- vnpy **4.4.0**（2026-05-14）：⭐ 40.6K stars，6,903 commits
- iFinD 列为正式支持的 datafeed
- 覆盖：股票、期货、基金、债券
- 新增 `vnpy.alpha` 模块（AI/ML 量化策略）

**实践启发**：
1. vnpy 4.4 + vnpy_ifind 提供了从数据获取到策略回测的一体化方案
2. 前复权数据对回测精度影响大（分红除权处理），此更新解决了常见痛点
3. `vnpy.alpha` 模块与现有 skill 中的 "Alpha 158 因子集 + LightGBM" 知识缺口相关联

---

### 发现 4：AI Agent 驱动的量化交易系统成为 2026 年新范式 — 🔴 前沿趋势

**典型案例：EasyUp Platform**
- 仓库：https://github.com/zhou343-de/easyup-platform
- 2026 年 5 月创建（极新）
- 核心架构：**AI Agent 多角色辩论选股 + Cron 全自动调度**
  - 🎯 猎手 Agent：发现潜在标的
  - 💰 账房 Agent：评估财务指标
  - 🛡️ 守夜人 Agent：风控审核
- 37 因子选股 + 8 层风控
- 每日自动盯盘 15 次
- 同花顺级数据大屏（K线、热力图、瀑布图）
- 免费数据源（东财/腾讯/新浪）
- 一键 Docker 部署

**马到成功 v3.0**：
- 仓库：https://github.com/yayale-lgtm/Happy-the-Year-of-the-Horse
- 基于 Streamlit 的现代化量化系统
- 策略工坊（在线代码编辑器 + 热加载）
- 内含 `jqktrader` 库（同花顺交易封装）

**实践启发**：
1. AI Agent 多角色辩论模式是全新的决策架构 — 多个 LLM 角色从不同维度评估，最终投票决策
2. 这与 Hermes 多 Agent 协作模式天然契合 — 可以用 delegate_task 实现类似的"猎手/账房/守夜人"模式
3. 免费数据源 + Docker 部署降低了准入门槛，Jetson 可以直接运行

---

### 发现 5：同花顺客户端 UI 重大变更 — ⚠️ 需要适配

**关键证据**：
- easytrader Issue #524（2026-03）：新版下单程序"已没有市场的选择"
- 这意味着同花顺对交易客户端进行了 UI 重构，移除了市场选择步骤
- 对基于 xdotool/pywinauto 的 GUI 自动化方案影响显著

**影响评估**：
| 方案 | 影响程度 | 应对 |
|------|---------|------|
| xdotool（Linux） | 🔴 高 | 元素定位可能失效 |
| easytrader（Windows） | 🟡 中 | 可能需要更新选择器 |
| MiniQMT/xtquant | 🟢 无 | API 调用不受 UI 变化影响 |

**核心结论**：同花顺客户端 UI 变化进一步证明了 **API 化交易（QMT/xtquant）是长期正确方向**，GUI 自动化方案需要持续维护适配。

---

### 发现 6：Streamlit/Web 化量化交易界面成为主流 — 📈 增长趋势

**证据链**：
1. 马到成功 v3.0 基于 Streamlit
2. EasyUp Platform 提供数据大屏
3. 现有 skill 中的 Streamlit Web UI 模块

**技术优势**：
- 跨平台：Linux/Windows/macOS 浏览器即可访问
- 实时刷新：WebSocket 推送行情
- 远程监控：手机/平板也能查看
- 与 Jetson Linux 环境天然兼容

---

## 二、技术细节与代码示例

### xtquant 250516 版新 API 速查

```python
# 银证转账（新功能）
from xtquant.xttrader import XtQuantTrader

trader = XtQuantTrader(path, session_id)
trader.start()

# 查询银行信息
bank_info = trader.query_bank_info(account)

# 资金转入证券账户
trader.bank_transfer_in(account, bank_id, amount)

# 资金转出至银行
trader.bank_transfer_out(account, bank_id, amount)

# 北交所交易（新支持）
trader.order_stock(account, '430047', xtconstant.STOCK_BUY,
                   xtconstant.FIX_PRICE, 100, 10.5,
                   strategy_name='北交所策略',
                   remark='北交所测试')

# datetime 时间范围查询（新支持）
from xtquant.xtdata import download_history_data, get_market_data
import datetime

start = datetime.datetime(2025, 1, 1)
end = datetime.datetime(2025, 12, 31)
download_history_data('000001.SZ', '1d', start.strftime('%Y%m%d'), end.strftime('%Y%m%d'))
```

### AI Agent 多角色辩论选股架构（参考 EasyUp Platform）

```python
# 概念模型 — 可在 Hermes 中用 delegate_task 实现
agents = {
    "hunter": "猎手：从全市场扫描异动标的，关注量价突破、板块轮动",
    "accountant": "账房：从 37 个因子评估标的财务健康度",
    "watchman": "守夜人：8 层风控审核，检查合规/流动性/集中度"
}

# 决策流程：
# 1. 猎手 Agent 提名 → 输出候选列表
# 2. 账房 Agent 评估 → 输出评分报告
# 3. 守夜人 Agent 审核 → 输出风控报告
# 4. 三方辩论/投票 → 最终决策

# 在 Hermes 中的实现：
# delegate_task(tasks=[
#     {"goal": "猎手：扫描全市场异动标的", "role": "leaf"},
#     {"goal": "账房：评估候选标的财务指标", "role": "leaf"},
#     {"goal": "守夜人：风控审核", "role": "leaf"}
# ])
```

---

## 三、知识缺口更新

### 已填补（从现有 skill 知识缺口列表）

| # | 缺口 | 状态 | 填补内容 |
|---|------|------|---------|
| 2 | iFinD SDK 安装 | ✅ 部分填补 | vnpy_ifind 通过 pip 安装，可能绕过独立 iFinD SDK |
| 6 | Tick 级数据管道 | ✅ 已填补 | 新浪 WebSocket TickDataSource 设计完成 |
| 7 | QMT 远程 API | ✅ 已填补 | RemoteQMTBroker HTTP 中转架构完成 |

### 新增缺口

| # | 缺口 | 优先级 | 说明 |
|---|------|--------|------|
| 13 | **同花顺新版客户端 UI 变更适配** | 🔴 高 | Issue #524 反映市场选择步骤被移除，影响 xdotool/easytrader |
| 14 | **AI Agent 多角色辩论选股框架** | 🟡 中 | EasyUp Platform 模式，可用 delegate_task 实现 |
| 15 | **xtquant 银证转账 + 北交所实盘测试** | 🟡 中 | 新 API 需 Windows 环境 + QMT 客户端验证 |
| 16 | **vnpy.alpha 与现有因子挖掘模块的集成** | 🟡 中 | Alpha 158 + LightGBM，需验证 Jetson aarch64 |

---

## 四、实践启发总结

1. **API 化趋势不可逆**：同花顺客户端 UI 变化反复，GUI 自动化需要持续维护。xtquant 上架 PyPI 是标志性事件，API 方案更稳定可靠
2. **Jetson 部署路径明确**：Windows 运行 QMT + xtquant → HTTP API → Jetson 策略计算。这条路径已被验证可行
3. **AI Agent 量化是新范式**：多角色辩论选股模式与 Hermes delegate_task 架构天然契合，可作为新的 skill 方向
4. **免费数据源生态成熟**：东财/腾讯/新浪/akshare 免费数据源足够支撑日线策略，iFinD 仅在需要高频/深度数据时必要
5. **Streamlit 是最佳前端**：跨平台、实时刷新、远程监控，Jetson 可直接运行

---

## 信息来源

| 来源 | URL | 获取时间 |
|------|-----|---------|
| easytrader GitHub | https://github.com/shidenggui/easytrader | 2026-05-18 |
| xtquant PyPI | https://pypi.org/project/xtquant/ | 2026-05-18 |
| vnpy_ifind GitHub | https://github.com/vnpy/vnpy_ifind | 2026-05-18 |
| vnpy 主框架 | https://github.com/vnpy/vnpy | 2026-05-18 |
| 马到成功 v3.0 | https://github.com/yayale-lgtm/Happy-the-Year-of-the-Horse | 2026-05-18 |
| EasyUp Platform | https://github.com/zhou343-de/easyup-platform | 2026-05-18 |

*最后更新: 2026-05-18*

## 相关笔记
- [wencai-stock-picker-notes](../2026-04-06-wencai-stock-picker-notes.md)
- [OpenClaw-4-things-persistent-tasks](../2026-04-10-OpenClaw-4-things-persistent-tasks.md)
- [stock-trading-discipline-washout](../2026-04-11-stock-trading-discipline-washout.md)
- [通达信tdxquant量化模拟交易封装](../2026-04-24-通达信tdxquant量化模拟交易封装.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [MACD-KDJ共振策略](../2026-05-08-MACD-KDJ共振策略.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](../2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [RSI布林带组合策略](../2026-05-11-RSI布林带组合策略.md)
- [板块轮动资金流向分析](../2026-05-11-板块轮动资金流向分析.md)
- [板块轮动概念轮动](../2026-05-18-板块轮动概念轮动.md)
- [rsi-bollinger-strategy](2026-05-06-rsi-bollinger-strategy.md)
- [板块轮动与北向资金流向](2026-05-06-板块轮动与北向资金流向.md)
- [技术指标组合策略-多指标确认](2026-05-09-技术指标组合策略-多指标确认.md)
- [动态止损策略对比](2026-05-17-动态止损策略对比.md)
- [北向资金主力资金流向指标有效性验证-深度研究](2026-05-17-北向资金主力资金流向指标有效性验证-深度研究.md)
- [北向资金主力资金流向指标有效性验证](2026-05-17-北向资金主力资金流向指标有效性验证.md)
- [实盘模拟vs真实交易技术差异](2026-05-17-实盘模拟vs真实交易技术差异.md)
- [ths-auto-trader-2025-2026-tech-ecosystem-update](2026-05-18-ths-auto-trader-2025-2026-tech-ecosystem-update.md)
- [VLA-AD视觉语言动作策略蒸馏](2026-05-19-VLA-AD视觉语言动作策略蒸馏.md)
- [ths-auto-trader-api-era-ecosystem](2026-05-19-ths-auto-trader-api-era-ecosystem.md)
- [板块轮动-北向资金](2026-05-19-板块轮动-北向资金.md)
- [板块轮动-概念轮动](2026-05-19-板块轮动-概念轮动.md)
- [easytrader-deep-dive-2026-05-17](easytrader-deep-dive-2026-05-17.md)
- [ths-auto-trader-2026](ths-auto-trader-2026.md)
- [ths-auto-trader-20260517](ths-auto-trader-20260517.md)
- [ths-auto-trader-architecture-deep-dive-20260517](ths-auto-trader-architecture-deep-dive-20260517.md)
- [ths-auto-trader-deep-dive](ths-auto-trader-deep-dive.md)
- [ths-auto-trader-deep-learn](ths-auto-trader-deep-learn.md)
- [ths-auto-trader-ecosystem-update-20260518](ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
