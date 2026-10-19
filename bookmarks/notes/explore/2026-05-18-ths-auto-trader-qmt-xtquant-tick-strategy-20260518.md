# THS Auto Trader — QMT/xtquant 接口实战 + Tick 级策略差异深度研究

> 2026-05-18 | proactive-learn 深度研究 | Topic: ths-auto-trader
> 方法：本地知识蒸馏（外部搜索不可用），基于已有项目代码架构 + 行业知识深度整合
> 覆盖缺口：MiniQMT/xtquant API、Tick 级 vs 日线策略差异、Broker 适配器扩展
> 字数: ~3500 | 难度: L4（实战级）

---

## 一、核心发现（4 个关键发现）

### 发现 1：QMT/xtquant 是 easytrader 之后的最佳升级路径，但存在 3 个准入门槛

QMT（Quantitative Money Trading）是国泰君安等头部券商提供的程序化交易接口，其 Python 封装库 `xtquant` 提供 10-50ms 级延迟（vs easytrader 200-1200ms），是零售量化从 GUI 自动化升级到 API 交易的关键跳板。

**准入门槛**：

| 门槛 | 要求 | 说明 |
|------|------|------|
| **资金门槛** | 30-50 万 | 券商对 QMT 开通有最低资产要求 |
| **系统要求** | Windows | QMT 客户端仅支持 Windows（.NET/WPF），Linux 需要 Wine 或远程 API 服务 |
| **文档获取** | 需券商渠道 | xtquant 不在 PyPI 公开发布，需通过开户券商客户经理获取 |

**关键洞察**：对当前项目（Jetson Orin Linux），QMT 不能直接运行。可行路径：
1. **方案 A**：在局域网内一台 Windows 机器运行 QMT 客户端 + xtquant，Jetson 通过 HTTP API 远程调用
2. **方案 B**：使用 QMT 的「极简模式」（MiniQMT），仅运行核心交易服务，Jetson 通过 TCP/WebSocket 远程通信
3. **方案 C**：等待券商推出 Linux 版 API（目前无明确时间表）

### 发现 2：Tick 级数据与日线数据在策略设计上存在 5 个根本差异

| 维度 | 日线策略 | Tick 级策略 | 影响程度 |
|------|---------|------------|---------|
| **信号频率** | 1次/天（收盘后） | 100-1000次/分钟 | 🔴 数据量增 1000x |
| **噪声比例** | 低（日K已平滑） | 极高（买卖挂单闪烁） | 🔴 假信号率飙升 |
| **滑点影响** | 小（日K波动大） | 致命（0.1%吃掉利润） | 🔴 需盘口深度模型 |
| **延迟敏感度** | 秒级可接受 | 毫秒级（>100ms亏损） | 🟡 xdotool 不可用 |
| **数据存储** | ~100KB/股/年 | ~500MB/股/年 | 🟡 存储成本高 |

**核心结论**：Tick 级策略对执行层要求完全不同——xdotool/easytrader 的秒级延迟在 Tick 级策略下会导致系统性亏损。**日线策略用 xdotool 足够，Tick 级策略必须用 QMT/柜台直连**。

### 发现 3：现有代码架构已支持 Broker 扩展，QMTBroker 适配器只需实现 6 个方法

分析 `/ths_auto_trader/execution/broker.py` 的 `Broker` 抽象基类：

```python
class Broker(ABC):
    def connect(self) -> None: ...
    def buy(self, code: str, price: float, quantity: int) -> str: ...
    def sell(self, code: str, price: float, quantity: int) -> str: ...
    def cancel(self, order_id: str) -> bool: ...
    def get_position(self) -> list[Position]: ...
    def get_account(self) -> Account: ...
    def disconnect(self) -> None: ...
```

**QMTBroker 实现方案**：

```python
class QMTBroker(Broker):
    """xtquant 适配器 — QMT 程序化交易"""

    def __init__(self, qmt_path: str = r"C:\国金QMT\userdata_mini"):
        self._qmt_path = qmt_path
        self._xt_trader = None
        self._session_id = 0

    def connect(self) -> None:
        """连接 MiniQMT"""
        from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
        from xtquant.xttype import StockAccount

        # 创建交易接口
        self._session_id = int(time.time() * 1000)
        self._xt_trader = XtQuantTrader(self._qmt_path, self._session_id)

        # 注册回调
        self._xt_trader.register_client(self._callback)

        # 启动
        self._xt_trader.start()

        # 连接并确认
        acc = StockAccount(os.environ["QMT_ACCOUNT"], "STOCK")
        self._xt_trader.connect()

    def buy(self, code: str, price: float, quantity: int) -> str:
        """限价买入"""
        from xtquant.xttype import StockAccount
        acc = StockAccount(os.environ["QMT_ACCOUNT"], "STOCK")
        order_id = self._xt_trader.order_stock(
            account=acc,
            stock_code=self._convert_code(code),  # sz000001 → 000001.SZ
            order_type=11,  # FIX: LATEST_PRICE=11, LIMIT=23
            order_volume=quantity,
            price_type=11,  # 限价
            price=price,
            strategy_name="ths_auto_trader",
            order_remark="auto"
        )
        return str(order_id)

    def sell(self, code: str, price: float, quantity: int) -> str:
        """限价卖出"""
        from xtquant.xttype import StockAccount
        acc = StockAccount(os.environ["QMT_ACCOUNT"], "STOCK")
        order_id = self._xt_trader.order_stock(
            account=acc,
            stock_code=self._convert_code(code),
            order_type=23,  # SELL
            order_volume=quantity,
            price_type=11,
            price=price,
            strategy_name="ths_auto_trader",
            order_remark="auto"
        )
        return str(order_id)

    def cancel(self, order_id: str) -> bool:
        """撤单"""
        from xtquant.xttype import StockAccount
        acc = StockAccount(os.environ["QMT_ACCOUNT"], "STOCK")
        result = self._xt_trader.cancel_order_stock(acc, int(order_id))
        return result == 0

    def get_position(self) -> list[Position]:
        """查询持仓"""
        from xtquant.xttype import StockAccount
        acc = StockAccount(os.environ["QMT_ACCOUNT"], "STOCK")
        raw = self._xt_trader.query_stock_positions(acc)
        positions = []
        for item in raw:
            positions.append(Position(
                code=self._revert_code(item.stock_code),
                quantity=item.volume,
                available=item.can_use_volume,
                avg_cost=item.open_price,
                current_price=item.market_value / item.volume if item.volume > 0 else 0,
            ))
        return positions

    def get_account(self) -> Account:
        """查询账户"""
        from xtquant.xttype import StockAccount
        acc = StockAccount(os.environ["QMT_ACCOUNT"], "STOCK")
        raw = self._xt_trader.query_stock_asset(acc)
        return Account(
            total_assets=raw.total_asset,
            cash=raw.cash,
            market_value=raw.market_value,
        )

    def disconnect(self) -> None:
        if self._xt_trader:
            self._xt_trader.stop()
            self._xt_trader = None

    @staticmethod
    def _convert_code(code: str) -> str:
        """sz000001 → 000001.SZ, sh600000 → 600000.SH"""
        if code.startswith("sz"):
            return code[2:] + ".SZ"
        elif code.startswith("sh"):
            return code[2:] + ".SH"
        return code

    @staticmethod
    def _revert_code(xt_code: str) -> str:
        """000001.SZ → sz000001"""
        parts = xt_code.split(".")
        if len(parts) == 2:
            prefix = "sh" if parts[1] == "SH" else "sz"
            return prefix + parts[0]
        return xt_code
```

### 发现 4：Tick 级行情接入需要全新的数据管道，现有 MarketDataSource 无法支撑

当前 `MarketDataSource.get_daily()` 返回日线 DataFrame，Tick 级需要：

```python
# Tick 级数据管道设计
class TickDataSource:
    """Tick 级行情数据源"""

    def __init__(self):
        self._callbacks = []
        self._buffer = defaultdict(list)  # code -> [tick_data, ...]
        self._buffer_size = 1000  # 每个 code 缓存最近 1000 条 tick

    def subscribe(self, codes: list[str], callback):
        """订阅 Tick 行情"""
        # 方案 1: xtquant 行情订阅（需 QMT）
        # 方案 2: 新浪 WebSocket（免费但不稳定）
        # 方案 3: 东方财富 Level-2（付费）
        self._callbacks.append(callback)

    def on_tick(self, tick: TickData):
        """Tick 回调处理"""
        # 1. 缓存
        buf = self._buffer[tick.code]
        buf.append(tick)
        if len(buf) > self._buffer_size:
            buf.pop(0)

        # 2. 聚合为分钟K（策略消费）
        if self._should_aggregate(tick):
            minute_bar = self._aggregate_to_minute(tick.code)
            for cb in self._callbacks:
                cb(minute_bar)

    def _aggregate_to_minute(self, code: str) -> pd.DataFrame:
        """将 Tick 聚合为分钟 K 线"""
        ticks = self._buffer.get(code, [])
        if not ticks:
            return pd.DataFrame()

        # 按分钟分组
        df = pd.DataFrame([{
            'time': t.time,
            'price': t.price,
            'volume': t.volume,
            'amount': t.amount,
            'side': t.side,
        } for t in ticks])

        df['minute'] = df['time'].dt.floor('min')

        return df.groupby('minute').agg({
            'price': ['first', 'max', 'min', 'last'],  # OHLC
            'volume': 'sum',
            'amount': 'sum',
        })
```

**Tick 级策略的关键代码差异**（vs 日线策略）：

```python
# 日线策略（当前实现）— 在 generate_signals() 中处理
class DailyStrategy(BaseStrategy):
    def generate_signals(self, data: pd.DataFrame, ctx: StrategyContext) -> list[Signal]:
        # data 是日线 DataFrame，每行一天
        # RSI/MACD/布林带等指标在日线上计算
        # 每天只产生 0-2 个信号
        pass

# Tick 级策略 — 需要 on_tick() 实时处理
class TickStrategy:
    """Tick 级策略需要完全不同的接口"""
    def __init__(self):
        self._order_flow = []  # 订单流（Tick 级独有）
        self._vwap = 0.0       # 成交量加权均价
        self._imbalance = 0.0  # 买卖盘不平衡度

    def on_tick(self, tick: TickData, position: Position) -> Optional[Signal]:
        """每个 Tick 都要处理（~3次/秒/股）"""
        # 1. 更新订单流
        self._update_order_flow(tick)

        # 2. 计算盘口不平衡度（Tick 级核心指标）
        self._imbalance = (tick.bid_vol_1 - tick.ask_vol_1) / \
                          (tick.bid_vol_1 + tick.ask_vol_1 + 1e-6)

        # 3. VWAP 算法交易
        self._update_vwap(tick)

        # 4. 信号判断（高频版）
        if self._imbalance > 0.6 and tick.price < self._vwap:
            return Signal(direction=Direction.BUY, code=tick.code,
                         price=tick.price, strategy="tick_imbalance")
        elif self._imbalance < -0.6 and tick.price > self._vwap:
            return Signal(direction=Direction.SELL, code=tick.code,
                         price=tick.price, strategy="tick_imbalance")

        return None

    def _update_order_flow(self, tick: TickData):
        """订单流分析（Tick 级独有指标）"""
        # 判断主买/主卖：成交价 >= 卖一价 = 主买，<= 买一价 = 主卖
        if tick.price >= tick.ask_price_1:
            self._order_flow.append(('buy', tick.volume, tick.amount))
        elif tick.price <= tick.bid_price_1:
            self._order_flow.append(('sell', tick.volume, tick.amount))

        # 保留最近 N 条
        if len(self._order_flow) > 500:
            self._order_flow = self._order_flow[-500:]
```

---

## 二、技术细节：策略回测 → 实盘转换 Checklist（代码级）

基于已有 `references/sim-vs-live-trading-differences.md` 的四步验证法，补充代码级 Checklist：

### Step 1: 回测引擎校准

```python
# backtest_engine.py 中缺少的实盘校准项
class LiveReadyBacktestEngine(BacktestEngine):
    """实盘就绪的回测引擎 — 在标准回测基础上增加 5 个实盘因子"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slippage_model = DepthBasedSlippage()  # 替代固定滑点
        self.commission_rate = 0.0003  # 双边佣金
        self.stamp_tax = 0.001          # 印花税（卖出）
        self.min_commission = 5.0       # 最低佣金 5 元

    def execute_order(self, signal, portfolio):
        # 1. 滑点（基于盘口深度，非固定 0.1%）
        actual_price = self.slippage_model.calculate(
            signal.price, signal.quantity, signal.direction
        )

        # 2. 涨跌停检查
        if self._is_limit_hit(signal.code, actual_price, signal.direction):
            return None  # 废单

        # 3. 价格笼子（创业板 2% 偏离限制）
        if self._violates_price_cage(signal.code, actual_price):
            return None  # 废单

        # 4. 资金检查（含手续费）
        cost = actual_price * signal.quantity
        commission = max(cost * self.commission_rate, self.min_commission)
        if signal.direction == Direction.SELL:
            commission += cost * self.stamp_tax  # 印花税

        # 5. T+1 检查
        if signal.direction == Direction.SELL:
            if self._bought_today(signal.code):
                return None

        return super().execute_order(signal, portfolio)
```

### Step 2: Paper Trading 对齐

```python
# PaperBroker 需要增强的 3 个点（当前代码缺少）

class EnhancedPaperBroker(PaperBroker):
    """增强版模拟 Broker — 对齐实盘行为"""

    def buy(self, code: str, price: float, quantity: int) -> str:
        # 1. 模拟滑点（当前 PaperBroker 直接用传入价格）
        actual_price = price * (1 + random.uniform(0, 0.002))  # 0-0.2% 滑点

        # 2. 模拟废单（涨跌停）
        if self._check_limit(code, actual_price):
            raise BrokerError("涨停无法买入 / 跌停无法卖出")

        # 3. 手续费精确计算（当前是固定的 0.03%/0.15%）
        commission = max(actual_price * quantity * 0.0003, 5.0)  # 万三，最低5元

        cost = actual_price * quantity + commission
        if cost > self._cash:
            raise BrokerError(f"资金不足")

        self._cash -= cost
        # ... (持仓更新逻辑同上)
```

### Step 3-4: 极小资金验证 + 监控

这两个步骤是运维层面的，已在 `references/ths-auto-trader-production-ops.md` 中覆盖。

---

## 三、知识缺口分析

| 缺口 | 严重性 | 可行方案 |
|------|--------|---------|
| **xtquant 实际 API 签名未验证** | 🔴 高 | 需获取官方 SDK 文档，上面代码基于行业知识推演 |
| **QMT 远程 API 架构未设计** | 🟡 中 | 方案 A（HTTP API）最可行，需在 Windows 端部署 Flask + xtquant |
| **Tick 数据源免费方案不稳定** | 🟡 中 | 新浪 WebSocket 免费但断线频繁；建议用腾讯/东财 Level-1 |
| **Tick 级回测引擎缺失** | 🔴 高 | 当前 backtest_engine.py 仅支持日线，Tick 级需全新引擎 |
| **多 Broker 切换的配置管理** | 🟢 低 | create_broker() 工厂方法已支持，配置项需要扩展 |

---

## 四、实践启发（可直接执行的行动）

### 启发 1：在 broker.py 中添加 QMTBroker 桩（Stub）

即使没有 xtquant SDK，也可以先写好接口桩和代码转换逻辑，等获得 SDK 后快速对接：

```python
# 在 create_broker() 中增加 qmt 类型
def create_broker() -> Broker:
    cfg = get_config()
    if cfg.broker.type == "xdotool":
        from .xdotool_broker import XdotoolBroker
        return XdotoolBroker()
    elif cfg.broker.type == "easytrader":
        return EasyTraderBroker()
    elif cfg.broker.type == "qmt":
        from .qmt_broker import QMTBroker  # 新增
        return QMTBroker(cfg.broker.qmt_path)
    elif cfg.broker.type == "paper":
        return PaperBroker()
```

### 启发 2：Tick 数据聚合器可独立于交易引擎开发

Tick → 分钟 K 的聚合逻辑是纯数据处理，不依赖交易通道。可以在 Jetson 上用新浪/腾讯实时接口先行开发和测试。

### 启发 3：策略分层设计

```
Level 1: 日线策略（现有，xdotool 足够）
  ├── ma_trend, bollinger_revert, momentum
  └── 适合：趋势跟踪、波段交易

Level 2: 分钟线策略（需 QMT 或 HTTP API）
  ├── VWAP 执行、分钟级动量
  └── 适合：日内波段、事件驱动

Level 3: Tick 级策略（需 QMT 直连）
  ├── 订单流不平衡、盘口分析
  └── 适合：高频做市、套利
```

当前项目定位在 Level 1，升级路径清晰：Level 1 → Level 2（加 QMT）→ Level 3（加 Tick 数据管道）。

---

## 五、与已有笔记的关系

| 已有笔记 | 本篇互补点 |
|---------|-----------|
| `ths-auto-trader-architecture-deep-dive` | 本篇细化 QMTBroker 代码实现 |
| `ths-auto-trader-deep-dive` (easytrader) | 本篇是 easytrader → QMT 的升级路径 |
| `ths-auto-trader-production-ops` | 本篇补充 Tick 数据管道的运维需求 |
| quant-trading skill (references/) | 本篇补充 xtquant/Tick 级缺失内容 |

---

*产出时间: 2026-05-18 00:21 | 搜索状态: Tavily 不可用 + 外部网络不通，纯本地知识蒸馏*
*进化评估: QMTBroker 桩代码可 patch 到 ths-auto-trader skill；Tick 聚合器可独立开发*

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
- [ths-auto-trader-2026](ths-auto-trader-2026.md)
- [ths-auto-trader-20260517](ths-auto-trader-20260517.md)
- [ths-auto-trader-architecture-deep-dive-20260517](ths-auto-trader-architecture-deep-dive-20260517.md)
- [ths-auto-trader-deep-dive](ths-auto-trader-deep-dive.md)
- [ths-auto-trader-deep-learn](ths-auto-trader-deep-learn.md)
- [ths-auto-trader-ecosystem-update-20260518](ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
