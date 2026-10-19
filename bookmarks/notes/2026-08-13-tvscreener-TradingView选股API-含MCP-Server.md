# tvscreener — TradingView Screener Python API（含 MCP Server）

> GitHub: https://github.com/deepentropy/tvscreener (1.4k ⭐)
> PyPI: https://pypi.org/project/tvscreener
> 文档: https://deepentropy.github.io/tvscreener/docs/
> 日期：2026-08-13
> 主题：TradingView 选股器数据的 Python 库，支持 6 类资产、13000+ 字段、MCP Server
> 评分：⭐⭐⭐⭐ (4/5) — 量化选股/盯盘的高质量数据源，MCP 集成对 Agent 量化系统有直接价值

## 核心结论

**tvscreener 是 TradingView Screener 的非官方 Python API，覆盖股票/外汇/加密/债券/期货/币 6 类资产，13000+ 字段（从 ~300 扩展），返回 Pandas DataFrame。v0.2.0 新增 MCP Server，让 AI Agent 直接查行情数据——这与 Hermes 量化系统高度互补。**

## 功能矩阵

### 6 类 Screener

| Screener | 覆盖范围 | 默认行数 |
|----------|---------|---------|
| **StockScreener** | 全球股票 | 150 |
| **ForexScreener** | 外汇货币对 | 150 |
| **CryptoScreener** | 加密货币 | 150 |
| **BondScreener** | 政府/公司债券 | 150 |
| **FuturesScreener** | 期货合约 | 150 |
| **CoinScreener** | CEX/DEX 代币 | 150 |

### 核心特性

| 特性 | 说明 |
|------|------|
| **13000+ 字段** | 从 ~300 扩展，含全量技术指标（所有时间周期） |
| **Fluent API** | `select()` + `where()` 链式调用 |
| **Pythonic 比较语法** | `StockField.PRICE > 50`、`.between()`、`.isin()` |
| **Field Discovery** | `StockField.search("rsi")` 搜索字段 |
| **Field Presets** | 估值/股息/振荡器/均线等预定义字段组 |
| **Type-Safe** | 字段/Screener 类型不匹配时自动报错 |
| **任意时间周期** | 1/5/15/30/60/120/240/1D/1W/1M，**无需 TradingView 注册** |
| **Streaming** | `stream(interval=N)` 持续刷新行情 |
| **Styled Output** | TradingView 风格着色 + K/M/B/T 数字格式 |
| **MCP Server** | v0.2.0 — AI Agent 直接查行情 |

## API 用法

### 基础 Screener

```python
import tvscreener as tvs

# 股票
ss = tvs.StockScreener()
df = ss.get()  # 默认返回 150 行 DataFrame

# 加密货币
cs = tvs.CryptoScreener()
df = cs.get()
```

### Fluent API（链式过滤）

```python
from tvscreener import StockScreener, StockField

ss = StockScreener()
ss.select(
    StockField.NAME,
    StockField.PRICE,
    StockField.CHANGE_PERCENT,
    StockField.VOLUME,
    StockField.MARKET_CAPITALIZATION
)
ss.where(StockField.MARKET_CAPITALIZATION > 1e9)
ss.where(StockField.CHANGE_PERCENT > 5)
df = ss.get()
```

### Pythonic 过滤语法

```python
ss = StockScreener()
ss.where(StockField.PRICE > 50)
ss.where(StockField.VOLUME >= 1_000_000)
ss.where(StockField.MARKET_CAPITALIZATION.between(1e9, 50e9))
ss.where(StockField.SECTOR.isin(['Technology', 'Healthcare']))
df = ss.get()
```

### 技术指标 + 多时间周期

```python
ss = StockScreener()

# RSI 1小时周期
rsi_1h = StockField.RELATIVE_STRENGTH_INDEX_14.with_interval("60")

# MACD 4小时周期
macd_4h = StockField.MACD_LEVEL_12_26.with_interval("240")

ss.specific_fields = [
    StockField.NAME,
    StockField.PRICE,
    rsi_1h,
    macd_4h,
]
df = ss.get()
```

**可用周期**: `1, 5, 15, 30, 60, 120, 240, 1D, 1W, 1M`

### Field Presets（预定义字段组）

| 类别 | Presets |
|------|---------|
| Stock | `stock_price`, `stock_volume`, `stock_valuation`, `stock_dividend`, `stock_profitability`, `stock_performance`, `stock_oscillators`, `stock_moving_averages`, `stock_earnings` |
| Crypto | `crypto_price`, `crypto_volume`, `crypto_performance`, `crypto_technical` |
| Forex | `forex_price`, `forex_performance`, `forex_technical` |
| Bond | `bond_basic`, `bond_yield`, `bond_maturity` |

```python
from tvscreener import StockScreener, STOCK_VALUATION_FIELDS, STOCK_DIVIDEND_FIELDS

ss = StockScreener()
ss.specific_fields = STOCK_VALUATION_FIELDS + STOCK_DIVIDEND_FIELDS
df = ss.get()
```

### Field Discovery（字段搜索）

```python
from tvscreener import StockField

# 搜索 RSI 相关字段
rsi_fields = StockField.search("rsi")
print(f"Found {len(rsi_fields)} RSI-related fields")

# 获取所有技术指标字段
technicals = StockField.technicals()

# 获取推荐评级字段
recommendations = StockField.recommendations()
```

### Streaming（实时刷新）

```python
ss = tvs.StockScreener()
ss.set_markets(tvs.Market.AMERICA)

for df in ss.stream(interval=10, max_iterations=5):
    print(f"Got {len(df)} rows")
```

## MCP Server（v0.2.0）

### 安装

```bash
pip install tvscreener[mcp]

# 运行 MCP Server
tvscreener-mcp

# 注册到 Claude Code
claude mcp add tvscreener -- tvscreener-mcp
```

### MCP Tools

| Tool | 功能 |
|------|------|
| `discover_fields` | 按关键词搜索 3500+ 可用字段 |
| `custom_query` | 灵活查询：任意字段 + 任意过滤 |
| `search_stocks` / `search_crypto` / `search_forex` | 简化版 Screener |
| `get_top_movers` | 获取涨跌幅 Top N |

**对 Hermes 的价值**：注册为 MCP Server 后，Hermes Agent 可直接调用 TradingView 数据做选股/盯盘，无需自行实现 HTTP 请求 + 数据解析。

## Styled Output

```python
import tvscreener as tvs

ss = tvs.StockScreener()
df = ss.get()
styled = tvs.beautify(df, tvs.StockField)
# Rating: 买入↑(蓝) / 卖出↓(红) / 中性-(灰)
# 百分比: 正绿负红
# 数字: K/M/B/T 后缀
```

## 💡 分析与借鉴

### 对用户量化交易系统的直接价值

| 场景 | 用法 |
|------|------|
| **选股五要件验证** | `StockField.PRICE > StockField.SMA(20)` + `CHANGE_PERCENT > 9.9`(涨停) + `VOLUME` 放量 |
| **14 条铁律程序化** | 换手率>40% 过滤、价格<6 元过滤、偏离 MA5 偏差计算 |
| **盘中盯盘** | `stream(interval=20)` 每 20 秒刷新持仓行情 |
| **板块效应检测** | `SECTOR.isin([...])` + `CHANGE_PERCENT` 排序 |
| **多周期技术指标** | RSI/MACD/MA 任意周期，无需 TradingView 注册 |

### 与 Hermes 量化系统的集成路径

| 路径 | 说明 |
|------|------|
| **MCP Server 注册** | `tvscreener[mcp]` 安装后注册到 Hermes config，Agent 直接查行情 |
| **替代腾讯接口** | 当前 shentan-price-alert.py 用腾讯 qt.gtimg.cn 拉行情，tvscreener 提供更丰富字段（13000+ vs 腾讯~30） |
| **选股自动化** | 结合 14 条铁律做每日选股扫描（当前用 short_term_screener.py + 同花顺 i问财） |
| **回测数据源** | TradingView 技术指标可直接用于策略回测 |

### 注意事项

| 风险 | 说明 |
|------|------|
| **非官方** | 依赖 TradingView 未公开 API，可能随时变更 |
| **A 股覆盖** | 需验证 A 股股票代码格式和字段完整性（沪深两市） |
| **速率限制** | 高频请求可能被 TradingView 限流 |
| **数据延迟** | 免费用户可能有 15 分钟延迟（需实测验证） |
| **Streaming 间隔** | 最小 1 秒，实战建议 ≥10 秒避免限流 |

## 关联

- → 相关：2026-08-12-股票交易14条铁律-严格执行.md
- → 相关：quant-trading.md（金融量化分析技能）
- → 相关：a-stock-quant-system.md（A 股量化系统开发）
- → 相关：stock-iron-rules.md（14 条铁律决策引擎）
- → 相关：iwencai-stock-screener.md（同花顺 i 问财选股）
- → 项目：~/uclaw/project/a-stock-quant-system/


## 相关笔记

- [LLM量化多智能体2026-AlphaCrafter与可持续Alpha挖掘](./2026-07-04-LLM量化多智能体2026-AlphaCrafter与可持续Alpha挖掘.md) — LLM 驱动的量化因子挖掘框架，选股数据源互补
- [LLM推理引擎2026格局-SGLang崛起与架构收敛](./2026-08-05-LLM推理引擎2026格局-SGLang崛起与架构收敛.md) — 推理引擎生态，量化模型部署基础设施
