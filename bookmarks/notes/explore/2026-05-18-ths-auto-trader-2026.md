# 同花顺量化交易自动化系统 — 2025-2026 技术全景

> 学习时间: 2026-05-18 | Topic: ths-auto-trader | 来源: web_search 多源检索

## 一、核心发现

### 发现1: SuperMind 平台已实现「回测→实盘」1分钟直通
同花顺 SuperMind（原 MindGo）量化平台在 2025 年推出重磅更新：回测代码可直接用于实盘交易，无需重写实盘 API。通过 `research_trade()` 封装，回测策略代码只需外层包裹 TradeAPI 初始化即可实盘。这极大降低了从策略验证到实盘的门槛。

**关键代码模式：**
```python
from tick_trade_api import TradeAPI

trade_api = TradeAPI('资金账号', order_policy=MarketPolicy)

source_code = """
def init(context):
    pass
def handle_bar(context, bar_dict):
    order_id = order('000001.SZ', 100)
"""

rtrade = research_trade(
    '策略名称', source_code,
    frequency='MINUTE',
    trade_api=trade_api,
    signal_mode=False,
    recover_dt='today'
)
```

### 发现2: 微软 R&D-Agent-Quant 开创多智能体量化研发新范式
微软亚洲研究院推出 R&D-Agent-Quant（NeurIPS 2025 接收），以「用 AI 驱动 AI」为理念，构建数据驱动的量化研发体系：
- **五大功能单元**: 假设生成→代码实现→真实回测→反馈分析→迭代进化
- **因子工厂**: 自动生成/筛选/组合新因子，自动去重与有效性校验
- **联合优化**: 因子-模型协同，在 A 股沪深300上 IC≈0.0532, ARR≈14.21%, IR≈1.74
- **成本极低**: 端到端实验成本 < $10
- GitHub 开源: https://github.com/microsoft/RD-Agent

### 发现3: UI 自动化方案成熟 + iFinD 数据接口持续迭代
- **THSAutoTrader** (GitHub: linlb/THSAutoTrader): 基于同花顺客户端 UI 模拟操作，支持市价买/卖、持仓查询，提供 API 接口。完全基于用户操作模拟，不修改客户端，确保合规。
- **ths_trade** (Gitee: h8n/ths_trade): 同花顺 Web 下单接口 API，支持分策略交易和查询，全功能开源免费。
- **iFinD 数据接口**: 覆盖股票/基金/债券/期货/宏观等 2000+ 报表，支持日频/周频/分时/秒级高频数据，提供 Python/MATLAB/R/C++ 等多语言接口。

## 二、技术栈全景

### 2.1 数据层
| 组件 | 说明 | 接口 |
|------|------|------|
| iFinD 数据接口 | 全品种金融数据 | `THS_HistoryQuotes`, `THS_HighFrequenceSequence`, `THS_RealtimeQuotes` |
| SuperMind 数据 | 线上接口调用，不限流量 | `history()`, `history_ticks()` |
| i问财 | 自然语言选股 | HTTP API |

### 2.2 策略回测层
SuperMind 提供完整的回测框架：
- `init(context)` / `handle_bar(context, bar_dict)` / `handle_tick(context, tick)` 回调模型
- `run_daily` / `run_weekly` / `run_monthly` 定时调度
- `order(symbol, amount)` / `order_value` / `order_percent` 下单
- `set_slippage` / `set_commission` 滑点/佣金设置

### 2.3 实盘交易层
- **方案A**: SuperMind `research_trade()` 直通（官方推荐）
- **方案B**: `tick_trade_api.TradeAPI` + 市价/限价策略
- **方案C**: UI 自动化（pyautogui 等，需客户端运行）
- **方案D**: Web 下单接口（ths_trade 项目）

### 2.4 多智能体量化前沿
- **R&D-Agent-Quant**: 微软 NeurIPS 2025, 因子-模型联合优化
- **TradingAgents**: 模拟真实交易公司全流程
- **FinRL-X**: AI 原生模块化框架, Alpaca 实盘评估

## 三、VeighNa (vnpy) 集成
`vnpy_ifind` 项目提供 VeighNa 框架的同花顺 iFinD 数据服务接口，基于 iFinDPy 1.10.21.4 开发，支持：
- CFFEX / SHFE / DCE / CZEX / GFEX 期货 K线
- INE 原油期货及期权
- 中金所期货及期权

## 四、实践启发
1. **合规优先**: UI 自动化方案最安全（不破解客户端），但依赖 GUI 环境
2. **SuperMind 最省力**: 回测→实盘 1 分钟直通，适合快速验证
3. **数据双源**: iFinD（精准专业）+ SuperMind 内置（免费不限流量）
4. **多 Agent 趋势**: 微软 R&D-Agent-Quant 代表了量化研发自动化的最新方向

## 五、知识缺口
- SuperMind 实盘延迟和稳定性实测数据缺失
- iFinD 免费版 vs 付费版数据差异细节不清
- R&D-Agent-Quant 在港股/美股市场的适应性未知
- THSAutoTrader 在 Linux 环境（无 GUI）下的替代方案

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
- [ths-auto-trader-2025-2026-ecosystem-update](ths-auto-trader-2025-2026-ecosystem-update.md)
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
